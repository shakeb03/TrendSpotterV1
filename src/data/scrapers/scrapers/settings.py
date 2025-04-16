import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path to make imports work
project_root = Path(__file__).absolute().parents[4]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Load environment variables
env_file = os.path.join(project_root, '.env')
load_dotenv(env_file)

BOT_NAME = "scrapers"

SPIDER_MODULES = ["scrapers.spiders"]
NEWSPIDER_MODULE = "scrapers.spiders"

# Crawl responsibly by identifying yourself
USER_AGENT = "Toronto Trendspotter Project (+https://github.com/yourusername/Trendspotter-V1)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# Disable cookies for better crawling
COOKIES_ENABLED = False

# Configure item pipelines
ITEM_PIPELINES = {
    "scrapers.pipelines.MongoPipeline": 300,
    "scrapers.pipelines.JsonFilePipeline": 500,
}

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 1 day
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [503, 504, 505, 500, 400, 401, 402, 403, 404]

# Retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"