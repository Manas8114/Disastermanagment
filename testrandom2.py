import requests
import csv
import re
import spacy

API_KEY = '6feca183e0494d048dbbf18a4a6c8931'

# Load SpaCy NER model
nlp = spacy.load('en_core_web_sm')

def extract_location(text):
    # Use SpaCy NER to find location entities
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == 'GPE']
    return ', '.join(locations) if locations else None

def get_news_from_newsapi(keyword):
    url = f'https://newsapi.org/v2/everything?q={keyword}&language=en&apiKey={API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])

    scraped_data = []

    for article in articles:
        title = article['title']
        summary = article['description']
        link = article['url']
        location = extract_location(f"{title} {summary} {link}")

        scraped_data.append({
            'Title': title,
            'Link': link,
            'Summary': summary,
            'Published Date': article['publishedAt'],
            'Source': article['source']['name'],
            'Location': location
        })

    return scraped_data

def save_to_csv(data, filename='disaster_news.csv'):
    # Check if the file already exists; if not, write the header row
    file_exists = False
    try:
        with open(filename, 'r', encoding='utf-8') as existing_file:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Link', 'Summary', 'Published Date', 'Source', 'Location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write the header row only if the file is newly created

        writer.writerows(data)
        print("Data saved successfully!")

# Example usage:
keyword = 'flood OR earthquake OR disaster'
news_data = get_news_from_newsapi(keyword)
save_to_csv(news_data)