import os
import sys
import requests
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import logging

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.utils.db import get_mongodb_db
from src.data.models.mongodb_models import create_content, create_toronto_event

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventbriteClient:
    """Client for collecting Toronto events from Eventbrite API"""
    
    # Toronto coordinates (approximate center)
    TORONTO_LAT = 43.6532
    TORONTO_LON = -79.3832
    
    # Toronto area radius in kilometers
    TORONTO_RADIUS = 25
    
    def __init__(self):
        # Load environment variables
        env_file = os.path.join(project_root, '.env')
        load_dotenv(env_file)
        
        self.api_key = os.getenv("EVENTBRITE_API_KEY")
        if not self.api_key:
            logger.error("EVENTBRITE_API_KEY not found in environment variables")
            raise ValueError("EVENTBRITE_API_KEY not found")
            
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def search_events(self, categories=None, start_date=None, end_date=None, page=1):
        """
        Search for events in Toronto area
        
        Args:
            categories (list): List of category IDs to filter by
            start_date (datetime): Start date for events
            end_date (datetime): End date for events
            page (int): Page number for pagination
            
        Returns:
            dict: JSON response from API
        """
        if not start_date:
            start_date = datetime.now()
        if not end_date:
            end_date = start_date + timedelta(days=90)  # Next 90 days
            
        # Format dates as ISO strings
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        
        # Build parameters
        params = {
            "location.latitude": self.TORONTO_LAT,
            "location.longitude": self.TORONTO_LON,
            "location.within": f"{self.TORONTO_RADIUS}km",
            "start_date.range_start": start_date_str,
            "start_date.range_end": end_date_str,
            "page": page
        }
        
        if categories:
            params["categories"] = ",".join(categories)
            
        # Make API request
        url = f"{self.base_url}/events/search/"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching events from Eventbrite: {e}")
            return {"events": []}
    
    def get_event_details(self, event_id):
        """
        Get detailed information about a specific event
        
        Args:
            event_id (str): Eventbrite event ID
            
        Returns:
            dict: JSON response from API
        """
        url = f"{self.base_url}/events/{event_id}/"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching event details from Eventbrite: {e}")
            return {}
    
    def get_venue_details(self, venue_id):
        """
        Get detailed information about a venue
        
        Args:
            venue_id (str): Eventbrite venue ID
            
        Returns:
            dict: JSON response from API
        """
        url = f"{self.base_url}/venues/{venue_id}/"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching venue details from Eventbrite: {e}")
            return {}
    
    def collect_toronto_events(self, max_pages=5):
        """
        Collect events in Toronto and store them in the database
        
        Args:
            max_pages (int): Maximum number of pages to collect
            
        Returns:
            int: Number of events collected
        """
        # Initialize MongoDB connection
        mongo_db = get_mongodb_db()
        
        # Track collected events
        collected_count = 0
        page = 1
        
        try:
            while page <= max_pages:
                logger.info(f"Collecting events page {page}")
                
                # Search for events
                results = self.search_events(page=page)
                events = results.get("events", [])
                
                if not events:
                    logger.info("No more events found")
                    break
                
                # Process each event
                for event in events:
                    event_id = event.get("id")
                    
                    # Check if we already have this event
                    existing = mongo_db.content.find_one({
                        "source_url": f"https://www.eventbrite.com/e/{event_id}"
                    })
                    
                    if existing:
                        logger.debug(f"Event {event_id} already exists in database")
                        continue
                    
                    # Get venue details if available
                    venue_data = {}
                    venue_id = event.get("venue_id")
                    if venue_id:
                        venue_data = self.get_venue_details(venue_id)
                    
                    # Get basic event info
                    name = event.get("name", {}).get("text", "Unnamed Event")
                    description = event.get("description", {}).get("text", "")
                    start_date = datetime.fromisoformat(
                        event.get("start", {}).get("utc", datetime.now().isoformat())
                    )
                    end_date = datetime.fromisoformat(
                        event.get("end", {}).get("utc", start_date.isoformat())
                    )
                    
                    # Get image URL
                    image_url = event.get("logo", {}).get("url", "")
                    
                    # Store raw event data in MongoDB
                    mongo_db.raw_content.insert_one({
                        "source": "eventbrite",
                        "eventbrite_id": event_id,
                        "raw_data": event,
                        "venue_data": venue_data,
                        "collected_at": datetime.now()
                    })
                    
                    # Create content document
                    content = create_content(
                        title=name,
                        description=description,
                        image_url=image_url,
                        source_url=f"https://www.eventbrite.com/e/{event_id}",
                        categories=["event"],
                        tags=["toronto", "event"],
                        location={
                            "latitude": venue_data.get("latitude", self.TORONTO_LAT),
                            "longitude": venue_data.get("longitude", self.TORONTO_LON)
                        },
                        metadata={
                            "source": "eventbrite",
                            "eventbrite_id": event_id
                        }
                    )
                    
                    # Insert content into MongoDB
                    content_result = mongo_db.content.insert_one(content)
                    content_id = content_result.inserted_id
                    
                    # Create Toronto event document
                    toronto_event = create_toronto_event(
                        content_id=content_id,
                        event_name=name,
                        venue=venue_data.get("name", "Unknown Venue"),
                        start_date=start_date,
                        end_date=end_date,
                        address={
                            "address_1": venue_data.get("address", {}).get("address_1", ""),
                            "address_2": venue_data.get("address", {}).get("address_2", ""),
                            "city": venue_data.get("address", {}).get("city", "Toronto"),
                            "postal_code": venue_data.get("address", {}).get("postal_code", "")
                        },
                        price_range={
                            "currency": event.get("currency", "CAD"),
                            "is_free": event.get("is_free", False)
                        },
                        seasonal_relevance=self._determine_seasonal_relevance(start_date)
                    )
                    
                    # Insert Toronto event into MongoDB
                    mongo_db.toronto_events.insert_one(toronto_event)
                    
                    collected_count += 1
                    logger.info(f"Stored event: {name} ({event_id})")
                
                # Check if there are more pages
                pagination = results.get("pagination", {})
                if page >= pagination.get("page_count", 0):
                    logger.info("Reached last page of results")
                    break
                
                page += 1
                
            return collected_count
            
        except Exception as e:
            logger.error(f"Error collecting events: {e}")
            return collected_count
    
    def _determine_seasonal_relevance(self, date):
        """
        Determine seasonal relevance based on date
        
        Args:
            date (datetime): Event date
            
        Returns:
            list: List of seasonal tags
        """
        month = date.month
        day = date.day
        
        seasons = []
        
        # Season based on month
        if 3 <= month <= 5:
            seasons.append("spring")
        elif 6 <= month <= 8:
            seasons.append("summer")
        elif 9 <= month <= 11:
            seasons.append("fall")
        else:
            seasons.append("winter")
        
        # Special periods
        if month == 12:
            seasons.append("holiday")
        
        if month == 7:
            seasons.append("summer-festival")
        
        # Canada Day
        if month == 7 and day == 1:
            seasons.append("canada-day")
            
        # Halloween
        if month == 10 and day >= 25:
            seasons.append("halloween")
            
        # Thanksgiving (Canadian - second Monday in October)
        if month == 10 and 8 <= day <= 14:
            seasons.append("thanksgiving")
        
        return seasons


if __name__ == "__main__":
    # Simple test execution
    client = EventbriteClient()
    num_events = client.collect_toronto_events(max_pages=2)
    print(f"Collected {num_events} events from Eventbrite")