"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { Mission, Situation } from "@/lib/types";

const SituationMap = dynamic(() => import("./SituationMap"), { ssr: false });

const HOURS = [0, 6, 18];

export default function CommandCenter() {
  const [data, setData] = useState<Situation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);

  const load = useCallback(async () => {
    const s = await api.situation();
    setData(s);
  }, []);

  useEffect(() => {
    load().catch((e: Error) => setError(e.message));
  }, [load]);

  const run = async (fn: () => Promise<Situation>) => {
    setBusy(true);
    setError(null);
    try {
      setData(await fn());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  };

  const selectedMission = data?.missions.find((m) => m.id === selected);
  const selectedSettlement = data?.ranked.find((r) => r.id === selected);
  const drawerOpen = Boolean(selectedMission || selectedSettlement);

  const evidence = useMemo(() => {
    if (selectedMission) return selectedMission.evidence;
    if (!selectedSettlement || !data) return [];
    return data.missions.filter((m) => m.settlement_id === selectedSettlement.id).flatMap((m) => m.evidence);
  }, [data, selectedMission, selectedSettlement]);

  if (!data) {
    return (
      <div className="app" style={{ display: "block", padding: 24 }}>
        <p>Connecting to Aegis API at http://127.0.0.1:8000 …</p>
        {error && <p className="err">{error} Start the API with the README instructions.</p>}
      </div>
    );
  }

  return (
    <div className="app">
      <header className="top">
        <div className="brand">
          <strong>AEGIS HIMALAYA</strong>
          <span>
            {data.event.district}, {data.event.state} · {data.event.event_name}
          </span>
        </div>
        <div className="top-actions">
          <span className="badge">T+{data.clock_hour}h</span>
          <button className="primary" disabled={busy} onClick={() => run(api.runAgents)}>
            Run agents
          </button>
          <button disabled={busy} onClick={() => run(api.reset)}>
            Reset
          </button>
        </div>
      </header>

      <aside className="left">
        <h2>Prioritized communities</h2>
        {error && <p className="err">{error}</p>}
        {data.ranked.map((r) => (
          <article
            key={r.id}
            className={`card ${selected === r.id ? "active" : ""}`}
            onClick={() => setSelected(r.id)}
          >
            <h3>{r.name}</h3>
            <div className="meta">
              <span className={`badge ${r.isolated ? "iso" : "ok"}`}>{r.isolated ? "isolated" : "connected"}</span>
              <span className="badge">score {r.priority_score}</span>
              <span>{r.population.toLocaleString()} people</span>
            </div>
          </article>
        ))}
      </aside>

      <section className="map">
        <SituationMap data={data} selectedId={selected} onSelect={setSelected} />
        {drawerOpen && (
          <aside className="drawer">
            <button onClick={() => setSelected(null)} style={{ float: "right" }}>
              Close
            </button>
            <h3>{selectedMission ? selectedMission.id : selectedSettlement?.name}</h3>
            {selectedMission && <p className="briefing">{selectedMission.rationale}</p>}
            {selectedSettlement && !selectedMission && (
              <p className="briefing">
                Altitude {selectedSettlement.altitude_m} m · last contact {selectedSettlement.hours_since_contact}h ·
                elderly {Math.round(selectedSettlement.elderly_pct * 100)}%
              </p>
            )}
            <h2>Source traceability</h2>
            {evidence.length === 0 && <p className="meta">Run agents to attach satellite, weather, road and citizen evidence.</p>}
            {uniqEvidence(evidence).map((e) => (
              <div className="source" key={e.source_id + e.role}>
                <div className="role">{e.role}</div>
                <div>{e.snippet}</div>
                <div className="meta">{e.source_id}</div>
              </div>
            ))}
          </aside>
        )}
      </section>

      <aside className="right">
        <h2>Missions (human authorization)</h2>
        {data.missions.length === 0 && <p className="meta" style={{ padding: "0 12px" }}>No missions yet. Press Run agents.</p>}
        {data.missions.map((m) => (
          <MissionCard
            key={m.id}
            m={m}
            active={selected === m.id}
            busy={busy}
            onSelect={() => setSelected(m.id)}
            onDecide={(decision) =>
              run(async () => {
                await api.authorize(m.id, decision);
                return api.situation();
              })
            }
          />
        ))}
        <h2>Verified inventory</h2>
        {data.inventory.map((i) => (
          <div key={i.id} className="card" style={{ cursor: "default" }}>
            <h3>{i.label}</h3>
            <div className="meta">
              {i.warehouse_id} · qty {i.qty}
            </div>
          </div>
        ))}
      </aside>

      <footer className="bottom">
        <div>
          <div className="clock">
            {HOURS.map((h) => (
              <button
                key={h}
                className={data.clock_hour === h ? "active" : ""}
                disabled={busy}
                onClick={() => run(() => api.setClock(h))}
              >
                T+{h}h
              </button>
            ))}
            <span className="meta">Then press Run agents to replan against new closures.</span>
          </div>
          <p className="briefing">{data.briefing}</p>
        </div>
        <div>
          {data.weather.slice(-1).map((w) => (
            <div key={w.id}>
              <span className={`badge ${w.severity === "red" ? "iso" : "proposed"}`}>{w.severity}</span>
              <p className="briefing">{w.headline}</p>
            </div>
          ))}
        </div>
      </footer>
    </div>
  );
}

function MissionCard({
  m,
  active,
  busy,
  onSelect,
  onDecide,
}: {
  m: Mission;
  active: boolean;
  busy: boolean;
  onSelect: () => void;
  onDecide: (d: "authorized" | "rejected") => void;
}) {
  return (
    <article className={`card ${active ? "active" : ""}`} onClick={onSelect}>
      <h3>
        {m.id} · {m.settlement_name}
      </h3>
      <div className="meta">
        <span className={`badge ${m.status}`}>{m.status}</span>
        <span className={`badge ${m.mode}`}>{m.mode}</span>
        <span>{m.distance_km} km</span>
        {m.vehicle_name && <span>{m.vehicle_name}</span>}
      </div>
      <div className="meta" style={{ marginTop: 4 }}>
        {m.needs.map((n) => (
          <span key={n.sku}>
            {n.sku} ×{n.qty}
          </span>
        ))}
      </div>
      {m.status === "proposed" && (
        <div className="row-actions">
          <button
            className="good"
            disabled={busy}
            onClick={(e) => {
              e.stopPropagation();
              onDecide("authorized");
            }}
          >
            Authorize
          </button>
          <button
            className="bad"
            disabled={busy}
            onClick={(e) => {
              e.stopPropagation();
              onDecide("rejected");
            }}
          >
            Reject
          </button>
        </div>
      )}
    </article>
  );
}

function uniqEvidence(items: Mission["evidence"]) {
  const seen = new Set<string>();
  return items.filter((e) => {
    const k = e.source_id + e.role;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}
