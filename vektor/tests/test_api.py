import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from logistics.database import get_inventory
from logistics.main import app
from logistics.routing import (
    LocationNotFoundError,
    RoutingError,
    geocode_location,
    route_to_hub,
)


class PlanApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = os.path.join(self.temp_directory.name, "test.sqlite3")
        self.environment = patch.dict(os.environ, {"VEKTOR_DB_PATH": self.database_path})
        self.environment.start()
        self.geocode_patch = patch(
            "logistics.planner.geocode_location",
            return_value={"latitude": 28.6, "longitude": 77.2},
        )
        self.route_patch = patch(
            "logistics.planner.route_to_hub",
            return_value={
                "origin": {"latitude": 28.6, "longitude": 77.2},
                "distance_m": 12000.0,
                "duration_s": 1800.0,
                "geometry": [[28.6, 77.2], [28.61, 77.21]],
            },
        )
        self.geocode_patch.start()
        self.route_patch.start()
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.route_patch.stop()
        self.geocode_patch.stop()
        self.environment.stop()
        self.temp_directory.cleanup()

    def test_plan_returns_supplies_route_and_saves_mission(self) -> None:
        response = self.client.post(
            "/plan",
            json={"location": "New Delhi, India", "disaster_type": "flood"},
        )

        self.assertEqual(response.status_code, 200)
        plan = response.json()
        self.assertEqual(plan["disaster_type"], "flood")
        self.assertEqual(plan["destination"]["name"], "Delhi Relief Hub")
        self.assertEqual(plan["recommended_supplies"][0]["item_id"], "water")
        self.assertEqual(plan["recommended_supplies"][0]["quantity"], 300)
        self.assertEqual(plan["route"]["distance_m"], 12000.0)
        self.assertIn("Flood response", plan["mission_summary"])
        self.assertGreater(plan["id"], 0)

    def test_unknown_disaster_type_is_rejected(self) -> None:
        response = self.client.post(
            "/plan",
            json={"location": "New Delhi, India", "disaster_type": "meteor"},
        )

        self.assertEqual(response.status_code, 422)

    def test_inventory_has_ten_fixed_items(self) -> None:
        self.assertEqual(len(get_inventory()), 10)

    def test_map_page_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("leaflet", response.text.lower())

    def test_location_not_found_is_reported(self) -> None:
        with patch(
            "logistics.planner.geocode_location",
            side_effect=LocationNotFoundError("Location not found."),
        ):
            response = self.client.post(
                "/plan",
                json={"location": "Nowhere", "disaster_type": "flood"},
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Location not found.")

    def test_routing_service_failure_is_reported(self) -> None:
        with patch(
            "logistics.planner.route_to_hub",
            side_effect=RoutingError("OSRM is unavailable."),
        ):
            response = self.client.post(
                "/plan",
                json={"location": "New Delhi, India", "disaster_type": "flood"},
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "OSRM is unavailable.")

    def test_geocoder_converts_openstreetmap_coordinates(self) -> None:
        with patch(
            "logistics.routing._get_json",
            return_value=[{"lat": "28.6", "lon": "77.2"}],
        ):
            location = geocode_location("New Delhi")

        self.assertEqual(location, {"latitude": 28.6, "longitude": 77.2})

    def test_osrm_route_converts_geojson_for_leaflet(self) -> None:
        osrm_response = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 1000,
                    "duration": 120,
                    "geometry": {"coordinates": [[77.2, 28.6], [77.3, 28.7]]},
                }
            ],
        }
        with patch("logistics.routing._get_json", return_value=osrm_response):
            route = route_to_hub(
                {"latitude": 28.6, "longitude": 77.2},
                {"latitude": 28.7, "longitude": 77.3},
            )

        self.assertEqual(route["geometry"], [[28.6, 77.2], [28.7, 77.3]])
        self.assertEqual(route["distance_m"], 1000.0)


if __name__ == "__main__":
    unittest.main()
