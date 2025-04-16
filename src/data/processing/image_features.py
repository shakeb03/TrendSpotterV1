import os
import sys
import logging
import requests
import numpy as np
import tempfile
from pathlib import Path
from datetime import datetime
import tensorflow as tf
from io import BytesIO
from PIL import Image

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.utils.db import get_mongodb_db
from src.data.models.mongodb_models import create_feature_vector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageFeatureExtractor:
    """Extract features from images using pre-trained models"""
    
    def __init__(self):
        # Load MobileNetV2 model (without top classification layer)
        self.model = tf.keras.applications.MobileNetV2(
            include_top=False,
            weights='imagenet',
            input_shape=(224, 224, 3),
            pooling='avg'
        )
        logger.info("Loaded MobileNetV2 model for feature extraction")
    
    def preprocess_image(self, image_path_or_url):
        """
        Load and preprocess image for feature extraction
        
        Args:
            image_path_or_url (str): Local path or URL to image
            
        Returns:
            numpy.ndarray: Preprocessed image tensor or None if failed
        """
        try:
            if image_path_or_url.startswith(('http://', 'https://')):
                # Download image from URL
                response = requests.get(image_path_or_url, stream=True, timeout=10)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
            else:
                # Load image from local path
                img = Image.open(image_path_or_url)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to model input size
            img = img.resize((224, 224))
            
            # Convert to numpy array and preprocess
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path_or_url}: {e}")
            return None
    
    def extract_features(self, image_path_or_url):
        """
        Extract features from an image
        
        Args:
            image_path_or_url (str): Local path or URL to image
            
        Returns:
            numpy.ndarray: Feature vector or None if failed
        """
        try:
            # Preprocess image
            preprocessed_img = self.preprocess_image(image_path_or_url)
            
            if preprocessed_img is None:
                return None
            
            # Extract features
            features = self.model.predict(preprocessed_img)
            
            # Flatten features to 1D array
            features = features.flatten()
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from image {image_path_or_url}: {e}")
            return None
    
    def process_database_images(self, limit=100, skip_existing=True):
        """
        Process images from database and store feature vectors
        
        Args:
            limit (int): Maximum number of images to process
            skip_existing (bool): Skip images that already have features
            
        Returns:
            int: Number of images processed
        """
        # Initialize MongoDB connection
        mongo_db = get_mongodb_db()
        
        # Track processed images
        processed_count = 0
        
        try:
            # Query for content with image URLs
            filter_criteria = {
                "image_url": {"$ne": ""},
                "image_url": {"$exists": True}
            }
            
            # Get content from MongoDB
            contents = mongo_db.content.find(filter_criteria).limit(limit if limit else 0)
            
            for content in contents:
                content_id = content["_id"]
                
                # Check if features already exist
                if skip_existing:
                    existing = mongo_db.feature_vectors.find_one({
                        "content_id": content_id,
                        "feature_type": "image_mobilenet"
                    })
                    if existing:
                        logger.debug(f"Features already exist for content {content_id}")
                        continue
                
                # Extract features
                logger.info(f"Processing image for content {content_id}: {content['image_url']}")
                features = self.extract_features(content['image_url'])
                
                if features is not None:
                    # Create feature vector document
                    feature_vector = create_feature_vector(
                        content_id=content_id,
                        feature_type="image_mobilenet",
                        features=features.tolist(),  # Convert numpy array to list for MongoDB
                        metadata={
                            "model": "MobileNetV2",
                            "dimension": features.shape[0]
                        }
                    )
                    
                    # Store in MongoDB
                    mongo_db.feature_vectors.insert_one(feature_vector)
                    
                    processed_count += 1
                    logger.info(f"Stored features for content {content_id}")
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing database images: {e}")
            return processed_count


if __name__ == "__main__":
    # Simple test execution
    extractor = ImageFeatureExtractor()
    num_processed = extractor.process_database_images(limit=10)
    print(f"Processed {num_processed} images")