import os
import logging
from pymongo import MongoClient
from shapely.geometry import Point
import geopandas as gpd

# ------------------- CONFIG -------------------
# Load MongoDB URI from env or use fallback
MONGO_URI = "mongodb+srv://mohammedshak:Shakmongocluster03@trendspotter-cluster.wu00mmm.mongodb.net/?retryWrites=true&w=majority&appName=trendspotter-cluster"
DB_NAME = "trendspotter-prod"
COLLECTION_NAME = "content"

# Path to GeoJSON file of Toronto neighborhoods
GEOJSON_PATH = "neighbourhoods.geojson"

# Whether to force update even if neighborhood exists
FORCE_REPROCESS = True

# ------------------- SETUP --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("polygon-mapper")

# Load GeoJSON into GeoDataFrame
neighborhoods_gdf = gpd.read_file(GEOJSON_PATH)
neighborhoods_gdf = neighborhoods_gdf.to_crs("EPSG:4326")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
content_coll = db[COLLECTION_NAME]

# ------------------- FUNCTIONS --------------------
def find_neighborhood_by_point(lat, lon):
    point = Point(lon, lat)
    match = neighborhoods_gdf[neighborhoods_gdf.geometry.contains(point)]
    if not match.empty:
        return match.iloc[0]["AREA_NAME"]
    return None

def update_neighborhoods_polygon_based():
    query = {
        "location.latitude": {"$exists": True},
        "location.longitude": {"$exists": True},
        "$or": [
            {"location.neighborhood": {"$exists": False}},
            {"location.neighborhood": None},
            {"location.neighborhood": ""},
            {"location.neighborhood": "Downtown Core"}  # reprocess fallback
        ]
    }

    if FORCE_REPROCESS:
        query = {
            "location.latitude": {"$exists": True},
            "location.longitude": {"$exists": True}
        }

    contents = content_coll.find(query)
    updated = 0

    for content in contents:
        loc = content.get("location", {})
        lat = loc.get("latitude")
        lon = loc.get("longitude")

        if lat is None or lon is None:
            continue

        neighborhood = find_neighborhood_by_point(lat, lon)

        if neighborhood:
            result = content_coll.update_one(
                {"_id": content["_id"]},
                {"$set": {"location.neighborhood": neighborhood}}
            )
            if result.modified_count > 0:
                logger.info(f"✅ Updated content {content['_id']} → {neighborhood}")
                updated += 1
        else:
            logger.warning(f"⚠️ No polygon match for content {content['_id']} at ({lat}, {lon})")

    print(f"🎯 Polygon-based mapping complete: {updated} documents updated.")

# ------------------- MAIN --------------------
if __name__ == "__main__":
    update_neighborhoods_polygon_based()
