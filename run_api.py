#!/usr/bin/env python3
"""
Toronto Trendspotter: Recommendation API Runner

This script runs the FastAPI recommendation service for Toronto Trendspotter.
It provides an easy way to start the API and manage the service.
"""

import os
import sys
import logging
import argparse
import uvicorn
from pathlib import Path
import subprocess
import multiprocessing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')
    ]
)
logger = logging.getLogger(__name__)

def check_models_trained():
    """Check if recommendation models are trained"""
    # Add project root to path
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(current_file)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        from src.models.hybrid_recommender import HybridRecommender
        
        # Try to load hybrid model (which loads other models)
        model = HybridRecommender()
        if model.load_model():
            return True
        
        # If model doesn't exist, prompt to train
        print("Recommendation models not found or not trained.")
        train = input("Would you like to train them now? (y/n): ")
        
        if train.lower() == 'y':
            # Run training script
            print("Training recommendation models...")
            subprocess.call([sys.executable, "train_models.py"])
            return True
        else:
            print("Warning: API will start but may not work properly without trained models.")
            return False
            
    except Exception as e:
        logger.error(f"Error checking model training: {e}")
        return False

def start_api(host="127.0.0.1", port=8000, reload=False):
    """Start the FastAPI server"""
    api_module = "src.api.recommendation_api:app"
    
    logger.info(f"Starting Toronto Trendspotter API on {host}:{port}")
    print(f"\n{'='*50}")
    print(f"Toronto Trendspotter Recommendation API")
    print(f"{'='*50}")
    print(f"API will be available at: http://{host}:{port}")
    print(f"Documentation available at: http://{host}:{port}/docs")
    print(f"{'='*50}\n")
    
    uvicorn.run(
        api_module,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

def main():
    """Run the Toronto Trendspotter API"""
    parser = argparse.ArgumentParser(description="Run Toronto Trendspotter Recommendation API")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run API on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run API on")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    parser.add_argument("--skip-check", action="store_true", help="Skip checking if models are trained")
    
    args = parser.parse_args()
    
    # Check if models are trained (unless skip-check is specified)
    if not args.skip_check:
        check_models_trained()
    
    # Start the API
    try:
        start_api(args.host, args.port, args.reload)
    except KeyboardInterrupt:
        logger.info("API server stopped by user")
    except Exception as e:
        logger.error(f"Error running API: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()