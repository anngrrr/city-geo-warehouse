import requests
import re

url = "https://rapidapi.com/search/numbeo"
html = requests.get(url, timeout=30).text
print(len(html))
if "__NEXT_DATA__" in html:
    start = html.index("__NEXT_DATA__")
    print("next data index", start)
else:
    print("__NEXT_DATA__ not found")
    scripts = re.findall(r'/hub/_next/static/[^"\\]+', html)
    print("static scripts", len(scripts))
