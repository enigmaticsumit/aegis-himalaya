from __future__ import annotations

from typing import Any

from ..graph_engine import annotate_settlements, build_graph, vehicle_features
from ..models import Mission, MissionNeed
from ..state import WorldState, WORLD
from .briefing import summarize_briefing
from .damage import assess_damage
from .ingest import ingest
from .logistics import allocate, take_stock
from .priority import prioritize


def run_agents(world: WorldState | None = None) -> dict[str, Any]:
    world = world or WORLD
    ingested = ingest(world)
    g = assess_damage(world)
    ranked = prioritize(world, g)
    stats = allocate(world, g, ranked)

    isolated_n = sum(1 for r in ranked if r["isolated"])
    names = ", ".join(r["name"] for r in ranked if r["isolated"])
    wx = world.active_weather()
    wx_line = wx[-1]["headline"] if wx else "No weather alerts."
    facts = {
        "hour": world.clock_hour,
        "isolated": isolated_n,
        "isolated_names": names or "none",
        "weather": wx_line,
        "proposed": stats["proposed"],
        "replanned": stats["replanned"],
        "ingested": ingested,
        "top": [r["name"] for r in ranked[:5]],
    }
    world.briefing = summarize_briefing(facts)
    world.last_run = {
        "hour": world.clock_hour,
        "isolated": isolated_n,
        "proposed": stats["proposed"],
        "replanned": stats["replanned"],
        "ingested": ingested,
        "ranked_top": facts["top"],
    }
    return {"briefing": world.briefing, "last_run": world.last_run, "ranked": ranked}


def situation_payload(world: WorldState | None = None) -> dict[str, Any]:
    world = world or WORLD
    g = build_graph(world)
    ranked = world.ranked or annotate_settlements(world, g)
    rank_map = {r["id"]: r for r in ranked}
    status = world.road_status_map()

    settlements = {
        "type": "FeatureCollection",
        "features": [
            {
                **feat,
                "properties": {
                    **feat["properties"],
                    **{
                        k: rank_map[feat["properties"]["id"]][k]
                        for k in ("isolated", "priority_score", "needs", "hazard_ids", "at_risk")
                        if feat["properties"]["id"] in rank_map and k in rank_map[feat["properties"]["id"]]
                    },
                },
            }
            for feat in world.settlements_fc["features"]
        ],
    }
    roads = {
        "type": "FeatureCollection",
        "features": [
            {
                **feat,
                "properties": {**feat["properties"], "status": status.get(feat["properties"]["id"], "open")},
            }
            for feat in world.roads_fc["features"]
        ],
    }
    damage = {"type": "FeatureCollection", "features": world.active_damage_features()}
    return {
        "clock_hour": world.clock_hour,
        "event": world.timeline,
        "settlements": settlements,
        "roads": roads,
        "warehouses": world.warehouses_fc,
        "damage": damage,
        "vehicles_geo": vehicle_features(world),
        "ranked": ranked,
        "missions": world.missions,
        "inventory": world.inventory,
        "vehicles": world.vehicles,
        "weather": world.active_weather(),
        "briefing": world.briefing,
        "last_run": world.last_run,
        "ledger_size": len(world.ledger),
    }


def authorize_mission(mission_id: str, decision: str, actor: str, reason: str) -> Mission:
    world = WORLD
    mission = next((m for m in world.missions if m.id == mission_id), None)
    if mission is None:
        raise KeyError(mission_id)
    if mission.status != "proposed":
        raise ValueError(f"Mission {mission_id} is {mission.status}, not proposed")

    if decision == "authorized":
        if mission.warehouse_id:
            allocated = take_stock(
                world,
                mission.warehouse_id,
                {n.sku: n.qty for n in mission.needs},
            )
            mission.needs = [MissionNeed(sku=k, qty=v) for k, v in allocated.items() if v > 0]
        if mission.vehicle_id:
            for v in world.vehicles:
                if v["id"] == mission.vehicle_id and v["status"] == "available":
                    v["status"] = "assigned"
        mission.status = "authorized"
    else:
        mission.status = "rejected"

    mission.authorization = {
        "actor": actor,
        "decision": decision,
        "reason": reason,
        "at_hour": world.clock_hour,
    }
    return mission
