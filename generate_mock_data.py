#!/usr/bin/env python3
"""
Mock Data Generator for Toronto Trendspotter

This script generates mock data for the Toronto Trendspotter project.
It creates sample content, events, and places to simulate data that would
normally be collected from APIs.
"""

import os
import sys
import random
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Add project root to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(current_file)
sys.path.insert(0, project_root)

from src.utils.db import get_mongodb_db
from src.data.models.mongodb_models import create_content, create_toronto_event

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Toronto neighborhoods with coordinates
TORONTO_NEIGHBORHOODS = [
    {"name": "Downtown Core", "lat": 43.6511, "lon": -79.3832},
    {"name": "Distillery District", "lat": 43.6503, "lon": -79.3597},
    {"name": "Kensington Market", "lat": 43.6547, "lon": -79.4005},
    {"name": "The Beaches", "lat": 43.6762, "lon": -79.2995},
    {"name": "Yorkville", "lat": 43.6709, "lon": -79.3933},
    {"name": "Queen West", "lat": 43.6468, "lon": -79.4119},
    {"name": "Liberty Village", "lat": 43.6371, "lon": -79.4208},
    {"name": "Leslieville", "lat": 43.6626, "lon": -79.3357},
    {"name": "Little Italy", "lat": 43.6547, "lon": -79.4228},
    {"name": "Chinatown", "lat": 43.6529, "lon": -79.3975}
]

# Sample Pinterest-like data
SAMPLE_PINTEREST_CONTENT = [
    {
        "title": "Toronto Skyline at Sunset",
        "description": "Beautiful view of Toronto skyline with CN Tower at sunset",
        "image_url": "https://images.unsplash.com/photo-1514924013411-cbf25faa35bb",
        "categories": ["photography", "travel"],
        "tags": ["toronto", "skyline", "sunset", "urban"]
    },
    {
        "title": "Kensington Market Street Art",
        "description": "Colorful murals in Toronto's vibrant Kensington Market district",
        "image_url": "https://images.unsplash.com/photo-1596395464941-de917238027a",
        "categories": ["art", "travel"],
        "tags": ["toronto", "street-art", "mural", "urban"]
    },
    {
        "title": "Toronto Waterfront Trail",
        "description": "Scenic walking path along Toronto's beautiful waterfront",
        "image_url": "https://images.unsplash.com/photo-1586022383926-25e48eeaf9f1",
        "categories": ["outdoor", "travel"],
        "tags": ["toronto", "waterfront", "trail", "nature"]
    },
    {
        "title": "Distillery District Architecture",
        "description": "Historic Victorian industrial architecture in Toronto's Distillery District",
        "image_url": "https://images.unsplash.com/photo-1569880153113-76e33fc52d5f",
        "categories": ["architecture", "travel"],
        "tags": ["toronto", "distillery-district", "historic", "architecture"]
    },
    {
        "title": "CN Tower Edge Walk Experience",
        "description": "Thrilling adventure walking on the edge of Toronto's CN Tower",
        "image_url": "https://images.unsplash.com/photo-1503505129851-abbb9ddad40a",
        "categories": ["adventure", "travel"],
        "tags": ["toronto", "cn-tower", "adventure", "extreme"]
    }
]

# Sample Toronto events
SAMPLE_EVENTS = [
    {
        "event_name": "Toronto International Film Festival",
        "venue": "TIFF Bell Lightbox",
        "description": "Annual film festival featuring international and Canadian cinema",
        "image_url": "https://images.unsplash.com/photo-1485846234645-a62644f84728",
        "address": {"address_1": "350 King St W", "city": "Toronto", "postal_code": "M5V 3X5"},
        "tags": ["festival", "film", "culture", "entertainment"]
    },
    {
        "event_name": "Caribana Festival",
        "venue": "Exhibition Place",
        "description": "Toronto's Caribbean carnival with music, costumes, and food",
        "image_url": "https://images.unsplash.com/photo-1541535650810-10d26f5c2ab3",
        "address": {"address_1": "100 Princes' Blvd", "city": "Toronto", "postal_code": "M6K 3C3"},
        "tags": ["festival", "music", "culture", "caribbean"]
    },
    {
        "event_name": "Toronto Christmas Market",
        "venue": "Distillery District",
        "description": "European-style Christmas market with local crafts, food, and entertainment",
        "image_url": "https://images.unsplash.com/photo-1512909006721-3d6018887383",
        "address": {"address_1": "55 Mill St", "city": "Toronto", "postal_code": "M5A 3C4"},
        "tags": ["market", "holiday", "winter", "shopping"]
    },
    {
        "event_name": "Nuit Blanche Toronto",
        "venue": "Various Locations",
        "description": "All-night contemporary art event with installations throughout the city",
        "image_url": "https://images.unsplash.com/photo-1501854140801-50d01698950b",
        "address": {"address_1": "City Hall", "city": "Toronto", "postal_code": "M5H 2N2"},
        "tags": ["art", "culture", "installation", "night"]
    },
    {
        "event_name": "Toronto Blue Jays Home Game",
        "venue": "Rogers Centre",
        "description": "Major League Baseball game featuring Toronto's home team",
        "image_url": "https://images.unsplash.com/photo-1531676267288-efccb8aaad1a",
        "address": {"address_1": "1 Blue Jays Way", "city": "Toronto", "postal_code": "M5V 1J1"},
        "tags": ["sports", "baseball", "entertainment"]
    }
]

# Sample Toronto places
SAMPLE_PLACES = [
    {
        "title": "St. Lawrence Market",
        "description": "Historic market with food vendors, restaurants, and specialty shops",
        "image_url": "https://images.unsplash.com/photo-1604689558922-d677a411bbec",
        "categories": ["food", "shopping"],
        "tags": ["market", "food", "historic", "downtown"],
        "neighborhood": "Downtown Core"
    },
    {
        "title": "Alo Restaurant",
        "description": "Upscale French restaurant with tasting menu. Rating: 4.9/5",
        "image_url": "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c",
        "categories": ["food"],
        "tags": ["fine-dining", "french", "tasting-menu"],
        "neighborhood": "Queen West"
    },
    {
        "title": "Royal Ontario Museum",
        "description": "Museum of art, culture, and natural history with diverse collections",
        "image_url": "https://images.unsplash.com/photo-1569515170394-cde020a7e7d7",
        "categories": ["art", "culture"],
        "tags": ["museum", "history", "education", "family"],
        "neighborhood": "Yorkville"
    },
    {
        "title": "High Park",
        "description": "Large urban park with trails, gardens, zoo, and recreational facilities",
        "image_url": "https://images.unsplash.com/photo-1563514370576-8d608db4b82d",
        "categories": ["outdoor"],
        "tags": ["park", "nature", "trails", "recreation"],
        "neighborhood": "High Park"
    },
    {
        "title": "Graffiti Alley",
        "description": "Colorful street art along Rush Lane in the Fashion District",
        "image_url": "https://images.unsplash.com/photo-1596395463910-4ab618e3c4e4",
        "categories": ["art", "travel"],
        "tags": ["street-art", "graffiti", "urban"],
        "neighborhood": "Queen West"
    }
]

def generate_mock_pinterest_content(count=20):
    """Generate mock Pinterest-like content"""
    db = get_mongodb_db()
    content_ids = []
    
    # Use sample data and generate variations
    adjectives = ["Amazing", "Beautiful", "Stunning", "Incredible", "Breathtaking", "Cozy", "Modern", "Historic", "Vibrant"]
    
    for i in range(count):
        # Select a base content or create new one
        if i < len(SAMPLE_PINTEREST_CONTENT):
            base = SAMPLE_PINTEREST_CONTENT[i]
        else:
            base = random.choice(SAMPLE_PINTEREST_CONTENT)
        
        # Create variations
        title = f"{random.choice(adjectives)} {base['title']}" if i >= len(SAMPLE_PINTEREST_CONTENT) else base['title']
        
        # Create content
        content = create_content(
            title=title,
            description=base['description'],
            image_url=f"{base['image_url']}?random={i}",  # Add randomness to URL to simulate different images
            source_url=f"https://pinterest.ca/pin/{random.randint(100000, 999999)}",
            categories=base['categories'],
            tags=base['tags'] + [f"pin{i}"],  # Add unique tag
            metadata={
                "source": "pinterest",
                "pinterest_id": f"pin_{random.randint(100000, 999999)}",
                "mock_data": True
            }
        )
        
        # Insert into MongoDB
        result = db.content.insert_one(content)
        content_id = result.inserted_id
        content_ids.append(content_id)
        
        logger.info(f"Created mock Pinterest content: {title} ({content_id})")
    
    return content_ids

def generate_mock_events(count=15):
    """Generate mock Toronto events"""
    db = get_mongodb_db()
    event_ids = []
    
    # Generate dates spanning the next 90 days
    today = datetime.now()
    
    for i in range(count):
        # Select a base event or create variation
        if i < len(SAMPLE_EVENTS):
            base = SAMPLE_EVENTS[i]
        else:
            base = random.choice(SAMPLE_EVENTS)
            
        # Randomize dates
        start_days_ahead = random.randint(1, 90)
        duration_days = random.randint(1, 3)
        
        start_date = today + timedelta(days=start_days_ahead)
        end_date = start_date + timedelta(days=duration_days)
        
        # Randomize location
        neighborhood = random.choice(TORONTO_NEIGHBORHOODS)
        
        # Create event name variation if needed
        event_name = base['event_name']
        if i >= len(SAMPLE_EVENTS):
            year = today.year
            season = random.choice(["Spring", "Summer", "Fall", "Winter"])
            event_name = f"{event_name} {year} - {season} Edition"
        
        # Create content for the event
        content = create_content(
            title=event_name,
            description=base['description'],
            image_url=f"{base['image_url']}?event={i}",
            source_url=f"https://eventbrite.com/e/{random.randint(100000, 999999)}",
            categories=["event"],
            tags=base['tags'] + ["toronto", "event"],
            location={
                "latitude": neighborhood["lat"] + random.uniform(-0.01, 0.01),
                "longitude": neighborhood["lon"] + random.uniform(-0.01, 0.01)
            },
            metadata={
                "source": "eventbrite",
                "eventbrite_id": f"evt_{random.randint(100000, 999999)}",
                "neighborhood": neighborhood["name"],
                "mock_data": True
            }
        )
        
        # Insert content into MongoDB
        content_result = db.content.insert_one(content)
        content_id = content_result.inserted_id
        
        # Create Toronto event
        toronto_event = create_toronto_event(
            content_id=content_id,
            event_name=event_name,
            venue=base['venue'],
            start_date=start_date,
            end_date=end_date,
            address=base['address'],
            price_range={
                "currency": "CAD",
                "is_free": random.choice([True, False]),
                "price": random.randint(10, 100) if not random.choice([True, False]) else 0
            },
            seasonal_relevance=_determine_seasonal_relevance(start_date)
        )
        
        # Insert event into MongoDB
        event_result = db.toronto_events.insert_one(toronto_event)
        event_ids.append(event_result.inserted_id)
        
        logger.info(f"Created mock event: {event_name} ({event_result.inserted_id})")
    
    return event_ids

def generate_mock_places(count=15):
    """Generate mock Toronto places"""
    db = get_mongodb_db()
    place_ids = []
    
    # Rating options
    ratings = [4.2, 4.5, 4.7, 4.8, 4.9, 5.0]
    
    for i in range(count):
        # Select a base place or create variation
        if i < len(SAMPLE_PLACES):
            base = SAMPLE_PLACES[i]
        else:
            base = random.choice(SAMPLE_PLACES)
        
        # Get neighborhood
        neighborhood_name = base["neighborhood"]
        neighborhood = next((n for n in TORONTO_NEIGHBORHOODS if n["name"] == neighborhood_name), 
                           random.choice(TORONTO_NEIGHBORHOODS))
        
        # Create title variation if needed
        title = base["title"]
        if i >= len(SAMPLE_PLACES):
            prefix = random.choice(["The", "Toronto's", "Downtown", "Uptown", "Best", "Famous"])
            title = f"{prefix} {title} {random.randint(1, 99)}"
        
        # Create content for the place
        content = create_content(
            title=title,
            description=base['description'],
            image_url=f"{base['image_url']}?place={i}",
            source_url=f"https://maps.google.com/place/?q=place_id:{random.randint(100000, 999999)}",
            categories=base['categories'],
            tags=base['tags'] + ["toronto", neighborhood_name.lower().replace(" ", "-")],
            location={
                "latitude": neighborhood["lat"] + random.uniform(-0.005, 0.005),
                "longitude": neighborhood["lon"] + random.uniform(-0.005, 0.005),
                "address": f"{random.randint(1, 999)} {random.choice(['King', 'Queen', 'Dundas', 'College', 'Bloor'])} St, Toronto, ON"
            },
            metadata={
                "source": "google_places",
                "google_place_id": f"place_{random.randint(100000, 999999)}",
                "neighborhood": neighborhood_name,
                "rating": random.choice(ratings),
                "user_ratings_total": random.randint(50, 1200),
                "mock_data": True
            }
        )
        
        # Insert into MongoDB
        result = db.content.insert_one(content)
        place_id = result.inserted_id
        place_ids.append(place_id)
        
        logger.info(f"Created mock place: {title} ({place_id})")
    
    return place_ids

def _determine_seasonal_relevance(date):
    """Determine seasonal relevance based on date"""
    month = date.month
    
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
    
    return seasons

def main():
    """Generate mock data for Toronto Trendspotter"""
    load_dotenv()
    
    # Connect to MongoDB
    db = get_mongodb_db()
    
    try:
        # Check for existing mock data
        existing_mock = db.content.count_documents({"metadata.mock_data": True})
        if existing_mock > 0:
            logger.info(f"Found {existing_mock} existing mock data records")
            delete = input("Delete existing mock data? (y/n): ").lower() == 'y'
            
            if delete:
                # Delete existing mock data
                db.content.delete_many({"metadata.mock_data": True})
                db.toronto_events.delete_many({})  # Assuming all events are mock
                logger.info("Deleted existing mock data")
            else:
                logger.info("Keeping existing mock data")
                return
        
        # Generate new mock data
        logger.info("Generating mock data...")
        
        # Generate Pinterest content
        pinterest_ids = generate_mock_pinterest_content(count=20)
        logger.info(f"Generated {len(pinterest_ids)} mock Pinterest content items")
        
        # Generate Toronto events
        event_ids = generate_mock_events(count=15)
        logger.info(f"Generated {len(event_ids)} mock Toronto events")
        
        # Generate Toronto places
        place_ids = generate_mock_places(count=15)
        logger.info(f"Generated {len(place_ids)} mock Toronto places")
        
        logger.info(f"Successfully generated {len(pinterest_ids) + len(event_ids) + len(place_ids)} mock data records")
        
    except Exception as e:
        logger.error(f"Error generating mock data: {e}")

if __name__ == "__main__":
    main()