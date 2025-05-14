import random
from pymongo import MongoClient

# Replace with your MongoDB Atlas URI
MONGO_URI = "mongodb+srv://mohammedshak:Shakmongocluster03@trendspotter-cluster.wu00mmm.mongodb.net/?retryWrites=true&w=majority&appName=trendspotter-cluster"

client = MongoClient(MONGO_URI)

# Access the databases and collections
trendspotter_db = client['trendspotter']
trendspotter_prod_db = client['trendspotter-prod']

trendspotter_content = trendspotter_db['content']
trendspotter_prod_content = trendspotter_prod_db['content']

# Fetch all image_urls from trendspotter-prod.content
prod_documents = list(trendspotter_prod_content.find({}, {'image_url': 1}))
prod_image_urls = [doc['image_url'] for doc in prod_documents]

# Check if we have any image URLs to replace with
if not prod_image_urls:
    print("No image URLs found in trendspotter-prod.content.")
else:
    # Iterate through each document in trendspotter.content
    for doc in trendspotter_content.find():
        # Select a random image_url from the prod_image_urls
        new_image_url = random.choice(prod_image_urls)
        
        # Update the document with the new image_url
        trendspotter_content.update_one(
            {'_id': doc['_id']},
            {'$set': {'image_url': new_image_url}}
        )
        print(f"Updated document {doc['_id']} with new image_url: {new_image_url}")

print("Image URLs updated successfully.")
