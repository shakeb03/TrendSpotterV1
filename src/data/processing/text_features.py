import os
import sys
import logging
import numpy as np
import re
import ssl
from pathlib import Path
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

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

class TextFeatureExtractor:
    """Extract features from text content"""
    
    def __init__(self):
        # Download NLTK resources with SSL verification disabled if needed
        try:
            # Try to create an unverified SSL context to bypass certificate issues
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
                
            # Check if NLTK resources exist, download if needed
            nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
            os.makedirs(nltk_data_dir, exist_ok=True)
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', download_dir=nltk_data_dir, quiet=True)
            
            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                nltk.download('wordnet', download_dir=nltk_data_dir, quiet=True)
                
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', download_dir=nltk_data_dir, quiet=True)
                
            # Open Multilingual Wordnet
            try:
                nltk.data.find('corpora/omw-1.4')
            except LookupError:
                try:
                    nltk.download('omw-1.4', download_dir=nltk_data_dir, quiet=True)
                except:
                    logger.warning("Could not download omw-1.4, will proceed without it")
        
        except Exception as e:
            logger.warning(f"Error downloading NLTK resources: {e}")
            logger.warning("Try running the download_nltk_data.py script first")
        
        # Initialize stopwords and lemmatizer
        try:
            self.stop_words = set(nltk.corpus.stopwords.words('english'))
        except:
            logger.warning("Could not load stopwords, using a minimal set")
            self.stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 
                              'as', 'what', 'when', 'where', 'how', 'is', 'are', 'was', 
                              'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
                              'does', 'did', 'to', 'at', 'in', 'on', 'by', 'with', 'about', 
                              'for', 'of', 'this', 'that', 'these', 'those'}
        
        try:
            self.lemmatizer = nltk.stem.WordNetLemmatizer()
        except:
            logger.warning("Could not initialize WordNetLemmatizer, will use identity function")
            self.lemmatizer = type('', (), {'lemmatize': lambda self, word, *args, **kwargs: word})()
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = None
        logger.info("Initialized TextFeatureExtractor")
    
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
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenize
        tokens = nltk.word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        # Join tokens back to text
        processed_text = ' '.join(processed_tokens)
        
        return processed_text
    
    def fit_vectorizer(self, texts):
        """
        Fit TF-IDF vectorizer on texts
        
        Args:
            texts (list): List of text strings
            
        Returns:
            sklearn.feature_extraction.text.TfidfVectorizer: Fitted vectorizer
        """
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=100,  # Limit feature dimension
            min_df=2,  # Minimum document frequency
            max_df=0.85,  # Maximum document frequency
            stop_words='english',  # Additional stopwords removal
            ngram_range=(1, 2)  # Consider unigrams and bigrams
        )
        
        # Fit vectorizer on preprocessed texts
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
    
    def process_database_texts(self, limit=100, skip_existing=True):
        """
        Process texts from database and store feature vectors
        
        Args:
            limit (int): Maximum number of texts to process
            skip_existing (bool): Skip texts that already have features
            
        Returns:
            int: Number of texts processed
        """
        # Initialize MongoDB connection
        mongo_db = get_mongodb_db()
        
        # Track processed texts
        processed_count = 0
        
        try:
            # Query for content from MongoDB
            contents = mongo_db.content.find().limit(limit if limit else 0)
            
            # Preprocess all texts for fitting vectorizer
            all_texts = []
            content_texts = {}
            
            for content in contents:
                # Combine title and description
                combined_text = f"{content['title']} {content.get('description', '')}"
                
                # Preprocess text
                preprocessed_text = self.preprocess_text(combined_text)
                
                if preprocessed_text:
                    all_texts.append(preprocessed_text)
                    content_texts[content["_id"]] = preprocessed_text
            
            if not all_texts:
                logger.warning("No valid texts found for processing")
                return 0
            
            # Fit vectorizer on all texts
            self.fit_vectorizer(all_texts)
            logger.info(f"Fitted vectorizer with {len(all_texts)} texts")
            
            # Process each content item
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
                logger.info(f"Stored text features for content {content_id}")
            
            # Store vectorizer vocabulary for future use
            mongo_db.ml_models.insert_one({
                "model_type": "text_vectorizer",
                "vectorizer_vocab": list(self.vectorizer.vocabulary_.keys()),
                "created_at": datetime.now()
            })
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing database texts: {e}")
            return processed_count


if __name__ == "__main__":
    # Simple test execution
    extractor = TextFeatureExtractor()
    num_processed = extractor.process_database_texts(limit=50)
    print(f"Processed {num_processed} text items")

