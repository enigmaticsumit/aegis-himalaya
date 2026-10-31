# Aegis Himalaya

Hackathon MVP: an **agentic geospatial command center** for Himalayan climate disasters. Fragmented satellite, weather, road, citizen and inventory feeds become a district knowledge graph, scored communities, and **human-authorized** relief missions with full source traceability.

Demo theatre: **Uttarkashi, Uttarakhand** — Bhagirathi flash flood, then two landslides that cut the Gangotri highway.

## What this demo proves

1. One map fuses otherwise siloed feeds.
2. Isolated settlements are ranked, not just plotted.
3. Logistics agents **propose** deliveries; a human must **authorize** before stock is treated as committed.
4. Every mission opens a provenance chain (satellite / IMD / PWD / citizen / warehouse ledger).
5. Advancing the clock blocks new roads and **replans** an already-authorized mission.

## Stack

| Layer | Choice |
| --- | --- |
| Web | Next.js 15 + MapLibre |
| API | FastAPI |
| Graph | NetworkX (Neo4j-shaped nodes/edges, file-backed) |
| Geo | GeoJSON + Shapely |
| Optional | Docker PostGIS / Neo4j profiles in `docker-compose.yml` (not required) |

No live satellite downloads. Detections are pre-baked in `data/seed/`.

## Run locally

Use two terminals. Python 3.11+ and Node 20+ are expected.

**API**

```powershell
cd C:\Users\anils\aegis-himalaya
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r services\api\requirements.txt
uvicorn app.main:app --app-dir services\api --reload --port 8000
```

**Web** (second terminal)

```powershell
cd C:\Users\anils\aegis-himalaya\apps\web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Three-minute demo script

1. **T+0h.** Situation map shows the Bhagirathi corridor. Press **Run agents**. Maneri and Gangori light up from the flood polygon plus citizen SOS. Open a proposed mission — the drawer cites Sentinel-2, IMD, PWD silt, and the godown ledger.
2. **Authorize** the Maneri road mission. Inventory quantity drops; the vehicle is assigned. Rejecting is equally valid and stays on the ledger.
3. Click **T+6h**, then **Run agents**. NH-34 Maneri–Bhatwari is blocked. Upper-valley settlements (Bhatwari, Raithal, Sukki, Harsil, Gangotri, Jhala) go **isolated**. If you authorized a mission that used that road, it becomes **replanned** and a new proposed mission appears.
4. Click **T+18h**, **Run agents**. The Sukki–Harsil gorge buries. Harsil / Gangotri / Jhala lose the last road path → **airdrop** missions. Trace the ITBP citizen report and SAR coherence source.

Reset returns the world to T+0 with full stock.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/situation` | Map GeoJSON, scores, missions, inventory |
| POST | `/clock` | `{ "hour": 0 \| 6 \| 18 }` |
| POST | `/agents/run` | Ingest → damage/isolation → prioritize → allocate |
| POST | `/missions/{id}/authorize` | `{ "decision": "authorized" \| "rejected" }` |
| GET | `/trace/{entity_id}` | Evidence chain |
| POST | `/reset` | Reload seed |

## Layout

```
aegis-himalaya/
  apps/web/              command center
  services/api/          FastAPI + agents
  data/seed/             Uttarkashi GeoJSON + feeds
  docker-compose.yml     optional PostGIS / Neo4j
```

## Out of scope (intentionally)

Trained damage models, live departmental databases, production GIS operations, and real satellite tasking. Those are the next product increment; this MVP is the closed-loop relief story with auditability.
