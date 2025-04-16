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

# Import data collectors and preprocessors
from src.data.data_collector import run_data_collection
from src.data.data_preprocessor import run_data_preprocessing

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(project_root, "data", "pipeline.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_full_pipeline(collection_sources=None, processors=None, collection_limit=None, processing_limit=None):
    """
    Run the full data pipeline (collection and preprocessing)
    
    Args:
        collection_sources (list): Data sources for collection
        processors (list): Processors for feature extraction
        collection_limit (int): Limit for collection
        processing_limit (int): Limit for preprocessing
    """
    start_time = datetime.now()
    logger.info("Starting full data pipeline")
    
    # Run data collection
    logger.info("Step 1: Data Collection")
    collection_results = run_data_collection(sources=collection_sources)
    
    # Run data preprocessing
    logger.info("Step 2: Data Preprocessing")
    preprocessing_results = run_data_preprocessing(processors=processors, limit=processing_limit)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    
    logger.info(f"Full data pipeline completed in {duration:.2f} minutes")
    return {
        "collection": collection_results,
        "preprocessing": preprocessing_results,
        "duration_minutes": duration
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run data pipeline for Toronto Trendspotter")
    parser.add_argument(
        "--collection-sources", 
        nargs="+", 
        choices=["pinterest", "eventbrite"],
        help="Data sources for collection"
    )
    parser.add_argument(
        "--processors", 
        nargs="+", 
        choices=["image", "text", "location"],
        help="Processors for feature extraction"
    )
    parser.add_argument(
        "--collection-limit",
        type=int,
        help="Limit for collection"
    )
    parser.add_argument(
        "--processing-limit",
        type=int,
        help="Limit for preprocessing"
    )
    
    args = parser.parse_args()
    run_full_pipeline(
        collection_sources=args.collection_sources,
        processors=args.processors,
        collection_limit=args.collection_limit,
        processing_limit=args.processing_limit
    )