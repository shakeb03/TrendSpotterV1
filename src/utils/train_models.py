#!/usr/bin/env python3
"""
Toronto Trendspotter: Train Recommendation Models

This script trains all recommendation models for the Toronto Trendspotter project.
It trains the collaborative filtering, content-based, and hybrid models sequentially.
"""

import os
import sys
import logging
import argparse
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(current_file)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import recommendation models
from src.models.collaborative_filtering import CollaborativeFiltering
from src.models.content_based import ContentBasedRecommender
from src.models.hybrid_recommender import HybridRecommender

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('model_training.log')
    ]
)
logger = logging.getLogger(__name__)

def train_collaborative_filtering(force=False):
    """Train the collaborative filtering model"""
    logger.info("Training collaborative filtering model...")
    start_time = time.time()
    
    model = CollaborativeFiltering(approach="item")
    
    # Check if already trained
    if not force and model.load_model():
        logger.info("Collaborative filtering model already trained, loading from database")
    else:
        # Train the model
        success = model.train(min_interactions=2)
        if success:
            # Save the model
            model.save_model()
            logger.info("Collaborative filtering model trained and saved successfully")
        else:
            logger.error("Failed to train collaborative filtering model")
    
    elapsed_time = (time.time() - start_time) / 60
    logger.info(f"Collaborative filtering model training completed in {elapsed_time:.2f} minutes")
    
    return model

def train_content_based(force=False):
    """Train the content-based recommendation model"""
    logger.info("Training content-based recommendation model...")
    start_time = time.time()
    
    model = ContentBasedRecommender()
    
    # Check if already trained
    if not force and model.load_model():
        logger.info("Content-based model already trained, loading from database")
    else:
        # Train the model
        success = model.train()
        if success:
            # Save the model
            model.save_model()
            logger.info("Content-based model trained and saved successfully")
        else:
            logger.error("Failed to train content-based model")
    
    elapsed_time = (time.time() - start_time) / 60
    logger.info(f"Content-based model training completed in {elapsed_time:.2f} minutes")
    
    return model

def train_hybrid(force=False):
    """Train the hybrid recommendation model"""
    logger.info("Training hybrid recommendation model...")
    start_time = time.time()
    
    model = HybridRecommender()
    
    # Check if already trained
    if not force and model.load_model():
        logger.info("Hybrid model already trained, loading from database")
    else:
        # Train the model
        success = model.train()
        if success:
            # Save the model
            model.save_model()
            logger.info("Hybrid model trained and saved successfully")
        else:
            logger.error("Failed to train hybrid model")
    
    elapsed_time = (time.time() - start_time) / 60
    logger.info(f"Hybrid model training completed in {elapsed_time:.2f} minutes")
    
    return model

def train_all_models(force=False):
    """Train all recommendation models"""
    logger.info("Starting training of all recommendation models...")
    start_time = time.time()
    
    # Train models sequentially
    cf_model = train_collaborative_filtering(force)
    cb_model = train_content_based(force)
    hybrid_model = train_hybrid(force)
    
    elapsed_time = (time.time() - start_time) / 60
    logger.info(f"All models trained in {elapsed_time:.2f} minutes")
    
    return {
        "collaborative_filtering": cf_model,
        "content_based": cb_model,
        "hybrid": hybrid_model
    }

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Train Toronto Trendspotter recommendation models")
    parser.add_argument("--model", choices=["collaborative", "content", "hybrid", "all"], 
                      default="all", help="Model to train")
    parser.add_argument("--force", action="store_true", help="Force retraining even if model exists")
    
    args = parser.parse_args()
    
    start_time = time.time()
    logger.info(f"Starting model training: {args.model}")
    
    try:
        if args.model == "collaborative" or args.model == "all":
            train_collaborative_filtering(args.force)
        
        if args.model == "content" or args.model == "all":
            train_content_based(args.force)
        
        if args.model == "hybrid" or args.model == "all":
            train_hybrid(args.force)
        
        elapsed_time = (time.time() - start_time) / 60
        logger.info(f"Training completed in {elapsed_time:.2f} minutes")
        print(f"Training completed successfully in {elapsed_time:.2f} minutes")
        
    except Exception as e:
        logger.error(f"Error during training: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"Error during training: {e}")

if __name__ == "__main__":
    main()