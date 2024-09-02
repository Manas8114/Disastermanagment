import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['disaster_management']
news_collection = db['news_articles']

url = "https://www.bbc.com/news/articles/cd108y8439po"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = soup.find_all('article', class_='news-article')
    
    for article in articles:
        title = article.find('h2').get_text(strip=True)  
        link = article.find('a')['href']  
        summary = article.find('p').get_text(strip=True)  
        
        news_data = {
            'title': title,
            'link': link,
            'summary': summary
        }
        
        news_collection.insert_one(news_data)
        print(f'Inserted: {title}')
else:
    print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
