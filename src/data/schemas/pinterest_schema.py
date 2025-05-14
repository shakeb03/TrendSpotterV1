import json
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, root_validator, validator
from datetime import datetime

# Define nested models for complex structures
class PinterestImage(BaseModel):
    url: str
    height: Optional[int] = None
    width: Optional[int] = None

class PinterestImageSet(BaseModel):
    """Model for the various image sizes Pinterest provides"""
    orig: Optional[PinterestImage] = None
    original: Optional[PinterestImage] = None  # Alternative field name
    x236: Optional[PinterestImage] = Field(None, alias="236x")
    x136: Optional[PinterestImage] = Field(None, alias="136x136")
    x60: Optional[PinterestImage] = Field(None, alias="60x60")
    x170: Optional[PinterestImage] = Field(None, alias="170x")
    x474: Optional[PinterestImage] = Field(None, alias="474x")
    x564: Optional[PinterestImage] = Field(None, alias="564x")
    x736: Optional[PinterestImage] = Field(None, alias="736x")
    x600: Optional[PinterestImage] = Field(None, alias="600x315")
    
    # Support for arbitrary additional image sizes
    additional_sizes: Dict[str, PinterestImage] = Field(default_factory=dict)

    class Config:
        extra = "allow"  # Allow extra fields that might come from API
        arbitrary_types_allowed = True
        
    @root_validator(pre=True)
    def extract_additional_sizes(cls, values: Dict) -> Dict:
        """Extract image sizes that aren't explicitly defined in our model"""
        result = dict(values)
        additional = {}
        
        for key, value in values.items():
            if key not in ["236x", "136x136", "60x60", "170x", "474x", "564x", "736x", "600x315", "orig", "original"]:
                if isinstance(value, dict) and "url" in value:
                    additional[key] = value
                    
        result["additional_sizes"] = additional
        return result

class PinterestUser(BaseModel):
    """Model for Pinterest user data"""
    id: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    image_medium_url: Optional[str] = None
    image_small_url: Optional[str] = None
    followed_by_me: Optional[bool] = None
    explicitly_followed_by_me: Optional[bool] = None
    blocked_by_me: Optional[bool] = None
    follower_count: Optional[int] = None
    
    class Config:
        extra = "allow"  # Allow extra fields

class PinterestBoard(BaseModel):
    """Model for Pinterest board data"""
    id: str
    name: Optional[str] = None
    url: Optional[str] = None
    privacy: Optional[str] = None
    owner: Optional[PinterestUser] = None
    
    class Config:
        extra = "allow"

class PinterestAttribution(BaseModel):
    """Model for attribution data"""
    id: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    image_medium_url: Optional[str] = None
    followed_by_me: Optional[bool] = None
    follower_count: Optional[int] = None
    
    class Config:
        extra = "allow"

class AggregatedPinData(BaseModel):
    """Model for aggregated pin data"""
    id: Optional[str] = None
    comment_count: Optional[int] = None
    
    class Config:
        extra = "allow"

class PinterestPin(BaseModel):
    """Primary model for Pinterest pin data"""
    # Core pin identification
    id: str
    type: Optional[str] = "pin"
    url: Optional[str] = None
    
    # Pin content
    description: Optional[str] = None
    description_html: Optional[str] = None
    alt_text: Optional[str] = None
    domain: Optional[str] = None
    grid_title: Optional[str] = None
    
    # Pin stats
    comment_count: Optional[int] = 0
    favorite_user_count: Optional[int] = 0
    repin_count: Optional[int] = 0
    share_count: Optional[int] = 0
    comments_disabled: Optional[bool] = False
    
    # Visual elements
    dominant_color: Optional[str] = None
    image_signature: Optional[str] = None
    images: Optional[PinterestImageSet] = None
    videos: Optional[Any] = None
    embed: Optional[Any] = None
    
    # Relationships
    owner: Optional[PinterestUser] = None
    pinner: Optional[PinterestUser] = None
    board: Optional[PinterestBoard] = None
    attribution: Optional[PinterestAttribution] = None
    closeup_attribution: Optional[PinterestAttribution] = None
    
    # Additional metadata
    created_at: Optional[str] = None
    category: Optional[str] = None
    isRepin: Optional[bool] = None
    closeup_description: Optional[str] = None
    closeup_unified_description: Optional[str] = None
    aggregated_pin_data: Optional[AggregatedPinData] = None
    pinner_id: Optional[str] = None
    pinner_follower_count: Optional[int] = None
    
    # Custom fields for Toronto Trendspotter
    categories: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # System tracking fields (for internal use)
    created_in_system: Optional[datetime] = None
    updated_in_system: Optional[datetime] = None
    
    class Config:
        extra = "allow"  # Allow extra fields from the API
    
    @validator('created_in_system', 'updated_in_system', pre=True, always=True)
    def set_datetimes(cls, v):
        """Set default datetimes if not provided"""
        return v or datetime.now()

    def to_dict(self) -> Dict:
        """Convert model to dictionary for storage"""
        return json.loads(self.json(exclude_none=True))
    
    @classmethod
    def from_api_response(cls, data: Dict) -> 'PinterestPin':
        """Create instance from raw API response"""
        # Handle any special transformations here
        
        # Example: Extract tags from description if needed
        if 'description' in data and data['description'] and not data.get('tags'):
            # This is just an example - adjust according to your needs
            description = data['description']
            potential_tags = [word.strip('#') for word in description.split() 
                             if word.startswith('#')]
            if potential_tags:
                data['tags'] = potential_tags
                
        # For Toronto-specific pins, add a Toronto tag if not present
        if ('Toronto' in str(data.get('description', '')) or 
            'Toronto' in str(data.get('grid_title', '')) or
            'Toronto' in str(data.get('closeup_description', ''))) and 'tags' in data:
            
            if 'tags' not in data:
                data['tags'] = ['Toronto']
            elif 'Toronto' not in data['tags'] and 'toronto' not in data['tags']:
                data['tags'].append('Toronto')
        
        # Create the model instance
        return cls(**data)


# Schema for storing Pinterest data in MongoDB
PINTEREST_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["id"],
            "properties": {
                "id": {
                    "bsonType": "string",
                    "description": "The unique identifier for the pin"
                },
                "type": {
                    "bsonType": "string",
                    "description": "The type of Pinterest content (typically 'pin')"
                },
                "url": {
                    "bsonType": "string",
                    "description": "The URL of the pin on Pinterest"
                },
                "description": {
                    "bsonType": ["string", "null"],
                    "description": "The description of the pin"
                },
                "grid_title": {
                    "bsonType": ["string", "null"],
                    "description": "The title displayed in the grid view"
                },
                "domain": {
                    "bsonType": ["string", "null"],
                    "description": "The source domain of the pin content"
                },
                "images": {
                    "bsonType": ["object", "null"],
                    "description": "Various image sizes and URLs"
                },
                "created_at": {
                    "bsonType": ["string", "null"],
                    "description": "When the pin was created on Pinterest"
                },
                "categories": {
                    "bsonType": "array",
                    "description": "Categories assigned to the pin in our system"
                },
                "tags": {
                    "bsonType": "array",
                    "description": "Tags assigned to the pin in our system"
                },
                "metadata": {
                    "bsonType": "object",
                    "description": "Additional metadata about the pin"
                },
                "created_in_system": {
                    "bsonType": "date",
                    "description": "When the pin was first added to our database"
                },
                "updated_in_system": {
                    "bsonType": "date",
                    "description": "When the pin was last updated in our database"
                }
            }
        }
    },
    "validationLevel": "moderate",
    "validationAction": "warn"  # Use 'warn' instead of 'error' to avoid breaking changes
}

# Function to create MongoDB indexes
def create_pinterest_indexes(collection):
    """Create indexes for the Pinterest collection"""
    # Create indexes for common query fields
    collection.create_index("id", unique=True)
    collection.create_index("tags")
    collection.create_index("categories")
    collection.create_index("created_at")
    collection.create_index("domain")
    collection.create_index("grid_title")
    
    # Create text indexes for search functionality
    collection.create_index([
        ("description", "text"),
        ("grid_title", "text"),
        ("closeup_description", "text")
    ], name="text_search_index")
    
    # Create compound indexes for common queries
    collection.create_index([
        ("tags", 1),
        ("created_at", -1)
    ])
    
    # Geospatial index if you add location data later
    # collection.create_index([("location", "2dsphere")])

# Function to migrate existing data
def migrate_existing_data(old_collection, new_collection):
    """Migrate data from old schema to new schema"""
    for old_doc in old_collection.find():
        try:
            # Attempt to convert to new schema
            pin = PinterestPin.from_api_response(old_doc)
            
            # Update dates
            pin.created_in_system = old_doc.get('created_in_system', datetime.now())
            pin.updated_in_system = datetime.now()
            
            # Insert with upsert to avoid duplicates
            new_collection.update_one(
                {"id": pin.id},
                {"$set": pin.to_dict()},
                upsert=True
            )
        except Exception as e:
            print(f"Error migrating pin {old_doc.get('id')}: {str(e)}")