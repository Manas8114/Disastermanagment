from transformers import pipeline

sentiment_analysis = pipeline('sentiment-analysis')

tweets = social_media_collection.find()

for tweet in tweets:
    sentiment = sentiment_analysis(tweet['cleaned_text'])[0]
    social_media_collection.update_one({'_id': tweet['_id']}, {'$set': {'sentiment': sentiment}})
    print(f"Sentiment of tweet by {tweet['user']}: {sentiment}")
