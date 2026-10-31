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
| Graph | NetworkX (Neo4j-shaped nodes/edges, file-backed at `data/runtime/graph.json`) |
| Geo | GeoJSON + Shapely |
| Optional | Docker PostGIS / Neo4j profiles in `docker-compose.yml` (not required) |
| AI | Heuristic briefing; optional OpenAI summary if `OPENAI_API_KEY` is set |

No live satellite downloads. Detections are pre-baked in `data/seed/`.

## Run locally

Python 3.11+ and Node 20+ are expected. Use two terminals from the repo root.

**API**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r services\api\requirements.txt
uvicorn app.main:app --app-dir services\api --reload --port 8000
```

**Web** (second terminal)

```powershell
cd apps\web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Optional: copy `.env.example` and set `OPENAI_API_KEY` so the T+Nh briefing is an LLM summary of the fused facts. Without a key the demo still runs.

## Three-minute demo script

1. **T+0h.** Situation map shows the Bhagirathi corridor. Press **Run agents**. Maneri and Gangori light up from the flood polygon plus citizen SOS. Upper-valley towns (Bhatwari and above) are **at risk** because the only highway already has silted, one-lane PWD status.
2. Open the **Maneri** mission — the drawer cites Sentinel-2, IMD, PWD silt, PHC sitrep, and the godown ledger. Then open **Bhatwari** and **Authorize** that road mission (stock commits only now). Rejecting any other proposal is equally valid and stays on the ledger.
3. Click **T+6h**, then **Run agents**. NH-34 Maneri–Bhatwari is blocked. Upper-valley settlements (Bhatwari, Raithal, Sukki, Harsil, Gangotri, Jhala) go **isolated**. The authorized Bhatwari mission becomes **replanned** as an airdrop and a new proposed mission appears.
4. Click **T+18h**, **Run agents**. The Sukki–Harsil gorge buries. Trace the ITBP citizen report and SAR coherence source on Harsil / Gangotri airdrop proposals.

Reset returns the world to T+0 with full stock.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/situation` | Map GeoJSON, scores, missions, inventory |
| POST | `/clock` | `{ "hour": 0 \| 6 \| 18 }` |
| POST | `/agents/run` | Ingest → damage/isolation → prioritize → allocate |
| GET | `/missions` | Mission queue |
| POST | `/missions/{id}/authorize` | `{ "decision": "authorized" \| "rejected" }` |
| GET | `/trace/{entity_id}` | Evidence chain |
| GET | `/ledger` | Stamped feed records |
| POST | `/reset` | Reload seed |

## Layout

```
aegis-himalaya/
  apps/web/              command center
  services/api/          FastAPI + agents
  data/seed/             Uttarkashi GeoJSON + feeds
  data/runtime/          NetworkX JSON snapshot after each run
  docker-compose.yml     optional PostGIS / Neo4j
```

## Out of scope (intentionally)

Trained damage models, live departmental databases, production GIS operations, and real satellite tasking. Those are the next product increment; this MVP is the closed-loop relief story with auditability.
