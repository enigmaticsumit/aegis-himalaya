from __future__ import annotations

from typing import Any

import networkx as nx

from ..graph_engine import shortest_path_to_warehouse
from ..models import Evidence, Mission, MissionNeed
from ..state import WorldState


def _evidence_for(world: WorldState, row: dict[str, Any], road_ids: list[str]) -> list[Evidence]:
    items: list[Evidence] = []
    for hid in row["hazard_ids"]:
        feat = next(f for f in world.active_damage_features() if f["properties"]["id"] == hid)
        src = feat["properties"]["source_id"]
        s = world.source(src)
        items.append(
            Evidence(
                source_id=src,
                role=f"satellite:{feat['properties']['hazard']}",
                snippet=f"{s.get('publisher')}: {feat['properties']['summary']}",
            )
        )
    for cid in row["citizen_ids"]:
        c = next(x for x in world.active_citizen() if x["id"] == cid)
        s = world.source(c["source_id"])
        items.append(
            Evidence(
                source_id=c["source_id"],
                role="citizen",
                snippet=f"{s.get('publisher')}: {c['text']}",
            )
        )
    for rr in world.active_road_reports():
        if rr["road_id"] in road_ids:
            s = world.source(rr["source_id"])
            items.append(
                Evidence(
                    source_id=rr["source_id"],
                    role=f"road:{rr['status']}",
                    snippet=f"{s.get('publisher')}: {rr['detail']}",
                )
            )
    for w in world.active_weather():
        s = world.source(w["source_id"])
        items.append(
            Evidence(
                source_id=w["source_id"],
                role=f"weather:{w['severity']}",
                snippet=f"{s.get('publisher')}: {w['headline']}",
            )
        )
    if row.get("at_risk") and "rd-maneri-bhatwari" in road_ids:
        s = world.source("src-wx-imd")
        items.append(
            Evidence(
                source_id="src-wx-imd",
                role="weather:corridor-risk",
                snippet=f"{s.get('publisher')}: single-highway catchment; pre-position before further slope failure.",
            )
        )
    seen: set[str] = set()
    uniq: list[Evidence] = []
    for e in items:
        key = f"{e.source_id}:{e.role}"
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)
    return uniq[:8]


def _inventory_evidence(world: WorldState, warehouse_id: str | None) -> list[Evidence]:
    if not warehouse_id:
        return []
    for item in world.inventory:
        if item["warehouse_id"] == warehouse_id:
            s = world.source(item["source_id"])
            return [
                Evidence(
                    source_id=item["source_id"],
                    role="inventory",
                    snippet=f"{s.get('publisher')}: verified stock at {warehouse_id}.",
                )
            ]
    return []


def _take_stock(world: WorldState, warehouse_id: str, needs: dict[str, int]) -> dict[str, int]:
    allocated: dict[str, int] = {}
    for sku, qty in needs.items():
        if qty <= 0:
            continue
        for item in world.inventory:
            if item["warehouse_id"] == warehouse_id and item["sku"] == sku:
                take = min(qty, item["qty"])
                item["qty"] -= take
                allocated[sku] = take
                break
    return allocated


def restore_stock(world: WorldState, warehouse_id: str, needs: list[MissionNeed]) -> None:
    for n in needs:
        for item in world.inventory:
            if item["warehouse_id"] == warehouse_id and item["sku"] == n.sku:
                item["qty"] += n.qty


def _claimed_vehicles(world: WorldState) -> set[str]:
    return {
        m.vehicle_id
        for m in world.missions
        if m.vehicle_id and m.status in ("proposed", "authorized", "in_transit")
    }


def _pick_vehicle(world: WorldState, warehouse_id: str, load: int) -> dict[str, Any] | None:
    claimed = _claimed_vehicles(world)
    candidates = [
        v
        for v in world.vehicles
        if v["status"] == "available"
        and v["base_warehouse_id"] == warehouse_id
        and v["id"] not in claimed
    ]
    candidates.sort(key=lambda v: v["capacity_kits"], reverse=True)
    for v in candidates:
        if v["capacity_kits"] >= min(load, 20):
            return v
    return candidates[0] if candidates else None


def open_for_settlement(world: WorldState, settlement_id: str) -> bool:
    return any(
        m.settlement_id == settlement_id and m.status in ("proposed", "authorized", "in_transit")
        for m in world.missions
    )


def build_mission(
    world: WorldState,
    g: nx.Graph,
    row: dict[str, Any],
    parent_id: str | None = None,
    deduct: bool = False,
) -> Mission:
    wid, path, road_ids, dist = shortest_path_to_warehouse(g, world, row["id"])
    mode = "road" if wid else "airdrop"
    wh_name = None
    if wid:
        wh_name = world.warehouse_by_id(wid)["properties"]["name"]
        allocated = dict(row["needs"])
        if deduct:
            allocated = _take_stock(world, wid, row["needs"])
    else:
        allocated = {k: min(v, 20) for k, v in row["needs"].items()}

    load = sum(allocated.values())
    vehicle = _pick_vehicle(world, wid, load) if wid and mode == "road" else None
    if vehicle and deduct:
        vehicle["status"] = "assigned"

    evidence = _evidence_for(world, row, road_ids) + _inventory_evidence(world, wid)
    seen: set[str] = set()
    deduped: list[Evidence] = []
    for e in evidence:
        key = e.source_id + e.role
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)

    if mode == "airdrop":
        rationale = (
            f"{row['name']} has no remaining road path to a verified warehouse. "
            f"Propose air / mule last-mile using Harsil LZ doctrine. Needs: {allocated}."
        )
    else:
        rationale = (
            f"Route {wh_name} → {row['name']} ({dist:.1f} km, {len([r for r in road_ids if r and not str(r).startswith('wh-link')])} segments). "
            f"Isolation={row['isolated']}, at_risk={row.get('at_risk')}, score={row['priority_score']}."
        )

    return Mission(
        id=world.next_mission_id(),
        settlement_id=row["id"],
        settlement_name=row["name"],
        warehouse_id=wid,
        warehouse_name=wh_name,
        vehicle_id=vehicle["id"] if vehicle else None,
        vehicle_name=vehicle["name"] if vehicle else None,
        mode=mode,
        status="proposed",
        needs=[MissionNeed(sku=k, qty=v) for k, v in allocated.items() if v > 0],
        path=path,
        road_ids=[r for r in road_ids if r and not str(r).startswith("wh-link")],
        distance_km=round(dist, 1),
        priority_score=row["priority_score"],
        evidence=deduped,
        rationale=rationale,
        created_at_hour=world.clock_hour,
        parent_id=parent_id,
    )


def take_stock(world: WorldState, warehouse_id: str, needs: dict[str, int]) -> dict[str, int]:
    return _take_stock(world, warehouse_id, needs)


def allocate(world: WorldState, g: nx.Graph, ranked: list[dict[str, Any]]) -> dict[str, int]:
    replanned = 0
    by_id = {r["id"]: r for r in ranked}

    for m in list(world.missions):
        if m.status not in ("authorized", "proposed"):
            continue
        still_ok = True
        wid, _, _, _ = shortest_path_to_warehouse(g, world, m.settlement_id)
        if m.mode == "road":
            status = world.road_status_map()
            if any(status.get(rid) == "blocked" for rid in m.road_ids):
                still_ok = False
            if wid is None:
                still_ok = False
            elif m.warehouse_id and wid != m.warehouse_id:
                still_ok = False
        elif wid is not None and m.mode == "airdrop":
            still_ok = False
        if still_ok:
            continue
        if m.status == "proposed":
            m.status = "replanned"
            row = by_id[m.settlement_id]
            world.missions.append(build_mission(world, g, row, parent_id=m.id, deduct=False))
            replanned += 1
            continue
        m.status = "replanned"
        if m.vehicle_id:
            for v in world.vehicles:
                if v["id"] == m.vehicle_id:
                    v["status"] = "available"
        if m.warehouse_id:
            restore_stock(world, m.warehouse_id, m.needs)
        row = by_id[m.settlement_id]
        world.missions.append(build_mission(world, g, row, parent_id=m.id, deduct=False))
        replanned += 1

    proposed = 0
    targets = [
        r
        for r in ranked
        if r["isolated"] or r["hazard_ids"] or r["citizen_ids"] or r.get("at_risk") or r["priority_score"] >= 28
    ][:8]
    for row in targets:
        if open_for_settlement(world, row["id"]):
            continue
        world.missions.append(build_mission(world, g, row, deduct=False))
        proposed += 1

    return {"proposed": proposed, "replanned": replanned}
