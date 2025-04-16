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

# Import collectors
from src.data.collectors.eventbrite_client import EventbriteClient
from src.data.collectors.google_places_client import GooglePlacesClient
from src.data.run_pinterest_spider import run_pinterest_spider

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(project_root, "data", "collection.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def collect_pinterest_data():
    """Run Pinterest spider to collect data"""
    logger.info("Starting Pinterest data collection")
    try:
        run_pinterest_spider()
        logger.info("Pinterest data collection completed")
    except Exception as e:
        logger.error(f"Error collecting Pinterest data: {e}")

def collect_eventbrite_data(max_pages=3):
    """Collect event data from Eventbrite"""
    logger.info("Starting Eventbrite data collection")
    try:
        client = EventbriteClient()
        count = client.collect_toronto_events(max_pages=max_pages)
        logger.info(f"Collected {count} events from Eventbrite")
    except Exception as e:
        logger.error(f"Error collecting Eventbrite data: {e}")

def collect_google_places_data(place_types=None, max_pages_per_type=2):
    """Collect business data from Google Places"""
    logger.info("Starting Google Places data collection")
    try:
        client = GooglePlacesClient()
        count = client.collect_toronto_places(
            place_types=place_types,
            max_pages_per_type=max_pages_per_type
        )
        logger.info(f"Collected {count} places from Google Places")
    except Exception as e:
        logger.error(f"Error collecting Google Places data: {e}")

def run_data_collection(sources=None):
    """
    Run data collection process for specified sources
    
    Args:
        sources (list): List of data sources to collect from
                        Options: "pinterest", "eventbrite", "google_places"
                        If None, collect from all sources
    """
    if sources is None:
        sources = ["pinterest", "eventbrite"]
    
    logger.info(f"Starting data collection for sources: {sources}")
    start_time = datetime.now()
    
    if "pinterest" in sources:
        collect_pinterest_data()
    
    if "eventbrite" in sources:
        collect_eventbrite_data()
    
    if "google_places" in sources:
        collect_google_places_data()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    
    logger.info(f"Data collection completed in {duration:.2f} minutes")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect data for Toronto Trendspotter")
    parser.add_argument(
        "--sources", 
        nargs="+", 
        choices=["pinterest", "eventbrite"],
        help="Data sources to collect from"
    )
    
    args = parser.parse_args()
    run_data_collection(sources=args.sources)