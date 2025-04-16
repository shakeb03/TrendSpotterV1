import os
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB Atlas connection
def get_mongodb_client():
    """Get MongoDB client connection"""
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        logger.error("MONGO_URI not found in environment variables")
        raise ValueError("MONGO_URI not found")
        
    try:
        client = MongoClient(mongo_uri)
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {e}")
        raise

def get_mongodb_db():
    """Get MongoDB database instance"""
    client = get_mongodb_client()
    db_name = os.getenv("MONGO_DB_NAME", "trendspotter")
    return client[db_name]

# Utility function for generating unique IDs
def generate_uuid():
    """Generate a unique ID for MongoDB documents"""
    import uuid
    return str(uuid.uuid4())