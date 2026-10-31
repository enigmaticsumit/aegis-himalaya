from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agents.orchestrator import authorize_mission, run_agents, situation_payload
from .models import AuthorizeBody, ClockBody
from .state import WORLD

app = FastAPI(title="Aegis Himalaya", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "clock_hour": WORLD.clock_hour}


@app.get("/situation")
def situation():
    return situation_payload()


@app.post("/clock")
def set_clock(body: ClockBody):
    WORLD.clock_hour = body.hour
    return situation_payload()


@app.post("/agents/run")
def agents_run():
    run_agents()
    return situation_payload()


@app.post("/reset")
def reset():
    WORLD.reset()
    return situation_payload()


@app.get("/missions")
def missions():
    return WORLD.missions


@app.post("/missions/{mission_id}/authorize")
def authorize(mission_id: str, body: AuthorizeBody):
    try:
        return authorize_mission(mission_id, body.decision, body.actor, body.reason)
    except KeyError:
        raise HTTPException(404, f"Unknown mission {mission_id}") from None
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from None


@app.get("/trace/{entity_id}")
def trace(entity_id: str):
    mission = next((m for m in WORLD.missions if m.id == entity_id), None)
    if mission:
        sources = [WORLD.source(e.source_id) | {"role": e.role, "snippet": e.snippet} for e in mission.evidence]
        return {"entity_type": "mission", "entity": mission, "sources": sources}

    sett = next((f for f in WORLD.settlements_fc["features"] if f["properties"]["id"] == entity_id), None)
    if sett:
        related = [m for m in WORLD.missions if m.settlement_id == entity_id]
        source_ids: list[str] = []
        for m in related:
            source_ids.extend(e.source_id for e in m.evidence)
        for c in WORLD.active_citizen():
            if c["settlement_id"] == entity_id:
                source_ids.append(c["source_id"])
        uniq = []
        seen = set()
        for sid in source_ids:
            if sid in seen:
                continue
            seen.add(sid)
            src = WORLD.source(sid)
            uniq.append(src)
        return {"entity_type": "settlement", "entity": sett, "sources": uniq}

    if entity_id in WORLD.sources:
        return {"entity_type": "source", "entity": WORLD.sources[entity_id], "sources": [WORLD.sources[entity_id]]}

    raise HTTPException(404, f"No trace for {entity_id}")
