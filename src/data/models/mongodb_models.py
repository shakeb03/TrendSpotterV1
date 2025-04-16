"""
MongoDB schema models for Toronto Trendspotter.

These model classes help create structured documents for MongoDB.
They're not enforced by the database but provide consistency in our application.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import json

def create_user(
    username: str,
    location: Optional[Dict] = None,
    interests: Optional[List[str]] = None
) -> Dict:
    """
    Create a user document
    
    Args:
        username: Unique username
        location: Optional geolocation data
        interests: Optional list of user interests
        
    Returns:
        Dict: User document
    """
    from src.utils.db import generate_uuid
    
    return {
        "_id": generate_uuid(),
        "username": username,
        "location": location or {},
        "interests": interests or [],
        "created_at": datetime.now(),
        "last_active": datetime.now()
    }

def create_content(
    title: str,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    source_url: Optional[str] = None,
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    location: Optional[Dict] = None,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Create a content document
    
    Args:
        title: Content title
        description: Content description
        image_url: URL to image
        source_url: Original source URL
        categories: Content categories
        tags: Content tags
        location: Optional geolocation data
        metadata: Additional metadata
        
    Returns:
        Dict: Content document
    """
    from src.utils.db import generate_uuid
    
    return {
        "_id": generate_uuid(),
        "title": title,
        "description": description or "",
        "image_url": image_url or "",
        "source_url": source_url or "",
        "categories": categories or [],
        "tags": tags or [],
        "location": location or {},
        "created_at": datetime.now(),
        "metadata": metadata or {}
    }

def create_toronto_event(
    content_id: str,
    event_name: str,
    venue: str,
    start_date: datetime,
    end_date: datetime,
    address: Dict,
    price_range: Optional[Dict] = None,
    seasonal_relevance: Optional[List[str]] = None
) -> Dict:
    """
    Create a Toronto event document
    
    Args:
        content_id: Reference to content document
        event_name: Event name
        venue: Venue name
        start_date: Start date and time
        end_date: End date and time
        address: Address information
        price_range: Optional price information
        seasonal_relevance: Optional seasonal tags
        
    Returns:
        Dict: Toronto event document
    """
    from src.utils.db import generate_uuid
    
    return {
        "_id": generate_uuid(),
        "content_id": content_id,
        "event_name": event_name,
        "venue": venue,
        "start_date": start_date,
        "end_date": end_date,
        "address": address,
        "price_range": price_range or {},
        "seasonal_relevance": seasonal_relevance or []
    }

def create_interaction(
    user_id: str,
    content_id: str,
    interaction_type: str,
    session_id: str,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Create an interaction document
    
    Args:
        user_id: User ID
        content_id: Content ID
        interaction_type: Type of interaction (view, save, click)
        session_id: Session identifier
        metadata: Additional metadata
        
    Returns:
        Dict: Interaction document
    """
    from src.utils.db import generate_uuid
    
    return {
        "_id": generate_uuid(),
        "user_id": user_id,
        "content_id": content_id,
        "interaction_type": interaction_type,
        "timestamp": datetime.now(),
        "session_id": session_id,
        "metadata": metadata or {}
    }

def create_feature_vector(
    content_id: str,
    feature_type: str,
    features: Any,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Create a feature vector document
    
    Args:
        content_id: Content ID
        feature_type: Type of feature (image, text, location)
        features: Feature vector or data
        metadata: Additional metadata
        
    Returns:
        Dict: Feature vector document
    """
    from src.utils.db import generate_uuid
    
    return {
        "_id": generate_uuid(),
        "content_id": content_id,
        "feature_type": feature_type,
        "features": features,
        "created_at": datetime.now(),
        "metadata": metadata or {}
    }

def document_to_json(document: Dict) -> str:
    """
    Convert a document to JSON string with datetime handling
    
    Args:
        document: MongoDB document
        
    Returns:
        str: JSON string
    """
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)
    
    return json.dumps(document, cls=DateTimeEncoder)