"""Geocoding with OpenStreetMap Nominatim and driving routes with OSRM."""

import json
import math
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .inventory import RELIEF_HUBS

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
REQUEST_TIMEOUT_SECONDS = 12


class RoutingError(Exception):
    """Raised when a geocoding or routing service cannot provide a route."""


class LocationNotFoundError(Exception):
    """Raised when OpenStreetMap cannot find the requested location."""


def _get_json(url: str) -> Any:
    user_agent = os.environ.get(
        "VEKTOR_USER_AGENT", "VEKTOR-Logistics-Brain/1.0"
    )
    request = Request(url, headers={"User-Agent": user_agent})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RoutingError(f"Mapping service returned HTTP {error.code}.") from error
    except (URLError, TimeoutError) as error:
        reason = error.reason if isinstance(error, URLError) else error
        raise RoutingError(f"Could not reach a mapping service: {reason}.") from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RoutingError("Mapping service returned invalid JSON.") from error


def geocode_location(location: str) -> dict[str, float]:
    query = urlencode({"q": location, "format": "jsonv2", "limit": 1})
    results = _get_json(f"{NOMINATIM_URL}?{query}")
    if not results:
        raise LocationNotFoundError(f"OpenStreetMap could not find '{location}'.")
    try:
        return {
            "latitude": float(results[0]["lat"]),
            "longitude": float(results[0]["lon"]),
        }
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise RoutingError("OpenStreetMap returned an invalid location.") from error


def _distance_km(first: dict[str, float], second: dict[str, Any]) -> float:
    earth_radius_km = 6371
    first_latitude = math.radians(first["latitude"])
    second_latitude = math.radians(float(second["latitude"]))
    latitude_delta = second_latitude - first_latitude
    longitude_delta = math.radians(float(second["longitude"])) - math.radians(
        first["longitude"]
    )
    haversine = (
        math.sin(latitude_delta / 2) ** 2
        + math.cos(first_latitude)
        * math.cos(second_latitude)
        * math.sin(longitude_delta / 2) ** 2
    )
    return 2 * earth_radius_km * math.asin(math.sqrt(haversine))


def nearest_relief_hub(origin: dict[str, float]) -> dict[str, Any]:
    return min(
        RELIEF_HUBS,
        key=lambda hub: _distance_km(origin, hub),
    )


def route_to_hub(
    origin: dict[str, float], destination: dict[str, Any]
) -> dict[str, Any]:
    coordinates = (
        f"{origin['longitude']},{origin['latitude']};"
        f"{destination['longitude']},{destination['latitude']}"
    )
    query = urlencode({"overview": "full", "geometries": "geojson"})
    result = _get_json(f"{OSRM_URL}/{coordinates}?{query}")
    try:
        if result["code"] != "Ok" or not result["routes"]:
            raise RoutingError("OSRM could not find a driving route.")
        route = result["routes"][0]
        geometry = route["geometry"]["coordinates"]
        return {
            "origin": origin,
            "distance_m": float(route["distance"]),
            "duration_s": float(route["duration"]),
            "geometry": [
                [float(latitude), float(longitude)]
                for longitude, latitude in geometry
            ],
        }
    except RoutingError:
        raise
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise RoutingError("OSRM returned an invalid route.") from error
