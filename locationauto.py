import spacy
from pymongo import MongoClient

# Load the spaCy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
collection = db['social_media_posts']

def fetch_summaries():
    """
    Fetches all summaries from the MongoDB collection.
    """
    summaries = []
    ids = []
    for document in collection.find({}, {"summary": 1, "_id": 1}):
        summaries.append(document['summary'])
        ids.append(document['_id'])
    return summaries, ids

def extract_locations(text):
    """
    Extracts locations from text using spaCy's Named Entity Recognition.
    """
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    return locations

def store_locations(article_id, locations):
    """
    Stores the extracted locations in MongoDB.
    """
    if locations:
        collection.update_one(
            {"_id": article_id},
            {"$set": {"locations": locations}}
        )
        print(f"Stored locations for article ID {article_id}: {locations}")
    else:
        print(f"No locations found for article ID {article_id}.")

def main():
    """
    Main function to extract and store locations from articles.
    """
    summaries, ids = fetch_summaries()
    if not summaries:
        print("No summaries found in MongoDB.")
        return

    for summary, article_id in zip(summaries, ids):
        locations = extract_locations(summary)
        store_locations(article_id, locations)

if __name__ == "__main__":
    main()
