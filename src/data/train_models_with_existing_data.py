import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

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

def train_models():
    """
    Train recommendation models on existing MongoDB data
    """
    start_time = datetime.now()
    
    try:
        # Step 1: Train collaborative filtering model
        logger.info("Training collaborative filtering model...")
        cf_model = CollaborativeFiltering(approach="item")
        cf_success = cf_model.train(min_interactions=1)  # Low threshold for new data
        if cf_success:
            cf_model.save_model()
            logger.info("Collaborative filtering model trained and saved successfully")
        else:
            logger.warning("Failed to train collaborative filtering model")
        
        # Step 2: Train content-based model
        logger.info("Training content-based model...")
        cb_model = ContentBasedRecommender()
        cb_success = cb_model.train()
        if cb_success:
            cb_model.save_model()
            logger.info("Content-based model trained and saved successfully")
        else:
            logger.warning("Failed to train content-based model")
        
        # Step 3: Train hybrid model
        logger.info("Training hybrid model...")
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
        logger.info(f"Model training completed in {duration:.2f} minutes")
        
    except Exception as e:
        logger.error(f"Error training models: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    train_models()