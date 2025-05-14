import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.utils.db import get_mongodb_db
from src.data.models.mongodb_models import create_content

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def import_pinterest_json(file_path):
    """
    Import Pinterest data from a JSON file into MongoDB Atlas
    
    Args:
        file_path (str): Path to the JSON file containing Pinterest data
        
    Returns:
        int: Number of items imported
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return 0
    
    # Initialize MongoDB connection
    mongo_db = get_mongodb_db()
    
    # Track imported items
    imported_count = 0
    skipped_count = 0
    
    try:
        # Load JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            # Single object
            data = [data]
        
        logger.info(f"Found {len(data)} items in JSON file")
        
        for item in data:
            try:
                # Extract pin data from the Pinterest JSON
                pin_id = item.get('id')
                
                # Skip if we already have this item
                existing = mongo_db.content.find_one({
                    "metadata.pinterest_id": pin_id
                })
                
                if existing:
                    logger.debug(f"Pin {pin_id} already exists in database, skipping")
                    skipped_count += 1
                    continue
                
                # Extract data
                title = item.get('grid_title', '') or item.get('title', '') or item.get('closeup_description', '')
                description = item.get('description', '') or item.get('closeup_unified_description', '') or ''
                
                # Extract image URL
                image_url = ''
                if 'images' in item:
                    # Try to get original image first, then fallback to other sizes
                    if 'orig' in item['images']:
                        image_url = item['images']['orig']['url']
                    elif '736x' in item['images']:
                        image_url = item['images']['736x']['url']
                    elif '564x' in item['images']:
                        image_url = item['images']['564x']['url']
                    elif '474x' in item['images']:
                        image_url = item['images']['474x']['url']
                    elif '236x' in item['images']:
                        image_url = item['images']['236x']['url']
                
                # Source URL
                source_url = item.get('url', f"https://www.pinterest.com/pin/{pin_id}/")
                
                # Extract domain for additional context
                domain = item.get('domain', '')
                
                # Determine categories and tags
                categories = []
                if item.get('category'):
                    categories.append(item['category'].lower())
                
                # Add Toronto-specific categories based on description
                if 'food' in title.lower() or 'restaurant' in title.lower() or 'eat' in title.lower():
                    categories.append('food')
                elif 'art' in title.lower() or 'gallery' in title.lower() or 'museum' in title.lower():
                    categories.append('art')
                elif 'event' in title.lower() or 'festival' in title.lower():
                    categories.append('event')
                elif 'park' in title.lower() or 'trail' in title.lower() or 'beach' in title.lower():
                    categories.append('outdoor')
                elif 'shopping' in title.lower() or 'shop' in title.lower() or 'store' in title.lower():
                    categories.append('shopping')
                
                # Ensure at least one category
                if not categories:
                    categories = ['misc']
                
                # Remove duplicates
                categories = list(set(categories))
                
                # Generate tags from title and description
                tags = ['toronto']
                
                # Add neighborhood tags if mentioned
                toronto_neighborhoods = [
                    'Downtown Core', 'Distillery District', 'Kensington Market', 
                    'Queen West', 'Yorkville', 'The Beaches', 'Liberty Village',
                    'Leslieville', 'Little Italy', 'Chinatown'
                ]
                
                for neighborhood in toronto_neighborhoods:
                    if neighborhood.lower() in title.lower() or neighborhood.lower() in description.lower():
                        tags.append(neighborhood.lower().replace(' ', '-'))
                
                # Add board name as tag if available
                if 'board' in item and 'name' in item['board']:
                    board_name = item['board']['name'].lower()
                    for tag in board_name.split():
                        if len(tag) > 3 and tag not in tags:
                            tags.append(tag)
                
                # Store raw data in MongoDB
                mongo_db.raw_content.insert_one({
                    "source": "pinterest",
                    "pinterest_id": pin_id,
                    "raw_data": item,
                    "collected_at": datetime.now()
                })
                
                # Create structured content document
                content = create_content(
                    title=title,
                    description=description,
                    image_url=image_url,
                    source_url=source_url,
                    categories=categories,
                    tags=tags,
                    location=None,  # Will be enriched later
                    metadata={
                        "source": "pinterest",
                        "pinterest_id": pin_id,
                        "domain": domain,
                        "repin_count": item.get('repin_count', 0),
                        "comment_count": item.get('comment_count', 0),
                        "original_created_at": item.get('created_at')
                    }
                )
                
                # Insert into MongoDB
                mongo_db.content.insert_one(content)
                imported_count += 1
                
                if imported_count % 100 == 0:
                    logger.info(f"Imported {imported_count} pins so far...")
                
            except Exception as e:
                logger.error(f"Error processing pin {item.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully imported {imported_count} pins, skipped {skipped_count}")
        return imported_count
        
    except Exception as e:
        logger.error(f"Error importing Pinterest data: {e}")
        return imported_count

def main():
    """
    Main function to import Pinterest data
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Pinterest data from JSON file')
    parser.add_argument('file_path', help='Path to the JSON file')
    
    args = parser.parse_args()
    
    import_pinterest_json(args.file_path)

if __name__ == "__main__":
    main()