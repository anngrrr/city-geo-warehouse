import requests
from bs4 import BeautifulSoup

html = requests.get('https://rapidapi.com/numbeo/api/numbeo/', timeout=30).text
soup = BeautifulSoup(html, 'html.parser')
for script in soup.find_all('script'):
    if script.get('type') == 'application/json' and script.get('id') == '__NEXT_DATA__':
        print(len(script.string))
        print(script.string[:200])
        break
else:
    print('not found')
