import nltk
import spacy
from pymongo import MongoClient

nltk.download('punkt')
nltk.download('stopwords')

nlp = spacy.load('en_core_web_sm')

client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
news_collection = db['news_articles']

news_articles = news_collection.find()

def preprocess_text(text):
    tokens = nltk.word_tokenize(text.lower())

    stop_words = set(nltk.corpus.stopwords.words('english'))
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]

    doc = nlp(' '.join(tokens))
    lemmatized_text = ' '.join([token.lemma_ for token in doc])

    return lemmatized_text

for article in news_articles:
    processed_text = preprocess_text(article['cleaned_summary'])
    news_collection.update_one({'_id': article['_id']}, {'$set': {'preprocessed_text': processed_text}})
    print(f"Preprocessed and updated article: {article['title']}")
