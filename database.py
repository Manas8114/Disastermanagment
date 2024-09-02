from pymongo import MongoClient

# Replace the URI string with your MongoDB deployment's connection string.
# For a local MongoDB instance, use 'mongodb://localhost:27017/'.
client = MongoClient('mongodb://localhost:27017/')

# Create or access a database named 'disaster_management'
db = client['disaster_management']

# Create or access collections
news_collection = db['news_articles']
social_media_collection = db['social_media_posts']

print("Connected to MongoDB and initialized collections.")
