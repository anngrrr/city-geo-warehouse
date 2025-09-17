import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
GEODB_API_KEY = os.getenv('GEODB_API_KEY')

# API endpoints
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
GEODB_BASE_URL = "https://wft-geo-db.p.rapidapi.com/v1/geo"
TELEPORT_BASE_URL = "https://api.teleport.org/api/urban_areas"

# API configuration
API_TIMEOUT = 30  # seconds
RATE_LIMIT_DELAY = 1  # seconds between API calls
