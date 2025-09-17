import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def show(title: str, response: requests.Response) -> None:
    print(f"--- {title} ---")
    print('Status:', response.status_code)
    if response.headers.get('content-type', '').startswith('application/json'):
        try:
            data = response.json()
        except Exception as exc:  # noqa: BLE001
            print('JSON parse error:', exc)
            print(response.text[:500])
        else:
            snippet = json.dumps(data, ensure_ascii=False, indent=2)
            print(snippet[:800])
    else:
        print(response.text[:500])
    print()


def test_geodb() -> None:
    key = os.getenv('GEODB_API_KEY')
    if not key:
        print('GEODB_API_KEY not set')
        return
    try:
        response = requests.get(
            'https://wft-geo-db.p.rapidapi.com/v1/geo/cities',
            headers={
                'X-RapidAPI-Key': key,
                'X-RapidAPI-Host': 'wft-geo-db.p.rapidapi.com',
            },
            params={'namePrefix': 'Berlin', 'countryIds': 'DE', 'limit': 1},
            timeout=30,
        )
    except Exception as exc:  # noqa: BLE001
        print('GeoDB request failed:', exc)
    else:
        show('GeoDB cities', response)


def test_teleport() -> None:
    try:
        response = requests.get(
            'https://api.teleport.org/api/urban_areas/slug:berlin/details',
            timeout=30,
        )
    except Exception as exc:  # noqa: BLE001
        print('Teleport request failed:', exc)
    else:
        show('Teleport details', response)


def test_openweather() -> None:
    key = os.getenv('OPENWEATHER_API_KEY')
    if not key:
        print('OPENWEATHER_API_KEY not set')
        return
    try:
        response = requests.get(
            'https://api.openweathermap.org/data/2.5/weather',
            params={'q': 'Berlin,DE', 'appid': key, 'units': 'metric'},
            timeout=30,
        )
    except Exception as exc:  # noqa: BLE001
        print('OpenWeather request failed:', exc)
    else:
        show('OpenWeather current weather', response)


def main() -> None:
    test_geodb()
    test_teleport()
    test_openweather()


if __name__ == '__main__':
    main()
