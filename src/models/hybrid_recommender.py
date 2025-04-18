"""
Hybrid Recommendation System for Toronto Trendspotter

This module implements a hybrid recommendation system that combines collaborative filtering
and content-based approaches to provide better recommendations.
"""

import os
import sys
import logging
import numpy as np
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Add project root to path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models.recommendation_base import RecommendationBase
from src.models.collaborative_filtering import CollaborativeFiltering
from src.models.content_based import ContentBasedRecommender
from src.utils.db import get_mongodb_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HybridRecommender(RecommendationBase):
    """
    Hybrid recommendation system that combines multiple recommendation approaches.
    
    This class implements a weighted blend of collaborative filtering and content-based
    recommendations, with additional Toronto-specific features.
    """
    
    def __init__(self, name="hybrid_recommender", model_weights=None):
        """
        Initialize the hybrid recommendation system
        
        Args:
            name (str): Model name
            model_weights (dict): Weights for combining different models
        """
        super().__init__(name=name)
        
        if model_weights is None:
            model_weights = {
                "collaborative_filtering": 0.6,
                "content_based": 0.4
            }
        
        self.model_weights = model_weights
        self.models = {}
        self.parameters = {
            "model_weights": model_weights,
            "seasonal_boost": 0.2,
            "location_boost": 0.3,
            "popularity_boost": 0.1
        }
        
        logger.info(f"Initialized hybrid recommender with weights: {model_weights}")
    
    def _initialize_models(self):
        """Initialize all component models"""
        # Collaborative filtering model
        if "collaborative_filtering" not in self.models and self.model_weights.get("collaborative_filtering", 0) > 0:
            cf_model = CollaborativeFiltering(approach="item")
            
            # Try to load from database, or train if not available
            if not cf_model.load_model():
                logger.info("Training collaborative filtering model")
                cf_model.train()
                cf_model.save_model()
            
            self.models["collaborative_filtering"] = cf_model
            logger.info("Initialized collaborative filtering model")
        
        # Content-based model
        if "content_based" not in self.models and self.model_weights.get("content_based", 0) > 0:
            cb_model = ContentBasedRecommender()
            
            # Try to load from database, or train if not available
            if not cb_model.load_model():
                logger.info("Training content-based model")
                cb_model.train()
                cb_model.save_model()
            
            self.models["content_based"] = cb_model
            logger.info("Initialized content-based model")
    
    def train(self, **kwargs):
        """
        Train the hybrid recommendation model
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            bool: True if training was successful
        """
        # Update parameters if provided
        for key, value in kwargs.items():
            if key in self.parameters:
                self.parameters[key] = value
            elif key == "model_weights" and isinstance(value, dict):
                self.model_weights.update(value)
        
        # Initialize and train component models
        self._initialize_models()
        
        # The hybrid model is trained if all component models are trained
        self.is_trained = all(model.is_trained for model in self.models.values())
        
        if self.is_trained:
            logger.info("Successfully trained hybrid recommender")
        else:
            logger.error("Failed to train all component models")
            
        return self.is_trained
    
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
        
        # Get recommendations from each model
        all_recommendations = {}
        
        for model_name, model in self.models.items():
            weight = self.model_weights.get(model_name, 0)
            if weight <= 0:
                continue
            
            try:    
                # Get recommendations from this model
                model_recs = model.recommend_for_user(user_id, n=n*2)  # Get more to blend
                
                # Add to combined recommendations
                for rec in model_recs:
                    content_id = rec["content_id"]
                    score = rec["score"] * weight
                    
                    if content_id in all_recommendations:
                        all_recommendations[content_id]["score"] += score
                        all_recommendations[content_id]["sources"].append(model_name)
                    else:
                        all_recommendations[content_id] = {
                            "content_id": content_id,
                            "score": score,
                            "sources": [model_name]
                        }
            except Exception as e:
                # If a model fails, log it and continue with other models
                logger.warning(f"Error getting recommendations from {model_name} model: {e}")
                continue
        
        # If we have no recommendations, fall back to popular items
        if not all_recommendations and "content_based" in self.models:
            try:
                logger.info("No recommendations from component models, falling back to popular items")
                popular_recs = self.models["content_based"]._recommend_popular_items(n=n)
                
                for rec in popular_recs:
                    content_id = rec["content_id"]
                    all_recommendations[content_id] = {
                        "content_id": content_id,
                        "score": rec["score"],
                        "sources": ["popularity"]
                    }
            except Exception as e:
                logger.warning(f"Error getting popularity recommendations: {e}")
        
        # Apply Toronto-specific boosts
        self._apply_toronto_boosts(all_recommendations, user_id)
        
        # Sort and get top N
        sorted_recs = sorted(all_recommendations.values(), key=lambda x: x["score"], reverse=True)[:n]
        
        # Format the recommendations
        recommendations = []
        for rec in sorted_recs:
            recommendations.append({
                "content_id": rec["content_id"],
                "score": float(rec["score"]),
                "model": self.name,
                "approach": "hybrid",
                "sources": rec.get("sources", [])
            })
        
        return recommendations
    
    def _apply_toronto_boosts(self, recommendations, user_id):
        """
        Apply Toronto-specific boosts to recommendations
        
        Args:
            recommendations (dict): Recommendations to boost
            user_id (str): User ID
        """
        seasonal_boost = self.parameters.get("seasonal_boost", 0.2)
        location_boost = self.parameters.get("location_boost", 0.3)
        popularity_boost = self.parameters.get("popularity_boost", 0.1)
        
        # Get user's neighborhood preferences if available
        user_neighborhoods = set()
        
        # Check content-based model's user profiles
        if "content_based" in self.models:
            cb_model = self.models["content_based"]
            if hasattr(cb_model, "user_profiles") and user_id in cb_model.user_profiles:
                profile = cb_model.user_profiles[user_id]
                neighborhoods = profile.get("neighborhoods", {})
                
                # Add neighborhoods with significant preference
                for neighborhood, weight in neighborhoods.items():
                    if weight > 0.1:  # Threshold for considering it a preference
                        user_neighborhoods.add(neighborhood)
        
        # If no neighborhoods from profile, try to get from user document
        if not user_neighborhoods:
            user = self.get_user_data(user_id)
            if user and "neighborhood_preferences" in user:
                user_neighborhoods.update(user["neighborhood_preferences"])
        
        # Get current season
        current_season = self._get_current_season()
        
        # Apply boosts to each recommendation
        for content_id, rec in recommendations.items():
            # Get content data
            content = self.get_content_data(content_id)
            if not content:
                continue
            
            # 1. Seasonal boost
            if content.get("metadata", {}).get("seasonal_relevance") == current_season:
                rec["score"] += seasonal_boost
            
            # For events, check direct seasonal relevance
            event = self.db.toronto_events.find_one({"content_id": content_id})
            if event and "seasonal_relevance" in event:
                if current_season in event["seasonal_relevance"]:
                    rec["score"] += seasonal_boost * 1.5  # Stronger boost for events
            
            # 2. Location boost for neighborhood match
            if user_neighborhoods:
                content_neighborhood = content.get("location", {}).get("neighborhood")
                if content_neighborhood and content_neighborhood in user_neighborhoods:
                    rec["score"] += location_boost
            
            # 3. Popularity boost
            interaction_count = self.db.interactions.count_documents({"content_id": content_id})
            if interaction_count > 0:
                # Normalize by log to avoid too much bias towards very popular items
                popularity_score = np.log1p(interaction_count) / 10.0  # Scale to reasonable range
                rec["score"] += popularity_score * popularity_boost
    
    def _get_current_season(self):
        """
        Determine the current season based on date
        
        Returns:
            str: Current season
        """
        now = datetime.now()
        month = now.month
        
        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "fall"
        else:
            return "winter"
    
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
        
        # Prioritize content-based similarity for this task
        if "content_based" in self.models:
            return self.models["content_based"].recommend_similar_to_content(content_id, n=n, **kwargs)
        
        # Fall back to collaborative filtering if content-based not available
        elif "collaborative_filtering" in self.models:
            return self.models["collaborative_filtering"].recommend_similar_to_content(content_id, n=n, **kwargs)
        
        # If no models available, return empty list
        return []
    
    def get_toronto_specific_recommendations(self, user_id=None, location=None, season=None, n=10):
        """
        Get Toronto-specific recommendations based on location and season
        
        Args:
            user_id (str): Optional user ID for personalization
            location (dict): Location data with coordinates or neighborhood
            season (str): Season to filter by
            n (int): Number of recommendations to generate
            
        Returns:
            list: Recommended content IDs with scores
        """
        if not self.is_trained:
            logger.warning("Model not trained yet")
            return []
            
        # Prioritize content-based for location-aware recommendations
        if "content_based" not in self.models:
            logger.warning("Content-based model required for location-aware recommendations")
            return self.recommend_for_user(user_id, n=n) if user_id else []
            
        cb_model = self.models["content_based"]
        
        # Base recommendations on user if provided
        base_recommendations = {}
        if user_id:
            user_recs = self.recommend_for_user(user_id, n=n*2)
            
            for rec in user_recs:
                base_recommendations[rec["content_id"]] = {
                    "content_id": rec["content_id"],
                    "score": rec["score"],
                    "sources": rec.get("sources", [])
                }
        
        # Current season if not specified
        if not season:
            season = self._get_current_season()
        
        # Boost scores based on location and season
        query = {}
        
        # Add seasonal filter if specified
        if season:
            # For events collection, check seasonal_relevance
            seasonal_events = []
            event_query = {}
            if season:
                event_query["seasonal_relevance"] = season
            
            for event in self.db.toronto_events.find(event_query):
                seasonal_events.append(event["content_id"])
            
            # Add generic season tag for content collection
            if seasonal_events:
                query = {"$or": [
                    {"_id": {"$in": seasonal_events}},
                    {"tags": season}
                ]}
            else:
                query["tags"] = season
        
        # Add location filter if specified
        if location:
            neighborhood = location.get("neighborhood")
            if neighborhood:
                # Add neighborhood condition
                if "tags" in query:
                    # Add to existing query with $and
                    query = {"$and": [
                        query,
                        {"$or": [
                            {"location.neighborhood": neighborhood},
                            {"tags": neighborhood.lower().replace(" ", "-")}
                        ]}
                    ]}
                else:
                    # Create a new query
                    query["$or"] = [
                        {"location.neighborhood": neighborhood},
                        {"tags": neighborhood.lower().replace(" ", "-")}
                    ]
        
        # If no filters were applied, just return base recommendations
        if not query and base_recommendations:
            sorted_recs = sorted(base_recommendations.values(), key=lambda x: x["score"], reverse=True)[:n]
            
            # Format the recommendations
            recommendations = []
            for rec in sorted_recs:
                recommendations.append({
                    "content_id": rec["content_id"],
                    "score": float(rec["score"]),
                    "model": self.name,
                    "approach": "hybrid",
                    "sources": rec.get("sources", [])
                })
            
            return recommendations
        
        # Get relevant content
        filtered_content = list(self.db.content.find(query).limit(100))
        
        # Combine with base recommendations
        all_recommendations = base_recommendations.copy()
        
        for content in filtered_content:
            content_id = content["_id"]
            
            # Skip if already in recommendations
            if content_id in all_recommendations:
                # Boost score for matching criteria
                all_recommendations[content_id]["score"] += 0.5
                continue
                
            # Calculate base score
            base_score = 1.0
            
            # Adjust score based on content properties
            
            # Seasonal boost
            content_tags = content.get("tags", [])
            if season and season in content_tags:
                base_score += 0.3
            
            # Neighborhood boost
            if location and "location" in content:
                content_neighborhood = content["location"].get("neighborhood")
                if content_neighborhood and content_neighborhood == location.get("neighborhood"):
                    base_score += 0.5
            
            # Add to recommendations
            all_recommendations[content_id] = {
                "content_id": content_id,
                "score": base_score,
                "sources": ["toronto_specific"]
            }
        
        # Sort and get top N
        sorted_recs = sorted(all_recommendations.values(), key=lambda x: x["score"], reverse=True)[:n]
        
        # Format the recommendations
        recommendations = []
        for rec in sorted_recs:
            recommendations.append({
                "content_id": rec["content_id"],
                "score": float(rec["score"]),
                "model": self.name,
                "approach": "toronto_specific",
                "sources": rec.get("sources", [])
            })
        
        return recommendations
    
    def _save_to_db(self):
        """Save model data to database"""
        try:
            # For hybrid model, we save very little - mainly just the parameters
            # since the component models are saved separately
            
            model_data = {
                "model_type": self.name,
                "created_at": datetime.now(),
                "parameters": self.parameters,
                "model_weights": self.model_weights,
                "is_trained": self.is_trained,
                "component_models": list(self.models.keys())
            }
            
            # Check if model already exists
            existing = self.db.ml_models.find_one({"model_type": self.name})
            if existing:
                self.db.ml_models.update_one(
                    {"model_type": self.name},
                    {"$set": model_data}
                )
            else:
                self.db.ml_models.insert_one(model_data)
                
            logger.info("Saved hybrid model to database")
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
            self.model_weights = model_data.get("model_weights", {})
            
            # Initialize component models
            self._initialize_models()
            
            self.is_trained = model_data.get("is_trained", False)
            logger.info("Loaded hybrid model from database")
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
            logger.warning("Model not trained yet")
            return {"error": "Model not trained"}
        
        # If no test data provided, create test data from interactions
        if test_data is None:
            logger.info("Creating test set from interactions")
            # Create test set by hiding 20% of interactions
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
            try:
                user_id = test_item["user_id"]
                target_id = test_item["content_id"]
                
                # Get recommendations
                recs = self.recommend_for_user(user_id, n=10)
                rec_ids = [r["content_id"] for r in recs]
                
                # Check if target is in recommendations
                if target_id in rec_ids:
                    hits += 1
                    rank = rec_ids.index(target_id) + 1
                    reciprocal_ranks.append(1.0 / rank)
                
                total += 1
            except Exception as e:
                logger.warning(f"Error evaluating for user {user_id}: {e}")
                continue
        
        if total > 0:
            hr = hits / total
            mrr = sum(reciprocal_ranks) / total if reciprocal_ranks else 0
        else:
            hr = 0
            mrr = 0
        
        metrics = {
            "hit_rate": hr,
            "mean_reciprocal_rank": mrr,
            "num_test_users": total
        }
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics


if __name__ == "__main__":
    # Example usage
    model = HybridRecommender()
    model.train()
    model.save_model()
    
    # Example recommendation
    user_id = next(model.db.users.find().limit(1))["_id"]
    recommendations = model.recommend_for_user(user_id, n=5)
    print(f"Recommendations for user {user_id}:")
    for rec in recommendations:
        content = model.get_content_data(rec["content_id"])
        print(f"- {content['title']} (Score: {rec['score']:.4f}, Sources: {rec['sources']})")