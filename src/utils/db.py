import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# PostgreSQL connection
def get_postgres_engine():
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
    return create_engine(connection_string)

def get_db_session():
    engine = get_postgres_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# MongoDB connection
def get_mongodb_client():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    return client

def get_mongodb_db():
    client = get_mongodb_client()
    db_name = os.getenv("MONGO_DB_NAME")
    return client[db_name]