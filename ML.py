import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from pymongo import MongoClient
import re
import string

nltk.download('punkt')
nltk.download('stopwords')

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
collection = db['social_media_posts']

# Function to fetch all summaries from MongoDB
def fetch_summaries():
    """
    Fetches all summaries from the MongoDB collection.
    """
    summaries = []
    for document in collection.find({}, {"summary": 1}):
        summaries.append(document['summary'])
    return summaries

# Function to clean text
def clean_text(text):
    """
    Cleans the text data by removing stop words, punctuation, and converting to lowercase.
    """
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize and remove stop words
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    cleaned_text = ' '.join([word for word in words if word not in stop_words])
    return cleaned_text

# Function to perform text vectorization
def vectorize_text(summaries):
    """
    Vectorizes the text summaries using TF-IDF vectorization.
    """
    cleaned_summaries = [clean_text(summary) for summary in summaries]
    vectorizer = TfidfVectorizer(max_features=1000)  # Limit to top 1000 features
    X = vectorizer.fit_transform(cleaned_summaries)
    return X

# Function to perform clustering
def perform_clustering(X, n_clusters=5):
    """
    Performs K-Means clustering on the TF-IDF vectorized text data.
    """
    model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(X)
    return model

# Function to store cluster labels in MongoDB
def store_cluster_labels(labels):
    """
    Stores the cluster labels in MongoDB.
    """
    for i, label in enumerate(labels):
        collection.update_one(
            {"_id": i + 1},  # Assuming post_id is a sequential integer starting from 1
            {"$set": {"cluster": int(label)}}
        )
    print("Cluster labels stored in MongoDB.")

def main():
    """
    Main function to perform clustering on disaster summaries.
    """
    # Fetch summaries from MongoDB
    summaries = fetch_summaries()
    if not summaries:
        print("No summaries found in MongoDB.")
        return
    
    # Vectorize the text summaries
    X = vectorize_text(summaries)
    
    # Perform clustering
    model = perform_clustering(X, n_clusters=5)
    
    # Store cluster labels in MongoDB
    store_cluster_labels(model.labels_)

if __name__ == "__main__":
    main()
