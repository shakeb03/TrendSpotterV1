import os
import sys
import logging
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from geopy.distance import geodesic

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.utils.db import get_mongodb_db
from src.data.models.mongodb_models import create_feature_vector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocationEnricher:
    """Enrich content with location-based features"""
    
    # Toronto neighborhood data
    # For a real implementation, this would be loaded from a more comprehensive dataset
    TORONTO_NEIGHBORHOODS = [
        {"name": "Downtown Core", "lat": 43.6511, "lon": -79.3832, "tags": ["urban", "central", "business"]},
        {"name": "Distillery District", "lat": 43.6503, "lon": -79.3597, "tags": ["historic", "artistic", "trendy"]},
        {"name": "Kensington Market", "lat": 43.6547, "lon": -79.4005, "tags": ["eclectic", "multicultural", "shopping"]},
        {"name": "The Beaches", "lat": 43.6762, "lon": -79.2995, "tags": ["lakefront", "relaxed", "family-friendly"]},
        {"name": "Yorkville", "lat": 43.6709, "lon": -79.3933, "tags": ["upscale", "luxury", "shopping"]},
        {"name": "Queen West", "lat": 43.6468, "lon": -79.4119, "tags": ["trendy", "fashion", "artistic"]},
        {"name": "Liberty Village", "lat": 43.6371, "lon": -79.4208, "tags": ["modern", "urban", "young-professional"]},
        {"name": "Leslieville", "lat": 43.6626, "lon": -79.3357, "tags": ["trendy", "family-friendly", "foodie"]},
        {"name": "Little Italy", "lat": 43.6547, "lon": -79.4228, "tags": ["italian", "foodie", "lively"]},
        {"name": "Chinatown", "lat": 43.6529, "lon": -79.3975, "tags": ["asian", "multicultural", "foodie"]}
    ]
    
    # Toronto points of interest
    TORONTO_POIS = [
        {"name": "CN Tower", "lat": 43.6426, "lon": -79.3871, "tags": ["landmark", "tourist", "attraction"]},
        {"name": "Royal Ontario Museum", "lat": 43.6677, "lon": -79.3948, "tags": ["museum", "culture", "education"]},
        {"name": "Art Gallery of Ontario", "lat": 43.6536, "lon": -79.3924, "tags": ["art", "culture", "gallery"]},
        {"name": "Toronto Islands", "lat": 43.6228, "lon": -79.3817, "tags": ["outdoor", "leisure", "waterfront"]},
        {"name": "St. Lawrence Market", "lat": 43.6498, "lon": -79.3719, "tags": ["market", "food", "historic"]},
        {"name": "Ripley's Aquarium", "lat": 43.6424, "lon": -79.3860, "tags": ["attraction", "family", "aquarium"]},
        {"name": "High Park", "lat": 43.6465, "lon": -79.4637, "tags": ["park", "outdoor", "nature"]},
        {"name": "Rogers Centre", "lat": 43.6414, "lon": -79.3894, "tags": ["sports", "entertainment", "baseball"]},
        {"name": "Toronto Eaton Centre", "lat": 43.6544, "lon": -79.3807, "tags": ["shopping", "mall", "urban"]},
        {"name": "Casa Loma", "lat": 43.6781, "lon": -79.4094, "tags": ["castle", "historic", "attraction"]}
    ]
    
    def __init__(self):
        # Toronto city center coordinates
        self.toronto_center = (43.6532, -79.3832)
        logger.info("Initialized LocationEnricher")
    
    def get_nearest_neighborhood(self, lat, lon):
        """
        Find the nearest Toronto neighborhood to the given coordinates
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            dict: Neighborhood information
        """
        if lat is None or lon is None:
            return None
        
        nearest_dist = float('inf')
        nearest_neighborhood = None
        
        for neighborhood in self.TORONTO_NEIGHBORHOODS:
            neighborhood_coords = (neighborhood["lat"], neighborhood["lon"])
            distance = geodesic((lat, lon), neighborhood_coords).kilometers
            
            if distance < nearest_dist:
                nearest_dist = distance
                nearest_neighborhood = neighborhood
        
        # Add distance to result
        if nearest_neighborhood:
            result = dict(nearest_neighborhood)
            result["distance_km"] = nearest_dist
            return result
        
        return None
    
    def get_nearby_pois(self, lat, lon, max_distance=2.0):
        """
        Find points of interest near the given coordinates
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            max_distance (float): Maximum distance in kilometers
            
        Returns:
            list: Nearby POIs with distances
        """
        if lat is None or lon is None:
            return []
        
        nearby_pois = []
        
        for poi in self.TORONTO_POIS:
            poi_coords = (poi["lat"], poi["lon"])
            distance = geodesic((lat, lon), poi_coords).kilometers
            
            if distance <= max_distance:
                poi_with_distance = dict(poi)
                poi_with_distance["distance_km"] = distance
                nearby_pois.append(poi_with_distance)
        
        # Sort by distance
        nearby_pois.sort(key=lambda x: x["distance_km"])
        
        return nearby_pois
    
    def calculate_downtown_proximity(self, lat, lon):
        """
        Calculate proximity to downtown Toronto
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            float: Proximity score (0-1), higher means closer to downtown
        """
        if lat is None or lon is None:
            return 0.5  # Default middle value
        
        # Calculate distance to city center
        distance = geodesic((lat, lon), self.toronto_center).kilometers
        
        # Convert to proximity score (closer = higher score)
        # Max distance within Toronto is about 25km from center
        max_distance = 25.0
        proximity = max(0, 1 - (distance / max_distance))
        
        return proximity
    
    def enrich_content_location(self, content_id=None, limit=100):
        """
        Enrich content with location-based features
        
        Args:
            content_id (str): Specific content ID to enrich, or None for batch processing
            limit (int): Maximum number of content items to process in batch mode
            
        Returns:
            int: Number of content items enriched
        """
        # Initialize MongoDB connection
        mongo_db = get_mongodb_db()
        
        # Track enriched content
        enriched_count = 0
        
        try:
            # Query for content with location data
            filter_criteria = {"location": {"$ne": {}}}
            if content_id:
                filter_criteria["_id"] = content_id
            
            # Get content from MongoDB
            contents = mongo_db.content.find(filter_criteria).limit(limit if limit else 0)
            
            logger.info(f"Found content items with location data to enrich")
            
            for content in contents:
                # Extract location
                location = content.get("location", {})
                
                if not location:
                    logger.warning(f"Content {content['_id']} has invalid location data")
                    continue
                
                # Get coordinates
                lat = location.get("latitude")
                lon = location.get("longitude")
                
                if lat is None or lon is None:
                    logger.warning(f"Content {content['_id']} is missing latitude or longitude")
                    continue
                
                # Get nearest neighborhood
                neighborhood = self.get_nearest_neighborhood(lat, lon)
                
                # Get nearby POIs
                nearby_pois = self.get_nearby_pois(lat, lon)
                
                # Calculate downtown proximity
                downtown_proximity = self.calculate_downtown_proximity(lat, lon)
                
                # Create location features
                location_features = {
                    "neighborhood": neighborhood,
                    "nearby_pois": nearby_pois,
                    "downtown_proximity": downtown_proximity
                }
                
                # Store enriched data in MongoDB as feature vector
                feature_vector = create_feature_vector(
                    content_id=content["_id"],
                    feature_type="location",
                    features=location_features
                )
                
                mongo_db.feature_vectors.insert_one(feature_vector)
                
                # Update content tags with neighborhood and POI tags
                tags = set(content.get("tags", []))
                
                # Add neighborhood tags
                if neighborhood:
                    tags.update(neighborhood.get("tags", []))
                    tags.add(neighborhood["name"].lower().replace(" ", "-"))
                
                # Add top 2 POI tags if they're close
                for poi in nearby_pois[:2]:
                    if poi["distance_km"] < 1.0:  # Only if very close
                        tags.update(poi.get("tags", []))
                
                # Update content tags and metadata in database
                update_data = {
                    "$set": {
                        "tags": list(tags)
                    }
                }
                
                # Add neighborhood name to metadata
                if neighborhood:
                    if not content.get("metadata"):
                        update_data["$set"]["metadata"] = {}
                    
                    update_data["$set"]["metadata.neighborhood"] = neighborhood["name"]
                
                # Update the document
                mongo_db.content.update_one(
                    {"_id": content["_id"]},
                    update_data
                )
                
                enriched_count += 1
                logger.info(f"Enriched location for content {content['_id']}")
            
            return enriched_count
            
        except Exception as e:
            logger.error(f"Error enriching content locations: {e}")
            return enriched_count


if __name__ == "__main__":
    # Simple test execution
    enricher = LocationEnricher()
    num_enriched = enricher.enrich_content_location(limit=50)
    print(f"Enriched {num_enriched} content items with location data")