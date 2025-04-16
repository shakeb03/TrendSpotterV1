from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Content:
    id: str
    title: str
    description: Optional[str]
    image_url: str
    source_url: Optional[str]
    categories: List[str]
    tags: List[str]
    location: Optional[dict]  # Geolocation for Toronto places
    created_at: datetime
    metadata: dict  # Additional content attributes

@dataclass
class TorontoEvent:
    id: str
    content_id: str  # Reference to base Content
    event_name: str
    venue: str
    start_date: datetime
    end_date: datetime
    address: dict
    price_range: Optional[dict]
    seasonal_relevance: Optional[List[str]]  # E.g., "summer", "holiday"