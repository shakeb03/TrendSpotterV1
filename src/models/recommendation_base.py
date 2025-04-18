"""
Base Recommendation System for Toronto Trendspotter

This module provides the core architecture for the recommendation system,
defining common interfaces and functionality for different recommendation strategies.
"""

import os
import sys
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

# Add project root to path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.db import get_mongodb_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RecommendationBase(ABC):
    """Base class for all recommendation strategies"""
    
    def __init__(self, name="base"):
        """
        Initialize the recommendation system
        
        Args:
            name (str): Name of this recommendation strategy
        """
        self.name = name
        self.db = get_mongodb_db()
        self.model = None
        self.is_trained = False
        logger.info(f"Initialized {name} recommendation system")
    
    @abstractmethod
    def train(self, **kwargs):
        """
        Train the recommendation model
        
        Args:
            **kwargs: Additional training parameters
            
        Returns:
            bool: True if training was successful
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    def save_model(self, path=None):
        """
        Save the model to a file or database
        
        Args:
            path (str): Path to save the model, or None to save to database
            
        Returns:
            bool: True if save was successful
        """
        if not self.is_trained:
            logger.warning("Cannot save untrained model")
            return False
            
        if path:
            # Save to file
            os.makedirs(os.path.dirname(path), exist_ok=True)
            try:
                # Implementation depends on the specific model
                if hasattr(self, '_save_to_file'):
                    return self._save_to_file(path)
                logger.warning("File saving not implemented for this model")
                return False
            except Exception as e:
                logger.error(f"Error saving model to file: {e}")
                return False
        else:
            # Save to database
            try:
                if hasattr(self, '_save_to_db'):
                    return self._save_to_db()
                    
                # Generic implementation
                model_data = {
                    "model_type": self.name,
                    "created_at": datetime.now(),
                    "parameters": getattr(self, 'parameters', {}),
                    "is_trained": self.is_trained
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
                    
                return True
            except Exception as e:
                logger.error(f"Error saving model to database: {e}")
                return False
    
    def load_model(self, path=None):
        """
        Load the model from a file or database
        
        Args:
            path (str): Path to load the model from, or None to load from database
            
        Returns:
            bool: True if load was successful
        """
        if path:
            # Load from file
            if not os.path.exists(path):
                logger.error(f"Model file not found: {path}")
                return False
                
            try:
                # Implementation depends on the specific model
                if hasattr(self, '_load_from_file'):
                    success = self._load_from_file(path)
                    if success:
                        self.is_trained = True
                    return success
                logger.warning("File loading not implemented for this model")
                return False
            except Exception as e:
                logger.error(f"Error loading model from file: {e}")
                return False
        else:
            # Load from database
            try:
                if hasattr(self, '_load_from_db'):
                    success = self._load_from_db()
                    if success:
                        self.is_trained = True
                    return success
                    
                # Generic implementation
                model_data = self.db.ml_models.find_one({"model_type": self.name})
                if not model_data:
                    logger.error(f"No saved model found for {self.name}")
                    return False
                    
                self.parameters = model_data.get("parameters", {})
                self.is_trained = model_data.get("is_trained", False)
                return True
            except Exception as e:
                logger.error(f"Error loading model from database: {e}")
                return False
    
    def evaluate(self, test_data=None):
        """
        Evaluate the model performance
        
        Args:
            test_data: Test data for evaluation
            
        Returns:
            dict: Evaluation metrics
        """
        if not self.is_trained:
            logger.warning("Cannot evaluate untrained model")
            return {"error": "Model not trained"}
            
        # Default implementation - override in subclasses
        if hasattr(self, '_evaluate_model'):
            return self._evaluate_model(test_data)
            
        logger.warning("Evaluation not implemented for this model")
        return {"warning": "Evaluation not implemented"}

    def get_user_data(self, user_id):
        """
        Get user data from the database
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User data or None if not found
        """
        return self.db.users.find_one({"_id": user_id})
    
    def get_content_data(self, content_id):
        """
        Get content data from the database
        
        Args:
            content_id (str): Content ID
            
        Returns:
            dict: Content data or None if not found
        """
        return self.db.content.find_one({"_id": content_id})
    
    def get_interactions(self, user_id=None, content_id=None, limit=None):
        """
        Get interactions from the database
        
        Args:
            user_id (str): Filter by user ID
            content_id (str): Filter by content ID
            limit (int): Maximum number of interactions to return
            
        Returns:
            list: Interaction data
        """
        query = {}
        if user_id:
            query["user_id"] = user_id
        if content_id:
            query["content_id"] = content_id
            
        cursor = self.db.interactions.find(query)
        if limit:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    def get_feature_vector(self, content_id=None, user_id=None, feature_type=None):
        """
        Get a feature vector from the database
        
        Args:
            content_id (str): Content ID
            user_id (str): User ID
            feature_type (str): Type of feature vector
            
        Returns:
            dict: Feature vector data or None if not found
        """
        query = {}
        if content_id:
            query["content_id"] = content_id
        if user_id:
            query["user_id"] = user_id
        if feature_type:
            query["feature_type"] = feature_type
            
        return self.db.feature_vectors.find_one(query)
    
    def log_recommendation(self, user_id, content_ids, source):
        """
        Log a recommendation to the database
        
        Args:
            user_id (str): User ID
            content_ids (list): Recommended content IDs
            source (str): Source of the recommendation
            
        Returns:
            str: Recommendation log ID
        """
        recommendation_log = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "content_ids": content_ids,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "model_name": self.name
        }
        
        result = self.db.recommendation_logs.insert_one(recommendation_log)
        return result.inserted_id