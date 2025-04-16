import os
import sys
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from dotenv import load_dotenv

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Add scrapy project to path
scrapy_path = Path(__file__).parent / "scrapers"
if str(scrapy_path) not in sys.path:
    sys.path.append(str(scrapy_path))

def run_pinterest_spider():
    """Run the Pinterest spider to collect data"""
    # Load environment variables
    env_file = os.path.join(project_root, '.env')
    load_dotenv(env_file)
    
    # Get Scrapy settings
    os.chdir(scrapy_path)
    settings = get_project_settings()
    
    # Create and start Crawler Process
    process = CrawlerProcess(settings)
    process.crawl("pinterest")
    process.start()
    
    print("Pinterest spider completed")

if __name__ == "__main__":
    run_pinterest_spider()