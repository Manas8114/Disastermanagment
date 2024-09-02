import requests
import csv
from bs4 import BeautifulSoup
import re
import time
import random
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist

nltk.download('punkt')

# List of news websites to scrape
news_sources = [
    "https://www.bbc.com",
    "https://www.cnn.com",
    "https://www.nytimes.com",
    "https://www.theguardian.com",
    "https://www.aljazeera.com",
    "https://www.washingtonpost.com",
    "https://www.forbes.com",
    "https://www.bloomberg.com",
    "https://www.nbcnews.com",
    "https://www.abcnews.go.com",
    "https://www.npr.org",
    "https://www.msnbc.com",
    "https://www.dailymail.co.uk",
    "https://www.huffpost.com",
    "https://www.smithsonianmag.com",
    "https://www.wired.com",
    "https://www.techcrunch.com",
    "https://www.buzzfeednews.com",
    "https://www.vox.com",
    "https://www.economist.com",
    "https://www.cbsnews.com",
    "https://www.chicagotribune.com",
    "https://www.pbs.org",
    "https://www.dallasnews.com"
]

# Keywords to search for in articles
keywords = ['earthquake', 'drought', 'rain', 'flood', 'storm']

def fetch_article_text(url):
    """
    Fetches the text content of an article from a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the title and content of the article
        title = soup.title.string if soup.title else 'No Title'
        paragraphs = soup.find_all('p')
        article_text = ' '.join([para.get_text() for para in paragraphs])
        
        return title, article_text
    except requests.RequestException as e:
        print(f"Error fetching the article from {url}: {e}")
        return None, None

def summarize_text(text, num_sentences=3):
    """
    Summarizes the given text by extracting the most significant sentences.
    """
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

def scrape_news_articles():
    """
    Scrapes news articles from the defined news sources and saves relevant data to a CSV file.
    """
    scraped_data = []

    for source in news_sources:
        print(f"Processing source: {source}")
        title, article_text = fetch_article_text(source)
        
        if not title or not article_text:
            print(f"Skipping source {source} due to fetching issues.")
            continue
        
        # Check for relevant keywords in the title or article text
        relevant_keywords = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', article_text, re.IGNORECASE)]
        
        if relevant_keywords:
            summary = summarize_text(article_text)

            # Append relevant data to the list
            scraped_data.append({
                'Title': title,
                'Link': source,
                'Keywords': ', '.join(relevant_keywords),
                'Location': 'Not specified',  # Modify if you have a way to extract location
                'Summary': summary
            })

        time.sleep(random.randint(5, 15))  # Sleep to avoid overwhelming the sources with requests

    # Sort the data by the number of relevant keywords found (most relevant first)
    scraped_data.sort(key=lambda x: len(x['Keywords']), reverse=True)

    # Save data to a CSV file
    csv_filename = 'disaster_news_with_summaries.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Link', 'Keywords', 'Location', 'Summary']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scraped_data)

    print(f"Data saved successfully in {csv_filename}!")

if __name__ == "__main__":
    scrape_news_articles()
