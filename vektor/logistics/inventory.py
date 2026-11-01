"""The starter inventory and simple disaster-specific quantities."""

INVENTORY_ITEMS = (
    {"item_id": "water", "name": "Bottled water", "unit": "bottles", "stock": 1200},
    {"item_id": "food", "name": "Food rations", "unit": "meals", "stock": 600},
    {"item_id": "first_aid", "name": "First-aid kits", "unit": "kits", "stock": 100},
    {"item_id": "blankets", "name": "Thermal blankets", "unit": "blankets", "stock": 300},
    {"item_id": "tents", "name": "Family tents", "unit": "tents", "stock": 120},
    {"item_id": "hygiene", "name": "Hygiene kits", "unit": "kits", "stock": 200},
    {
        "item_id": "water_purification",
        "name": "Water purification tablets",
        "unit": "tablets",
        "stock": 2400,
    },
    {"item_id": "masks", "name": "Protective masks", "unit": "masks", "stock": 1000},
    {"item_id": "rescue_rope", "name": "Rescue rope", "unit": "ropes", "stock": 80},
    {"item_id": "flashlights", "name": "Flashlights", "unit": "lights", "stock": 180},
)

# Quantities are starter estimates for one response, not medical or operational advice.
DISASTER_RULES = {
    "flood": {
        "water": 300,
        "food": 120,
        "first_aid": 15,
        "blankets": 40,
        "hygiene": 30,
        "water_purification": 600,
        "rescue_rope": 15,
        "flashlights": 30,
    },
    "earthquake": {
        "water": 200,
        "food": 100,
        "first_aid": 20,
        "blankets": 50,
        "tents": 20,
        "hygiene": 30,
        "water_purification": 400,
        "masks": 100,
        "rescue_rope": 10,
        "flashlights": 30,
    },
    "wildfire": {
        "water": 150,
        "food": 80,
        "first_aid": 12,
        "blankets": 20,
        "tents": 10,
        "hygiene": 15,
        "masks": 300,
        "flashlights": 10,
    },
    "cyclone": {
        "water": 250,
        "food": 120,
        "first_aid": 15,
        "blankets": 40,
        "tents": 20,
        "hygiene": 25,
        "water_purification": 500,
        "masks": 50,
        "rescue_rope": 12,
        "flashlights": 25,
    },
    "landslide": {
        "water": 160,
        "food": 80,
        "first_aid": 20,
        "blankets": 30,
        "tents": 10,
        "hygiene": 15,
        "masks": 80,
        "rescue_rope": 20,
        "flashlights": 25,
    },
}

# Example relief hubs. Replace these with verified, operational locations before deployment.
RELIEF_HUBS = (
    {"name": "Delhi Relief Hub", "latitude": 28.6139, "longitude": 77.2090},
    {"name": "Jaipur Relief Hub", "latitude": 26.9124, "longitude": 75.7873},
    {"name": "Lucknow Relief Hub", "latitude": 26.8467, "longitude": 80.9462},
)
