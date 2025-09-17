import requests
from bs4 import BeautifulSoup

url = 'https://lite.bing.com/search?q=Numbeo+RapidAPI'
html = requests.get(url, timeout=30).text
soup = BeautifulSoup(html, 'html.parser')
for li in soup.select('li.b_algo')[:5]:
    a = li.find('a')
    if not a:
        continue
    title = a.get_text(strip=True)
    href = a['href']
    snippet = li.find('div', class_='b_caption')
    snippet_text = snippet.get_text(' ', strip=True) if snippet else ''
    print(title)
    print(href)
    print(snippet_text)
    print('-'*60)
