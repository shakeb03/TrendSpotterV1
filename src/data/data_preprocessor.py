import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Add project root to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
sys.path.insert(0, project_root)


# Import feature extractors and processors
from src.data.processing.image_features import ImageFeatureExtractor
from src.data.processing.text_features import TextFeatureExtractor
from src.data.processing.location_enrichment import LocationEnricher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(project_root, "data", "preprocessing.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_image_features(limit=None):
    """Extract features from images"""
    logger.info("Starting image feature extraction")
    try:
        extractor = ImageFeatureExtractor()
        count = extractor.process_database_images(limit=limit)
        logger.info(f"Extracted image features for {count} content items")
        return count
    except Exception as e:
        logger.error(f"Error extracting image features: {e}")
        return 0

def extract_text_features(limit=None):
    """Extract features from text content"""
    logger.info("Starting text feature extraction")
    try:
        extractor = TextFeatureExtractor()
        count = extractor.process_database_texts(limit=limit)
        logger.info(f"Extracted text features for {count} content items")
        return count
    except Exception as e:
        logger.error(f"Error extracting text features: {e}")
        return 0

def enrich_location_data(limit=None):
    """Enrich content with location-based features"""
    logger.info("Starting location data enrichment")
    try:
        enricher = LocationEnricher()
        count = enricher.enrich_content_location(limit=limit)
        logger.info(f"Enriched location data for {count} content items")
        return count
    except Exception as e:
        logger.error(f"Error enriching location data: {e}")
        return 0

def run_data_preprocessing(processors=None, limit=None):
    """
    Run data preprocessing and feature extraction
    
    Args:
        processors (list): List of processors to run
                        Options: "image", "text", "location"
                        If None, run all processors
        limit (int): Maximum number of items to process per processor
    """
    if processors is None:
        processors = ["image", "text", "location"]
    
    logger.info(f"Starting data preprocessing with processors: {processors}")
    start_time = datetime.now()
    
    results = {}
    
    if "image" in processors:
        results["image"] = extract_image_features(limit=limit)
    
    if "text" in processors:
        results["text"] = extract_text_features(limit=limit)
    
    if "location" in processors:
        results["location"] = enrich_location_data(limit=limit)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    
    logger.info(f"Data preprocessing completed in {duration:.2f} minutes")
    logger.info(f"Results: {results}")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess data for Toronto Trendspotter")
    parser.add_argument(
        "--processors", 
        nargs="+", 
        choices=["image", "text", "location"],
        help="Processors to run"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of items to process per processor"
    )
    
    args = parser.parse_args()
    run_data_preprocessing(processors=args.processors, limit=args.limit)