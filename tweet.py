import tweepy

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

keywords = ['earthquake', 'flood', 'hurricane', 'wildfire', 'disaster']

for tweet in tweepy.Cursor(api.search_tweets, q=' OR '.join(keywords), lang='en', tweet_mode='extended').items(100):
    print(f"User: {tweet.user.screen_name}")
    print(f"Tweet: {tweet.full_text}")
    print(f"Created at: {tweet.created_at}")
    print('-' * 50)
