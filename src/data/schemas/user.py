from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class User:
    id: str
    username: str
    location: Optional[dict]  # Geolocation data for Toronto-specific recommendations
    interests: List[str]
    created_at: datetime
    last_active: datetime

@dataclass
class Interaction:
    id: str
    user_id: str
    content_id: str
    interaction_type: str  # "view", "save", "click", etc.
    timestamp: datetime
    session_id: str
    metadata: dict  # Additional context about the interaction