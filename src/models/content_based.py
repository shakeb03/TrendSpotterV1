"""
Content-Based Recommendation for Toronto Trendspotter

This module implements content-based recommendation strategies that analyze item features to
make recommendations based on content similarity and user preferences.
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime
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

class ContentBasedRecommender(RecommendationBase):
    """
    Content-based recommendation model.
    
    This class implements content-based filtering using text, category, and location
    features to recommend items similar to a user's preferences.
    """
    
    def __init__(self, name="content_based", feature_types=None):
        """
        Initialize the content-based recommendation model
        
        Args:
            name (str): Model name
            feature_types (list): Types of features to use (text, location, category)
        """
        super().__init__(name=name)
        
        if feature_types is None:
            feature_types = ["text", "location", "category"]
        
        self.feature_types = feature_types
        self.content_features = {}
        self.similarity_matrix = None
        self.content_map = {}  # Maps content_id to matrix index
        self.rev_content_map = {}  # Reverse mapping
        self.user_profiles = {}
        self.parameters = {
            "feature_types": feature_types,
            "feature_weights": {
                "text": 0.5,
                "location": 0.3,
                "category": 0.2
            }
        }
        logger.info(f"Initialized content-based recommender using {feature_types}")
    
    def _create_content_features(self):
        """
        Create content feature matrix from database
        
        Returns:
            dict: Feature matrices for each feature type
        """
        logger.info("Creating content feature matrices...")
        
        # Get all content items
        content_items = list(self.db.content.find({}))
        logger.info(f"Found {len(content_items)} content items")
        
        # Create mappings
        self.content_map = {item["_id"]: i for i, item in enumerate(content_items)}
        self.rev_content_map = {i: item["_id"] for i, item in enumerate(content_items)}
        
        result = {}
        
        # Process text features
        if "text" in self.feature_types:
            logger.info("Processing text features...")
            
            # Try to get text feature vectors
            text_vectors = list(self.db.feature_vectors.find({"feature_type": "text_simple"}))
            
            if text_vectors:
                # Create text feature matrix
                n_items = len(content_items)
                # Use a reasonable feature dimension
                feature_dim = len(text_vectors[0].get("features", [])) if text_vectors else 50
                text_matrix = np.zeros((n_items, feature_dim))
                
                # Fill in the matrix with available feature vectors
                text_map = {}
                for vector in text_vectors:
                    content_id = vector["content_id"]
                    if content_id in self.content_map:
                        idx = self.content_map[content_id]
                        features = vector["features"]
                        if isinstance(features, list):
                            text_matrix[idx, :] = features
                        text_map[content_id] = features
                
                if not any(np.any(text_matrix[i] != 0) for i in range(n_items)):
                    # If all vectors are zero, try to use category and tag information directly
                    logger.info("No text feature vectors found, using categories and tags")
                    self._create_category_features(content_items, result)
                else:
                    result["text"] = {
                        "matrix": text_matrix,
                        "map": text_map
                    }
                    logger.info(f"Created text feature matrix with shape {text_matrix.shape}")
            else:
                # If no text vectors, use category and tag information directly
                logger.info("No text feature vectors found, using categories and tags")
                self._create_category_features(content_items, result)
        
        # Process location features
        if "location" in self.feature_types:
            logger.info("Processing location features...")
            
            # Try to get location feature vectors
            location_vectors = list(self.db.feature_vectors.find({"feature_type": "location_simple"}))
            
            if location_vectors:
                logger.info(f"Found {len(location_vectors)} location feature vectors")
                
                # Create location feature matrix - we'll use a special format for geospatial data
                location_features = {}
                
                # Process each vector
                for vector in location_vectors:
                    content_id = vector["content_id"]
                    features = vector["features"]
                    location_features[content_id] = features
                
                result["location"] = {
                    "features": location_features
                }
                logger.info(f"Processed {len(location_features)} location feature vectors")
            else:
                # Try to extract location information directly from content items
                logger.info("No location feature vectors, using raw location data")
                location_features = {}
                
                # Get Toronto center coordinates for reference
                toronto_center = (43.6532, -79.3832)
                
                for item in content_items:
                    if "location" in item and item["location"]:
                        loc = item["location"]
                        lat = loc.get("latitude")
                        lon = loc.get("longitude")
                        neighborhood = loc.get("neighborhood")
                        
                        if lat and lon:
                            # Calculate distance from Toronto center
                            distance = ((lat - toronto_center[0]) ** 2 + 
                                       (lon - toronto_center[1]) ** 2) ** 0.5
                            
                            location_features[item["_id"]] = {
                                "coordinates": (lat, lon),
                                "neighborhood": neighborhood,
                                "distance_to_center": distance
                            }
                
                result["location"] = {
                    "features": location_features
                }
                logger.info(f"Extracted {len(location_features)} location features from content")
        
        return result
    
    def _create_category_features(self, content_items, result_dict):
        """
        Create category features from content tags and categories
        
        Args:
            content_items (list): List of content items
            result_dict (dict): Dictionary to store the result
        """
        logger.info("Creating category features from tags and categories")
        
        # Collect all unique tags and categories
        all_tags = set()
        all_categories = set()
        
        for item in content_items:
            tags = item.get("tags", [])
            categories = item.get("categories", [])
            
            all_tags.update(tags)
            all_categories.update(categories)
        
        # Create mapping from tags/categories to indices
        tag_to_idx = {tag: i for i, tag in enumerate(all_tags)}
        cat_to_idx = {cat: i + len(tag_to_idx) for i, cat in enumerate(all_categories)}
        
        # Create binary feature matrix
        n_items = len(content_items)
        n_features = len(tag_to_idx) + len(cat_to_idx)
        
        category_matrix = np.zeros((n_items, n_features))
        
        for i, item in enumerate(content_items):
            tags = item.get("tags", [])
            categories = item.get("categories", [])
            
            # Set tag features
            for tag in tags:
                if tag in tag_to_idx:
                    category_matrix[i, tag_to_idx[tag]] = 1
            
            # Set category features
            for cat in categories:
                if cat in cat_to_idx:
                    category_matrix[i, cat_to_idx[cat]] = 1
        
        # Store in result dictionary
        result_dict["category"] = {
            "matrix": category_matrix,
            "tag_map": tag_to_idx,
            "cat_map": cat_to_idx
        }
        
        logger.info(f"Created category feature matrix with {n_features} features")
    
    def _calculate_similarity_matrix(self):
        """
        Calculate similarity matrix between content items
        
        Returns:
            numpy.ndarray: Similarity matrix
        """
        # Get number of items
        n_items = len(self.content_map)
        
        # Initialize similarity matrix
        similarity = np.zeros((n_items, n_items))
        
        # Combine similarities from different feature types
        feature_weights = self.parameters["feature_weights"]
        
        # Process text features
        if "text" in self.content_features:
            logger.info("Calculating text-based similarity...")
            text_matrix = self.content_features["text"]["matrix"]
            text_similarity = cosine_similarity(text_matrix)
            similarity += text_similarity * feature_weights.get("text", 0.5)
        
        # Process category features
        if "category" in self.content_features:
            logger.info("Calculating category-based similarity...")
            category_matrix = self.content_features["category"]["matrix"]
            category_similarity = cosine_similarity(category_matrix)
            similarity += category_similarity * feature_weights.get("category", 0.2)
        
        # Process location features - this is special since it's not a matrix
        if "location" in self.content_features:
            logger.info("Calculating location-based similarity...")
            location_features = self.content_features["location"]["features"]
            
            # Calculate pairwise distances
            for i in range(n_items):
                content_id_i = self.rev_content_map[i]
                
                # Skip if no location data
                if content_id_i not in location_features:
                    continue
                
                loc_i = location_features[content_id_i]
                
                for j in range(n_items):
                    content_id_j = self.rev_content_map[j]
                    
                    # Skip if no location data
                    if content_id_j not in location_features:
                        continue
                    
                    loc_j = location_features[content_id_j]
                    
                    # Calculate similarity based on location
                    if "coordinates" in loc_i and "coordinates" in loc_j:
                        # Coordinates-based similarity
                        lat_i, lon_i = loc_i["coordinates"]
                        lat_j, lon_j = loc_j["coordinates"]
                        
                        # Calculate distance
                        distance = ((lat_i - lat_j) ** 2 + (lon_i - lon_j) ** 2) ** 0.5
                        
                        # Convert distance to similarity (closer = more similar)
                        # Using exponential decay: exp(-distance/scale)
                        scale = 0.05  # Adjust based on coordinate scale
                        loc_similarity = np.exp(-distance / scale)
                        
                        similarity[i, j] += loc_similarity * feature_weights.get("location", 0.3)
                    
                    # Additional bonus for same neighborhood
                    if "neighborhood" in loc_i and "neighborhood" in loc_j:
                        if loc_i["neighborhood"] == loc_j["neighborhood"]:
                            similarity[i, j] += 0.1 * feature_weights.get("location", 0.3)
        
        # Normalize similarity to [0, 1]
        row_maxes = similarity.max(axis=1, keepdims=True)
        row_maxes[row_maxes == 0] = 1.0  # Avoid division by zero
        similarity = similarity / row_maxes
        
        logger.info(f"Created content similarity matrix with shape {similarity.shape}")
        return similarity
    
    def _create_user_profiles(self):
        """
        Create user profiles based on their interaction history
        
        Returns:
            dict: User profiles
        """
        logger.info("Creating user profiles...")
        
        user_profiles = {}
        
        # Get all users
        users = list(self.db.users.find({}))
        logger.info(f"Found {len(users)} users")
        
        for user in users:
            user_id = user["_id"]
            
            # Get user interactions
            interactions = list(self.db.interactions.find({"user_id": user_id}))
            
            # Skip users with no interactions
            if not interactions:
                continue
            
            # Calculate weights based on interaction type
            interaction_weights = {
                "view": 1.0,
                "click": 2.0,
                "save": 3.0,
                "share": 4.0
            }
            
            # Create a weighted average of content features
            user_vector = np.zeros(100)  # Placeholder
            has_vector = False
            
            # For text features
            if "text" in self.content_features:
                text_matrix = self.content_features["text"]["matrix"]
                user_text_vector = np.zeros(text_matrix.shape[1])
                total_weight = 0
                
                for interaction in interactions:
                    content_id = interaction["content_id"]
                    if content_id in self.content_map:
                        idx = self.content_map[content_id]
                        weight = interaction_weights.get(interaction["interaction_type"], 1.0)
                        user_text_vector += text_matrix[idx] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    user_text_vector /= total_weight
                
                user_vector = user_text_vector
                has_vector = True
            
            # For category features
            elif "category" in self.content_features:
                category_matrix = self.content_features["category"]["matrix"]
                user_cat_vector = np.zeros(category_matrix.shape[1])
                total_weight = 0
                
                for interaction in interactions:
                    content_id = interaction["content_id"]
                    if content_id in self.content_map:
                        idx = self.content_map[content_id]
                        weight = interaction_weights.get(interaction["interaction_type"], 1.0)
                        user_cat_vector += category_matrix[idx] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    user_cat_vector /= total_weight
                
                user_vector = user_cat_vector
                has_vector = True
            
            # For location features - track preference by neighborhood
            neighborhood_preferences = defaultdict(float)
            
            if "location" in self.content_features:
                location_features = self.content_features["location"]["features"]
                total_weight = 0
                
                for interaction in interactions:
                    content_id = interaction["content_id"]
                    if content_id in location_features:
                        loc_data = location_features[content_id]
                        if "neighborhood" in loc_data and loc_data["neighborhood"]:
                            weight = interaction_weights.get(interaction["interaction_type"], 1.0)
                            neighborhood_preferences[loc_data["neighborhood"]] += weight
                            total_weight += weight
                
                # Normalize neighborhood preferences
                if total_weight > 0:
                    for neighborhood in neighborhood_preferences:
                        neighborhood_preferences[neighborhood] /= total_weight
            
            # Store user profile data
            if has_vector or neighborhood_preferences:
                user_profiles[user_id] = {
                    "vector": user_vector.tolist() if has_vector else None,
                    "neighborhoods": dict(neighborhood_preferences),
                    "interaction_count": len(interactions)
                }
        
        logger.info(f"Created {len(user_profiles)} user profiles")
        return user_profiles
    
    def train(self, **kwargs):
        """
        Train the content-based recommendation model
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            bool: True if training was successful
        """
        # Update parameters if provided
        for key, value in kwargs.items():
            if key in self.parameters:
                self.parameters[key] = value
        
        # Create content feature matrices
        self.content_features = self._create_content_features()
        if not self.content_features:
            logger.error("Failed to create content features")
            return False
        
        # Calculate content similarity matrix
        self.similarity_matrix = self._calculate_similarity_matrix()
        if self.similarity_matrix is None:
            logger.error("Failed to calculate similarity matrix")
            return False
        
        # Create user profiles
        self.user_profiles = self._create_user_profiles()
        
        self.is_trained = True
        logger.info("Successfully trained content-based recommender")
        return True
    
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
        
        # If we have a user profile, use it for recommendations
        if user_id in self.user_profiles:
            return self._recommend_based_on_profile(user_id, n=n, **kwargs)
        
        # If no profile, but we have interactions, use those
        interactions = list(self.db.interactions.find({"user_id": user_id}).sort("timestamp", -1).limit(10))
        
        if interactions:
            # Get most recent interactions
            recent_items = [interaction["content_id"] for interaction in interactions]
            return self._recommend_based_on_items(recent_items, n=n, **kwargs)
        
        # If no interactions, use popularity or random items
        logger.warning(f"No data for user {user_id}, using popularity-based recommendations")
        return self._recommend_popular_items(n=n)
    
    def _recommend_based_on_profile(self, user_id, n=10, **kwargs):
        """Generate recommendations based on user profile"""
        profile = self.user_profiles[user_id]
        
        # Get user's interacted items to exclude
        interacted_items = set()
        for interaction in self.db.interactions.find({"user_id": user_id}):
            interacted_items.add(interaction["content_id"])
        
        # Calculate scores for each item
        scores = {}
        
        # If we have a feature vector for the user
        if profile.get("vector") is not None:
            user_vector = np.array(profile["vector"])
            
            # Calculate similarity with all items
            if "text" in self.content_features:
                text_matrix = self.content_features["text"]["matrix"]
                for i, content_id in enumerate(self.rev_content_map.values()):
                    if content_id in interacted_items:
                        continue
                    scores[content_id] = scores.get(content_id, 0) + \
                                       cosine_similarity([user_vector], [text_matrix[i]])[0][0] * \
                                       self.parameters["feature_weights"].get("text", 0.5)
            
            elif "category" in self.content_features:
                category_matrix = self.content_features["category"]["matrix"]
                for i, content_id in enumerate(self.rev_content_map.values()):
                    if content_id in interacted_items:
                        continue
                    scores[content_id] = scores.get(content_id, 0) + \
                                       cosine_similarity([user_vector], [category_matrix[i]])[0][0] * \
                                       self.parameters["feature_weights"].get("category", 0.2)
        
        # If we have neighborhood preferences
        if profile.get("neighborhoods"):
            neighborhood_prefs = profile["neighborhoods"]
            
            # Boost scores for items in preferred neighborhoods
            if "location" in self.content_features:
                location_features = self.content_features["location"]["features"]
                
                for content_id, loc_data in location_features.items():
                    if content_id in interacted_items:
                        continue
                    
                    if "neighborhood" in loc_data and loc_data["neighborhood"] in neighborhood_prefs:
                        weight = neighborhood_prefs[loc_data["neighborhood"]]
                        scores[content_id] = scores.get(content_id, 0) + \
                                          weight * self.parameters["feature_weights"].get("location", 0.3)
        
        # Get top-scoring items
        top_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
        
        if not top_items:
            # If no scores were calculated, try similarity-based
            return self._recommend_based_on_items(list(interacted_items), n=n)
        
        recommendations = []
        for content_id, score in top_items:
            recommendations.append({
                "content_id": content_id,
                "score": float(score),
                "model": self.name,
                "approach": "user profile"
            })
        
        return recommendations
    
    def _recommend_based_on_items(self, content_ids, n=10, **kwargs):
        """Generate recommendations based on a list of content IDs"""
        # Get items that are similar to the ones the user has interacted with
        if not content_ids:
            return []
        
        # Get user's all interacted items to exclude
        user_id = kwargs.get("user_id")
        interacted_items = set()
        if user_id:
            for interaction in self.db.interactions.find({"user_id": user_id}):
                interacted_items.add(interaction["content_id"])
        
        # Calculate scores based on similarity to the provided items
        scores = defaultdict(float)
        
        for content_id in content_ids:
            if content_id not in self.content_map:
                continue
                
            item_idx = self.content_map[content_id]
            similar_items = self.similarity_matrix[item_idx]
            
            # Add similarity scores to the combined scores
            for j, score in enumerate(similar_items):
                if j == item_idx:
                    continue  # Skip the item itself
                
                similar_id = self.rev_content_map[j]
                
                # Skip items the user has already interacted with
                if similar_id in interacted_items:
                    continue
                    
                scores[similar_id] += score
        
        # Get top-scoring items
        top_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
        
        recommendations = []
        for content_id, score in top_items:
            recommendations.append({
                "content_id": content_id,
                "score": float(score),
                "model": self.name,
                "approach": "item similarity"
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
        if content_id not in self.content_map:
            logger.warning(f"Content {content_id} not in training data")
            return []
        
        # Get similarity scores for this item
        item_idx = self.content_map[content_id]
        similarity_scores = self.similarity_matrix[item_idx]
        
        # Zero out the item itself
        similarity_scores[item_idx] = 0
        
        # Get top N items
        top_indices = np.argsort(-similarity_scores)[:n]
        
        recommendations = []
        for idx in top_indices:
            if similarity_scores[idx] > 0:
                similar_id = self.rev_content_map[idx]
                recommendations.append({
                    "content_id": similar_id,
                    "score": float(similarity_scores[idx]),
                    "model": self.name,
                    "approach": "content similarity"
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
    
    def _extract_category_tags(self, content_id):
        """
        Extract categories and tags for a content item
        
        Args:
            content_id (str): Content ID
            
        Returns:
            tuple: (categories, tags)
        """
        content = self.get_content_data(content_id)
        if not content:
            return [], []
            
        categories = content.get("categories", [])
        tags = content.get("tags", [])
        
        return categories, tags
    
    def _extract_location_data(self, content_id):
        """
        Extract location data for a content item
        
        Args:
            content_id (str): Content ID
            
        Returns:
            dict: Location data
        """
        content = self.get_content_data(content_id)
        if not content or "location" not in content:
            return {}
            
        location = content["location"]
        
        # Extract neighborhood
        neighborhood = location.get("neighborhood")
        
        # Extract coordinates
        latitude = location.get("latitude")
        longitude = location.get("longitude")
        
        return {
            "neighborhood": neighborhood,
            "coordinates": (latitude, longitude) if latitude and longitude else None
        }
    
    def _save_to_db(self):
        """Save model data to database"""
        try:
            # Prepare model data
            model_data = {
                "model_type": self.name,
                "created_at": datetime.now(),
                "parameters": self.parameters,
                "is_trained": self.is_trained,
                "content_map": self.content_map
            }
            
            # We can't store the full similarity matrix easily, so we'll store top similarities per item
            if self.similarity_matrix is not None:
                top_similarities = {}
                for item_idx in range(self.similarity_matrix.shape[0]):
                    item_id = self.rev_content_map[item_idx]
                    similarities = self.similarity_matrix[item_idx]
                    
                    # Get top 50 similarities
                    top_indices = np.argsort(-similarities)[:50]
                    top_similarities[item_id] = {
                        self.rev_content_map[idx]: float(similarities[idx])
                        for idx in top_indices if similarities[idx] > 0
                    }
                
                model_data["top_similarities"] = top_similarities
            
            # Store user profiles
            if self.user_profiles:
                model_data["user_profiles_count"] = len(self.user_profiles)
                
                # We store user profiles separately to avoid too large documents
                # Delete existing user profiles for this model
                self.db.user_profiles.delete_many({"model_type": self.name})
                
                # Insert new user profiles
                profiles_to_insert = []
                for user_id, profile in self.user_profiles.items():
                    profiles_to_insert.append({
                        "model_type": self.name,
                        "user_id": user_id,
                        "vector": profile.get("vector"),
                        "neighborhoods": profile.get("neighborhoods", {}),
                        "interaction_count": profile.get("interaction_count", 0),
                        "created_at": datetime.now()
                    })
                
                if profiles_to_insert:
                    self.db.user_profiles.insert_many(profiles_to_insert)
            
            # Check if model already exists
            existing = self.db.ml_models.find_one({"model_type": self.name})
            if existing:
                self.db.ml_models.update_one(
                    {"model_type": self.name},
                    {"$set": model_data}
                )
            else:
                self.db.ml_models.insert_one(model_data)
                
            logger.info(f"Saved content-based model to database")
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
            self.content_map = model_data.get("content_map", {})
            self.rev_content_map = {i: content_id for content_id, i in self.content_map.items()}
            
            # Load similarity data
            if "top_similarities" in model_data:
                top_similarities = model_data["top_similarities"]
                n_items = len(self.content_map)
                self.similarity_matrix = np.zeros((n_items, n_items))
                
                for item_id, similarities in top_similarities.items():
                    if item_id in self.content_map:
                        item_idx = self.content_map[item_id]
                        for other_id, similarity in similarities.items():
                            if other_id in self.content_map:
                                other_idx = self.content_map[other_id]
                                self.similarity_matrix[item_idx, other_idx] = similarity
            
            # Load user profiles
            user_profiles_count = model_data.get("user_profiles_count", 0)
            if user_profiles_count > 0:
                self.user_profiles = {}
                
                # Retrieve user profiles
                profiles = self.db.user_profiles.find({"model_type": self.name})
                
                for profile in profiles:
                    user_id = profile["user_id"]
                    self.user_profiles[user_id] = {
                        "vector": profile.get("vector"),
                        "neighborhoods": profile.get("neighborhoods", {}),
                        "interaction_count": profile.get("interaction_count", 0)
                    }
                
                logger.info(f"Loaded {len(self.user_profiles)} user profiles")
            
            self.is_trained = model_data.get("is_trained", False)
            logger.info(f"Loaded content-based model from database")
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
            "num_test_users": total
        }
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics


if __name__ == "__main__":
    # Example usage
    model = ContentBasedRecommender()
    model.train()
    model.save_model()
    
    # Example recommendation
    user_id = next(model.db.users.find().limit(1))["_id"]
    recommendations = model.recommend_for_user(user_id, n=5)
    print(f"Recommendations for user {user_id}:")
    for rec in recommendations:
        content = model.get_content_data(rec["content_id"])
        print(f"- {content['title']} (Score: {rec['score']:.4f})")