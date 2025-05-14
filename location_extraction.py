import os
import logging
import spacy
from pymongo import MongoClient
from geopy.geocoders import Nominatim

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("location-guesser")

nlp = spacy.load("en_core_web_sm")
geolocator = Nominatim(user_agent="trendspotter_locator")

# MongoDB setup
MONGO_URI = "mongodb+srv://mohammedshak:Shakmongocluster03@trendspotter-cluster.wu00mmm.mongodb.net/?retryWrites=true&w=majority&appName=trendspotter-cluster"
client = MongoClient(MONGO_URI)
db = client["trendspotter-prod"]
content_coll = db["content"]

# Toronto known places dictionary
TORONTO_KEY_LOCATIONS = {
    "cn tower": (43.6426, -79.3871, "Downtown Core"),
    "distillery district": (43.6503, -79.3597, "Distillery District"),
    "kensington market": (43.6547, -79.4005, "Kensington Market"),
    "the beaches": (43.6762, -79.2995, "The Beaches"),
    "yorkville": (43.6709, -79.3933, "Yorkville"),
    "queen west": (43.6468, -79.4119, "Queen West"),
    "liberty village": (43.6371, -79.4208, "Liberty Village"),
    "leslieville": (43.6626, -79.3357, "Leslieville"),
    "little italy": (43.6547, -79.4228, "Little Italy"),
    "chinatown": (43.6529, -79.3975, "Chinatown"),
    "flatiron building": (43.6486, -79.3757, "St. Lawrence Market"),
    "toronto islands": (43.6228, -79.3817, "Toronto Islands")
}

DEFAULT_LOCATION = {
    "latitude": 43.6532,
    "longitude": -79.3832,
    "neighborhood": "Downtown Core"
}

def guess_location(texts):
    texts_joined = " ".join([t.lower() for t in texts if t])
    
    # Keyword match first
    for keyword, (lat, lon, name) in TORONTO_KEY_LOCATIONS.items():
        if keyword in texts_joined:
            logger.info(f"Matched keyword '{keyword}' → ({lat}, {lon})")
            return {"latitude": lat, "longitude": lon, "neighborhood": name}

    # Use spaCy NER and geocode
    doc = nlp(texts_joined)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            place = f"{ent.text}, Toronto, Canada"
            try:
                location = geolocator.geocode(place)
                if location:
                    logger.info(f"Geocoded '{ent.text}' to ({location.latitude}, {location.longitude})")
                    return {
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "neighborhood": DEFAULT_LOCATION["neighborhood"]  # temporary fallback tag
                    }
            except Exception as e:
                logger.warning(f"Geolocation failed for {ent.text}: {e}")

    return None  # No good match

def update_all_content_locations():
    updated = 0
    contents = content_coll.find({})  # 👈 Process all documents

    for content in contents:
        texts = [
            content.get("description", ""),
            content.get("grid_title", ""),
            content.get("board", {}).get("name", ""),
            content.get("pinner", {}).get("username", ""),
            content.get("domain", "")
        ]

        guessed = guess_location(texts)
        if guessed:
            new_loc = guessed
        else:
            logger.warning(f"No location found for content {content['_id']} – applying default.")
            new_loc = DEFAULT_LOCATION

        # Overwrite location entirely
        content_coll.update_one(
            {"_id": content["_id"]},
            {"$set": {"location": new_loc}}
        )
        updated += 1
        logger.info(f"✅ Rewritten location for {content['_id']}: {new_loc}")

    print(f"🎯 Updated {updated} documents with fresh location data.")

if __name__ == "__main__":
    update_all_content_locations()
