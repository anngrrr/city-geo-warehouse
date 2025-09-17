import json
import re

import requests


def fetch_search(query: str) -> list[dict]:
    url = f"https://rapidapi.com/search/{query}"
    html = requests.get(url, timeout=30).text
    match = re.search(r'__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not match:
        return []
    data = json.loads(match.group(1))
    try:
        items = data["props"]["pageProps"]["searchResults"]["items"]
    except Exception:  # noqa: BLE001
        return []
    results = []
    for item in items:
        content = item.get("content", {})
        results.append(
            {
                "title": content.get("title") or content.get("name"),
                "slug": content.get("slug") or content.get("id"),
                "description": content.get("description"),
                "categories": content.get("categories"),
            }
        )
    return results


def main():
    for query in ("quality%20of%20life", "city%20data", "education%20index", "safety%20city", "transport%20city", "cost%20of%20living"):
        print("===", query.replace('%20', ' '), "===")
        for result in fetch_search(query)[:5]:
            title = result["title"] or "<no title>"
            print(title)
            if result["slug"]:
                print(" slug:", result["slug"])
            if result["description"]:
                print(" desc:", result["description"][:180])
            if result["categories"]:
                print(" categories:", result["categories"])
            print("-" * 40)
        print()


if __name__ == "__main__":
    main()
