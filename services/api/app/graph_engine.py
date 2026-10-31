from __future__ import annotations

from typing import Any

import networkx as nx

from .geo import point_in_any_polygon
from .state import WorldState


def build_graph(world: WorldState) -> nx.Graph:
    g = nx.Graph()
    for feat in world.settlements_fc["features"]:
        p = feat["properties"]
        g.add_node(p["id"], kind="settlement", **p, lon=feat["geometry"]["coordinates"][0], lat=feat["geometry"]["coordinates"][1])
    for feat in world.warehouses_fc["features"]:
        p = feat["properties"]
        g.add_node(p["id"], kind="warehouse", **p)
        g.add_edge(p["id"], p["settlement_id"], road_id=f"wh-link-{p['id']}", length_km=0.2, status="open", name="depot spur")

    status = world.road_status_map()
    for feat in world.roads_fc["features"]:
        p = feat["properties"]
        st = status.get(p["id"], "open")
        if st == "blocked":
            continue
        weight = p["length_km"] * (2.5 if st == "degraded" else 1.0)
        g.add_edge(
            p["from"],
            p["to"],
            road_id=p["id"],
            length_km=p["length_km"],
            weight=weight,
            status=st,
            name=p["name"],
        )
    return g


def warehouse_ids(world: WorldState) -> list[str]:
    return [f["properties"]["id"] for f in world.warehouses_fc["features"]]


def reachable_from_warehouses(g: nx.Graph, world: WorldState) -> set[str]:
    reachable: set[str] = set()
    for wid in warehouse_ids(world):
        if wid not in g:
            continue
        reachable |= set(nx.node_connected_component(g, wid))
    return reachable


def shortest_path_to_warehouse(
    g: nx.Graph, world: WorldState, settlement_id: str
) -> tuple[str | None, list[str], list[str], float]:
    best: tuple[str | None, list[str], list[str], float] = (None, [], [], 1e9)
    for wid in warehouse_ids(world):
        if wid not in g or settlement_id not in g:
            continue
        if not nx.has_path(g, wid, settlement_id):
            continue
        path = nx.shortest_path(g, wid, settlement_id, weight="weight")
        dist = 0.0
        roads: list[str] = []
        for a, b in zip(path, path[1:]):
            data = g.edges[a, b]
            dist += float(data.get("length_km", 0))
            roads.append(data.get("road_id", ""))
        if dist < best[3]:
            best = (wid, path, roads, dist)
    if best[0] is None:
        return (None, [], [], 0.0)
    return best


def annotate_settlements(world: WorldState, g: nx.Graph) -> list[dict[str, Any]]:
    reachable = reachable_from_warehouses(g, world)
    damage = world.active_damage_features()
    citizens = world.active_citizen()
    by_set: dict[str, list[dict[str, Any]]] = {}
    for c in citizens:
        by_set.setdefault(c["settlement_id"], []).append(c)

    max_pop = max(f["properties"]["population"] for f in world.settlements_fc["features"])
    ranked: list[dict[str, Any]] = []

    for feat in world.settlements_fc["features"]:
        p = feat["properties"]
        lon, lat = feat["geometry"]["coordinates"]
        isolated = p["id"] not in reachable
        hits = point_in_any_polygon(lon, lat, damage)
        hazard = 1.0 if hits else 0.35
        pop_n = (p["population"] ** 0.5) / (max_pop ** 0.5)
        contact_n = min(p["hours_since_contact"] / 24.0, 1.0)
        alt_n = min(p["altitude_m"] / 3200.0, 1.0)
        vuln = 0.4 * p["elderly_pct"] / 0.26 + 0.3 * alt_n + 0.3 * contact_n
        iso_f = 1.0 if isolated else 0.42
        if hits:
            iso_f = max(iso_f, 0.8)
        score = round(100 * iso_f * (0.34 * pop_n + 0.36 * min(vuln, 1.2) + 0.30 * hazard), 1)

        food = max(6, int(p["population"] / 5)) if isolated or hits else max(4, int(p["population"] / 18))
        tarps = 8 if hits else (4 if isolated else 0)
        if hits:
            tarps = max(tarps, int(hits[0]["properties"].get("estimated_structures_damaged", 8)))
        med = 3 if isolated or hits or p["id"] in by_set else 1

        ranked.append(
            {
                "id": p["id"],
                "name": p["name"],
                "population": p["population"],
                "isolated": isolated,
                "priority_score": score,
                "hazard_ids": [h["properties"]["id"] for h in hits],
                "citizen_ids": [c["id"] for c in by_set.get(p["id"], [])],
                "needs": {
                    "food_kit": food,
                    "tarp": tarps,
                    "medicine_kit": med,
                },
                "lon": lon,
                "lat": lat,
                "elderly_pct": p["elderly_pct"],
                "altitude_m": p["altitude_m"],
                "hours_since_contact": p["hours_since_contact"],
            }
        )
    ranked.sort(key=lambda r: r["priority_score"], reverse=True)
    return ranked
