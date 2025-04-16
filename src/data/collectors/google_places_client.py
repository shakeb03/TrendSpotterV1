import os
import sys
import requests
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging

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

class GooglePlacesClient:
    """Client for collecting Toronto businesses from Google Places API"""
    
    # Toronto coordinates (approximate center)
    TORONTO_LAT = 43.6532
    TORONTO_LON = -79.3832
    
    # Toronto area radius in meters
    TORONTO_RADIUS = 25000  # 25 km
    
    # Place types to collect
    PLACE_TYPES = [
        "restaurant", "cafe", "bar", "museum", "art_gallery", 
        "tourist_attraction", "shopping_mall", "park"
    ]
    
    def __init__(self):
        # Load environment variables
        env_file = os.path.join(project_root, '.env')
        load_dotenv(env_file)
        
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_PLACES_API_KEY not found in environment variables")
            raise ValueError("GOOGLE_PLACES_API_KEY not found")
            
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def nearby_search(self, place_type, next_page_token=None):
        """
        Search for places near Toronto
        
        Args:
            place_type (str): Type of place to search for
            next_page_token (str): Token for pagination
            
        Returns:
            dict: JSON response from API
        """
        url = f"{self.base_url}/nearbysearch/json"
        
        if next_page_token:
            params = {
                "pagetoken": next_page_token,
                "key": self.api_key
            }
        else:
            params = {
                "location": f"{self.TORONTO_LAT},{self.TORONTO_LON}",
                "radius": self.TORONTO_RADIUS,
                "type": place_type,
                "key": self.api_key
            }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching places from Google Places API: {e}")
            return {"results": []}
    
    def get_place_details(self, place_id):
        """
        Get detailed information about a specific place
        
        Args:
            place_id (str): Google Places place ID
            
        Returns:
            dict: JSON response from API
        """
        url = f"{self.base_url}/details/json"
        
        params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_address,formatted_phone_number,website,opening_hours,photos,types,user_ratings_total,price_level,geometry",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("result", {})
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching place details from Google Places API: {e}")
            return {}
    
    def get_place_photo(self, photo_reference, max_width=800):
        """
        Get photo URL for a place
        
        Args:
            photo_reference (str): Photo reference from Places API
            max_width (int): Maximum width of photo
            
        Returns:
            str: Photo URL
        """
        if not photo_reference:
            return ""
            
        return f"{self.base_url}/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.api_key}"
    
    def collect_toronto_places(self, place_types=None, max_pages_per_type=2):
        """
        Collect businesses in Toronto and store them in the database
        
        Args:
            place_types (list): List of place types to collect
            max_pages_per_type (int): Maximum number of pages to collect per type
            
        Returns:
            int: Number of places collected
        """
        if not place_types:
            place_types = self.PLACE_TYPES
            
        # Initialize MongoDB connection
        mongo_db = get_mongodb_db()
        
        # Track collected places
        collected_count = 0
        
        try:
            for place_type in place_types:
                logger.info(f"Collecting places of type: {place_type}")
                
                page_count = 0
                next_page_token = None
                
                while page_count < max_pages_per_type:
                    # If we have a next page token, we need to wait a bit
                    if next_page_token:
                        time.sleep(2)  # API requires a delay before using next_page_token
                    
                    # Search for places
                    results = self.nearby_search(place_type, next_page_token)
                    places = results.get("results", [])
                    
                    if not places:
                        logger.info(f"No more places found for type: {place_type}")
                        break
                    
                    # Process each place
                    for place in places:
                        place_id = place.get("place_id")
                        
                        # Check if we already have this place
                        existing = mongo_db.content.find_one({
                            "metadata.google_place_id": place_id
                        })
                        
                        if existing:
                            logger.debug(f"Place {place_id} already exists in database")
                            continue
                        
                        # Get place details
                        details = self.get_place_details(place_id)
                        
                        if not details:
                            logger.warning(f"Could not get details for place {place_id}")
                            continue
                        
                        # Get basic place info
                        name = details.get("name", "Unnamed Place")
                        
                        # Get description (combine info if available)
                        description_parts = []
                        if "rating" in details:
                            description_parts.append(f"Rating: {details['rating']}/5")
                        if "user_ratings_total" in details:
                            description_parts.append(f"Based on {details['user_ratings_total']} reviews")
                        if "price_level" in details:
                            price_level = "$" * details.get("price_level", 0)
                            description_parts.append(f"Price: {price_level}")
                        
                        description = " · ".join(description_parts)
                        
                        # Get image URL (first photo if available)
                        image_url = ""
                        if "photos" in details and details["photos"]:
                            photo_reference = details["photos"][0].get("photo_reference")
                            image_url = self.get_place_photo(photo_reference)
                        
                        # Get website URL
                        website = details.get("website", "")
                        
                        # Get location
                        location = details.get("geometry", {}).get("location", {})
                        latitude = location.get("lat", self.TORONTO_LAT)
                        longitude = location.get("lng", self.TORONTO_LON)
                        
                        # Store raw place data in MongoDB
                        mongo_db.raw_content.insert_one({
                            "source": "google_places",
                            "google_place_id": place_id,
                            "raw_data": details,
                            "collected_at": datetime.now()
                        })
                        
                        # Determine categories and tags
                        types = details.get("types", [place_type])
                        
                        # Map Google place types to more Pinterest-like categories
                        category_mapping = {
                            "restaurant": "food",
                            "cafe": "food",
                            "bar": "food",
                            "museum": "art",
                            "art_gallery": "art",
                            "tourist_attraction": "travel",
                            "shopping_mall": "shopping",
                            "park": "outdoor"
                        }
                        
                        categories = []
                        for t in types:
                            if t in category_mapping:
                                categories.append(category_mapping[t])
                        
                        # Ensure at least one category
                        if not categories and place_type in category_mapping:
                            categories = [category_mapping[place_type]]
                        elif not categories:
                            categories = ["local"]
                        
                        # Remove duplicates
                        categories = list(set(categories))
                        
                        # Create content document
                        content = create_content(
                            title=name,
                            description=description,
                            image_url=image_url,
                            source_url=website or f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                            categories=categories,
                            tags=["toronto", place_type],
                            location={
                                "latitude": latitude,
                                "longitude": longitude,
                                "address": details.get("formatted_address", "")
                            },
                            metadata={
                                "source": "google_places",
                                "google_place_id": place_id,
                                "place_type": place_type,
                                "rating": details.get("rating"),
                                "user_ratings_total": details.get("user_ratings_total"),
                                "price_level": details.get("price_level")
                            }
                        )
                        
                        # Insert into MongoDB
                        mongo_db.content.insert_one(content)
                        collected_count += 1
                        logger.info(f"Stored place: {name} ({place_id})")
                    
                    # Check if there are more pages
                    next_page_token = results.get("next_page_token")
                    if not next_page_token:
                        logger.info(f"No more pages for place type: {place_type}")
                        break
                    
                    page_count += 1
            
            return collected_count
            
        except Exception as e:
            logger.error(f"Error collecting places: {e}")
            return collected_count


if __name__ == "__main__":
    # Simple test execution
    client = GooglePlacesClient()
    num_places = client.collect_toronto_places(place_types=["restaurant", "cafe"], max_pages_per_type=1)
    print(f"Collected {num_places} places from Google Places API")