import tweepy
from pymongo import MongoClient

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
social_media_collection = db['social_media_posts']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

keywords = ['earthquake', 'flood', 'hurricane', 'wildfire', 'disaster']

for tweet in tweepy.Cursor(api.search_tweets, q=' OR '.join(keywords), lang='en', tweet_mode='extended').items(100):
    tweet_data = {
        'user': tweet.user.screen_name,
        'text': tweet.full_text,
        'created_at': tweet.created_at
    }
    
    social_media_collection.insert_one(tweet_data)
    print(f'Inserted tweet from {tweet.user.screen_name}')
