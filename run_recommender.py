#!/usr/bin/env python3
"""
Toronto Trendspotter Recommender System Runner

This script runs the Toronto Trendspotter recommendation system, allowing you to:
1. Train different recommendation models
2. Generate recommendations for users
3. Find similar content items
4. Evaluate model performance
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from tabulate import tabulate
import random

# Add project root to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(current_file)
sys.path.insert(0, project_root)

# Import recommendation models
from src.models.collaborative_filtering import CollaborativeFiltering
from src.models.content_based import ContentBasedRecommender
from src.models.hybrid_recommender import HybridRecommender
from src.utils.db import get_mongodb_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def train_model(model_type, force=False):
    """
    Train a recommendation model
    
    Args:
        model_type (str): Type of model to train
        force (bool): Force retraining even if model exists
        
    Returns:
        object: Trained model
    """
    # Initialize model based on type
    if model_type == "collaborative":
        model = CollaborativeFiltering(approach="item")
    elif model_type == "content":
        model = ContentBasedRecommender()
    elif model_type == "hybrid":
        model = HybridRecommender()
    else:
        logger.error(f"Unknown model type: {model_type}")
        return None
    
    # Check if model is already trained
    if not force and model.load_model():
        logger.info(f"Loaded existing {model_type} model")
        return model
    
    # Train the model
    start_time = datetime.now()
    logger.info(f"Training {model_type} model...")
    
    success = model.train()
    
    if success:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        logger.info(f"Successfully trained {model_type} model in {duration:.2f} minutes")
        
        # Save the model
        if model.save_model():
            logger.info(f"Saved {model_type} model to database")
    else:
        logger.error(f"Failed to train {model_type} model")
    
    return model if success else None

def get_recommendations(model, user_id=None, content_id=None, location=None, n=10):
    """
    Get recommendations from a model
    
    Args:
        model: Recommendation model
        user_id (str): User ID for user-based recommendations
        content_id (str): Content ID for content-based recommendations
        location (dict): Location data for Toronto-specific recommendations
        n (int): Number of recommendations to get
        
    Returns:
        list: Recommendations
    """
    if not model:
        logger.error("No model provided")
        return []
    
    if not model.is_trained:
        logger.error("Model not trained")
        return []
    
    # Get recommendations based on input
    if user_id:
        if isinstance(model, HybridRecommender) and location:
            # Use Toronto-specific recommendations
            recommendations = model.get_toronto_specific_recommendations(
                user_id=user_id, 
                location=location, 
                n=n
            )
        else:
            # Use regular user recommendations
            recommendations = model.recommend_for_user(user_id, n=n)
    elif content_id:
        # Get similar content
        recommendations = model.recommend_similar_to_content(content_id, n=n)
    else:
        logger.error("Either user_id or content_id must be provided")
        return []
    
    return recommendations

def print_recommendations(recommendations, model):
    """
    Print recommendations in a nice format
    
    Args:
        recommendations (list): List of recommendations
        model: Recommendation model to use for content lookup
    """
    if not recommendations:
        print("No recommendations found")
        return
    
    # Prepare table data
    table_data = []
    
    for i, rec in enumerate(recommendations, 1):
        content_id = rec["content_id"]
        score = rec["score"]
        approach = rec.get("approach", "unknown")
        
        # Get content details
        content = model.get_content_data(content_id)
        if not content:
            continue
            
        title = content.get("title", "Unknown")
        
        # Get category and tags
        categories = ", ".join(content.get("categories", []))
        tags = ", ".join(content.get("tags", [])[:3])  # Just show first 3 tags
        
        # Get neighborhood if available
        neighborhood = content.get("location", {}).get("neighborhood", "")
        
        # For events, get extra info
        event_info = ""
        event = model.db.toronto_events.find_one({"content_id": content_id})
        if event:
            start_date = event.get("start_date", "")
            if isinstance(start_date, str):
                try:
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    start_date_str = start_date.strftime("%Y-%m-%d")
                except:
                    start_date_str = start_date
            else:
                start_date_str = start_date.strftime("%Y-%m-%d") if hasattr(start_date, 'strftime') else str(start_date)
            
            event_info = f"{start_date_str} @ {event.get('venue', '')}"
        
        # Add to table
        table_data.append([
            i, 
            title, 
            categories, 
            neighborhood,
            event_info,
            f"{score:.3f}",
            approach
        ])
    
    # Print table
    headers = ["#", "Title", "Categories", "Neighborhood", "Event Info", "Score", "Method"]
    print(tabulate(table_data, headers=headers, tablefmt="pretty"))

def evaluate_models():
    """Evaluate and compare different recommendation models"""
    # Initialize models
    models = {
        "collaborative": CollaborativeFiltering(),
        "content": ContentBasedRecommender(),
        "hybrid": HybridRecommender()
    }
    
    # Load or train models
    for name, model in models.items():
        if not model.load_model():
            logger.info(f"Training {name} model...")
            model.train()
            model.save_model()
    
    # Create evaluation dataset
    db = get_mongodb_db()
    
    # Get 50 random users
    all_users = list(db.users.find({}, {"_id": 1}))
    test_users = random.sample(all_users, min(50, len(all_users)))
    test_user_ids = [user["_id"] for user in test_users]
    
    # Create test set - latest interaction for each user
    test_data = []
    for user_id in test_user_ids:
        latest = db.interactions.find_one(
            {"user_id": user_id},
            sort=[("timestamp", -1)]
        )
        
        if latest:
            test_data.append({
                "user_id": user_id,
                "content_id": latest["content_id"],
                "rating": 1.0
            })
    
    # Evaluate each model
    results = {}
    
    for name, model in models.items():
        logger.info(f"Evaluating {name} model...")
        metrics = model._evaluate_model(test_data)
        results[name] = metrics
    
    # Print results
    print("\nModel Evaluation Results:")
    print("-" * 50)
    
    table_data = []
    for name, metrics in results.items():
        hr = metrics.get("hit_rate", 0)
        mrr = metrics.get("mean_reciprocal_rank", 0)
        table_data.append([name, f"{hr:.4f}", f"{mrr:.4f}"])
    
    headers = ["Model", "Hit Rate", "Mean Reciprocal Rank"]
    print(tabulate(table_data, headers=headers, tablefmt="pretty"))
    
    return results

def recommend_for_random_users(model, n_users=5, n_recommendations=5):
    """
    Generate recommendations for random users
    
    Args:
        model: Recommendation model
        n_users (int): Number of users to recommend for
        n_recommendations (int): Number of recommendations per user
    """
    if not model or not model.is_trained:
        logger.error("Model not trained")
        return
    
    # Get random users
    db = get_mongodb_db()
    all_users = list(db.users.find())
    
    if not all_users:
        logger.error("No users found in database")
        return
    
    selected_users = random.sample(all_users, min(n_users, len(all_users)))
    
    # Generate and print recommendations
    for user in selected_users:
        user_id = user["_id"]
        username = user.get("username", user_id)
        
        print(f"\nRecommendations for User: {username}")
        print("-" * 50)
        
        # Get user's interests for context
        interests = user.get("interests", [])
        neighborhoods = user.get("neighborhood_preferences", [])
        
        print(f"Interests: {', '.join(interests)}")
        print(f"Preferred Neighborhoods: {', '.join(neighborhoods)}")
        print()
        
        # Get recommendations
        recommendations = model.recommend_for_user(user_id, n=n_recommendations)
        print_recommendations(recommendations, model)
        
        # For comparison, also show this user's recent interactions
        interactions = list(db.interactions.find(
            {"user_id": user_id}, 
            sort=[("timestamp", -1)],
            limit=3
        ))
        
        if interactions:
            print("\nRecent Interactions:")
            for interaction in interactions:
                content_id = interaction["content_id"]
                content = model.get_content_data(content_id)
                if content:
                    print(f"- {content.get('title', 'Unknown')} ({interaction['interaction_type']})")
        
        print("\n" + "="*80 + "\n")

def main():
    """Run the Toronto Trendspotter recommender system"""
    parser = argparse.ArgumentParser(description="Toronto Trendspotter Recommender System")
    
    # Main operation
    parser.add_argument("--action", choices=["train", "recommend", "evaluate", "recommend-random"],
                      default="recommend-random", help="Action to perform")
    
    # Model selection
    parser.add_argument("--model", choices=["collaborative", "content", "hybrid"],
                      default="hybrid", help="Model type to use")
    
    # Training options
    parser.add_argument("--force", action="store_true", help="Force model retraining")
    
    # Recommendation options
    parser.add_argument("--user-id", help="User ID for recommendations")
    parser.add_argument("--content-id", help="Content ID for similar recommendations")
    parser.add_argument("--neighborhood", help="Neighborhood for Toronto-specific recommendations")
    parser.add_argument("--count", type=int, default=10, help="Number of recommendations to generate")
    
    args = parser.parse_args()
    
    try:
        if args.action == "train":
            # Train the selected model
            model = train_model(args.model, force=args.force)
            if model:
                print(f"\n{args.model.capitalize()} model trained successfully!")
            else:
                print(f"\nFailed to train {args.model} model.")
        
        elif args.action == "recommend":
            # First ensure model is trained
            model = train_model(args.model, force=args.force)
            
            if not model:
                print(f"Failed to load or train {args.model} model.")
                return
            
            # Prepare location data if neighborhood provided
            location = None
            if args.neighborhood:
                location = {"neighborhood": args.neighborhood}
            
            # Get recommendations
            recommendations = get_recommendations(
                model, 
                user_id=args.user_id, 
                content_id=args.content_id,
                location=location,
                n=args.count
            )
            
            # Print recommendations
            if args.user_id:
                print(f"\nRecommendations for User {args.user_id}:")
            elif args.content_id:
                content = model.get_content_data(args.content_id)
                title = content.get("title", "Unknown") if content else "Unknown"
                print(f"\nSimilar content to: {title}")
            
            print_recommendations(recommendations, model)
        
        elif args.action == "evaluate":
            # Evaluate all models
            results = evaluate_models()
            
        elif args.action == "recommend-random":
            # First ensure model is trained
            model = train_model(args.model, force=args.force)
            
            if not model:
                print(f"Failed to load or train {args.model} model.")
                return
            
            # Generate recommendations for random users
            recommend_for_random_users(model, n_users=5, n_recommendations=5)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()