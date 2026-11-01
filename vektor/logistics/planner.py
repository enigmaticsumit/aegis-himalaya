"""Build an explainable starter mission plan from rules and live route data."""

from datetime import datetime, timezone
from typing import Any

from . import database
from .inventory import DISASTER_RULES
from .routing import geocode_location, nearest_relief_hub, route_to_hub


def build_mission_plan(location: str, disaster_type: str) -> dict[str, Any]:
    cleaned_location = location.strip()
    origin = geocode_location(cleaned_location)
    destination = nearest_relief_hub(origin)
    route = route_to_hub(origin, destination)
    inventory = database.get_inventory()

    recommendations = []
    for item_id, requested_quantity in DISASTER_RULES[disaster_type].items():
        item = inventory[item_id]
        available_quantity = item["stock"]
        planned_quantity = min(requested_quantity, available_quantity)
        recommendations.append(
            {
                "item_id": item_id,
                "name": item["name"],
                "quantity": planned_quantity,
                "requested_quantity": requested_quantity,
                "available_quantity": available_quantity,
                "shortage": requested_quantity - planned_quantity,
                "unit": item["unit"],
            }
        )

    supply_count = len(recommendations)
    mission_summary = (
        f"{disaster_type.title()} response for {cleaned_location}: prepare "
        f"{supply_count} supply types and route to {destination['name']}."
    )
    return {
        "location": cleaned_location,
        "disaster_type": disaster_type,
        "destination": destination,
        "route": route,
        "recommended_supplies": recommendations,
        "mission_summary": mission_summary,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
