#!/usr/bin/env python3
"""
Process Text Features for Toronto Trendspotter

This script runs the simple text feature extractor to process all content in the MongoDB database.
It extracts text features from content titles and descriptions and stores them as feature vectors.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(current_file)
sys.path.insert(0, project_root)

# Import the simple text feature extractor
from src.data.processing.simple_text_features import SimpleTextFeatureExtractor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_text_features(limit=None, max_features=100):
    """
    Process text features for all content
    
    Args:
        limit (int): Maximum number of content items to process
        max_features (int): Maximum number of features in vectors
    """
    start_time = datetime.now()
    logger.info(f"Starting text feature processing (limit={limit}, max_features={max_features})")
    
    try:
        # Create and run the text feature extractor
        extractor = SimpleTextFeatureExtractor()
        processed_count = extractor.process_database_texts(
            limit=limit,
            max_features=max_features
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        logger.info(f"Text feature processing completed:")
        logger.info(f"- Processed {processed_count} content items")
        logger.info(f"- Completed in {duration:.2f} minutes")
        logger.info(f"- Features per item: {max_features}")
        
    except Exception as e:
        logger.error(f"Error processing text features: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process text features for Toronto Trendspotter")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of content items to process")
    parser.add_argument("--max-features", type=int, default=100, help="Maximum number of features in vectors")
    
    args = parser.parse_args()
    process_text_features(limit=args.limit, max_features=args.max_features)