#!/usr/bin/env python3
"""
Toronto Trendspotter: Enhanced Mock Data Generator Runner

This script runs the enhanced mock data generator to populate the MongoDB database
with realistic Toronto-specific data for the recommendation engine.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the enhanced mock data generator"""
    parser = argparse.ArgumentParser(description="Generate enhanced mock data for Toronto Trendspotter")
    parser.add_argument("--content", type=int, default=500, help="Number of Pinterest content items to generate (default: 500)")
    parser.add_argument("--events", type=int, default=300, help="Number of Toronto events to generate (default: 300)")
    parser.add_argument("--places", type=int, default=200, help="Number of Toronto places to generate (default: 200)")
    parser.add_argument("--users", type=int, default=200, help="Number of users to generate (default: 200)")
    parser.add_argument("--force", action="store_true", help="Force deletion of existing mock data without prompting")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check MongoDB connection
    try:
        # Add project root to Python path
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(current_file)
        sys.path.insert(0, project_root)
        
        from src.utils.db import get_mongodb_db
        
        # Test MongoDB connection
        db = get_mongodb_db()
        db.command("ping")
        logger.info("MongoDB connection successful!")
        
        # Import and run the enhanced mock data generator
        start_time = datetime.now()
        logger.info(f"Starting enhanced mock data generation...")
        
        # Import the generator module
        import generate_enhanced_mock_data as gen
        
        # Check for existing mock data
        existing_mock = db.content.count_documents({"metadata.mock_data": True})
        if existing_mock > 0:
            logger.info(f"Found {existing_mock} existing mock data records")
            
            if args.force:
                delete = True
            else:
                delete = input("Delete existing mock data? (y/n): ").lower() == 'y'
            
            if delete:
                # Delete existing mock data
                deleted_content = db.content.delete_many({"metadata.mock_data": True})
                deleted_events = db.toronto_events.delete_many({})
                deleted_interactions = db.interactions.delete_many({})
                db.users.delete_many({})
                logger.info(f"Deleted {deleted_content.deleted_count} content items, {deleted_events.deleted_count} events, and all interaction data")
            else:
                logger.info("Keeping existing mock data")
                return
        
        # Generate data with custom counts
        logger.info(f"Generating data with: {args.content} content items, {args.events} events, {args.places} places, {args.users} users")
        
        # Generate Pinterest content
        content_ids = gen.generate_mock_pinterest_content(count=args.content)
        logger.info(f"Generated {len(content_ids)} Pinterest content items")
        
        # Generate Toronto events
        event_ids = gen.generate_mock_events(count=args.events)
        logger.info(f"Generated {len(event_ids)} Toronto events")
        
        # Generate Toronto places
        place_ids = gen.generate_mock_places(count=args.places)
        logger.info(f"Generated {len(place_ids)} Toronto places")
        
        # Combine all content IDs
        all_content_ids = content_ids + [event["content_id"] for event in db.toronto_events.find({}, {"content_id": 1})]
        
        # Generate user interaction data
        interaction_count = gen.generate_interaction_data(
            all_content_ids, 
            user_count=args.users, 
            interactions_per_user_range=(5, 30)
        )
        logger.info(f"Generated {interaction_count} user interactions")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        logger.info(f"Successfully generated enhanced mock data in {duration:.1f} minutes")
        
        # Print collection statistics
        content_count = db.content.count_documents({})
        event_count = db.toronto_events.count_documents({})
        user_count = db.users.count_documents({})
        interaction_count = db.interactions.count_documents({})
        
        logger.info(f"Database statistics:")
        logger.info(f"- Content collection: {content_count} documents")
        logger.info(f"- Toronto events collection: {event_count} documents")
        logger.info(f"- Users collection: {user_count} documents")
        logger.info(f"- Interactions collection: {interaction_count} documents")
        
        logger.info("Mock data generation complete! You can now proceed with Week 2 implementation.")
        
    except ImportError as e:
        logger.error(f"Error importing modules: {e}")
        logger.error("Make sure you're running this script from the project root directory.")
    except Exception as e:
        logger.error(f"Error generating mock data: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()