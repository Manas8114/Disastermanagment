import asyncio
import aiohttp
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from pymongo import MongoClient
import spacy
import random
import time

nltk.download('punkt')

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
collection = db['social_media_posts']

# Load the spaCy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")

# Define a list of disaster-related keywords
DISASTER_KEYWORDS = [
    "earthquake", "flood", "hurricane", "wildfire", "tsunami", "tornado", "forestfires", "killed", "death",
    "volcano", "drought", "avalanche", "cyclone", "storm", "landslide", "pandemic", "fires", "attack"
]

news_sources = [
    {"base_url": "https://www.bbc.com", "search_url": "https://www.bbc.com/search?q={keyword}"},
    {"base_url": "https://www.cnn.com", "search_url": "https://www.cnn.com/search/?q={keyword}"},
    {"base_url": "https://www.nytimes.com", "search_url": "https://www.nytimes.com/search?query={keyword}"},
    {"base_url": "https://www.reuters.com", "search_url": "https://www.reuters.com/search/news?blob={keyword}"},
    {"base_url": "https://www.forbes.com", "search_url": "https://www.forbes.com/search/?q={keyword}"},
    {"base_url": "https://www.bloomberg.com", "search_url": "https://www.bloomberg.com/search?query={keyword}"},
    {"base_url": "https://www.nbcnews.com", "search_url": "https://www.nbcnews.com/search/?q={keyword}"},
    {"base_url": "https://abcnews.go.com", "search_url": "https://abcnews.go.com/search?searchtext={keyword}"},
    {"base_url": "https://www.politico.com", "search_url": "https://www.politico.com/search?q={keyword}"},
    {"base_url": "https://www.npr.org", "search_url": "https://www.npr.org/search?query={keyword}"},
    {"base_url": "https://www.usatoday.com", "search_url": "https://www.usatoday.com/search/?q={keyword}"},
    {"base_url": "https://www.msnbc.com", "search_url": "https://www.msnbc.com/search/?q={keyword}"},
    {"base_url": "https://www.huffpost.com", "search_url": "https://www.huffpost.com/search?q={keyword}"},
    {"base_url": "https://www.smithsonianmag.com", "search_url": "https://www.smithsonianmag.com/search/?q={keyword}"},
    {"base_url": "https://www.wired.com", "search_url": "https://www.wired.com/search/?q={keyword}"},
    {"base_url": "https://www.techcrunch.com", "search_url": "https://www.techcrunch.com/search/{keyword}"},
    {"base_url": "https://www.economist.com", "search_url": "https://www.economist.com/search?q={keyword}"},
    {"base_url": "https://www.newsweek.com", "search_url": "https://www.newsweek.com/search/site/{keyword}"},
    {"base_url": "https://www.cbsnews.com", "search_url": "https://www.cbsnews.com/search/?q={keyword}"},
    {"base_url": "https://www.latimes.com", "search_url": "https://www.latimes.com/search?q={keyword}"},
    {"base_url": "https://www.chicagotribune.com", "search_url": "https://www.chicagotribune.com/search/?q={keyword}"},
    {"base_url": "https://www.pbs.org", "search_url": "https://www.pbs.org/search/?q={keyword}"},
    {"base_url": "https://www.ndtv.com", "search_url": "https://www.ndtv.com/search?searchtext={keyword}"},
    {"base_url": "https://www.thehindu.com", "search_url": "https://www.thehindu.com/search/?q={keyword}"},
    {"base_url": "https://timesofindia.indiatimes.com", "search_url": "https://timesofindia.indiatimes.com/topic/{keyword}"},
    {"base_url": "https://indianexpress.com", "search_url": "https://indianexpress.com/?s={keyword}"},
    {"base_url": "https://www.hindustantimes.com", "search_url": "https://www.hindustantimes.com/search?q={keyword}"},
    {"base_url": "https://www.indiatoday.in", "search_url": "https://www.indiatoday.in/search?search={keyword}"},
    {"base_url": "https://zeenews.india.com", "search_url": "https://zeenews.india.com/search?q={keyword}"},
    {"base_url": "https://www.abplive.com", "search_url": "https://www.abplive.com/search?q={keyword}"}
]

async def fetch_article_text(session, url):
    """Fetches the text content of an article from a given URL using async requests."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            soup = BeautifulSoup(await response.text(), 'html.parser')
            paragraphs = soup.find_all('p')
            article_text = ' '.join([para.get_text() for para in paragraphs])
            
            # Check for disaster-related keywords
            if any(keyword in article_text.lower() for keyword in DISASTER_KEYWORDS):
                return article_text
            else:
                print(f"Article from {url} does not mention disaster-related keywords.")
                return ""
    except Exception as e:
        print(f"Error fetching the article from {url}: {e}")
        return ""

def summarize_text(text, num_sentences=3):
    """Summarizes the given text by extracting the most significant sentences."""
    if not text:
        return "No text provided for summarization."

    sentences = sent_tokenize(text)

    if len(sentences) <= num_sentences:
        return text 

    word_frequencies = FreqDist(word.lower() for sentence in sentences for word in word_tokenize(sentence))
    sentence_scores = {}
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        sentence_scores[sentence] = sum(word_frequencies[word] for word in words if word in word_frequencies)

    sorted_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    summary_sentences = sorted_sentences[:num_sentences]
    summary = ' '.join(summary_sentences)
    return summary

def extract_key_points(text, num_points=5):
    """Extracts key points from the text if the article is too short for a summary."""
    if not text:
        return "No text provided for key point extraction."

    sentences = sent_tokenize(text)
    key_points = sentences[:num_points]
    return ' '.join(key_points)

async def summarize_article(session, url):
    """Fetches and summarizes the article from the given URL, and extracts keywords."""
    article_text = await fetch_article_text(session, url)
    if not article_text:
        return None, []  # Return None if the article does not mention disaster-related keywords

    # Extract keywords from the text
    keywords = [keyword for keyword in DISASTER_KEYWORDS if keyword in article_text.lower()]

    if len(article_text) < 50:
        return extract_key_points(article_text), keywords

    summary = summarize_text(article_text)
    return summary, keywords

def get_next_post_id():
    """Gets the next available post_id by incrementing a counter stored in MongoDB."""
    counter_doc = db['counters'].find_one_and_update(
        {'_id': 'post_id'},
        {'$inc': {'sequence_value': 1}},
        upsert=True,
        return_document=True
    )
    return counter_doc['sequence_value']

def store_summary(url, summary, keywords):
    """Stores the summarized article in MongoDB with a unique post_id and keywords."""
    post_id = get_next_post_id()
    data = {
        'post_id': post_id,
        'url': url,
        'summary': summary,
        'keywords': keywords
    }
    try:
        collection.insert_one(data)
        print("Stored summary in MongoDB with post_id:", post_id)
    except Exception as e:
        print(f"Error storing summary in MongoDB: {e}")

def extract_locations(text):
    """Extracts locations from text using spaCy's Named Entity Recognition."""
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    return locations

def store_locations(article_id, locations):
    """Stores the extracted locations in MongoDB."""
    if locations:
        collection.update_one(
            {"_id": article_id},
            {"$set": {"locations": locations}}
        )
        print(f"Stored locations for article ID {article_id}: {locations}")
    else:
        print(f"No locations found for article ID {article_id}.")

async def fetch_and_store_news():
    """Fetches and stores summaries of articles from random news sources asynchronously."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for source in random.sample(news_sources, len(news_sources)):  # Shuffle and iterate over news sources
            print(f"Processing URL: {source['base_url']}")
            task = asyncio.create_task(summarize_article(session, source['search_url'].format(keyword=random.choice(DISASTER_KEYWORDS))))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        for summary, keywords in results:
            if summary:  # Only store if there is a valid summary
                print(f"Summary: {summary}")
                store_summary(source['base_url'], summary, keywords)
            else:
                print(f"No relevant disaster-related content found in {source}. Skipping.")

async def main():
    """Main function to continuously fetch and process news articles."""
    while True:
        await fetch_and_store_news()
        print("Waiting for the next cycle...")
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())