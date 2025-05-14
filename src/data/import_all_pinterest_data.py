import os
import sys
import glob
import logging
from pathlib import Path

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.data.import_pinterest_data import import_pinterest_json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def import_all_pinterest_data(data_dir):
    """
    Import all Pinterest JSON files from a directory
    
    Args:
        data_dir (str): Path to directory containing Pinterest JSON files
        
    Returns:
        int: Total number of pins imported
    """
    if not os.path.isdir(data_dir):
        logger.error(f"Directory not found: {data_dir}")
        return 0
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(data_dir, "**", "*.json"), recursive=True)
    
    if not json_files:
        logger.error(f"No JSON files found in {data_dir}")
        return 0
    
    logger.info(f"Found {len(json_files)} JSON files to import")
    
    # Import each file
    total_imported = 0
    for json_file in json_files:
        logger.info(f"Importing {json_file}...")
        count = import_pinterest_json(json_file)
        total_imported += count
    
    logger.info(f"Total pins imported: {total_imported}")
    return total_imported

def main():
    """
    Main function to import all Pinterest data
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Import all Pinterest JSON files from a directory')
    parser.add_argument('data_dir', help='Path to directory containing Pinterest JSON files')
    
    args = parser.parse_args()
    
    import_all_pinterest_data(args.data_dir)

if __name__ == "__main__":
    main()