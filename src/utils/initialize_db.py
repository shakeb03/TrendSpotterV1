import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to Python path to make imports work
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.db import get_mongodb_db
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_mongodb():
    """Initialize MongoDB Atlas collections and indexes"""
    logger.info("Initializing MongoDB Atlas database...")
    db = get_mongodb_db()
    
    # Define main collections
    collections = [
        "users",            # User profiles
        "content",          # Content items (pins, events, places)
        "interactions",     # User-content interactions
        "toronto_events",   # Toronto-specific events
        "raw_content",      # Raw scraped data
        "feature_vectors",  # Feature vectors for ML
        "ml_models"         # ML model metadata
    ]
    
    # Create collections if they don't exist
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            logger.info(f"Created collection: {collection}")
    
    # Create indexes for better query performance
    try:
        # User indexes
        db.users.create_index("username", unique=True)
        
        # Content indexes
        db.content.create_index("title")
        db.content.create_index("source_url", unique=True, sparse=True)
        db.content.create_index("categories")
        db.content.create_index("tags")
        
        # Interaction indexes
        db.interactions.create_index([("user_id", 1), ("content_id", 1)])
        db.interactions.create_index("timestamp")
        
        # Toronto events indexes
        db.toronto_events.create_index("event_name")
        db.toronto_events.create_index("content_id", unique=True)
        db.toronto_events.create_index("start_date")
        
        # Feature vectors indexes
        db.feature_vectors.create_index([("content_id", 1), ("feature_type", 1)])
        
        logger.info("Created indexes for all collections")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
    
    # Create an initial admin document to verify everything works
    try:
        db.system.insert_one({
            "name": "Toronto Trendspotter",
            "initialized_at": datetime.now(),
            "status": "active"
        })
        logger.info("Database initialization complete.")
    except Exception as e:
        logger.error(f"Error creating system document: {e}")

if __name__ == "__main__":
    load_dotenv()
    initialize_mongodb()
    logger.info("Database initialization complete.")