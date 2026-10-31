from __future__ import annotations

from ..ledger import stamp
from ..state import WorldState


def ingest(world: WorldState) -> int:
    """Load active feeds into the provenance ledger with source stamps."""
    world.ledger.clear()
    added = 0

    for feat in world.active_damage_features():
        p = feat["properties"]
        src = world.source(p["source_id"])
        world.ledger.append(
            stamp(
                record_id=p["id"],
                source_id=p["source_id"],
                source_type="satellite",
                observed_at=str(src.get("acquired_at", "")),
                confidence=float(p.get("confidence", 0.7)),
                summary=p["summary"],
                payload={"hazard": p["hazard"], "valid_from_hour": p["valid_from_hour"]},
            )
        )
        added += 1

    for w in world.active_weather():
        src = world.source(w["source_id"])
        world.ledger.append(
            stamp(
                record_id=w["id"],
                source_id=w["source_id"],
                source_type="weather",
                observed_at=str(src.get("acquired_at", "")),
                confidence=0.9,
                summary=w["headline"],
                payload={"severity": w["severity"], "detail": w["detail"]},
            )
        )
        added += 1

    for r in world.active_road_reports():
        src = world.source(r["source_id"])
        world.ledger.append(
            stamp(
                record_id=r["id"],
                source_id=r["source_id"],
                source_type="road",
                observed_at=str(src.get("acquired_at", "")),
                confidence=0.85,
                summary=r["detail"],
                payload={"road_id": r["road_id"], "status": r["status"]},
            )
        )
        added += 1

    for c in world.active_citizen():
        src = world.source(c["source_id"])
        world.ledger.append(
            stamp(
                record_id=c["id"],
                source_id=c["source_id"],
                source_type="citizen",
                observed_at=str(src.get("acquired_at", "")),
                confidence=float(c.get("confidence", 0.6)),
                summary=c["text"],
                payload={"settlement_id": c["settlement_id"]},
            )
        )
        added += 1

    for item in world.inventory:
        src = world.source(item["source_id"])
        world.ledger.append(
            stamp(
                record_id=item["id"],
                source_id=item["source_id"],
                source_type="inventory",
                observed_at=str(src.get("acquired_at", "")),
                confidence=0.95,
                summary=f"{item['label']}: {item['qty']} at {item['warehouse_id']}",
                payload={"sku": item["sku"], "qty": item["qty"], "warehouse_id": item["warehouse_id"]},
            )
        )
        added += 1

    return added
