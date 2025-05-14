import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Import feature extraction modules
from src.data.processing.simple_text_features import SimpleTextFeatureExtractor
from src.data.processing.location_enrichment import LocationEnricher

# Import recommendation models
from src.models.collaborative_filtering import CollaborativeFiltering
from src.models.content_based import ContentBasedRecommender
from src.models.hybrid_recommender import HybridRecommender

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_data_and_train():
    """
    Process imported data and train recommendation models
    """
    start_time = datetime.now()
    
    # Step 1: Process text features
    logger.info("Step 1: Processing text features...")
    text_extractor = SimpleTextFeatureExtractor()
    text_count = text_extractor.process_database_texts(skip_existing=True)
    logger.info(f"Processed text features for {text_count} items")
    
    # Step 2: Enrich with location data
    logger.info("Step 2: Enriching with location data...")
    location_enricher = LocationEnricher()
    location_count = location_enricher.enrich_content_location()
    logger.info(f"Enriched {location_count} items with location data")
    
    # Step 3: Train collaborative filtering model
    logger.info("Step 3: Training collaborative filtering model...")
    cf_model = CollaborativeFiltering(approach="item")
    cf_success = cf_model.train(min_interactions=1)  # Lower threshold for new data
    if cf_success:
        cf_model.save_model()
        logger.info("Collaborative filtering model trained and saved successfully")
    else:
        logger.warning("Failed to train collaborative filtering model")
    
    # Step 4: Train content-based model
    logger.info("Step 4: Training content-based model...")
    cb_model = ContentBasedRecommender()
    cb_success = cb_model.train()
    if cb_success:
        cb_model.save_model()
        logger.info("Content-based model trained and saved successfully")
    else:
        logger.warning("Failed to train content-based model")
    
    # Step 5: Train hybrid model
    logger.info("Step 5: Training hybrid model...")
    hybrid_model = HybridRecommender()
    hybrid_success = hybrid_model.train()
    if hybrid_success:
        hybrid_model.save_model()
        logger.info("Hybrid model trained and saved successfully")
    else:
        logger.warning("Failed to train hybrid model")
    
    # Track execution time
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    logger.info(f"Data processing and model training completed in {duration:.2f} minutes")

if __name__ == "__main__":
    process_data_and_train()