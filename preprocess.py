import re
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
news_collection = db['news_articles']
social_media_collection = db['social_media_posts']

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

news_articles = news_collection.find()
for article in news_articles:
    cleaned_summary = clean_text(article['summary'])
    news_collection.update_one({'_id': article['_id']}, {'$set': {'cleaned_summary': cleaned_summary}})
    print(f"Cleaned and updated news article: {article['title']}")

tweets = social_media_collection.find()
for tweet in tweets:
    cleaned_text = clean_text(tweet['text'])
    social_media_collection.update_one({'_id': tweet['_id']}, {'$set': {'cleaned_text': cleaned_text}})
    print(f"Cleaned and updated tweet from: {tweet['user']}")
