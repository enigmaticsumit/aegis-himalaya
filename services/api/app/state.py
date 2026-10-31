from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .models import LedgerEntry, Mission
from .paths import SEED


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class WorldState:
    def __init__(self) -> None:
        self.clock_hour = 0
        self.timeline = _load_json(SEED / "timeline.json")
        self.settlements_fc = _load_json(SEED / "settlements.geojson")
        self.warehouses_fc = _load_json(SEED / "warehouses.geojson")
        self.roads_fc = _load_json(SEED / "roads.geojson")
        self.damage_fc = _load_json(SEED / "damage.geojson")
        self.inventory_seed = _load_json(SEED / "inventory.json")["items"]
        self.vehicles_seed = _load_json(SEED / "vehicles.json")["vehicles"]
        self.weather = _load_json(SEED / "weather.json")["alerts"]
        self.citizen = _load_json(SEED / "citizen_reports.json")["reports"]
        self.road_reports = _load_json(SEED / "road_reports.json")["reports"]
        self.sources = {s["id"]: s for s in _load_json(SEED / "sources.json")["sources"]}
        self.inventory = copy.deepcopy(self.inventory_seed)
        self.vehicles = copy.deepcopy(self.vehicles_seed)
        self.missions: list[Mission] = []
        self.ledger: list[LedgerEntry] = []
        self.ranked: list[dict[str, Any]] = []
        self.isolated_ids: set[str] = set()
        self.briefing = "Agents have not run yet. Advance the clock or press Run agents."
        self.last_run: dict[str, Any] | None = None
        self.mission_seq = 0

    def reset(self) -> None:
        self.__init__()

    def next_mission_id(self) -> str:
        self.mission_seq += 1
        return f"msn-{self.mission_seq:03d}"

    def source(self, source_id: str) -> dict[str, Any]:
        return self.sources.get(source_id, {"id": source_id, "type": "unknown", "publisher": "unknown"})

    def active_weather(self) -> list[dict[str, Any]]:
        return [w for w in self.weather if w["valid_from_hour"] <= self.clock_hour]

    def active_citizen(self) -> list[dict[str, Any]]:
        return [c for c in self.citizen if c["valid_from_hour"] <= self.clock_hour]

    def active_road_reports(self) -> list[dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        for r in self.road_reports:
            if r["valid_from_hour"] <= self.clock_hour:
                prev = latest.get(r["road_id"])
                if prev is None or r["valid_from_hour"] >= prev["valid_from_hour"]:
                    latest[r["road_id"]] = r
        return list(latest.values())

    def active_damage_features(self) -> list[dict[str, Any]]:
        return [
            f
            for f in self.damage_fc["features"]
            if f["properties"]["valid_from_hour"] <= self.clock_hour
        ]

    def road_status_map(self) -> dict[str, str]:
        status = {f["properties"]["id"]: "open" for f in self.roads_fc["features"]}
        for r in self.active_road_reports():
            status[r["road_id"]] = r["status"]
        return status

    def settlement_by_id(self, sid: str) -> dict[str, Any]:
        for f in self.settlements_fc["features"]:
            if f["properties"]["id"] == sid:
                return f
        raise KeyError(sid)

    def warehouse_by_id(self, wid: str) -> dict[str, Any]:
        for f in self.warehouses_fc["features"]:
            if f["properties"]["id"] == wid:
                return f
        raise KeyError(wid)


WORLD = WorldState()
