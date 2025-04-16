"""
Simple Text Feature Extractor for Toronto Trendspotter

This module provides a simplified text feature extraction that doesn't rely heavily on NLTK.
It implements basic text processing and TF-IDF vectorization for content text.
"""

import os
import sys
import logging
import numpy as np
import re
import string
from pathlib import Path
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

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

class SimpleTextFeatureExtractor:
    """Extract features from text content without heavy NLTK dependencies"""
    
    def __init__(self):
        # Common English stopwords
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what', 
            'when', 'where', 'how', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'to', 'at', 'in', 'on', 'by',
            'with', 'about', 'for', 'of', 'this', 'that', 'these', 'those', 'it', 'its',
            'i', 'you', 'he', 'she', 'we', 'they', 'them', 'their', 'his', 'her', 'our',
            'your', 'my', 'from', 'then', 'than', 'so', 'which', 'who', 'whom', 'will',
            'would', 'should', 'could', 'can', 'may', 'might', 'must'
        }
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = None
        logger.info("Initialized SimpleTextFeatureExtractor")
    
    def preprocess_text(self, text):
        """
        Preprocess text for feature extraction
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove numbers
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenize by splitting on whitespace
        tokens = text.split()
        
        # Remove stopwords and short words
        processed_tokens = [
            token for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        # Join tokens back to text
        processed_text = ' '.join(processed_tokens)
        
        return processed_text
    
    def fit_vectorizer(self, texts, max_features=100):
        """
        Fit TF-IDF vectorizer on texts
        
        Args:
            texts (list): List of text strings
            max_features (int): Maximum number of features
            
        Returns:
            sklearn.feature_extraction.text.TfidfVectorizer: Fitted vectorizer
        """
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,  # Limit feature dimension
            min_df=2,  # Minimum document frequency
            max_df=0.85,  # Maximum document frequency
            stop_words='english',  # Additional stopwords removal
            ngram_range=(1, 2)  # Consider unigrams and bigrams
        )
        
        # Fit vectorizer on texts
        self.vectorizer.fit(texts)
        
        return self.vectorizer
    
    def extract_features(self, text):
        """
        Extract features from text
        
        Args:
            text (str): Text to extract features from
            
        Returns:
            numpy.ndarray: Feature vector
        """
        # Check if vectorizer is fitted
        if self.vectorizer is None:
            logger.error("Vectorizer not fitted. Call fit_vectorizer first.")
            return None
        
        # Preprocess text
        preprocessed_text = self.preprocess_text(text)
        
        if not preprocessed_text:
            # Return zero vector for empty text
            return np.zeros((self.vectorizer.max_features,))
        
        # Transform to feature vector
        features = self.vectorizer.transform([preprocessed_text])
        
        # Convert to dense array
        features_dense = features.toarray()[0]
        
        return features_dense
    
    def process_database_texts(self, limit=100, skip_existing=True, max_features=100):
        """
        Process texts from database and store feature vectors
        
        Args:
            limit (int): Maximum number of texts to process
            skip_existing (bool): Skip texts that already have features
            max_features (int): Maximum number of features in the vector
            
        Returns:
            int: Number of texts processed
        """
        # Initialize MongoDB connection
        mongo_db = get_mongodb_db()
        
        # Track processed texts
        processed_count = 0
        
        try:
            # Query for content from MongoDB
            logger.info(f"Querying MongoDB for content (limit={limit if limit else 'None'})")
            contents = list(mongo_db.content.find().limit(limit if limit else 0))
            logger.info(f"Found {len(contents)} content items to process")
            
            # Preprocess all texts for fitting vectorizer
            all_texts = []
            content_texts = {}
            
            logger.info("Preprocessing text for all content items...")
            for content in contents:
                # Combine title and description
                combined_text = f"{content.get('title', '')} {content.get('description', '')}"
                
                # Preprocess text
                preprocessed_text = self.preprocess_text(combined_text)
                
                if preprocessed_text:
                    all_texts.append(preprocessed_text)
                    content_texts[content["_id"]] = preprocessed_text
            
            if not all_texts:
                logger.warning("No valid texts found for processing")
                return 0
            
            # Fit vectorizer on all texts
            logger.info(f"Fitting TF-IDF vectorizer on {len(all_texts)} texts with max_features={max_features}")
            self.fit_vectorizer(all_texts, max_features=max_features)
            
            # Process each content item
            logger.info("Generating feature vectors for each content item...")
            for content_id, preprocessed_text in content_texts.items():
                # Check if features already exist
                if skip_existing:
                    existing = mongo_db.feature_vectors.find_one({
                        "content_id": content_id,
                        "feature_type": "text_tfidf"
                    })
                    if existing:
                        logger.debug(f"Features already exist for content {content_id}")
                        continue
                
                # Transform text to feature vector
                features = self.vectorizer.transform([preprocessed_text])
                features_dense = features.toarray()[0]
                
                # Create feature vector document
                feature_vector = create_feature_vector(
                    content_id=content_id,
                    feature_type="text_tfidf",
                    features=features_dense.tolist(),
                    metadata={
                        "vectorizer_vocab": list(self.vectorizer.vocabulary_.keys())
                    }
                )
                
                # Store in MongoDB
                mongo_db.feature_vectors.insert_one(feature_vector)
                
                processed_count += 1
                if processed_count % 100 == 0:
                    logger.info(f"Processed {processed_count} content items so far")
            
            # Store vectorizer vocabulary for future use
            logger.info("Storing vectorizer vocabulary in database")
            mongo_db.ml_models.insert_one({
                "model_type": "text_vectorizer",
                "vectorizer_vocab": list(self.vectorizer.vocabulary_.keys()),
                "max_features": max_features,
                "created_at": datetime.now()
            })
            
            logger.info(f"Successfully processed {processed_count} content items")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing database texts: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return processed_count


if __name__ == "__main__":
    # Simple test execution
    extractor = SimpleTextFeatureExtractor()
    num_processed = extractor.process_database_texts(limit=50)
    print(f"Processed {num_processed} text items")