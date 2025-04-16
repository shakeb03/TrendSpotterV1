#!/usr/bin/env python3
"""
TrendSpotter Data Pipeline Runner

This script provides a simple way to run the TrendSpotter data pipeline.
Run this from the project root directory.
"""

import os
import sys
import argparse

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.data_collector import run_data_collection
from src.data.data_preprocessor import run_data_preprocessing


def main():
    parser = argparse.ArgumentParser(description="Run TrendSpotter data pipeline")
    parser.add_argument(
        "--mode",
        choices=["full", "collect", "process"],
        default="full",
        help="Pipeline mode: full pipeline, just collection, or just processing"
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["pinterest", "eventbrite"],
        help="Data sources to collect from (for collection mode)"
    )
    parser.add_argument(
        "--processors",
        nargs="+",
        choices=["image", "text", "location"],
        help="Processors to run (for processing mode)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of items to process"
    )
    
    args = parser.parse_args()
    
    print("=====================================================")
    print("Toronto TrendSpotter - Data Pipeline")
    print("=====================================================")
    
    if args.mode in ["full", "collect"]:
        print("\n🔍 Running Data Collection")
        run_data_collection(sources=args.sources)
    
    if args.mode in ["full", "process"]:
        print("\n⚙️ Running Data Processing")
        run_data_preprocessing(processors=args.processors, limit=args.limit)
    
    print("\n✅ Pipeline completed!")

if __name__ == "__main__":
    main()