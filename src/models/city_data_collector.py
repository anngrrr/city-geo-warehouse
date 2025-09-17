import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests
from pyowm import OWM
from pyowm.commons.exceptions import APIRequestError, NotFoundError

from src.config.api_config import (
    API_TIMEOUT,
    GEODB_API_KEY,
    GEODB_BASE_URL,
    OPENWEATHER_API_KEY,
    RATE_LIMIT_DELAY,
    TELEPORT_BASE_URL,
)
from src.models.natural_features import NaturalFeatureAnalyzer

logger = logging.getLogger(__name__)


class CityDataCollector:
    """Collects city metrics from external APIs."""

    def __init__(self) -> None:
        if not OPENWEATHER_API_KEY:
            raise ValueError("OPENWEATHER_API_KEY is not configured. Add it to .env")
        if not GEODB_API_KEY:
            raise ValueError("GEODB_API_KEY is not configured. Add it to .env")

        self.owm = OWM(OPENWEATHER_API_KEY)
        self.geodb_headers = {
            "X-RapidAPI-Key": GEODB_API_KEY,
            "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com",
        }
        self.natural_analyzer = NaturalFeatureAnalyzer()

    @staticmethod
    def _apply_rate_limit() -> None:
        if RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY)

    @staticmethod
    def _slugify_city_name(city_name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", city_name.lower()).strip("-")
        return slug or city_name.lower()

    @staticmethod
    def _resolve_country_code(country: str) -> Optional[str]:
        if len(country) == 2 and country.isalpha():
            return country.upper()
        return None

    def _safe_get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[requests.Response]:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            self._apply_rate_limit()
            return response
        except requests.RequestException as exc:
            logger.error("Request failed %s: %s", url, exc)
            return None

    def get_basic_city_info(self, city_name: str, country: str) -> Dict[str, Any]:
        """Basic city info from GeoDB Cities."""
        params: Dict[str, Any] = {"namePrefix": city_name, "limit": 1}
        if country_code := self._resolve_country_code(country):
            params["countryIds"] = country_code

        response = self._safe_get(f"{GEODB_BASE_URL}/cities", headers=self.geodb_headers, params=params)
        if response is None:
            return {}

        payload = response.json()
        if not payload.get("data"):
            logger.warning("GeoDB did not return a match for %s (%s)", city_name, country)
            return {}

        city_data = payload["data"][0]
        return {
            "city_id": city_data.get("id"),
            "latitude": city_data.get("latitude"),
            "longitude": city_data.get("longitude"),
            "population": city_data.get("population"),
            "region": city_data.get("region"),
            "country_code": city_data.get("countryCode"),
        }

    def get_city_details(self, city_name: str) -> tuple[Optional[str], Dict[str, Any]]:
        """Urban area details from Teleport."""
        slug = self._slugify_city_name(city_name)
        url = f"{TELEPORT_BASE_URL}/slug:{slug}"
        response = self._safe_get(url)
        if response is None:
            return None, {}
        return url, response.json()

    def get_quality_of_life_metrics(self, city_name: str) -> Dict[str, Any]:
        """Quality-of-life and economy metrics from Teleport."""
        try:
            url, _ = self.get_city_details(city_name)
            if not url:
                return {}

            scores_response = self._safe_get(f"{url}/scores")
            details_response = self._safe_get(f"{url}/details")
            if scores_response is None or details_response is None:
                return {}

            scores_data = scores_response.json()
            details_data = details_response.json()

            categories = {
                category["name"]: category.get("score_out_of_10", 0)
                for category in scores_data.get("categories", [])
            }

            def _extract_section(section_id: str) -> Dict[str, Any]:
                return next(
                    (section for section in details_data.get("categories", []) if section.get("id") == section_id),
                    {},
                )

            salary_data = _extract_section("SALARY")
            economy_data = _extract_section("ECONOMY")
            housing_data = _extract_section("HOUSING")

            median_salary = next(
                (item.get("median_value") for item in salary_data.get("data", []) if item.get("id") == "DEVELOPER-SALARY"),
                None,
            )
            gdp_growth = next(
                (item.get("float_value") for item in economy_data.get("data", []) if item.get("id") == "GDP-GROWTH-RATE"),
                None,
            )
            rent_index = next(
                (item.get("currency_dollar_value") for item in housing_data.get("data", []) if item.get("id") == "APARTMENT-RENT-LARGE"),
                None,
            )

            return {
                "happiness_index": categories.get("Housing", 0) * 10,
                "health_index": categories.get("Healthcare", 0) * 10,
                "traffic_congestion_score": 100 - (categories.get("Commute", 0) * 10),
                "education_level_score": categories.get("Education", 0) * 10,
                "cultural_events_per_capita": categories.get("Culture", 0) * 10,
                "sports_facilities_per_capita": categories.get("Outdoors", 0) * 10,
                "green_space_ratio": categories.get("Environmental Quality", 0) * 10,
                "cost_of_living_index": categories.get("Cost of Living", 0) * 10,
                "housing_price_index": categories.get("Housing", 0) * 10,
                "economic_growth_rate": gdp_growth,
                "average_salary": median_salary,
                "rent_price_index": rent_index,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Teleport metrics fetch failed: %s", exc)
            return {}

    def get_environmental_metrics(self, lat: float, lon: float) -> Dict[str, Any]:
        """Weather and air-quality metrics from OpenWeatherMap."""
        try:
            weather_manager = self.owm.weather_manager()
            observation = weather_manager.weather_at_coords(lat, lon)
            weather = observation.weather

            air_quality_index: Optional[int] = None
            try:
                air_manager = self.owm.airpollution_manager()
                air_quality = air_manager.air_quality_at_coords(lat, lon)
                air_quality_index = getattr(air_quality, "aqi", None)
            except (APIRequestError, NotFoundError) as air_exc:
                logger.warning("OpenWeather air quality unavailable: %s", air_exc)

            return {
                "wind_speed_avg": (weather.wind().get("speed") if weather.wind() else None),
                "air_quality_index": air_quality_index,
                "temperature": weather.temperature("celsius").get("temp"),
                "humidity": weather.humidity,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenWeather metrics fetch failed: %s", exc)
            return {}

    def get_detailed_city_info(self, city_id: str) -> Dict[str, Any]:
        """Detailed city info from GeoDB Cities."""
        response = self._safe_get(f"{GEODB_BASE_URL}/cities/{city_id}/details", headers=self.geodb_headers)
        if response is None:
            return {}
        return response.json().get("data", {})

    def collect_all_city_data(self, city_name: str, country: str) -> Dict[str, Any]:
        """Aggregate data from all available sources."""
        basic_info = self.get_basic_city_info(city_name, country)
        if not basic_info:
            logger.error("Unable to obtain base info for %s, %s", city_name, country)
            return {}

        lat = basic_info.get("latitude")
        lon = basic_info.get("longitude")
        city_id = basic_info.get("city_id")

        detailed_info = self.get_detailed_city_info(city_id) if city_id else {}
        qol_metrics = self.get_quality_of_life_metrics(city_name)
        env_metrics = self.get_environmental_metrics(lat, lon) if lat is not None and lon is not None else {}

        logger.info("Analysing natural features for %s", city_name)
        natural_features = (
            self.natural_analyzer.analyze_natural_features(lat, lon, city_name)
            if lat is not None and lon is not None
            else {}
        )
        if lat is not None and lon is not None:
            green_space_ratio = self.natural_analyzer.calculate_green_space_ratio(lat, lon, city_name)
            if green_space_ratio is not None:
                natural_features["green_space_ratio"] = green_space_ratio

        return {
            "city_name": city_name,
            "country": country,
            "timestamp": datetime.now(timezone.utc),
            "population": basic_info.get("population"),
            "latitude": lat,
            "longitude": lon,
            "region": basic_info.get("region"),
            "elevation": detailed_info.get("elevation"),
            "timezone": detailed_info.get("timezone"),
            "happiness_index": qol_metrics.get("happiness_index"),
            "health_index": qol_metrics.get("health_index"),
            "cost_of_living_index": qol_metrics.get("cost_of_living_index"),
            "housing_price_index": qol_metrics.get("housing_price_index"),
            "traffic_congestion_score": qol_metrics.get("traffic_congestion_score"),
            "education_level_score": qol_metrics.get("education_level_score"),
            "cultural_events_per_capita": qol_metrics.get("cultural_events_per_capita"),
            "sports_facilities_per_capita": qol_metrics.get("sports_facilities_per_capita"),
            "economic_growth_rate": qol_metrics.get("economic_growth_rate"),
            "average_salary": qol_metrics.get("average_salary"),
            "rent_price_index": qol_metrics.get("rent_price_index"),
            "wind_speed_avg": env_metrics.get("wind_speed_avg"),
            "air_quality_index": env_metrics.get("air_quality_index"),
            "temperature": env_metrics.get("temperature"),
            "humidity": env_metrics.get("humidity"),
            "distance_to_water": natural_features.get("distance_to_water"),
            "distance_to_mountains": natural_features.get("distance_to_mountains"),
            "distance_to_forest": natural_features.get("distance_to_forest"),
            "distance_to_park": natural_features.get("distance_to_park"),
            "forest_proximity_score": natural_features.get("forest_proximity_score"),
            "green_space_ratio": natural_features.get("green_space_ratio"),
        }
