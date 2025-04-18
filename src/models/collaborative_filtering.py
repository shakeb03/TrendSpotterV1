"""
Collaborative Filtering Recommendation for Toronto Trendspotter

This module implements collaborative filtering recommendation strategies including:
- User-based collaborative filtering
- Item-based collaborative filtering

These models analyze user-item interactions to find patterns and make recommendations.
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# Add project root to path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models.recommendation_base import RecommendationBase
from src.utils.db import get_mongodb_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CollaborativeFiltering(RecommendationBase):
    """
    Collaborative Filtering recommendation model.
    
    This class implements both user-based and item-based collaborative filtering,
    as well as matrix factorization approaches for recommendations.
    """
    
    def __init__(self, name="collaborative_filtering", approach="item"):
        """
        Initialize the collaborative filtering model
        
        Args:
            name (str): Model name
            approach (str): Recommendation approach ('user', 'item', or 'matrix')
        """
        super().__init__(name=name)
        self.approach = approach
        self.user_item_matrix = None
        self.user_factors = None
        self.item_factors = None
        self.user_map = {}  # Maps user_id to matrix index
        self.item_map = {}  # Maps content_id to matrix index
        self.rev_user_map = {}  # Reverse mapping
        self.rev_item_map = {}  # Reverse mapping
        self.item_similarity = None
        self.user_similarity = None
        self.parameters = {
            "approach": approach,
            "n_factors": 20,
            "min_interactions": 2
        }
        logger.info(f"Initialized {approach}-based collaborative filtering")
    
    def _create_user_item_matrix(self, interaction_threshold=2):
        """
        Create user-item interaction matrix from database
        
        Args:
            interaction_threshold (int): Minimum number of interactions to include a user
            
        Returns:
            scipy.sparse.csr_matrix: User-item interaction matrix
        """
        logger.info("Creating user-item interaction matrix...")
        
        # Get all interactions
        interactions = list(self.db.interactions.find({}))
        logger.info(f"Found {len(interactions)} interactions")
        
        # Create interaction dataframe
        interaction_data = []
        for interaction in interactions:
            interaction_data.append({
                "user_id": interaction["user_id"],
                "content_id": interaction["content_id"],
                "interaction_type": interaction["interaction_type"],
                "timestamp": interaction["timestamp"]
            })
        
        if not interaction_data:
            logger.error("No interaction data found")
            return None
            
        df = pd.DataFrame(interaction_data)
        
        # Create weighted interaction strength based on interaction type
        interaction_weights = {
            "view": 1.0,
            "click": 2.0,
            "save": 3.0,
            "share": 4.0
        }
        
        df["weight"] = df["interaction_type"].map(interaction_weights)
        
        # Aggregate interactions by user and content
        df_agg = df.groupby(["user_id", "content_id"])["weight"].sum().reset_index()
        
        # Filter users with few interactions
        user_interaction_counts = df["user_id"].value_counts()
        active_users = user_interaction_counts[user_interaction_counts >= interaction_threshold].index
        df_agg = df_agg[df_agg["user_id"].isin(active_users)]
        
        # Create mappings between IDs and matrix indices
        unique_users = df_agg["user_id"].unique()
        unique_items = df_agg["content_id"].unique()
        
        self.user_map = {user_id: i for i, user_id in enumerate(unique_users)}
        self.item_map = {content_id: i for i, content_id in enumerate(unique_items)}
        
        self.rev_user_map = {i: user_id for user_id, i in self.user_map.items()}
        self.rev_item_map = {i: content_id for content_id, i in self.item_map.items()}
        
        # Create sparse matrix
        rows = df_agg["user_id"].map(self.user_map)
        cols = df_agg["content_id"].map(self.item_map)
        data = df_agg["weight"]
        
        matrix = csr_matrix((data, (rows, cols)), shape=(len(unique_users), len(unique_items)))
        
        logger.info(f"Created matrix with {matrix.shape[0]} users and {matrix.shape[1]} items")
        return matrix
    
    def _train_item_based(self):
        """Train an item-based collaborative filtering model"""
        if self.user_item_matrix is None or self.user_item_matrix.shape[0] == 0:
            logger.error("Cannot train - empty user-item matrix")
            return False
            
        logger.info("Training item-based collaborative filtering model")
        
        # Calculate item-item similarity matrix
        self.item_similarity = cosine_similarity(self.user_item_matrix.T)
        
        logger.info(f"Calculated item similarity matrix with shape {self.item_similarity.shape}")
        return True
    
    def _train_user_based(self):
        """Train a user-based collaborative filtering model"""
        if self.user_item_matrix is None or self.user_item_matrix.shape[0] == 0:
            logger.error("Cannot train - empty user-item matrix")
            return False
            
        logger.info("Training user-based collaborative filtering model")
        
        # Calculate user-user similarity matrix
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        
        logger.info(f"Calculated user similarity matrix with shape {self.user_similarity.shape}")
        return True
    
    def _train_matrix_factorization(self):
        """Train a matrix factorization model"""
        if self.user_item_matrix is None or self.user_item_matrix.shape[0] == 0:
            logger.error("Cannot train - empty user-item matrix")
            return False
            
        logger.info("Training matrix factorization model")
        
        # Normalize the matrix
        matrix_norm = self.user_item_matrix.copy()
        
        # Replace zeros with NaN for normalization
        matrix_dense = matrix_norm.toarray()
        matrix_mean = np.nanmean(np.where(matrix_dense > 0, matrix_dense, np.nan), axis=1)
        matrix_mean = np.nan_to_num(matrix_mean)
        
        # Subtract mean for each user
        for i in range(matrix_dense.shape[0]):
            matrix_dense[i, matrix_dense[i, :] > 0] -= matrix_mean[i]
        
        # Replace NaN with zero
        matrix_dense = np.nan_to_num(matrix_dense)
        
        # Perform SVD
        U, sigma, Vt = svds(matrix_dense, k=self.parameters["n_factors"])
        
        # Convert to more convenient representation
        sigma_diag = np.diag(sigma)
        self.user_factors = U
        self.item_factors = Vt.T
        self.user_means = matrix_mean
        
        logger.info(f"Trained matrix factorization with {self.parameters['n_factors']} factors")
        return True
    
    def train(self, min_interactions=2, n_factors=20, **kwargs):
        """
        Train the collaborative filtering model
        
        Args:
            min_interactions (int): Minimum interactions for a user to be included
            n_factors (int): Number of latent factors for matrix factorization
            **kwargs: Additional parameters
            
        Returns:
            bool: True if training was successful
        """
        # Update parameters
        self.parameters["min_interactions"] = min_interactions
        self.parameters["n_factors"] = n_factors
        
        # Create user-item matrix
        self.user_item_matrix = self._create_user_item_matrix(interaction_threshold=min_interactions)
        if self.user_item_matrix is None:
            return False
        
        # Train based on the selected approach
        if self.approach == "item":
            success = self._train_item_based()
        elif self.approach == "user":
            success = self._train_user_based()
        elif self.approach == "matrix":
            success = self._train_matrix_factorization()
        else:
            logger.error(f"Unknown approach: {self.approach}")
            return False
        
        if success:
            self.is_trained = True
            logger.info(f"Successfully trained {self.approach}-based collaborative filtering")
        else:
            logger.error(f"Failed to train {self.approach}-based collaborative filtering")
            
        return success
    
    def recommend_for_user(self, user_id, n=10, **kwargs):
        """
        Generate recommendations for a specific user
        
        Args:
            user_id (str): User ID
            n (int): Number of recommendations to generate
            **kwargs: Additional parameters
            
        Returns:
            list: Recommended content IDs with scores
        """
        if not self.is_trained:
            logger.warning("Model not trained yet")
            return []
        
        # Handle case where matrix is None
        if self.user_item_matrix is None:
            logger.warning("User-item matrix not loaded, recreating it...")
            self.user_item_matrix = self._create_user_item_matrix(interaction_threshold=self.parameters.get("min_interactions", 2))
            
            # If still None, return popular items
            if self.user_item_matrix is None:
                logger.warning("Failed to create user-item matrix, using popularity fallback")
                return self._recommend_popular_items(n=n)
        
        # Handle case where user is not in training data
        if user_id not in self.user_map:
            logger.warning(f"User {user_id} not in training data, using content popularity")
            return self._recommend_popular_items(n=n)
        
        user_idx = self.user_map[user_id]
        
        if self.approach == "item":
            return self._recommend_item_based(user_idx, n=n)
        elif self.approach == "user":
            return self._recommend_user_based(user_idx, n=n)
        elif self.approach == "matrix":
            return self._recommend_matrix_factorization(user_idx, n=n)
        else:
            logger.error(f"Unknown approach: {self.approach}")
            return []
    
    def _recommend_item_based(self, user_idx, n=10):
        """Generate recommendations using item-based collaborative filtering"""
        # Get user's interactions
        user_interactions = self.user_item_matrix[user_idx].toarray().flatten()
        interacted_items = np.where(user_interactions > 0)[0]
        
        if len(interacted_items) == 0:
            return self._recommend_popular_items(n=n)
        
        # Calculate scores for all items
        scores = np.zeros(self.user_item_matrix.shape[1])
        
        for item_idx in interacted_items:
            # Get similarity scores of this item to all others
            similar_items = self.item_similarity[item_idx]
            # Weight by the user's interaction with this item
            weight = user_interactions[item_idx]
            scores += similar_items * weight
        
        # Zero out items the user has already interacted with
        scores[interacted_items] = 0
        
        # Get top N items
        top_indices = np.argsort(-scores)[:n]
        
        recommendations = []
        for idx in top_indices:
            if scores[idx] > 0:
                content_id = self.rev_item_map[idx]
                recommendations.append({
                    "content_id": content_id,
                    "score": float(scores[idx]),
                    "model": self.name,
                    "approach": "item-based CF"
                })
        
        return recommendations
    
    def _recommend_user_based(self, user_idx, n=10):
        """Generate recommendations using user-based collaborative filtering"""
        # Find similar users
        user_similarities = self.user_similarity[user_idx]
        
        # Get items the user has interacted with
        user_interactions = self.user_item_matrix[user_idx].toarray().flatten()
        interacted_items = set(np.where(user_interactions > 0)[0])
        
        # Calculate scores for all items
        scores = np.zeros(self.user_item_matrix.shape[1])
        
        # For each item
        for item_idx in range(self.user_item_matrix.shape[1]):
            # Skip if the user has already interacted with this item
            if item_idx in interacted_items:
                continue
                
            # Find users who have interacted with this item
            item_users = np.where(self.user_item_matrix.toarray()[:, item_idx] > 0)[0]
            
            # Skip if no users have interacted with this item
            if len(item_users) == 0:
                continue
                
            # Calculate weighted average of similar users' interactions
            weighted_sum = 0
            similarity_sum = 0
            
            for other_user_idx in item_users:
                similarity = user_similarities[other_user_idx]
                if similarity <= 0:
                    continue
                    
                # Get other user's interactions with this item
                interaction_weight = self.user_item_matrix[other_user_idx, item_idx]
                weighted_sum += similarity * interaction_weight
                similarity_sum += similarity
            
            if similarity_sum > 0:
                scores[item_idx] = weighted_sum / similarity_sum
        
        # Get top N items
        top_indices = np.argsort(-scores)[:n]
        
        recommendations = []
        for idx in top_indices:
            if scores[idx] > 0:
                content_id = self.rev_item_map[idx]
                recommendations.append({
                    "content_id": content_id,
                    "score": float(scores[idx]),
                    "model": self.name,
                    "approach": "user-based CF"
                })
        
        return recommendations
    
    def _recommend_matrix_factorization(self, user_idx, n=10):
        """Generate recommendations using matrix factorization"""
        if self.user_factors is None or self.item_factors is None:
            logger.error("Matrix factorization model not trained")
            return []
            
        # Get user's predicted ratings
        user_pred = np.dot(self.user_factors[user_idx], self.item_factors.T) + self.user_means[user_idx]
        
        # Get user's interactions to exclude already interacted items
        user_interactions = self.user_item_matrix[user_idx].toarray().flatten()
        interacted_items = np.where(user_interactions > 0)[0]
        
        # Zero out items the user has already interacted with
        user_pred[interacted_items] = 0
        
        # Get top N items
        top_indices = np.argsort(-user_pred)[:n]
        
        recommendations = []
        for idx in top_indices:
            if user_pred[idx] > 0:
                content_id = self.rev_item_map[idx]
                recommendations.append({
                    "content_id": content_id,
                    "score": float(user_pred[idx]),
                    "model": self.name,
                    "approach": "matrix factorization"
                })
        
        return recommendations
    
    def _recommend_popular_items(self, n=10):
        """Recommend the most popular items"""
        # Count interactions per item
        item_interactions = defaultdict(int)
        for interaction in self.db.interactions.find({}):
            item_interactions[interaction["content_id"]] += 1
        
        # Sort by popularity
        popular_items = sorted(item_interactions.items(), key=lambda x: x[1], reverse=True)
        
        # Get top N
        recommendations = []
        for content_id, count in popular_items[:n]:
            recommendations.append({
                "content_id": content_id,
                "score": float(count),
                "model": self.name,
                "approach": "popularity"
            })
        
        return recommendations
    
    def recommend_similar_to_content(self, content_id, n=10, **kwargs):
        """
        Find content similar to a specific item
        
        Args:
            content_id (str): Content ID
            n (int): Number of similar items to find
            **kwargs: Additional parameters
            
        Returns:
            list: Similar content IDs with scores
        """
        if not self.is_trained:
            logger.warning("Model not trained yet")
            return []
        
        # Handle case where content is not in training data
        if content_id not in self.item_map:
            logger.warning(f"Content {content_id} not in training data")
            return []
        
        item_idx = self.item_map[content_id]
        
        if self.approach == "item":
            # Get similarity scores for this item
            similarity_scores = self.item_similarity[item_idx]
            
            # Zero out the item itself
            similarity_scores[item_idx] = 0
            
            # Get top N items
            top_indices = np.argsort(-similarity_scores)[:n]
            
            recommendations = []
            for idx in top_indices:
                if similarity_scores[idx] > 0:
                    similar_id = self.rev_item_map[idx]
                    recommendations.append({
                        "content_id": similar_id,
                        "score": float(similarity_scores[idx]),
                        "model": self.name,
                        "approach": "item similarity"
                    })
            
            return recommendations
        elif self.approach == "matrix":
            # Use latent factors to determine similarity
            item_factors = self.item_factors[item_idx]
            
            # Calculate similarity using dot product
            similarity_scores = np.dot(self.item_factors, item_factors)
            
            # Zero out the item itself
            similarity_scores[item_idx] = 0
            
            # Get top N items
            top_indices = np.argsort(-similarity_scores)[:n]
            
            recommendations = []
            for idx in top_indices:
                if similarity_scores[idx] > 0:
                    similar_id = self.rev_item_map[idx]
                    recommendations.append({
                        "content_id": similar_id,
                        "score": float(similarity_scores[idx]),
                        "model": self.name,
                        "approach": "latent factor similarity"
                    })
            
            return recommendations
        else:
            logger.warning(f"Content similarity not fully supported for {self.approach} approach")
            return []
    
    def _save_to_db(self):
        """Save model data to database"""
        try:
            # Prepare model data
            model_data = {
                "model_type": self.name,
                "created_at": datetime.now(),
                "parameters": self.parameters,
                "is_trained": self.is_trained,
                "approach": self.approach,
                "user_map": self.user_map,
                "item_map": self.item_map
            }
            
            # For item-based CF, save the similarity matrix
            if self.approach == "item" and self.item_similarity is not None:
                # Convert to list for MongoDB storage
                # We only save the top similarities to save space
                top_similarities = {}
                for item_idx in range(self.item_similarity.shape[0]):
                    item_id = self.rev_item_map[item_idx]
                    similarities = self.item_similarity[item_idx]
                    
                    # Get top 100 similarities
                    top_indices = np.argsort(-similarities)[:100]
                    top_similarities[item_id] = {
                        self.rev_item_map[idx]: float(similarities[idx])
                        for idx in top_indices if similarities[idx] > 0
                    }
                
                model_data["item_similarity"] = top_similarities
            
            # For user-based CF, save the similarity matrix
            elif self.approach == "user" and self.user_similarity is not None:
                # We only save the top similarities to save space
                top_similarities = {}
                for user_idx in range(self.user_similarity.shape[0]):
                    user_id = self.rev_user_map[user_idx]
                    similarities = self.user_similarity[user_idx]
                    
                    # Get top 100 similarities
                    top_indices = np.argsort(-similarities)[:100]
                    top_similarities[user_id] = {
                        self.rev_user_map[idx]: float(similarities[idx])
                        for idx in top_indices if similarities[idx] > 0
                    }
                
                model_data["user_similarity"] = top_similarities
            
            # For matrix factorization, save the factors
            elif self.approach == "matrix":
                if self.user_factors is not None and self.item_factors is not None:
                    # Convert numpy arrays to lists for MongoDB
                    model_data["user_factors"] = self.user_factors.tolist()
                    model_data["item_factors"] = self.item_factors.tolist()
                    model_data["user_means"] = self.user_means.tolist()
            
            # Check if model already exists
            existing = self.db.ml_models.find_one({"model_type": self.name})
            if existing:
                self.db.ml_models.update_one(
                    {"model_type": self.name},
                    {"$set": model_data}
                )
            else:
                self.db.ml_models.insert_one(model_data)
                
            logger.info(f"Saved {self.approach}-based model to database")
            return True
        except Exception as e:
            logger.error(f"Error saving model to database: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _load_from_db(self):
        """Load model data from database"""
        try:
            # Find model data
            model_data = self.db.ml_models.find_one({"model_type": self.name})
            if not model_data:
                logger.error(f"No saved model found for {self.name}")
                return False
            
            # Load parameters
            self.parameters = model_data.get("parameters", {})
            self.approach = model_data.get("approach", self.approach)
            self.user_map = model_data.get("user_map", {})
            self.item_map = model_data.get("item_map", {})
            
            # Create reverse mappings
            self.rev_user_map = {i: user_id for user_id, i in self.user_map.items()}
            self.rev_item_map = {i: content_id for content_id, i in self.item_map.items()}
            
            # Load approach-specific data
            if self.approach == "item" and "item_similarity" in model_data:
                # Convert from MongoDB format to numpy array
                item_similarity_dict = model_data["item_similarity"]
                n_items = len(self.item_map)
                self.item_similarity = np.zeros((n_items, n_items))
                
                for item_id, similarities in item_similarity_dict.items():
                    if item_id in self.item_map:
                        item_idx = self.item_map[item_id]
                        for other_id, similarity in similarities.items():
                            if other_id in self.item_map:
                                other_idx = self.item_map[other_id]
                                self.item_similarity[item_idx, other_idx] = similarity
            
            elif self.approach == "user" and "user_similarity" in model_data:
                # Convert from MongoDB format to numpy array
                user_similarity_dict = model_data["user_similarity"]
                n_users = len(self.user_map)
                self.user_similarity = np.zeros((n_users, n_users))
                
                for user_id, similarities in user_similarity_dict.items():
                    if user_id in self.user_map:
                        user_idx = self.user_map[user_id]
                        for other_id, similarity in similarities.items():
                            if other_id in self.user_map:
                                other_idx = self.user_map[other_id]
                                self.user_similarity[user_idx, other_idx] = similarity
            
            elif self.approach == "matrix":
                if "user_factors" in model_data and "item_factors" in model_data:
                    self.user_factors = np.array(model_data["user_factors"])
                    self.item_factors = np.array(model_data["item_factors"])
                    self.user_means = np.array(model_data["user_means"])
            
            self.is_trained = model_data.get("is_trained", False)
            logger.info(f"Loaded {self.approach}-based model from database")
            return True
        except Exception as e:
            logger.error(f"Error loading model from database: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _evaluate_model(self, test_data=None):
        """
        Evaluate the model using held-out test data
        
        Args:
            test_data: Test data for evaluation
            
        Returns:
            dict: Evaluation metrics
        """
        if not self.is_trained:
            return {"error": "Model not trained"}
            
        # If no test data provided, use random sampling
        if test_data is None:
            # Create test set by hiding 20% of interactions
            logger.info("Creating test set from 20% of interactions")
            all_interactions = list(self.db.interactions.find({}))
            np.random.shuffle(all_interactions)
            
            n_test = int(len(all_interactions) * 0.2)
            test_interactions = all_interactions[:n_test]
            
            # Create test data format
            test_data = []
            for interaction in test_interactions:
                test_data.append({
                    "user_id": interaction["user_id"],
                    "content_id": interaction["content_id"],
                    "rating": 1.0  # Binary interaction
                })
        
        # Calculate metrics
        hits = 0
        total = 0
        reciprocal_ranks = []
        
        for test_item in test_data:
            user_id = test_item["user_id"]
            target_id = test_item["content_id"]
            
            # Skip users not in training set
            if user_id not in self.user_map:
                continue
            
            # Get recommendations
            recs = self.recommend_for_user(user_id, n=10)
            rec_ids = [r["content_id"] for r in recs]
            
            # Check if target is in recommendations
            if target_id in rec_ids:
                hits += 1
                rank = rec_ids.index(target_id) + 1
                reciprocal_ranks.append(1.0 / rank)
            
            total += 1
        
        if total > 0:
            hr = hits / total
            mrr = sum(reciprocal_ranks) / total if reciprocal_ranks else 0
        else:
            hr = 0
            mrr = 0
        
        metrics = {
            "hit_rate": hr,
            "mean_reciprocal_rank": mrr,
            "num_test_users": total,
            "approach": self.approach
        }
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics


if __name__ == "__main__":
    # Example usage
    model = CollaborativeFiltering(approach="item")
    model.train()
    model.save_model()
    
    # Example recommendation
    user_id = next(model.db.users.find().limit(1))["_id"]
    recommendations = model.recommend_for_user(user_id, n=5)
    print(f"Recommendations for user {user_id}:")
    for rec in recommendations:
        content = model.get_content_data(rec["content_id"])
        print(f"- {content['title']} (Score: {rec['score']:.4f})")