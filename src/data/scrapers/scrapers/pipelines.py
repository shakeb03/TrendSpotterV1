import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[4]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.utils.db import get_mongodb_db
from src.data.models.mongodb_models import create_content

class MongoPipeline:
    """Pipeline to store scraped data in MongoDB Atlas"""
    
    def __init__(self):
        self.db = None
        
    def open_spider(self, spider):
        self.db = get_mongodb_db()
        self.raw_collection = self.db["raw_content"]
        self.content_collection = self.db["content"]
        spider.logger.info("MongoDB pipeline initialized")
        
    def process_item(self, item, spider):
        try:
            # Store raw data in raw_content collection
            raw_item = dict(item)
            raw_item["scraped_at"] = datetime.now()
            raw_item["source"] = "pinterest"
            raw_item["spider"] = spider.name
            
            self.raw_collection.insert_one(raw_item)
            
            # Create structured content document
            content = create_content(
                title=item["title"],
                description=item["description"],
                image_url=item["image_url"],
                source_url=item["source_url"],
                categories=item["categories"],
                tags=item["tags"],
                location=None,  # Will be added in the location enrichment phase
                metadata={
                    "source": "pinterest",
                    "pinterest_id": item["id"],
                    "original_created_at": item["created_at"],
                    "search_keyword": item.get("metadata", {}).get("search_keyword", "")
                }
            )
            
            # Store in content collection
            result = self.content_collection.insert_one(content)
            content_id = result.inserted_id
            
            spider.logger.debug(f"Item stored in MongoDB: {content_id}")
            
        except Exception as e:
            spider.logger.error(f"Error storing item in MongoDB: {e}")
            
        return item
    
    def close_spider(self, spider):
        spider.logger.info("MongoDB pipeline closed")

class JsonFilePipeline:
    """Pipeline to store data in JSON files for backup and debugging"""
    
    def __init__(self):
        self.file = None
        self.items = []
        
    def open_spider(self, spider):
        # Ensure data/raw directory exists
        output_dir = Path(project_root) / "data" / "raw"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pinterest_{spider.name}_{timestamp}.json"
        self.file_path = output_dir / filename
        spider.logger.info(f"JSON pipeline initialized: {self.file_path}")
        
    def process_item(self, item, spider):
        # Convert datetime to string for JSON serialization
        json_item = dict(item)
        if "created_at" in json_item and isinstance(json_item["created_at"], datetime):
            json_item["created_at"] = json_item["created_at"].isoformat()
            
        self.items.append(json_item)
        return item
    
    def close_spider(self, spider):
        with open(self.file_path, 'w') as f:
            json.dump(self.items, f, indent=2)
        spider.logger.info(f"Saved {len(self.items)} items to {self.file_path}")