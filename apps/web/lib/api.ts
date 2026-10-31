import type { Mission, Situation } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  situation: () => json<Situation>("/situation"),
  setClock: (hour: number) => json<Situation>("/clock", { method: "POST", body: JSON.stringify({ hour }) }),
  runAgents: () => json<Situation>("/agents/run", { method: "POST" }),
  reset: () => json<Situation>("/reset", { method: "POST" }),
  authorize: (id: string, decision: "authorized" | "rejected", reason = "") =>
    json<Mission>(`/missions/${id}/authorize`, {
      method: "POST",
      body: JSON.stringify({ decision, reason, actor: "District Magistrate (demo)" }),
    }),
  trace: (id: string) =>
    json<{
      entity_type: string;
      entity: unknown;
      sources: { id: string; type: string; publisher: string; acquired_at?: string; note?: string; role?: string; snippet?: string }[];
    }>(`/trace/${id}`),
};
