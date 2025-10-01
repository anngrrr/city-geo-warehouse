from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import folium
import geopandas as gpd
import osmnx as ox
from haversine import haversine
from shapely.geometry import LineString, Point

GeoDataFrame = gpd.GeoDataFrame
SingleFeatureTags = dict[str, str | list[str] | bool]
FeatureTags = dict[str, SingleFeatureTags]

logger = logging.getLogger(__name__)


@dataclass
class CityBoundary:
    geometry: GeoDataFrame
    center: tuple[float, float]
    name: str
    buffer_size: float = 0.0

    @classmethod
    def from_coordinates(cls, lat: float, lon: float, city_name: str, buffer_size: float = 0.1) -> CityBoundary:
        point = Point(lon, lat)
        geometry = gpd.GeoDataFrame(geometry=[point.buffer(buffer_size)], crs="EPSG:4326")
        return cls(geometry=geometry, center=(lat, lon), name=city_name, buffer_size=buffer_size)

    @classmethod
    def from_geodataframe(cls, gdf: GeoDataFrame, city_name: str) -> CityBoundary:
        if gdf.empty:
            raise ValueError("GeoDataFrame is empty")
        geometry = gdf.to_crs("EPSG:4326").geometry.iloc[0]
        centroid = geometry.centroid
        wrapped = gpd.GeoDataFrame(geometry=[geometry], crs="EPSG:4326")
        return cls(geometry=wrapped, center=(centroid.y, centroid.x), name=city_name)

    def with_buffer(self, buffer_size: float) -> CityBoundary:
        return CityBoundary.from_coordinates(self.center[0], self.center[1], self.name, buffer_size)


class NaturalFeatureAnalyzer:
    def __init__(self, cache: bool = True) -> None:
        ox.config(use_cache=cache, log_console=False)

    def _get_city_area(self, lat: float, lon: float, city_name: str) -> CityBoundary:
        try:
            city_gdf = ox.geocode_to_gdf(city_name)
            return CityBoundary.from_geodataframe(city_gdf, city_name)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Unable to fetch %s boundary from OSM, using %.1f deg buffer: %s",
                city_name,
                0.1,
                exc,
            )
            return CityBoundary.from_coordinates(lat, lon, city_name)

    def _find_nearest_feature(self, lat: float, lon: float, tags: SingleFeatureTags, city: CityBoundary) -> tuple[float, Optional[Point]]:
        try:
            search_polygon = city.geometry.geometry.iloc[0]
            features = ox.features_from_polygon(search_polygon, tags=tags)

            if features.empty:
                expanded_city = city.with_buffer(0.5)
                search_polygon = expanded_city.geometry.geometry.iloc[0]
                features = ox.features_from_polygon(search_polygon, tags=tags)

            if features.empty:
                return float("inf"), None

            distances: list[float] = []
            points: list[Point] = []
            center = (lat, lon)

            for _, feature in features.iterrows():
                feature_geom = feature.geometry
                if feature_geom.is_empty:
                    continue
                feature_point = feature_geom if feature_geom.geom_type == "Point" else feature_geom.centroid
                feature_coord = (feature_point.y, feature_point.x)
                distance = haversine(center, feature_coord)
                distances.append(distance)
                points.append(Point(feature_point.x, feature_point.y))

            if not distances:
                return float("inf"), None

            min_index = distances.index(min(distances))
            return distances[min_index], points[min_index]
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to locate nearby feature: %s", exc)
            return float("inf"), None

    def analyze_natural_features(self, lat: float, lon: float, city_name: str) -> dict[str, Optional[float]]:
        try:
            city = self._get_city_area(lat, lon, city_name)

            feature_tags: FeatureTags = {
                "water": {
                    "natural": ["water", "bay"],
                    "water": True,
                },
                "forest": {
                    "natural": "wood",
                    "landuse": ["forest", "nature_reserve"],
                },
                "mountain": {
                    "natural": ["peak", "mountain"],
                },
                "park": {
                    "leisure": "park",
                },
            }

            water_dist, nearest_water = self._find_nearest_feature(lat, lon, feature_tags["water"], city)
            forest_dist, nearest_forest = self._find_nearest_feature(lat, lon, feature_tags["forest"], city)
            mountain_dist, nearest_mountain = self._find_nearest_feature(lat, lon, feature_tags["mountain"], city)
            park_dist, nearest_park = self._find_nearest_feature(lat, lon, feature_tags["park"], city)

            max_forest_distance = 10
            forest_score = 0.0 if forest_dist == float("inf") else max(0.0, 100.0 * (1 - forest_dist / max_forest_distance))

            self._create_feature_map(
                lat,
                lon,
                city_name,
                [
                    (nearest_water, "blue", "Water"),
                    (nearest_forest, "green", "Forest"),
                    (nearest_mountain, "red", "Mountain"),
                    (nearest_park, "lightgreen", "Park"),
                ],
                city,
            )

            return {
                "distance_to_water": round(water_dist, 2) if water_dist != float("inf") else None,
                "distance_to_mountains": round(mountain_dist, 2) if mountain_dist != float("inf") else None,
                "distance_to_forest": round(forest_dist, 2) if forest_dist != float("inf") else None,
                "distance_to_park": round(park_dist, 2) if park_dist != float("inf") else None,
                "forest_proximity_score": round(forest_score, 2),
                "green_space_ratio": None,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Natural feature analysis failed: %s", exc)
            return {}

    def calculate_green_space_ratio(self, lat: float, lon: float, city_name: str) -> Optional[float]:
        try:
            city_boundary = self._get_city_area(lat, lon, city_name)
            city_geom = city_boundary.geometry

            green_tags: SingleFeatureTags = {
                "leisure": ["park", "garden"],
                "landuse": ["forest", "grass", "greenfield", "meadow"],
                "natural": ["wood", "grassland", "heath"],
            }

            green_spaces = ox.features_from_polygon(city_geom.geometry.iloc[0], tags=green_tags)
            if green_spaces.empty:
                return None

            projected_city = city_geom.to_crs("EPSG:3857")
            projected_green = green_spaces.to_crs("EPSG:3857")

            city_area = projected_city.geometry.iloc[0].area
            if city_area <= 0:
                return None

            green_area = projected_green.geometry.area.sum()
            ratio = min((green_area / city_area) * 100, 100)
            return round(ratio, 2)
        except Exception as exc:  # noqa: BLE001
            logger.error("Green space ratio calculation failed: %s", exc)
            return None

    def _create_feature_map(
        self,
        lat: float,
        lon: float,
        city_name: str,
        features: list[tuple[Optional[Point], str, str]],
        city: CityBoundary,
    ) -> None:
        try:
            base_map = folium.Map(location=[lat, lon], zoom_start=11)

            folium.GeoJson(
                city.geometry.geometry.iloc[0].__geo_interface__,
                style_function=lambda _: {"color": "gray", "fillOpacity": 0.1},
            ).add_to(base_map)

            folium.Marker(
                [lat, lon],
                popup=f"{city_name} centre",
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(base_map)

            for feature_point, color, label in features:
                if feature_point is None:
                    continue
                folium.Marker(
                    [feature_point.y, feature_point.x],
                    popup=f"Nearest {label}",
                    icon=folium.Icon(color=color),
                ).add_to(base_map)
                line = LineString([(lon, lat), (feature_point.x, feature_point.y)])
                folium.GeoJson(
                    line.__geo_interface__,
                    style_function=lambda _: {"color": color, "weight": 2, "dashArray": "5, 5"},
                ).add_to(base_map)

            output_file = f"natural_features_{city_name.lower().replace(' ', '_')}.html"
            base_map.save(output_file)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to build natural feature map: %s", exc)
