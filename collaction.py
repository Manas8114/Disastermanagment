import requests
from bs4 import BeautifulSoup

url = 'https://www.bbc.com/news/live' # twitter API dont know if it will work because of the X

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = soup.find_all('article', class_='news-article')
    
    for article in articles:
        title = article.find('h2').get_text(strip=True)  
        link = article.find('a')['href'] 
        summary = article.find('p').get_text(strip=True)  
        
        print(f'Title: {title}')
        print(f'Link: {link}')
        print(f'Summary: {summary}')
        print('-' * 50)
else:
    print(f'Failed to retrieve the webpage. Status code: {response.status_code}')
