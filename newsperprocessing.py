from pymongo import MongoClient
from NLTK import nlp


client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
social_media_collection = db['social_media_posts']

tweets = social_media_collection.find()

def perform_ner(text):
    doc = nlp(text)
    entities = [(entity.text, entity.label_) for entity in doc.ents]
    return entities

for tweet in tweets:
    entities = perform_ner(tweet['cleaned_text'])
    social_media_collection.update_one({'_id': tweet['_id']}, {'$set': {'entities': entities}})
    print(f"Extracted entities from tweet by: {tweet['user']}")
