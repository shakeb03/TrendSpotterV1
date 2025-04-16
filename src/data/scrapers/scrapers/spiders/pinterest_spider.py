import json
import scrapy
import uuid
from datetime import datetime
from scrapy.http import Request

class PinterestSpider(scrapy.Spider):
    name = "pinterest"
    allowed_domains = ["pinterest.ca", "pinterest.com"]
    
    # Keywords relevant to Toronto
    TORONTO_KEYWORDS = [
        "Toronto food", "Toronto fashion", "Toronto events", 
        "Toronto art", "Toronto lifestyle", "Toronto travel",
        "Toronto design", "Toronto photography", "Toronto DIY"
    ]
    
    def start_requests(self):
        """Generate start URLs based on Toronto keywords"""
        for keyword in self.TORONTO_KEYWORDS:
            # Encode the keyword for URL
            encoded_keyword = keyword.replace(" ", "+")
            url = f"https://www.pinterest.ca/search/pins/?q={encoded_keyword}"
            yield Request(url=url, callback=self.parse, meta={"keyword": keyword})
    
    def parse(self, response):
        """Parse the Pinterest search results page"""
        keyword = response.meta.get("keyword")
        self.logger.info(f"Parsing results for keyword: {keyword}")
        
        # Extract pin data from the page
        # Pinterest loads data dynamically, so we'll simulate that structure
        # In a real implementation, you would need to handle JavaScript rendering
        
        # Find all pin elements
        pins = response.css("div[data-test-id='pin']")
        
        for pin in pins:
            # Extract data from each pin
            pin_id = pin.css("::attr(data-pin-id)").get()
            title = pin.css("div[data-test-id='pinTitle'] ::text").get()
            description = pin.css("div[data-test-id='pinDescription'] ::text").get()
            image_url = pin.css("img::attr(src)").get()
            
            # Create a unique ID if pin_id is not available
            if not pin_id:
                pin_id = str(uuid.uuid4())
            
            # Store the extracted data
            yield {
                "id": pin_id,
                "title": title or "",
                "description": description or "",
                "image_url": image_url or "",
                "source_url": f"https://www.pinterest.ca/pin/{pin_id}/",
                "categories": [keyword.split()[-1]],  # e.g., "food" from "Toronto food"
                "tags": keyword.split(),
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "search_keyword": keyword,
                    "scrape_date": datetime.now().isoformat()
                }
            }
        
        # Follow pagination if available
        next_page = response.css("a[aria-label='Next page']::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse, meta={"keyword": keyword})

    def closed(self, reason):
        """Log when spider closes"""
        self.logger.info(f"Spider closed: {reason}")