import requests
import re

url = 'https://rapidapi.com/search/city%20data'
html = requests.get(url, timeout=30).text
match = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
print('found' if match else 'not found')
if match:
    payload = match.group(1)
    print(len(payload))
    print(payload[:200])
