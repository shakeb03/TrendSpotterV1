import os
import sys
from pathlib import Path

# Add the project root to Python path to make imports work
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.utils.db import get_postgres_engine, get_mongodb_db
from src.data.models.database import Base
from dotenv import load_dotenv

def initialize_postgres():
    """Initialize PostgreSQL database tables"""
    print("Initializing PostgreSQL database...")
    engine = get_postgres_engine()
    Base.metadata.create_all(engine)
    print("PostgreSQL database initialized successfully.")

def initialize_mongodb():
    """Initialize MongoDB collections"""
    print("Initializing MongoDB collections...")
    db = get_mongodb_db()
    
    # Create collections if they don't exist
    if "raw_content" not in db.list_collection_names():
        db.create_collection("raw_content")
    
    if "feature_vectors" not in db.list_collection_names():
        db.create_collection("feature_vectors")
    
    print("MongoDB collections initialized successfully.")

if __name__ == "__main__":
    load_dotenv()
    initialize_postgres()
    initialize_mongodb()
    print("Database initialization complete.")