#!/usr/bin/env python3
"""
Enhanced Mock Data Generator for Toronto Trendspotter

This script generates a large, realistic dataset for the Toronto Trendspotter project with:
- Pinterest-like visual content (500+ items)
- Toronto events (300+ events across neighborhoods)
- Toronto places (200+ businesses and attractions)

The data includes detailed metadata, realistic locations, categories, and relationships
to support recommendation algorithms and data preprocessing tasks.
"""

import calendar  # Add this import at the top
import os
import sys
import random
import json
import uuid
import calendar
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import numpy as np
from pathlib import Path

# Add project root to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(current_file)
sys.path.insert(0, project_root)

from src.utils.db import get_mongodb_db
from src.data.models.mongodb_models import create_content, create_toronto_event

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Toronto neighborhoods with accurate coordinates and characteristics
TORONTO_NEIGHBORHOODS = [
    {"name": "Downtown Core", "lat": 43.6511, "lon": -79.3832, 
     "tags": ["urban", "central", "business", "tourist", "busy"], 
     "venues": ["Metro Toronto Convention Centre", "Scotiabank Arena", "CF Toronto Eaton Centre", "Nathan Phillips Square"],
     "characteristics": "High-rise buildings, corporate offices, tourist attractions, entertainment venues",
     "popular": True},
    
    {"name": "Distillery District", "lat": 43.6503, "lon": -79.3597, 
     "tags": ["historic", "artistic", "trendy", "cobblestone", "pedestrian"], 
     "venues": ["Young Centre for the Performing Arts", "Distillery Restaurants Corp", "Gooderham & Worts Distillery", "Arta Gallery"],
     "characteristics": "Victorian industrial architecture, art galleries, restaurants, shops, pedestrian-only",
     "popular": True},
    
    {"name": "Kensington Market", "lat": 43.6547, "lon": -79.4005, 
     "tags": ["eclectic", "multicultural", "bohemian", "vintage", "food"], 
     "venues": ["Kensington Market", "Blue Banana Market", "Wanda's Pie in the Sky", "Courage My Love"],
     "characteristics": "Diverse food shops, vintage clothing, international cuisines, street art, bohemian vibe",
     "popular": True},
    
    {"name": "The Beaches", "lat": 43.6762, "lon": -79.2995, 
     "tags": ["lakefront", "relaxed", "family-friendly", "outdoor", "beach"], 
     "venues": ["Woodbine Beach Park", "Kew Gardens", "The Beaches Boardwalk", "Fox Theatre"],
     "characteristics": "Sandy beaches, lakefront boardwalk, family-oriented, relaxed atmosphere",
     "popular": True},
    
    {"name": "Yorkville", "lat": 43.6709, "lon": -79.3933, 
     "tags": ["upscale", "luxury", "shopping", "fashion", "elegant"], 
     "venues": ["Hazelton Hotel", "Yorkville Village", "Sassafraz", "Holt Renfrew"],
     "characteristics": "Luxury boutiques, fine dining, high-end hotels, affluent atmosphere",
     "popular": True},
    
    {"name": "Queen West", "lat": 43.6468, "lon": -79.4119, 
     "tags": ["trendy", "fashion", "artistic", "hip", "nightlife"], 
     "venues": ["The Drake Hotel", "Trinity Bellwoods Park", "Museum of Contemporary Art", "Ossington Strip"],
     "characteristics": "Trendy shops, galleries, bars, music venues, fashion-forward crowd",
     "popular": True},
    
    {"name": "Liberty Village", "lat": 43.6371, "lon": -79.4208, 
     "tags": ["modern", "urban", "young-professional", "lofts", "tech"], 
     "venues": ["Liberty Market Building", "Brazen Head Irish Pub", "Lamport Stadium", "Balzac's Coffee"],
     "characteristics": "Condos, converted factories, tech startups, restaurants, young professionals",
     "popular": True},
    
    {"name": "Leslieville", "lat": 43.6626, "lon": -79.3357, 
     "tags": ["trendy", "family-friendly", "foodie", "residential", "cafes"], 
     "venues": ["Greenwood Park", "Lady Marmalade", "Ed's Real Scoop", "The Opera House"],
     "characteristics": "Brunch spots, young families, boutiques, cafes, residential feel",
     "popular": True},
    
    {"name": "Little Italy", "lat": 43.6547, "lon": -79.4228, 
     "tags": ["italian", "foodie", "lively", "restaurants", "cafes"], 
     "venues": ["Cafe Diplomatico", "Dufferin Grove Park", "Royal Cinema", "Bar Raval"],
     "characteristics": "Italian restaurants, cafes, bars, vibrant nightlife, cultural heritage",
     "popular": True},
    
    {"name": "Chinatown", "lat": 43.6529, "lon": -79.3975, 
     "tags": ["asian", "multicultural", "foodie", "busy", "markets"], 
     "venues": ["Dragon City Mall", "Kensington Mall", "Lai Wah Heen", "Dumpling House"],
     "characteristics": "Chinese restaurants, groceries, shops, affordable dining, cultural diversity",
     "popular": True},
     
    {"name": "Annex", "lat": 43.6688, "lon": -79.4030, 
     "tags": ["student", "academic", "bookish", "historic", "youthful"], 
     "venues": ["University of Toronto", "Bloor Hot Docs Cinema", "Lee's Palace", "BMV Books"],
     "characteristics": "Historic mansions, student population, bookstores, cafes, Victorian architecture",
     "popular": True},
     
    {"name": "Danforth/Greektown", "lat": 43.6796, "lon": -79.3518, 
     "tags": ["greek", "family-friendly", "restaurants", "lively", "cultural"], 
     "venues": ["The Danforth Music Hall", "Withrow Park", "Messini Authentic Gyros", "Alexander the Great Parkette"],
     "characteristics": "Greek restaurants, Mediterranean culture, family-owned businesses, Taste of the Danforth",
     "popular": True},
     
    {"name": "Harbourfront", "lat": 43.6382, "lon": -79.3767, 
     "tags": ["waterfront", "tourist", "scenic", "cultural", "recreational"], 
     "venues": ["Harbourfront Centre", "Toronto Islands Ferry Terminal", "Power Plant Contemporary Art Gallery", "Queens Quay Terminal"],
     "characteristics": "Waterfront promenades, cultural activities, marinas, condo developments, tourist attractions",
     "popular": True},
     
    {"name": "Roncesvalles", "lat": 43.6393, "lon": -79.4487, 
     "tags": ["polish", "family-friendly", "quiet", "residential", "cafes"], 
     "venues": ["High Park", "Revue Cinema", "Cafe Polonez", "Cherry Bomb Coffee"],
     "characteristics": "Polish community, family-oriented, independent shops, quiet atmosphere",
     "popular": False},
     
    {"name": "West Queen West", "lat": 43.6442, "lon": -79.4196, 
     "tags": ["arty", "creative", "galleries", "fashion", "edgy"], 
     "venues": ["The Gladstone Hotel", "Graffiti Alley", "Museum of Contemporary Art", "The Great Hall"],
     "characteristics": "Art galleries, design shops, fashion boutiques, creative energy",
     "popular": True},
     
    {"name": "Financial District", "lat": 43.6481, "lon": -79.3798, 
     "tags": ["business", "corporate", "professional", "busy", "skyscrapers"], 
     "venues": ["TD Centre", "First Canadian Place", "Royal Bank Plaza", "Hockey Hall of Fame"],
     "characteristics": "Banking towers, corporate headquarters, underground PATH system, workday hustle",
     "popular": True},
     
    {"name": "Entertainment District", "lat": 43.6467, "lon": -79.3877, 
     "tags": ["nightlife", "entertainment", "theatre", "tourism", "dining"], 
     "venues": ["Royal Alexandra Theatre", "Princess of Wales Theatre", "TIFF Bell Lightbox", "Rogers Centre"],
     "characteristics": "Theatres, clubs, restaurants, tourist attractions, high-energy atmosphere",
     "popular": True},
     
    {"name": "St. Lawrence Market", "lat": 43.6498, "lon": -79.3719, 
     "tags": ["historic", "market", "foodie", "shopping", "community"], 
     "venues": ["St. Lawrence Market", "Sony Centre for the Performing Arts", "Berczy Park", "George Brown College"],
     "characteristics": "Historic market, fresh food, restaurants, heritage buildings, urban charm",
     "popular": True},
     
    {"name": "Parkdale", "lat": 43.6389, "lon": -79.4307, 
     "tags": ["diverse", "eclectic", "artistic", "affordable", "vibrant"], 
     "venues": ["Cadillac Lounge", "Grand Trunk", "Parts & Labour", "The Rhino"],
     "characteristics": "Diverse communities, hipster vibe, affordable eateries, vintage shops",
     "popular": False},
     
    {"name": "Corktown", "lat": 43.6554, "lon": -79.3647, 
     "tags": ["historic", "residential", "charming", "quiet", "redeveloped"], 
     "venues": ["Corktown Common", "Dominion Pub & Kitchen", "Little Trinity Church", "Underpass Park"],
     "characteristics": "Historic district, restored cottages, parks, quiet streets",
     "popular": False}
]

# Toronto points of interest with accurate details
TORONTO_POIS = [
    {"name": "CN Tower", "lat": 43.6426, "lon": -79.3871, 
     "tags": ["landmark", "tourist", "attraction", "observation", "iconic"],
     "description": "Toronto's most iconic landmark offering 360-degree views from its observation deck, glass floor, and the famous EdgeWalk experience.",
     "category": "attraction",
     "rating": 4.7,
     "popular": True},
    
    {"name": "Royal Ontario Museum", "lat": 43.6677, "lon": -79.3948, 
     "tags": ["museum", "culture", "education", "exhibits", "history"],
     "description": "Canada's largest museum featuring art, culture, and natural history collections with over 6 million items and 40 galleries.",
     "category": "museum",
     "rating": 4.6,
     "popular": True},
    
    {"name": "Art Gallery of Ontario", "lat": 43.6536, "lon": -79.3924, 
     "tags": ["art", "culture", "gallery", "exhibits", "architecture"],
     "description": "Major art gallery with a collection of more than 90,000 works spanning from the 1st century to the present day.",
     "category": "gallery",
     "rating": 4.6,
     "popular": True},
    
    {"name": "Toronto Islands", "lat": 43.6228, "lon": -79.3817, 
     "tags": ["outdoor", "leisure", "waterfront", "park", "recreation"],
     "description": "Car-free island community featuring beaches, parks, a small amusement park, and stunning views of Toronto's skyline.",
     "category": "outdoor",
     "rating": 4.8,
     "popular": True},
    
    {"name": "St. Lawrence Market", "lat": 43.6498, "lon": -79.3719, 
     "tags": ["market", "food", "historic", "shopping", "local"],
     "description": "Historic market complex dating back to 1803, featuring food vendors, restaurants and specialty shops.",
     "category": "food",
     "rating": 4.7,
     "popular": True},
    
    {"name": "Ripley's Aquarium of Canada", "lat": 43.6424, "lon": -79.3860, 
     "tags": ["attraction", "family", "aquarium", "marine", "educational"],
     "description": "Downtown aquatic attraction with 5.7 million liters of water showcasing marine and freshwater habitats from around the world.",
     "category": "attraction",
     "rating": 4.6,
     "popular": True},
    
    {"name": "High Park", "lat": 43.6465, "lon": -79.4637, 
     "tags": ["park", "outdoor", "nature", "recreation", "gardens"],
     "description": "Toronto's largest public park featuring trails, gardens, sports facilities, a zoo, and beautiful cherry blossoms in spring.",
     "category": "outdoor",
     "rating": 4.8,
     "popular": True},
    
    {"name": "Rogers Centre", "lat": 43.6414, "lon": -79.3894, 
     "tags": ["sports", "entertainment", "baseball", "venue", "stadium"],
     "description": "Multi-purpose stadium with a retractable roof, home to the Toronto Blue Jays baseball team and major events.",
     "category": "sports",
     "rating": 4.5,
     "popular": True},
    
    {"name": "Toronto Eaton Centre", "lat": 43.6544, "lon": -79.3807, 
     "tags": ["shopping", "mall", "urban", "retail", "downtown"],
     "description": "Bustling urban shopping mall featuring over 250 retailers, restaurants, and services in the heart of downtown.",
     "category": "shopping",
     "rating": 4.5,
     "popular": True},
    
    {"name": "Casa Loma", "lat": 43.6781, "lon": -79.4094, 
     "tags": ["castle", "historic", "attraction", "mansion", "garden"],
     "description": "Gothic Revival style mansion and garden that now serves as a museum and landmark, built in the early 20th century.",
     "category": "attraction",
     "rating": 4.6,
     "popular": True},
     
    {"name": "Kensington Market", "lat": 43.6547, "lon": -79.4005, 
     "tags": ["market", "eclectic", "multicultural", "shopping", "food"],
     "description": "Distinctive multicultural neighborhood with vintage shops, food markets, cafes, and vibrant street scenes.",
     "category": "shopping",
     "rating": 4.7,
     "popular": True},
     
    {"name": "Distillery District", "lat": 43.6503, "lon": -79.3597, 
     "tags": ["historic", "pedestrian", "arts", "shopping", "dining"],
     "description": "Pedestrian-only village with Victorian industrial architecture housing arts, culture, food and shopping.",
     "category": "attraction",
     "rating": 4.7,
     "popular": True},
     
    {"name": "Hockey Hall of Fame", "lat": 43.6472, "lon": -79.3772, 
     "tags": ["sports", "hockey", "museum", "history", "entertainment"],
     "description": "Museum dedicated to the history of ice hockey, showcasing memorabilia, exhibits and the Stanley Cup.",
     "category": "museum",
     "rating": 4.6,
     "popular": True},
     
    {"name": "Toronto Zoo", "lat": 43.8207, "lon": -79.1865, 
     "tags": ["zoo", "wildlife", "family", "conservation", "animals"],
     "description": "Canada's largest zoo, home to over 5,000 animals representing 500 species on over 700 acres of land.",
     "category": "attraction",
     "rating": 4.5,
     "popular": True},
     
    {"name": "Ontario Science Centre", "lat": 43.7163, "lon": -79.3390, 
     "tags": ["science", "museum", "interactive", "educational", "family"],
     "description": "Science museum with hundreds of interactive exhibits focused on technology, nature, and innovation.",
     "category": "museum",
     "rating": 4.4,
     "popular": True},
     
    {"name": "Scarborough Bluffs", "lat": 43.7063, "lon": -79.2270, 
     "tags": ["nature", "cliffs", "beach", "park", "scenic"],
     "description": "Escarpment and natural landmark along the shoreline of Lake Ontario with parks, beaches, and stunning views.",
     "category": "outdoor",
     "rating": 4.7,
     "popular": False},
     
    {"name": "Graffiti Alley", "lat": 43.6477, "lon": -79.4005, 
     "tags": ["street-art", "urban", "artistic", "colorful", "photography"],
     "description": "Outdoor art gallery featuring stunning murals and street art along Rush Lane in the Fashion District.",
     "category": "attraction",
     "rating": 4.5,
     "popular": False}
]

# Toronto events with realistic details
TORONTO_ANNUAL_EVENTS = [
    {"name": "Toronto International Film Festival", 
     "description": "World-renowned film festival showcasing international and Canadian films with premieres, galas, and celebrity appearances.",
     "venue": "TIFF Bell Lightbox",
     "category": "festival",
     "neighborhood": "Entertainment District",
     "tags": ["film", "entertainment", "international", "arts", "celebrity"],
     "month": 9,  # September
     "duration": 11,
     "price_range": {"min": 20, "max": 150, "currency": "CAD"},
     "popular": True},
    
    {"name": "Canadian National Exhibition", 
     "description": "Annual end-of-summer fair featuring rides, games, food, shopping, and entertainment at Exhibition Place.",
     "venue": "Exhibition Place",
     "category": "fair",
     "neighborhood": "Exhibition Place",
     "tags": ["family", "entertainment", "rides", "food", "summer"],
     "month": 8,  # August
     "duration": 18,
     "price_range": {"min": 20, "max": 30, "currency": "CAD"},
     "popular": True},
    
    {"name": "Caribana Festival", 
     "description": "Vibrant Caribbean carnival celebrating Caribbean culture with music, costumes, and food.",
     "venue": "Exhibition Place & Lakeshore Boulevard",
     "category": "festival",
     "neighborhood": "Harbourfront",
     "tags": ["caribbean", "music", "parade", "culture", "summer"],
     "month": 8,  # August
     "duration": 3,
     "price_range": {"min": 0, "max": 50, "currency": "CAD"},
     "popular": True},
    
    {"name": "Toronto Christmas Market", 
     "description": "European-style Christmas market with local crafts, food, and entertainment in the historic Distillery District.",
     "venue": "Distillery District",
     "category": "market",
     "neighborhood": "Distillery District",
     "tags": ["christmas", "holiday", "shopping", "food", "winter"],
     "month": 12,  # December
     "duration": 30,
     "price_range": {"min": 0, "max": 15, "currency": "CAD"},
     "popular": True},
    
    {"name": "Nuit Blanche", 
     "description": "All-night contemporary art event with installations throughout the city, transforming Toronto into an artistic playground.",
     "venue": "Various Locations",
     "category": "art",
     "neighborhood": "Downtown Core",
     "tags": ["art", "contemporary", "night", "installation", "free"],
     "month": 10,  # October
     "duration": 1,
     "price_range": {"min": 0, "max": 0, "currency": "CAD"},
     "popular": True},
    
    {"name": "Toronto Pride Parade", 
     "description": "Colorful celebration of LGBTQ+ communities with one of the largest pride parades in North America.",
     "venue": "Church-Wellesley Village",
     "category": "parade",
     "neighborhood": "Church-Wellesley Village",
     "tags": ["pride", "lgbtq+", "parade", "celebration", "summer"],
     "month": 6,  # June
     "duration": 3,
     "price_range": {"min": 0, "max": 0, "currency": "CAD"},
     "popular": True},
    
    {"name": "Taste of the Danforth", 
     "description": "Canada's largest street festival celebrating Greek food, culture, and music on the Danforth.",
     "venue": "Danforth Avenue",
     "category": "festival",
     "neighborhood": "Danforth/Greektown",
     "tags": ["food", "greek", "culture", "music", "summer"],
     "month": 8,  # August
     "duration": 3,
     "price_range": {"min": 0, "max": 0, "currency": "CAD"},
     "popular": True},
    
    {"name": "Toronto Jazz Festival", 
     "description": "Annual jazz festival featuring performances by local and international jazz artists in venues across the city.",
     "venue": "Various Venues",
     "category": "music",
     "neighborhood": "Yorkville",
     "tags": ["jazz", "music", "concert", "performance", "summer"],
     "month": 6,  # June
     "duration": 10,
     "price_range": {"min": 30, "max": 150, "currency": "CAD"},
     "popular": True},
    
    {"name": "Winterlicious", 
     "description": "Culinary celebration with prix fixe menus at hundreds of Toronto restaurants during winter months.",
     "venue": "Various Restaurants",
     "category": "food",
     "neighborhood": "Multiple",
     "tags": ["food", "dining", "culinary", "winter", "restaurant"],
     "month": 2,  # February
     "duration": 14,
     "price_range": {"min": 23, "max": 65, "currency": "CAD"},
     "popular": True},
    
    {"name": "Hot Docs Festival", 
     "description": "North America's largest documentary festival featuring screenings, discussions, and workshops.",
     "venue": "Hot Docs Ted Rogers Cinema",
     "category": "film",
     "neighborhood": "Annex",
     "tags": ["documentary", "film", "festival", "international", "spring"],
     "month": 4,  # April
     "duration": 11,
     "price_range": {"min": 17, "max": 25, "currency": "CAD"},
     "popular": True},
     
    {"name": "Summerlicious", 
     "description": "Summer version of Winterlicious featuring prix fixe menus at restaurants throughout Toronto.",
     "venue": "Various Restaurants",
     "category": "food",
     "neighborhood": "Multiple",
     "tags": ["food", "dining", "culinary", "summer", "restaurant"],
     "month": 7,  # July
     "duration": 14,
     "price_range": {"min": 23, "max": 65, "currency": "CAD"},
     "popular": True},
     
    {"name": "Toronto Outdoor Art Fair", 
     "description": "Canada's largest outdoor art fair showcasing contemporary art in Nathan Phillips Square.",
     "venue": "Nathan Phillips Square",
     "category": "art",
     "neighborhood": "Downtown Core",
     "tags": ["art", "outdoor", "fair", "contemporary", "summer"],
     "month": 7,  # July
     "duration": 3,
     "price_range": {"min": 0, "max": 0, "currency": "CAD"},
     "popular": False},
     
    {"name": "Doors Open Toronto", 
     "description": "Annual event providing free access to architecturally, historically, and culturally significant buildings across Toronto.",
     "venue": "Various Locations",
     "category": "cultural",
     "neighborhood": "Multiple",
     "tags": ["architecture", "history", "culture", "tour", "spring"],
     "month": 5,  # May
     "duration": 2,
     "price_range": {"min": 0, "max": 0, "currency": "CAD"},
     "popular": True},
     
    {"name": "Toronto Craft Beer Festival", 
     "description": "Festival celebrating Ontario's craft beer scene with tastings, food pairings, and live entertainment.",
     "venue": "Ontario Place",
     "category": "food-drink",
     "neighborhood": "Harbourfront",
     "tags": ["beer", "craft", "festival", "tasting", "summer"],
     "month": 6,  # June
     "duration": 3,
     "price_range": {"min": 30, "max": 95, "currency": "CAD"},
     "popular": False},
     
    {"name": "Cavalcade of Lights", 
     "description": "Annual holiday tradition featuring the lighting of Toronto's official Christmas Tree, performances, and fireworks.",
     "venue": "Nathan Phillips Square",
     "category": "holiday",
     "neighborhood": "Downtown Core",
     "tags": ["christmas", "lights", "holiday", "winter", "family"],
     "month": 11,  # November
     "duration": 1,
     "price_range": {"min": 0, "max": 0, "currency": "CAD"},
     "popular": True}
]

# Toronto restaurant types for generating mock places
TORONTO_RESTAURANT_TYPES = [
    {"cuisine": "Italian", "dishes": ["pasta", "pizza", "risotto", "tiramisu"], "price_level": [2, 3, 4]},
    {"cuisine": "Japanese", "dishes": ["sushi", "ramen", "tempura", "sashimi"], "price_level": [2, 3, 4]},
    {"cuisine": "Chinese", "dishes": ["dim sum", "noodles", "dumplings", "Peking duck"], "price_level": [1, 2, 3]},
    {"cuisine": "Indian", "dishes": ["curry", "tandoori", "biryani", "naan"], "price_level": [2, 3]},
    {"cuisine": "Mexican", "dishes": ["tacos", "enchiladas", "guacamole", "quesadillas"], "price_level": [2, 3]},
    {"cuisine": "Greek", "dishes": ["souvlaki", "moussaka", "spanakopita", "gyros"], "price_level": [2, 3]},
    {"cuisine": "Thai", "dishes": ["pad thai", "curry", "tom yum", "mango sticky rice"], "price_level": [2, 3]},
    {"cuisine": "French", "dishes": ["coq au vin", "bouillabaisse", "ratatouille", "crème brûlée"], "price_level": [3, 4]},
    {"cuisine": "Vietnamese", "dishes": ["pho", "banh mi", "spring rolls", "bun cha"], "price_level": [1, 2]},
    {"cuisine": "Korean", "dishes": ["bibimbap", "bulgogi", "kimchi", "korean fried chicken"], "price_level": [2, 3]},
    {"cuisine": "Caribbean", "dishes": ["jerk chicken", "roti", "rice and peas", "plantains"], "price_level": [2, 3]},
    {"cuisine": "Ethiopian", "dishes": ["injera", "wat", "kitfo", "tibs"], "price_level": [2, 3]},
    {"cuisine": "Middle Eastern", "dishes": ["hummus", "falafel", "shawarma", "tabbouleh"], "price_level": [1, 2, 3]},
    {"cuisine": "Canadian", "dishes": ["poutine", "butter tarts", "peameal bacon", "maple syrup"], "price_level": [2, 3, 4]},
    {"cuisine": "Fusion", "dishes": ["fusion tacos", "sushi burritos", "kimchi poutine", "banh mi burgers"], "price_level": [3, 4]},
]

# Toronto coffee shops, bars, and specialty shops types
TORONTO_SHOP_TYPES = [
    {"type": "Coffee Shop", "products": ["espresso", "pour over", "cold brew", "baked goods"], "price_level": [1, 2, 3]},
    {"type": "Craft Beer Bar", "products": ["IPA", "stout", "sour beer", "local brews"], "price_level": [2, 3]},
    {"type": "Cocktail Bar", "products": ["craft cocktails", "martinis", "negronis", "old fashioneds"], "price_level": [3, 4]},
    {"type": "Wine Bar", "products": ["wine flights", "charcuterie", "cheese plates", "tapas"], "price_level": [3, 4]},
    {"type": "Bakery", "products": ["bread", "pastries", "cakes", "cookies"], "price_level": [2, 3]},
    {"type": "Ice Cream Shop", "products": ["gelato", "ice cream", "sorbet", "sundaes"], "price_level": [1, 2]},
    {"type": "Specialty Food Shop", "products": ["artisanal cheese", "charcuterie", "gourmet olive oil", "imported goods"], "price_level": [3, 4]},
    {"type": "Tea House", "products": ["loose leaf tea", "bubble tea", "high tea", "tea ceremony"], "price_level": [2, 3]},
    {"type": "Vegan Restaurant", "products": ["plant-based burgers", "buddha bowls", "vegan desserts", "smoothies"], "price_level": [2, 3]},
    {"type": "Food Truck", "products": ["street food", "fusion cuisine", "gourmet sandwiches", "ethnic specialties"], "price_level": [1, 2]},
    {"type": "Brunch Spot", "products": ["eggs benedict", "avocado toast", "pancakes", "mimosas"], "price_level": [2, 3]},
    {"type": "Pub", "products": ["beer", "pub food", "wings", "burgers"], "price_level": [2, 3]},
    {"type": "Dessert Café", "products": ["cakes", "macarons", "chocolates", "specialty desserts"], "price_level": [2, 3]},
]

# Pinterest-style content categories for Toronto
TORONTO_CONTENT_CATEGORIES = [
    {"category": "Toronto Skyline", 
     "tags": ["cityscape", "skyline", "cn tower", "lake ontario", "urban", "photography"],
     "description_templates": [
         "Stunning view of Toronto's skyline from {location}",
         "Beautiful Toronto skyline featuring the iconic CN Tower",
         "Toronto cityscape at {time_of_day} captured from {location}",
         "{season} view of Toronto's impressive skyline",
         "Urban photography showcasing Toronto's distinctive skyline"
     ],
     "locations": ["Toronto Islands", "Polson Pier", "Harbourfront", "CN Tower", "Lake Ontario", "Humber Bay Park"]},
    
    {"category": "Toronto Architecture", 
     "tags": ["architecture", "design", "building", "structure", "urban design", "historic"],
     "description_templates": [
         "The unique architecture of {building} in {neighborhood}",
         "Historic meets modern in this Toronto architectural gem",
         "Geometric patterns and lines of {building}'s distinctive design",
         "Architectural details of Toronto's {building}",
         "{architectural_style} architecture in the heart of Toronto"
     ],
     "buildings": ["Royal Ontario Museum", "Art Gallery of Ontario", "Toronto City Hall", "Union Station", 
                  "Gooderham Building", "Ontario Legislative Building", "OCAD University", "TD Centre"]},
    
    {"category": "Toronto Food Scene", 
     "tags": ["food", "cuisine", "restaurant", "foodie", "culinary", "dining"],
     "description_templates": [
         "Delicious {cuisine} food from {restaurant} in {neighborhood}",
         "Must-try {dish} at {restaurant} in Toronto",
         "Toronto's best {cuisine} spots: {restaurant}",
         "Exploring Toronto's diverse food scene with {dish}",
         "Hidden gem in Toronto's {neighborhood}: {restaurant}"
     ],
     "dishes": ["poutine", "peameal bacon sandwich", "dim sum", "butter tarts", "sushi", "ramen", "jerk chicken", 
               "pasta", "tacos", "pho", "dumplings", "butter chicken", "shawarma", "pizza"]},
    
    {"category": "Toronto Street Art", 
     "tags": ["street art", "graffiti", "mural", "urban art", "public art", "artist"],
     "description_templates": [
         "Colorful street art in Toronto's {neighborhood}",
         "Urban expression through street art in {neighborhood}",
         "Toronto's vibrant mural scene: artwork in {neighborhood}",
         "Stunning mural by {artist} in {neighborhood}, Toronto",
         "Toronto's streets as a canvas: graffiti art in {neighborhood}"
     ],
     "artists": ["anonymous", "local artist", "international artist", "street artist", "muralist"],
     "areas": ["Graffiti Alley", "Kensington Market", "Queen West", "Dundas West", "Leslieville", "Junction"]},
    
    {"category": "Toronto Parks & Nature", 
     "tags": ["park", "nature", "outdoor", "green space", "garden", "trail"],
     "description_templates": [
         "Peaceful moment at {location} in Toronto",
         "Toronto's urban oasis: {location}",
         "{season} colors at {location}",
         "Natural beauty in the heart of Toronto at {location}",
         "Exploring Toronto's {location} on a {weather} day"
     ],
     "locations": ["High Park", "Toronto Islands", "Edwards Gardens", "Trinity Bellwoods Park", "Scarborough Bluffs", 
                  "Don Valley", "Rouge National Urban Park", "Humber Bay Park"]},
    
    {"category": "Toronto Events", 
     "tags": ["event", "festival", "celebration", "entertainment", "culture", "performance"],
     "description_templates": [
         "Highlights from {event} in Toronto",
         "Experience Toronto's {event} festival",
         "Toronto comes alive during {event}",
         "Annual {event} brings Toronto together",
         "Cultural celebration at Toronto's {event}"
     ],
     "events": ["Toronto International Film Festival", "Caribana", "Nuit Blanche", "Pride Toronto", 
               "Canadian National Exhibition", "Toronto Jazz Festival", "Taste of the Danforth"]},
    
    {"category": "Toronto Neighborhoods", 
     "tags": ["neighborhood", "local", "community", "urban life", "city living", "district"],
     "description_templates": [
         "Exploring the vibrant {neighborhood} neighborhood in Toronto",
         "Local charm in Toronto's {neighborhood} district",
         "What makes Toronto's {neighborhood} unique",
         "Hidden gems in {neighborhood}, one of Toronto's most {adjective} areas",
         "A walk through Toronto's historic {neighborhood}"
     ],
     "adjectives": ["charming", "vibrant", "trendy", "historic", "eclectic", "diverse", "lively", "artsy"]},
    
    {"category": "Toronto Shopping", 
     "tags": ["shopping", "retail", "fashion", "boutique", "market", "store"],
     "description_templates": [
         "Shopping paradise at {location} in Toronto",
         "Unique finds at Toronto's {location}",
         "Toronto's best shopping district: {location}",
         "Local designers and boutiques at {location}",
         "Vintage treasures from {location} in Toronto"
     ],
     "locations": ["Kensington Market", "Queen Street West", "Yorkville", "Distillery District", 
                  "Eaton Centre", "St. Lawrence Market", "Bloor Street", "Yorkdale Mall"]},
    
    {"category": "Toronto Night Life", 
     "tags": ["nightlife", "bar", "club", "entertainment", "evening", "social"],
     "description_templates": [
         "Toronto after dark: nightlife at {location}",
         "Evening vibes at {location} in Toronto",
         "Toronto's hottest nightspot: {location}",
         "Cocktail culture at {location} in {neighborhood}",
         "Dancing the night away at Toronto's {location}"
     ],
     "locations": ["King Street West", "Queen Street West", "Entertainment District", "Ossington Avenue", 
                  "College Street", "Church-Wellesley Village", "Kensington Market", "Distillery District"]},
    
    {"category": "Toronto Seasonal", 
     "tags": ["season", "weather", "holiday", "seasonal", "tradition", "celebration"],
     "description_templates": [
         "Toronto in {season}: {activity} at {location}",
         "{season} traditions in Toronto include {activity}",
         "Beautiful {season} day in Toronto at {location}",
         "Celebrating {holiday} Toronto-style at {location}",
         "Toronto transforms during {season} with {activity}"
     ],
     "seasons": ["spring", "summer", "fall", "winter"],
     "holidays": ["Christmas", "Halloween", "Canada Day", "Thanksgiving", "New Year's Eve"],
     "activities": ["ice skating", "cherry blossom viewing", "leaf peeping", "beach day", "festival attendance", 
                   "light displays", "parades", "snowshoeing", "hiking", "sailing"]}
]

# Image URL templates for realistic mock data
IMAGE_URL_TEMPLATES = [
    "https://images.unsplash.com/photo-{photo_id}?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
    "https://live.staticflickr.com/{server}/{photo_id}_{secret}_b.jpg",
]

# Realistic photo IDs for Toronto content
TORONTO_PHOTO_IDS = [
    # Skyline/Cityscape Photos
    "1514924013411-cbf25faa35bb", "1486325212164-1b5c35a60847", "1574174227462-55421fb50ba1",
    "1570168682642-ec0ebc8196e5", "1517935706615-2717063c22b4", "1586611292717-f977fa7ab062",
    
    # Architecture
    "1534190760602-26fca5d54f61", "1569880153113-76e33fc52d5f", "1525287335486-3b0b0e58d0c1",
    "1605993439244-eb346c6d9260", "1579033385971-d5e9b6ba93d7", "1544161513-0179fe746fd4",
    
    # Food
    "1558024920-b41e1887dc32", "1543826173-70651703d5c1", "1493770348161-369560ae357d",
    "1504674900247-0877df9cc836", "1559948239-c63451293bf9", "1602330104722-8a7f8de1dc8a",
    
    # Street Art
    "1506716247784-3c01b3e7703e", "1596395464941-de917238027a", "1596395463910-4ab618e3c4e4",
    "1517999144842-f977fa0bfc76", "1606066887405-4abf5aa91ed1", "1583532452513-a02186582ccd",
    
    # Parks & Nature
    "1563514370576-8d608db4b82d", "1564098005179-97f8a19a3286", "1586022383926-25e48eeaf9f1",
    "1586999768562-09be030bb7b6", "1590686810572-6016d7a22e4d", "1605460510613-5e7a67159c96",
    
    # Events
    "1541534741688-6078c6bfb5c5", "1469510879524-4398a4d0e758", "1530023426775-6cc2e8a5b74d",
    "1531058020387-3be344556be6", "1485846234645-a62644f84728", "1504480448699-1f3be3a3f6e2",
    
    # Neighborhoods
    "1516731415016-070f338ac55b", "1589309736404-9a2c0f6b6966", "1566888685795-6513223dff19",
    "1587203561664-b03cb7a6e079", "1633942955632-54c22fb965ab", "1582560486886-6e757a975a79",
    
    # Shopping
    "1591085656364-35af54fd5777", "1609709383021-f658d56bd0fa", "1604689558922-d677a411bbec",
    "1607083206325-cad9d1e33a37", "1567053810492-cb3d56c8a00e", "1590512071255-c60c6550dc57",
    
    # Nightlife
    "1517457373958-b7bdd4791db5", "1578530204702-6ba87baeb068", "1566417905469-70d3a5ffd261",
    "1528145103278-972c10a973a6", "1525610553991-2f67aec1329f", "1569059364542-aa68e96a3c3e",
    
    # Seasonal
    "1513878683536-4cf1a94d0be8", "1481743862978-4edffd5eef16", "1531179493933-41454cd0bf31",
    "1508607388715-4c5d0df491aa", "1512910412923-a0592f36a719", "1606334431063-3ee4a92a6e43"
]

# Flickr-style IDs for variety in image sources
FLICKR_SERVERS = ["65535", "66022", "65833", "65834", "66066", "65535"]
FLICKR_SECRETS = ["ffe8461cc2", "fa5ae2adcb", "c8b5dae642", "df77ae88a7", "f9c16e8626"]
FLICKR_PHOTO_IDS = [str(random.randint(10000000000, 99999999999)) for _ in range(100)]

def random_image_url():
    """Generate a random realistic image URL"""
    template = random.choice(IMAGE_URL_TEMPLATES)
    
    if "unsplash" in template or "pexels" in template:
        photo_id = random.choice(TORONTO_PHOTO_IDS)
        return template.format(photo_id=photo_id)
    else:  # Flickr template
        server = random.choice(FLICKR_SERVERS)
        photo_id = random.choice(FLICKR_PHOTO_IDS)
        secret = random.choice(FLICKR_SECRETS)
        return template.format(server=server, photo_id=photo_id, secret=secret)

def random_profile_image_url():
    """Generate a random profile image URL"""
    photo_id = random.randint(1000, 9999)
    return f"https://randomuser.me/api/portraits/men/{photo_id}.jpg"

def generate_uuid():
    """Generate a unique ID"""
    return str(uuid.uuid4())

def generate_username():
    """Generate a random username"""
    prefixes = ["toronto", "the6ix", "6side", "tdot", "to", "gta", "ontario", "canada", "maple", "drake", "raptors"]
    suffixes = ["fan", "lover", "explorer", "native", "traveler", "foodie", "photographer", "local"]
    numbers = ["", str(random.randint(0, 999)), str(random.randint(2000, 2025))]
    
    return f"{random.choice(prefixes)}{random.choice(suffixes)}{random.choice(numbers)}"

def generate_interaction_data(content_ids, user_count=200, interactions_per_user_range=(5, 30)):
    """Generate user interaction data"""
    db = get_mongodb_db()
    
    logger.info(f"Generating interaction data for {user_count} users...")
    
    # Create users
    users = []
    used_usernames = set()
    
    for i in range(user_count):
        # Determine user preferences (weighted towards certain categories)
        interest_count = random.randint(2, 5)
        all_categories = ["food", "art", "travel", "outdoor", "architecture", "events", 
                          "nightlife", "shopping", "family", "sports", "music", "photography"]
        interests = random.sample(all_categories, interest_count)
        
        # Some users have location preferences
        has_neighborhood_preference = random.random() < 0.6
        neighborhood_preferences = []
        if has_neighborhood_preference:
            neighborhood_count = random.randint(1, 3)
            neighborhoods = [n["name"] for n in TORONTO_NEIGHBORHOODS]
            neighborhood_preferences = random.sample(neighborhoods, neighborhood_count)
        
        user = {
            "_id": generate_uuid(),
            "username": generate_username(used_usernames),
            "profile_image": random_profile_image_url(),
            "interests": interests,
            "neighborhood_preferences": neighborhood_preferences,
            "account_created": (datetime.now() - timedelta(days=random.randint(1, 730))).isoformat(),
            "is_toronto_local": random.random() < 0.7,  # 70% are locals
        }
        users.append(user)
    
    # Insert users in batches
    batch_size = 100
    for i in range(0, len(users), batch_size):
        batch = users[i:i+batch_size]
        try:
            db.users.insert_many(batch)
            logger.info(f"Inserted {len(batch)} users (batch {i//batch_size + 1}/{(len(users)-1)//batch_size + 1})")
        except Exception as e:
            # If a batch fails, insert one by one to continue with the non-duplicates
            logger.warning(f"Batch insert failed: {e}. Trying one by one...")
            successful_inserts = 0
            for user in batch:
                try:
                    db.users.insert_one(user)
                    successful_inserts += 1
                except Exception as individual_error:
                    logger.warning(f"Could not insert user {user['username']}: {individual_error}")
            logger.info(f"Inserted {successful_inserts}/{len(batch)} users individually")
    
    # Get actual inserted user IDs
    user_ids = [user["_id"] for user in db.users.find({}, {"_id": 1})]
    
    # Generate interaction data
    all_interactions = []
    interaction_count = 0
    interaction_types = ["view", "save", "click", "share"]
    interaction_weights = [0.6, 0.25, 0.1, 0.05]  # More views than saves, more saves than clicks, etc.
    
    for user_id in user_ids:
        # Each user interacts with a random number of content items
        user_interaction_count = random.randint(*interactions_per_user_range)
        user_content_ids = random.sample(content_ids, min(user_interaction_count, len(content_ids)))
        
        # Generate interactions
        for content_id in user_content_ids:
            # Some users have multiple interactions with the same content
            interaction_count = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            
            for _ in range(interaction_count):
                interaction_type = random.choices(interaction_types, weights=interaction_weights)[0]
                
                # Determine when the interaction happened (more recent = more likely)
                days_ago = random.choices(
                    [1, 7, 30, 90, 180], 
                    weights=[0.4, 0.3, 0.2, 0.05, 0.05]
                )[0] * random.random()
                
                interaction = {
                    "_id": generate_uuid(),
                    "user_id": user_id,
                    "content_id": content_id,
                    "interaction_type": interaction_type,
                    "timestamp": (datetime.now() - timedelta(days=days_ago)).isoformat(),
                    "session_id": generate_uuid(),
                    "metadata": {
                        "platform": random.choice(["web", "mobile", "app"]),
                        "duration": random.randint(5, 300) if interaction_type == "view" else None,
                    }
                }
                all_interactions.append(interaction)
    
    # Insert interactions in batches
    batch_size = 1000
    for i in range(0, len(all_interactions), batch_size):
        batch = all_interactions[i:i+batch_size]
        db.interactions.insert_many(batch)
        interaction_count += len(batch)
        logger.info(f"Inserted {len(batch)} interactions (batch {i//batch_size + 1}/{(len(all_interactions)-1)//batch_size + 1})")
    
    return interaction_count

def generate_mock_pinterest_content(count=500):
    """Generate mock Pinterest-like content with Toronto-specific themes"""
    db = get_mongodb_db()
    content_ids = []
    
    logger.info(f"Generating {count} Pinterest-like content items...")
    
    # Set the distribution among categories
    category_weights = [0.15, 0.12, 0.14, 0.08, 0.12, 0.1, 0.08, 0.07, 0.08, 0.06]  # Relative weights
    
    # Generate content across all categories
    for i in range(count):
        # Select a category based on weights
        category_data = random.choices(TORONTO_CONTENT_CATEGORIES, weights=category_weights)[0]
        
        # Prepare category-specific data
        time_of_day = random.choice(["sunrise", "morning", "afternoon", "sunset", "night", "golden hour"])
        season = random.choice(["spring", "summer", "fall", "winter"])
        weather = random.choice(["sunny", "rainy", "snowy", "cloudy", "foggy", "clear"])
        neighborhood = random.choice([n["name"] for n in TORONTO_NEIGHBORHOODS])
        building = random.choice(category_data.get("buildings", ["building", "structure", "landmark", "site"]))
        location = random.choice(category_data.get("locations", [neighborhood, "Toronto", "Downtown", "Waterfront"]))
        artist = random.choice(category_data.get("artists", ["artist"]))
        event = random.choice(category_data.get("events", ["event"]))
        cuisine = random.choice([r["cuisine"] for r in TORONTO_RESTAURANT_TYPES])
        restaurant = f"{random.choice(['The', 'Café', '', 'Bistro'])} {random.choice(['Royal', 'Golden', 'Silver', 'Blue', 'Red', 'Green'])} {random.choice(['Fork', 'Plate', 'Table', 'Spoon', 'Kitchen'])}"
        dish = random.choice([dish for r in TORONTO_RESTAURANT_TYPES for dish in r["dishes"]])
        holiday = random.choice(category_data.get("holidays", ["holiday"]))
        activity = random.choice(category_data.get("activities", ["activity"]))
        adjective = random.choice(category_data.get("adjectives", ["beautiful", "amazing", "stunning", "incredible"]))
        architectural_style = random.choice(["Modern", "Victorian", "Art Deco", "Brutalist", "Gothic", "Neoclassical", "Contemporary", "Postmodern"])


        # Format the description template with variables
        description_template = random.choice(category_data["description_templates"])
        description = description_template.format(
            location=location, time_of_day=time_of_day, season=season, 
            building=building, neighborhood=neighborhood, artist=artist,
            event=event, cuisine=cuisine, restaurant=restaurant, dish=dish,
            weather=weather, holiday=holiday, activity=activity, adjective=adjective,
            architectural_style=architectural_style
        )
        
        # Create a title from the description or category
        if random.random() < 0.7:
            # Create a shorter version of the description
            title = description.split(":")[0] if ":" in description else description
            if len(title) > 60:
                title = " ".join(title.split()[:6]) + "..."
        else:
            # Create a title from the category
            title = f"{category_data['category']} - {random.choice(category_data['tags']).title()}"
        
        # Add some Toronto-specific tags
        base_tags = category_data["tags"]
        toronto_tags = ["toronto", "the6ix", "ontario", "canada", "yyz"]
        specific_tags = [neighborhood.lower().replace(" ", ""), season, time_of_day.replace(" ", "")]
        
        tags = random.sample(base_tags, min(4, len(base_tags)))
        tags.append(random.choice(toronto_tags))
        tags.extend(random.sample(specific_tags, random.randint(1, len(specific_tags))))
        
        # Get random neighborhood for location data
        neighborhood_data = random.choice(TORONTO_NEIGHBORHOODS)
        
        # Add slight randomness to coordinates for variety
        lat = neighborhood_data["lat"] + random.uniform(-0.01, 0.01)
        lon = neighborhood_data["lon"] + random.uniform(-0.01, 0.01)
        
        # Create document
        content = create_content(
            title=title,
            description=description,
            image_url=random_image_url(),
            source_url=f"https://pinterest.ca/pin/{random.randint(100000000, 999999999)}",
            categories=[category_data["category"].lower().replace(" ", "-")] + random.sample(base_tags, 1),
            tags=tags,
            location={
                "latitude": lat,
                "longitude": lon,
                "neighborhood": neighborhood_data["name"]
            },
            metadata={
                "source": "pinterest",
                "pinterest_id": f"pin_{random.randint(100000000, 999999999)}",
                "mock_data": True,
                "category": category_data["category"],
                "neighborhood": neighborhood_data["name"]
            }
        )
        
        # Insert into MongoDB
        result = db.content.insert_one(content)
        content_id = result.inserted_id
        content_ids.append(content_id)
        
        if (i + 1) % 50 == 0:
            logger.info(f"Created {i + 1} mock Pinterest content items")
    
    logger.info(f"Generated {len(content_ids)} Pinterest content items")
    return content_ids

def generate_mock_events(count=300):
    """Generate mock Toronto events"""
    db = get_mongodb_db()
    event_ids = []
    
    logger.info(f"Generating {count} Toronto events...")
    
    # Today's date for reference
    today = datetime.now()
    
    # Create variations of annual events
    annual_event_ids = []
    for annual_event in TORONTO_ANNUAL_EVENTS:
        # Determine how many variations to create (more popular events get more instances)
        variations = random.randint(4, 10) if annual_event["popular"] else random.randint(2, 5)
        
        for i in range(variations):
            # Create a unique event name for this instance
            if i == 0:
                event_name = annual_event["name"]
            else:
                year = today.year if today.month < annual_event["month"] else today.year + 1
                event_name = f"{annual_event['name']} {year}"
                
                # Add variation to some event names
                if random.random() < 0.3:
                    variation_types = ["Special Edition", "Presentation", "Showcase", "Exhibition", "Featured Event"]
                    event_name += f" - {random.choice(variation_types)}"
            
            # Set the event date based on its month
            event_month = annual_event["month"]
            event_year = today.year if event_month >= today.month else today.year + 1
            
            # Random day within the month
            _, days_in_month = calendar.monthrange(event_year, event_month)
            event_day = random.randint(1, days_in_month)
            
            # Create start and end dates
            start_date = datetime(event_year, event_month, event_day)
            end_date = start_date + timedelta(days=annual_event["duration"])
            
            # Adjust if current date is within the event period
            if today > start_date and today < end_date:
                start_date = today - timedelta(days=random.randint(1, 3))
            
            # Get neighborhood data
            if annual_event["neighborhood"] == "Multiple":
                neighborhood_data = random.choice(TORONTO_NEIGHBORHOODS)
            else:
                neighborhood_data = next((n for n in TORONTO_NEIGHBORHOODS if n["name"] == annual_event["neighborhood"]), 
                                       random.choice(TORONTO_NEIGHBORHOODS))
            
            # Determine price
            price_range = annual_event["price_range"]
            is_free = price_range["min"] == 0 and price_range["max"] == 0
            
            if not is_free:
                actual_price = random.randint(price_range["min"], price_range["max"])
            else:
                actual_price = 0
            
            # Create content for the event
            content = create_content(
                title=event_name,
                description=annual_event["description"],
                image_url=random_image_url(),
                source_url=f"https://eventbrite.com/e/{random.randint(100000000, 999999999)}",
                categories=[annual_event["category"]],
                tags=annual_event["tags"] + ["toronto", "event", neighborhood_data["name"].lower().replace(" ", "-")],
                location={
                    "latitude": neighborhood_data["lat"] + random.uniform(-0.005, 0.005),
                    "longitude": neighborhood_data["lon"] + random.uniform(-0.005, 0.005),
                    "neighborhood": neighborhood_data["name"]
                },
                metadata={
                    "source": "eventbrite",
                    "eventbrite_id": f"evt_{random.randint(100000000, 999999999)}",
                    "mock_data": True,
                    "event_type": annual_event["category"],
                    "neighborhood": neighborhood_data["name"],
                    "popular": annual_event["popular"]
                }
            )
            
            # Insert content into MongoDB
            content_result = db.content.insert_one(content)
            content_id = content_result.inserted_id
            
            # Create Toronto event
            toronto_event = create_toronto_event(
                content_id=content_id,
                event_name=event_name,
                venue=annual_event["venue"],
                start_date=start_date,
                end_date=end_date,
                address={
                    "address_1": f"{random.randint(1, 999)} {neighborhood_data['name']} St",
                    "address_2": "",
                    "city": "Toronto",
                    "postal_code": f"M{random.choice(['1', '2', '3', '4', '5', '6'])}J {random.randint(1, 9)}{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(1, 9)}"
                },
                price_range={
                    "currency": "CAD",
                    "is_free": is_free,
                    "price": actual_price
                },
                seasonal_relevance=_determine_seasonal_relevance(start_date)
            )
            
            # Insert event into MongoDB
            event_result = db.toronto_events.insert_one(toronto_event)
            event_ids.append(event_result.inserted_id)
            annual_event_ids.append(event_result.inserted_id)
    
    logger.info(f"Generated {len(annual_event_ids)} annual event variations")
    
    # Generate additional random events to reach the desired count
    additional_count = count - len(annual_event_ids)
    
    if additional_count > 0:
        logger.info(f"Generating {additional_count} additional random events...")
        
        event_types = [
            "Workshop", "Seminar", "Conference", "Meetup", "Concert", "Exhibition", "Performance", 
            "Tour", "Class", "Tasting", "Launch", "Celebration", "Fundraiser", "Competition"
        ]
        
        topics = [
            "Technology", "Business", "Art", "Music", "Food", "Wine", "Beer", "Health", "Fitness", 
            "Science", "Literature", "History", "Photography", "Film", "Fashion", "Design", "Education"
        ]
        
        for i in range(additional_count):
            # Create random event name
            event_type = random.choice(event_types)
            topic = random.choice(topics)
            event_name = f"{topic} {event_type}"
            
            # Add specificity to some event names
            if random.random() < 0.7:
                specifics = [
                    f"Toronto {topic}", f"{topic} in the 6ix", f"The {topic} Experience", 
                    f"{topic} Showcase", f"{topic} Festival", f"The Future of {topic}", 
                    f"{topic} Masterclass", f"Introduction to {topic}", f"Advanced {topic}", 
                    f"{topic} for Beginners", f"{topic} & {random.choice(topics)} Fusion"
                ]
                event_name = f"{random.choice(specifics)} {event_type}"
            
            # Set random future date within next 6 months
            days_ahead = random.randint(1, 180)
            start_date = today + timedelta(days=days_ahead)
            
            # Duration between 1 and 3 days for most events
            duration = random.choices([1, 2, 3, 7, 14], weights=[0.5, 0.25, 0.15, 0.05, 0.05])[0]
            end_date = start_date + timedelta(days=duration)
            
            # Choose a neighborhood
            neighborhood_data = random.choice(TORONTO_NEIGHBORHOODS)
            
            # Choose a venue
            if random.random() < 0.7 and neighborhood_data["venues"]:
                venue = random.choice(neighborhood_data["venues"])
            else:
                venue_types = ["Hotel", "Gallery", "Studio", "Hall", "Theatre", "Centre", "Space", "Lounge", "Venue"]
                venue = f"The {neighborhood_data['name']} {random.choice(venue_types)}"
            
            # Generate a description
            description_templates = [
                "Join us for this exciting {event_type} about {topic} in Toronto's {neighborhood}. Perfect for {audience} interested in {interest}.",
                "Experience Toronto's premier {topic} {event_type} at {venue}. This {duration}-day event will feature {features}.",
                "The {ordinal} Annual {topic} {event_type} returns to {neighborhood}. Don't miss this opportunity to {benefit}.",
                "{topic} enthusiasts will love this {adjective} {event_type} in the heart of {neighborhood}. Learn from {experts} and network with fellow {community}.",
                "Discover the world of {topic} at this hands-on {event_type}. Located in Toronto's vibrant {neighborhood}, this event promises {promise}."
            ]
            
            # Variables for description
            audience = random.choice(["beginners", "professionals", "enthusiasts", "students", "experts", "hobbyists"])
            interest = random.choice(["learning new skills", "networking", "cutting-edge developments", "hands-on experience"])
            features = random.choice(["workshops", "expert speakers", "networking opportunities", "interactive sessions", "exclusive content"])
            ordinal = random.choice(["1st", "2nd", "3rd", "4th", "5th", "10th"])
            benefit = random.choice(["learn from industry leaders", "expand your network", "gain practical skills", "be inspired", "transform your approach"])
            adjective = random.choice(["informative", "inspiring", "hands-on", "interactive", "innovative", "cutting-edge"])
            experts = random.choice(["industry leaders", "renowned experts", "leading professionals", "celebrated practitioners", "experienced instructors"])
            community = random.choice(["enthusiasts", "professionals", "creators", "practitioners", "community members"])
            promise = random.choice(["a transformative experience", "valuable insights", "practical knowledge", "new connections", "inspiration"])
            
            description_template = random.choice(description_templates)
            description = description_template.format(
                event_type=event_type, topic=topic, neighborhood=neighborhood_data["name"],
                audience=audience, interest=interest, venue=venue, duration=duration,
                features=features, ordinal=ordinal, benefit=benefit, adjective=adjective,
                experts=experts, community=community, promise=promise
            )
            
            # Determine price
            is_free = random.random() < 0.2  # 20% chance of free event
            if is_free:
                price = 0
            else:
                base_prices = {
                    "Workshop": (30, 150),
                    "Seminar": (25, 100),
                    "Conference": (100, 500),
                    "Meetup": (0, 20),
                    "Concert": (25, 150),
                    "Exhibition": (15, 30),
                    "Performance": (20, 120),
                    "Tour": (15, 75),
                    "Class": (25, 120),
                    "Tasting": (30, 80),
                    "Launch": (0, 50),
                    "Celebration": (10, 50),
                    "Fundraiser": (50, 200),
                    "Competition": (25, 75)
                }
                price_range = base_prices.get(event_type, (15, 50))
                price = random.randint(price_range[0], price_range[1])
            
            # Create tags
            tags = [topic.lower(), event_type.lower(), "toronto", "event", neighborhood_data["name"].lower().replace(" ", "-")]
            if is_free:
                tags.append("free")
            if duration > 1:
                tags.append(f"{duration}-day")
            
            # Add seasonal tags
            season = _determine_seasonal_relevance(start_date)[0] if _determine_seasonal_relevance(start_date) else "spring"
            tags.append(season)
            
            # Create content for the event
            content = create_content(
                title=event_name,
                description=description,
                image_url=random_image_url(),
                source_url=f"https://eventbrite.com/e/{random.randint(100000000, 999999999)}",
                categories=[topic.lower(), event_type.lower()],
                tags=tags,
                location={
                    "latitude": neighborhood_data["lat"] + random.uniform(-0.005, 0.005),
                    "longitude": neighborhood_data["lon"] + random.uniform(-0.005, 0.005),
                    "neighborhood": neighborhood_data["name"]
                },
                metadata={
                    "source": "eventbrite",
                    "eventbrite_id": f"evt_{random.randint(100000000, 999999999)}",
                    "mock_data": True,
                    "event_type": event_type,
                    "topic": topic,
                    "neighborhood": neighborhood_data["name"],
                    "popular": random.random() < 0.3  # 30% chance of being popular
                }
            )
            
            # Insert content into MongoDB
            content_result = db.content.insert_one(content)
            content_id = content_result.inserted_id
            
            # Create Toronto event
            toronto_event = create_toronto_event(
                content_id=content_id,
                event_name=event_name,
                venue=venue,
                start_date=start_date,
                end_date=end_date,
                address={
                    "address_1": f"{random.randint(1, 999)} {random.choice(['King', 'Queen', 'Dundas', 'College', 'Bloor', 'Yonge', neighborhood_data['name']])} St",
                    "address_2": random.choice(["", f"Suite {random.randint(100, 999)}", f"Unit {random.randint(1, 100)}"]),
                    "city": "Toronto",
                    "postal_code": f"M{random.choice(['1', '2', '3', '4', '5', '6'])}J {random.randint(1, 9)}{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(1, 9)}"
                },
                price_range={
                    "currency": "CAD",
                    "is_free": is_free,
                    "price": price
                },
                seasonal_relevance=_determine_seasonal_relevance(start_date)
            )
            
            # Insert event into MongoDB
            event_result = db.toronto_events.insert_one(toronto_event)
            event_ids.append(event_result.inserted_id)
            
            if (i + 1) % 50 == 0:
                logger.info(f"Created {i + 1} additional random events")
    
    logger.info(f"Generated {len(event_ids)} Toronto events")
    return event_ids

def generate_mock_places(count=200):
    """Generate mock Toronto places"""
    db = get_mongodb_db()
    place_ids = []
    
    logger.info(f"Generating {count} Toronto places...")
    
    # Create restaurant, cafe, and bar places
    food_places_count = int(count * 0.6)  # 60% food places
    logger.info(f"Generating {food_places_count} food and drink places...")
    
    for i in range(food_places_count):
        # Determine the type of place
        if random.random() < 0.7:  # 70% restaurants, 30% other food/drink places
            # Create a restaurant
            restaurant_type = random.choice(TORONTO_RESTAURANT_TYPES)
            cuisine = restaurant_type["cuisine"]
            dishes = restaurant_type["dishes"]
            price_level = random.choice(restaurant_type["price_level"])
            
            # Generate restaurant name
            name_patterns = [
                "{adjective} {cuisine}",
                "The {cuisine} {noun}",
                "{cuisine} {location}",
                "{firstName}'s {cuisine}",
                "{location} {cuisine}",
                "Café {firstName}",
                "{firstName} & {firstName}",
                "The {adjective} {noun}",
                "{noun} {number}",
                "{firstName}'s"
            ]
            
            adjectives = ["Royal", "Little", "Golden", "Blue", "Red", "Spicy", "Sweet", "Tasty", "Fresh", "Wild"]
            nouns = ["Fork", "Plate", "Table", "Spoon", "Kitchen", "Bistro", "Grill", "House", "Restaurant", "Café"]
            locations = ["Toronto", "Yorkville", "Queen", "King", "Bloor", "Harbourfront", "Junction", "Parkdale", "Riverside"]
            firstNames = ["Maria", "Luigi", "Chen", "Raj", "Mohamed", "Aaliyah", "Sofia", "Luca", "Daniel", "Priya"]
            numbers = ["6", "TO", "416", "647", "One", "Two", "Six", "Seven"]
            
            name_pattern = random.choice(name_patterns)
            place_name = name_pattern.format(
                adjective=random.choice(adjectives),
                cuisine=cuisine,
                noun=random.choice(nouns),
                location=random.choice(locations),
                firstName=random.choice(firstNames),
                number=random.choice(numbers)
            )
            
            # Get a random neighborhood
            neighborhood_data = random.choice(TORONTO_NEIGHBORHOODS)
            
            # Create description
            dish_list = ", ".join(random.sample(dishes, min(3, len(dishes))))
            
            description_templates = [
                "{cuisine} restaurant in {neighborhood} serving {dishes}. {rating}/5 stars based on {reviews} reviews.",
                "Authentic {cuisine} cuisine featuring {dishes}. Located in {neighborhood}.",
                "Family-owned {cuisine} restaurant in the heart of {neighborhood}. Known for {dishes}.",
                "{adjective} {cuisine} dining experience in {neighborhood}. Must try: {dishes}.",
                "{price_level} {cuisine} restaurant with a {ambience} ambience. Popular dishes include {dishes}."
            ]
            
            description_template = random.choice(description_templates)
            rating = round(random.uniform(3.5, 4.9), 1)  # Most places have good ratings
            reviews = random.randint(10, 500)
            ambience = random.choice(["casual", "elegant", "cozy", "trendy", "upscale", "relaxed"])
            price_level_text = "Affordable" if price_level == 1 else "Moderate" if price_level == 2 else "Upscale" if price_level == 3 else "Fine dining"
            
            description = description_template.format(
                cuisine=cuisine,
                neighborhood=neighborhood_data["name"],
                dishes=dish_list,
                rating=rating,
                reviews=reviews,
                adjective=random.choice(["Delicious", "Fantastic", "Outstanding", "Amazing", "Excellent"]),
                price_level=price_level_text,
                ambience=ambience
            )
            
            # Create tags
            tags = [cuisine.lower(), "restaurant", "food", neighborhood_data["name"].lower().replace(" ", "-")]
            for dish in random.sample(dishes, min(2, len(dishes))):
                tags.append(dish.lower().replace(" ", "-"))
            
            if price_level == 1:
                tags.append("affordable")
            elif price_level == 4:
                tags.append("fine-dining")
            
            if random.random() < 0.3:
                tags.append("patio")
            if random.random() < 0.2:
                tags.append("takeout")
            
            # Determine whether it's popular
            popular = random.random() < 0.3 or neighborhood_data["popular"] or price_level >= 3
            
            place_type = "restaurant"
        else:
            # Create cafe, bar, or specialty food place
            place_data = random.choice(TORONTO_SHOP_TYPES)
            place_type = place_data["type"]
            products = place_data["products"]
            price_level = random.choice(place_data["price_level"])
            
            # Generate place name
            name_patterns = [
                "The {adjective} {noun}",
                "{firstName}'s {type}",
                "{location} {type}",
                "{adjective} {product} {type}",
                "The {product} {noun}",
                "{firstName} & {firstName}",
                "{noun} {number}",
                "{type} {location}",
                "{firstName}'s"
            ]
            
            adjectives = ["Cozy", "Little", "Golden", "Blue", "Red", "Urban", "Rustic", "Modern", "Artisanal", "Wild"]
            nouns = ["Corner", "Spot", "House", "Place", "Room", "Station", "Bar", "Shop", "Lounge", "Joint"]
            locations = ["Toronto", "Yorkville", "Queen", "King", "Bloor", "Distillery", "Junction", "Parkdale", "Riverside"]
            product = random.choice(products).split()[0]  # Just take the first word
            firstNames = ["Jake", "Olivia", "Sam", "Emma", "Tyler", "Zoe", "Leo", "Jasmine", "Blake", "Lily"]
            numbers = ["6", "TO", "416", "647", "One", "Two", "Six", "Seven"]
            
            name_pattern = random.choice(name_patterns)
            place_name = name_pattern.format(
                adjective=random.choice(adjectives),
                noun=random.choice(nouns),
                firstName=random.choice(firstNames),
                location=random.choice(locations),
                type=place_type.split()[0],  # Just the first word, e.g., "Coffee" from "Coffee Shop"
                product=product,
                number=random.choice(numbers)
            )
            
            # Get a random neighborhood
            neighborhood_data = random.choice(TORONTO_NEIGHBORHOODS)
            
            # Create description
            product_list = ", ".join(random.sample(products, min(3, len(products))))
            
            description_templates = [
                "{type} in {neighborhood} serving {products}. {rating}/5 stars based on {reviews} reviews.",
                "Trendy {type} featuring {products}. Located in {neighborhood}.",
                "Neighborhood {type} in the heart of {neighborhood}. Known for {products}.",
                "{adjective} {type} experience in {neighborhood}. Must try: {products}.",
                "{price_level} {type} with a {ambience} ambience. Popular items include {products}."
            ]
            
            description_template = random.choice(description_templates)
            rating = round(random.uniform(3.5, 4.9), 1)  # Most places have good ratings
            reviews = random.randint(10, 500)
            ambience = random.choice(["casual", "trendy", "cozy", "hip", "relaxed", "vibrant"])
            price_level_text = "Affordable" if price_level == 1 else "Moderate" if price_level == 2 else "Upscale" if price_level == 3 else "Premium"
            
            description = description_template.format(
                type=place_type,
                neighborhood=neighborhood_data["name"],
                products=product_list,
                rating=rating,
                reviews=reviews,
                adjective=random.choice(["Wonderful", "Fantastic", "Charming", "Amazing", "Excellent"]),
                price_level=price_level_text,
                ambience=ambience
            )
            
            # Create tags
            tags = [place_type.lower().replace(" ", "-"), neighborhood_data["name"].lower().replace(" ", "-")]
            
            if "Coffee" in place_type:
                tags.extend(["coffee", "cafe"])
            elif "Bar" in place_type:
                tags.extend(["drinks", "nightlife"])
            elif "Bakery" in place_type:
                tags.extend(["bakery", "food"])
            else:
                tags.append("food")
                
            for product in random.sample(products, min(2, len(products))):
                tags.append(product.lower().replace(" ", "-"))
            
            if price_level == 1:
                tags.append("affordable")
            
            if random.random() < 0.4:
                tags.append("wifi")
            
            # Determine whether it's popular
            popular = random.random() < 0.25 or neighborhood_data["popular"]
            
        # Create content for the place
        content = create_content(
            title=place_name,
            description=description,
            image_url=random_image_url(),
            source_url=f"https://maps.google.com/place/?q=place_id:{random.randint(100000000, 999999999)}",
            categories=[place_type.lower().replace(" ", "-")],
            tags=tags,
            location={
                "latitude": neighborhood_data["lat"] + random.uniform(-0.005, 0.005),
                "longitude": neighborhood_data["lon"] + random.uniform(-0.005, 0.005),
                "address": f"{random.randint(1, 999)} {random.choice(['King', 'Queen', 'Dundas', 'College', 'Bloor', 'Yonge', neighborhood_data['name']])} St, Toronto, ON",
                "neighborhood": neighborhood_data["name"]
            },
            metadata={
                "source": "google_places",
                "google_place_id": f"place_{random.randint(100000000, 999999999)}",
                "mock_data": True,
                "place_type": place_type,
                "cuisine": cuisine if place_type == "restaurant" else None,
                "neighborhood": neighborhood_data["name"],
                "popular": popular,
                "price_level": price_level,
                "rating": rating,
                "reviews": reviews
            }
        )
        
        # Insert into MongoDB
        result = db.content.insert_one(content)
        place_id = result.inserted_id
        place_ids.append(place_id)
        
        if (i + 1) % 50 == 0:
            logger.info(f"Created {i + 1} food/drink places")
    
    # Create attraction, shopping, and other places
    other_places_count = count - food_places_count
    logger.info(f"Generating {other_places_count} attractions and other places...")
    
    # Use real POIs for about half of these places
    real_pois_count = min(len(TORONTO_POIS), other_places_count // 2)
    
    # First, add real POIs
    for i in range(real_pois_count):
        poi = TORONTO_POIS[i]
        
        # Find the neighborhood for this POI
        closest_neighborhood = None
        closest_distance = float('inf')
        
        for neighborhood in TORONTO_NEIGHBORHOODS:
            distance = ((poi["lat"] - neighborhood["lat"]) ** 2 + (poi["lon"] - neighborhood["lon"]) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_neighborhood = neighborhood
        
        # Create content for the place
        content = create_content(
            title=poi["name"],
            description=poi["description"],
            image_url=random_image_url(),
            source_url=f"https://maps.google.com/place/?q=place_id:{random.randint(100000000, 999999999)}",
            categories=[poi["category"]],
            tags=poi["tags"] + [closest_neighborhood["name"].lower().replace(" ", "-"), "toronto"],
            location={
                "latitude": poi["lat"],
                "longitude": poi["lon"],
                "address": f"{random.randint(1, 999)} {random.choice(['King', 'Queen', 'Dundas', 'College', 'Bloor', 'Yonge'])} St, Toronto, ON",
                "neighborhood": closest_neighborhood["name"]
            },
            metadata={
                "source": "google_places",
                "google_place_id": f"place_{random.randint(100000000, 999999999)}",
                "mock_data": True,
                "place_type": poi["category"],
                "neighborhood": closest_neighborhood["name"],
                "popular": poi["popular"],
                "rating": poi["rating"],
                "reviews": random.randint(100, 2000)
            }
        )
        
        # Insert into MongoDB
        result = db.content.insert_one(content)
        place_id = result.inserted_id
        place_ids.append(place_id)
    
    # Then generate random other places to reach the desired count
    remaining_places = other_places_count - real_pois_count
    
    if remaining_places > 0:
        # Place types for non-food places
        place_types = [
            {"type": "Art Gallery", "features": ["exhibitions", "local artists", "art displays", "workshops", "contemporary art"]},
            {"type": "Museum", "features": ["exhibits", "collections", "artifacts", "historic items", "interactive displays"]},
            {"type": "Theater", "features": ["performances", "shows", "live entertainment", "plays", "musicals"]},
            {"type": "Bookstore", "features": ["books", "reading area", "author events", "rare editions", "local literature"]},
            {"type": "Park", "features": ["green space", "walking trails", "playground", "picnic areas", "sports fields"]},
            {"type": "Shopping Mall", "features": ["retail stores", "food court", "fashion", "electronics", "services"]},
            {"type": "Boutique", "features": ["fashion", "accessories", "local designers", "unique items", "clothing"]},
            {"type": "Fitness Center", "features": ["gym equipment", "classes", "personal training", "cardio area", "wellness services"]},
            {"type": "Spa", "features": ["massages", "treatments", "relaxation", "wellness", "skincare"]},
            {"type": "Vintage Shop", "features": ["vintage clothing", "antiques", "collectibles", "retro items", "second-hand"]},
            {"type": "Music Venue", "features": ["live music", "performances", "concerts", "local bands", "acoustics"]},
            {"type": "Record Store", "features": ["vinyl records", "music collection", "rare editions", "new releases", "listening stations"]},
            {"type": "Yoga Studio", "features": ["yoga classes", "meditation", "wellness", "workshops", "teacher training"]},
            {"type": "Cinema", "features": ["movies", "film screenings", "popcorn", "indie films", "blockbusters"]}
        ]
        
        for i in range(remaining_places):
            # Choose a random place type
            place_data = random.choice(place_types)
            place_type = place_data["type"]
            features = place_data["features"]
            
            # Generate place name
            name_patterns = [
                "The {adjective} {noun}",
                "{firstName}'s {type}",
                "{location} {type}",
                "{adjective} {feature} {type}",
                "The {feature} {noun}",
                "{firstName} & {firstName} {type}",
                "{noun} {number}",
                "{type} {location}",
                "{firstName}'s {type}"
            ]
            
            adjectives = ["Urban", "Modern", "Classic", "Vintage", "Contemporary", "Local", "Creative", "Tranquil", "Vibrant", "Hidden"]
            nouns = ["Space", "Spot", "House", "Studio", "Gallery", "Center", "Shop", "Place", "Collective", "Hub"]
            locations = ["Toronto", "Yorkville", "Queen", "King", "Bloor", "Distillery", "Junction", "Parkdale", "Riverside"]
            feature = random.choice(features).split()[0]  # Just take the first word
            firstNames = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Jamie", "Drew"]
            numbers = ["6", "TO", "416", "647", "One", "Two", "Six", "Seven"]
            
            name_pattern = random.choice(name_patterns)
            place_name = name_pattern.format(
                adjective=random.choice(adjectives),
                noun=random.choice(nouns),
                firstName=random.choice(firstNames),
                location=random.choice(locations),
                type=place_type.split()[0],  # Just the first word, e.g., "Art" from "Art Gallery"
                feature=feature,
                number=random.choice(numbers)
            )
            
            # Get a random neighborhood
            neighborhood_data = random.choice(TORONTO_NEIGHBORHOODS)
            
            # Create description
            feature_list = ", ".join(random.sample(features, min(3, len(features))))
            
            description_templates = [
                "{type} in {neighborhood} featuring {features}. {rating}/5 stars based on {reviews} reviews.",
                "Unique {type} showcasing {features}. Located in {neighborhood}.",
                "Local {type} in the heart of {neighborhood}. Known for {features}.",
                "{adjective} {type} experience in {neighborhood}. Highlights include: {features}.",
                "{type} with {ambience} atmosphere in {neighborhood}. Popular for {features}."
            ]
            
            description_template = random.choice(description_templates)
            rating = round(random.uniform(3.8, 4.9), 1)  # Most places have good ratings
            reviews = random.randint(10, 300)
            ambience = random.choice(["intimate", "spacious", "welcoming", "professional", "relaxed", "inspiring"])
            
            description = description_template.format(
                type=place_type,
                neighborhood=neighborhood_data["name"],
                features=feature_list,
                rating=rating,
                reviews=reviews,
                adjective=random.choice(["Amazing", "Fantastic", "Outstanding", "Delightful", "Excellent"]),
                ambience=ambience
            )
            
            # Create tags
            tags = [place_type.lower().replace(" ", "-"), neighborhood_data["name"].lower().replace(" ", "-"), "toronto"]
            for feature in random.sample(features, min(2, len(features))):
                tags.append(feature.lower().replace(" ", "-"))
            
            # Add category-specific tags
            if place_type == "Art Gallery":
                category = "gallery"
                tags.append("art")
            elif place_type == "Museum":
                category = "museum"
                tags.append("culture")
            elif place_type == "Park":
                category = "outdoor"
                tags.append("nature")
            elif place_type == "Shopping Mall" or place_type == "Boutique" or place_type == "Vintage Shop":
                category = "shopping"
                tags.append("retail")
            elif place_type == "Fitness Center" or place_type == "Yoga Studio":
                category = "fitness"
                tags.append("health")
            elif place_type == "Spa":
                category = "wellness"
                tags.append("relaxation")
            elif place_type == "Music Venue" or place_type == "Cinema" or place_type == "Theater":
                category = "entertainment"
                tags.append("performance")
            else:
                category = place_type.lower().replace(" ", "-")
            
            # Determine whether it's popular
            popular = random.random() < 0.3 or neighborhood_data["popular"]
            
            # Create content for the place
            content = create_content(
                title=place_name,
                description=description,
                image_url=random_image_url(),
                source_url=f"https://maps.google.com/place/?q=place_id:{random.randint(100000000, 999999999)}",
                categories=[category],
                tags=tags,
                location={
                    "latitude": neighborhood_data["lat"] + random.uniform(-0.005, 0.005),
                    "longitude": neighborhood_data["lon"] + random.uniform(-0.005, 0.005),
                    "address": f"{random.randint(1, 999)} {random.choice(['King', 'Queen', 'Dundas', 'College', 'Bloor', 'Yonge', neighborhood_data['name']])} St, Toronto, ON",
                    "neighborhood": neighborhood_data["name"]
                },
                metadata={
                    "source": "google_places",
                    "google_place_id": f"place_{random.randint(100000000, 999999999)}",
                    "mock_data": True,
                    "place_type": place_type,
                    "neighborhood": neighborhood_data["name"],
                    "popular": popular,
                    "rating": rating,
                    "reviews": reviews
                }
            )
            
            # Insert into MongoDB
            result = db.content.insert_one(content)
            place_id = result.inserted_id
            place_ids.append(place_id)
            
            if (i + 1) % 50 == 0 or i == remaining_places - 1:
                logger.info(f"Created {i + 1} other places")
    
    logger.info(f"Generated {len(place_ids)} Toronto places")
    return place_ids

def _determine_seasonal_relevance(date):
    """Determine seasonal relevance based on date"""
    month = date.month
    day = date.day
    
    seasons = []
    
    # Season based on month
    if 3 <= month <= 5:
        seasons.append("spring")
    elif 6 <= month <= 8:
        seasons.append("summer")
    elif 9 <= month <= 11:
        seasons.append("fall")
    else:
        seasons.append("winter")
    
    # Special periods
    if month == 12:
        seasons.append("holiday")
    
    if month == 7:
        seasons.append("summer-festival")
    
    # Canada Day
    if month == 7 and day == 1:
        seasons.append("canada-day")
        
    # Halloween
    if month == 10 and day >= 25:
        seasons.append("halloween")
        
    # Thanksgiving (Canadian - second Monday in October)
    if month == 10 and 8 <= day <= 14:
        seasons.append("thanksgiving")
    
    return seasons

def generate_username(used_usernames=None):
    """Generate a random username, ensuring it's unique"""
    if used_usernames is None:
        used_usernames = set()
        
    prefixes = ["toronto", "the6ix", "6side", "tdot", "to", "gta", "ontario", "canada", "maple", "drake", "raptors"]
    suffixes = ["fan", "lover", "explorer", "native", "traveler", "foodie", "photographer", "local"]
    numbers = ["", str(random.randint(0, 999)), str(random.randint(2000, 2025))]
    
    # Try to generate a unique username
    max_attempts = 10
    for _ in range(max_attempts):
        username = f"{random.choice(prefixes)}{random.choice(suffixes)}{random.choice(numbers)}"
        if username not in used_usernames:
            used_usernames.add(username)
            return username
    
    # If we couldn't generate a unique username after several attempts, add a random UUID
    username = f"{random.choice(prefixes)}{random.choice(suffixes)}{uuid.uuid4().hex[:6]}"
    used_usernames.add(username)
    return username

def main():
    """Generate enhanced mock data for Toronto Trendspotter"""
    load_dotenv()
    
    # Connect to MongoDB
    db = get_mongodb_db()
    
    try:
        # Check for existing mock data
        existing_mock = db.content.count_documents({"metadata.mock_data": True})
        if existing_mock > 0:
            logger.info(f"Found {existing_mock} existing mock data records")
            delete = input("Delete existing mock data? (y/n): ").lower() == 'y'
            
            if delete:
                # Delete existing mock data
                deleted_content = db.content.delete_many({"metadata.mock_data": True})
                deleted_events = db.toronto_events.delete_many({})
                deleted_interactions = db.interactions.delete_many({})
                db.users.delete_many({})
                logger.info(f"Deleted {deleted_content.deleted_count} content items, {deleted_events.deleted_count} events, and {deleted_interactions.deleted_count} interactions")
            else:
                logger.info("Keeping existing mock data")
                return
        
        # Generate new mock data
        logger.info("Generating enhanced mock data...")
        start_time = datetime.now()
        
        # Generate Pinterest content (500 items)
        pinterest_ids = generate_mock_pinterest_content(count=500)
        logger.info(f"Generated {len(pinterest_ids)} Pinterest content items")
        
        # Generate Toronto events (300 items)
        event_ids = generate_mock_events(count=300)
        logger.info(f"Generated {len(event_ids)} Toronto events")
        
        # Generate Toronto places (200 items)
        place_ids = generate_mock_places(count=200)
        logger.info(f"Generated {len(place_ids)} Toronto places")
        
        # Combine all content IDs
        all_content_ids = pinterest_ids + [event["content_id"] for event in db.toronto_events.find({}, {"content_id": 1})]
        
        # Generate user interaction data (200 users, 5-30 interactions each)
        interaction_count = generate_interaction_data(all_content_ids, user_count=200, interactions_per_user_range=(5, 30))
        logger.info(f"Generated {interaction_count} user interactions")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        logger.info(f"Successfully generated enhanced mock data in {duration:.1f} minutes:")
        logger.info(f"- {len(pinterest_ids)} Pinterest content items")
        logger.info(f"- {len(event_ids)} Toronto events")
        logger.info(f"- {len(place_ids)} Toronto places")
        logger.info(f"- {interaction_count} user interactions")
        logger.info(f"- Total content items: {len(pinterest_ids) + len(event_ids) + len(place_ids)}")
        
        # Print some DB stats
        content_count = db.content.count_documents({})
        event_count = db.toronto_events.count_documents({})
        user_count = db.users.count_documents({})
        interaction_count = db.interactions.count_documents({})
        
        logger.info(f"Database statistics:")
        logger.info(f"- Content collection: {content_count} documents")
        logger.info(f"- Toronto events collection: {event_count} documents")
        logger.info(f"- Users collection: {user_count} documents")
        logger.info(f"- Interactions collection: {interaction_count} documents")
        
    except Exception as e:
        logger.error(f"Error generating enhanced mock data: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()