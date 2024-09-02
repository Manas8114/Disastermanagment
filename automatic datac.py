import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import nltk
from datetime import datetime
import random
import time

nltk.download('punkt')

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
collection = db['disaster_events']

# List of disaster-related keywords
DISASTER_KEYWORDS = [
    "earthquake", "flood", "hurricane", "wildfire", "tsunami", "tornado", "volcano", 
    "drought", "cyclone", "storm", "landslide", "pandemic", "forestfire", "avalanche", "typhoon", "mudslide"
]

# List of Indian news sources and their respective search URL formats
indian_news_sources = [
    {"base_url": "https://www.ndtv.com", "search_url": "https://www.ndtv.com/search?searchtext={keyword}"},
    {"base_url": "https://www.thehindu.com", "search_url": "https://www.thehindu.com/search/?q={keyword}"},
    {"base_url": "https://timesofindia.indiatimes.com", "search_url": "https://timesofindia.indiatimes.com/topic/{keyword}"},
    {"base_url": "https://indianexpress.com", "search_url": "https://indianexpress.com/?s={keyword}"},
    {"base_url": "https://www.hindustantimes.com", "search_url": "https://www.hindustantimes.com/search?q={keyword}"},
    {"base_url": "https://www.indiatoday.in", "search_url": "https://www.indiatoday.in/search?search={keyword}"},
    {"base_url": "https://zeenews.india.com", "search_url": "https://zeenews.india.com/search?q={keyword}"},
    {"base_url": "https://www.abplive.com", "search_url": "https://www.abplive.com/search?q={keyword}"}
]

def fetch_disaster_events(base_url, search_url, keyword):
    """
    Fetches disaster events from a given source URL with a random keyword search.
    """
    try:
        # Generate the search URL by inserting the keyword
        search_url = search_url.format(keyword=keyword)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        events = []
        for link in soup.find_all('a', href=True):
            if any(keyword in link.get_text().lower() for keyword in DISASTER_KEYWORDS):
                event_url = link['href']
                if not event_url.startswith('http'):
                    event_url = base_url + event_url  # Fix relative URLs
                events.append(event_url)
                
        return events
    except requests.RequestException as e:
        print(f"Error fetching data from {base_url}: {e}")
        return []

def extract_disaster_details(url):
    """
    Extracts details of a disaster event from the given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: extracting a disaster event's details (customize based on actual content)
        event_name = soup.find('h1').get_text(strip=True) if soup.find('h1') else 'Unknown Event'
        event_type = next((kw.capitalize() for kw in DISASTER_KEYWORDS if kw in event_name.lower()), 'Unknown')
        date_text = soup.find('time').get('datetime') if soup.find('time') else 'Unknown'
        date = datetime.strptime(date_text, '%Y-%m-%d') if date_text != 'Unknown' else 'Unknown'
        location = soup.find('span', {'class': 'location'}).get_text(strip=True) if soup.find('span', {'class': 'location'}) else 'Unknown'
        description = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])
        
        return {
            '_id': url,
            'event_name': event_name,
            'event_type': event_type,
            'date': date,
            'location': location,
            'description': description,
            'source': url,
            'impact': 'Unknown'
        }

    except Exception as e:
        print(f"Error extracting details from {url}: {e}")
        return None

def store_disaster_event(event_data):
    """
    Stores disaster event data in MongoDB.
    """
    if not event_data:
        return
    
    try:
        collection.insert_one(event_data)
        print(f"Stored event: {event_data['event_name']}")
    except DuplicateKeyError:
        print(f"Duplicate event found, skipping: {event_data['_id']}")

def main():
    """
    Main function to fetch and store disaster events.
    """
    for source in indian_news_sources:
        # Select a random disaster keyword for the search
        random_keyword = random.choice(DISASTER_KEYWORDS)
        print(f"Processing source: {source['base_url']} with keyword: {random_keyword}")
        
        event_urls = fetch_disaster_events(source['base_url'], source['search_url'], random_keyword)
        
        for url in event_urls:
            event_data = extract_disaster_details(url)
            store_disaster_event(event_data)

if __name__ == "__main__":
    for i in range(100):
        print(f"Run #{i + 1}")
        main()
        time.sleep(5)  # Wait 10 seconds between each run to avoid overwhelming servers
