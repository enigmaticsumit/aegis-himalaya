"""Small SQLite helpers for inventory and saved mission plans."""

import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from .inventory import INVENTORY_ITEMS


def _database_path() -> Path:
    configured_path = os.environ.get("VEKTOR_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).with_name("vektor.db")


def initialize_database() -> None:
    """Create the tables and seed the fixed inventory without resetting stock."""
    database_path = _database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(database_path)) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                item_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                unit TEXT NOT NULL,
                stock INTEGER NOT NULL CHECK (stock >= 0)
            );
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                disaster_type TEXT NOT NULL,
                destination_json TEXT NOT NULL,
                route_json TEXT NOT NULL,
                supplies_json TEXT NOT NULL,
                mission_summary TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        connection.executemany(
            """
            INSERT OR IGNORE INTO inventory (item_id, name, unit, stock)
            VALUES (:item_id, :name, :unit, :stock)
            """,
            INVENTORY_ITEMS,
        )
        connection.commit()


def get_inventory() -> dict[str, dict[str, Any]]:
    with closing(sqlite3.connect(_database_path())) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT item_id, name, unit, stock FROM inventory ORDER BY rowid"
        ).fetchall()
    return {row["item_id"]: dict(row) for row in rows}


def save_mission(mission: dict[str, Any]) -> tuple[int, str]:
    created_at = mission["created_at"]
    with closing(sqlite3.connect(_database_path())) as connection:
        cursor = connection.execute(
            """
            INSERT INTO missions (
                location, disaster_type, destination_json, route_json,
                supplies_json, mission_summary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mission["location"],
                mission["disaster_type"],
                json.dumps(mission["destination"]),
                json.dumps(mission["route"]),
                json.dumps(mission["recommended_supplies"]),
                mission["mission_summary"],
                created_at,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid), created_at
