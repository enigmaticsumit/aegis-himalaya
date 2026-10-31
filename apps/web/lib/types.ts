export type MissionNeed = { sku: string; qty: number };

export type Evidence = {
  source_id: string;
  role: string;
  snippet: string;
};

export type Mission = {
  id: string;
  settlement_id: string;
  settlement_name: string;
  warehouse_id: string | null;
  warehouse_name: string | null;
  vehicle_id: string | null;
  vehicle_name: string | null;
  mode: "road" | "airdrop";
  status: "proposed" | "authorized" | "rejected" | "in_transit" | "replanned";
  needs: MissionNeed[];
  path: string[];
  road_ids: string[];
  distance_km: number;
  priority_score: number;
  evidence: Evidence[];
  rationale: string;
  created_at_hour: number;
  parent_id: string | null;
  authorization: { actor: string; decision: string; reason: string; at_hour: number } | null;
};

export type Ranked = {
  id: string;
  name: string;
  population: number;
  isolated: boolean;
  at_risk?: boolean;
  priority_score: number;
  hazard_ids: string[];
  citizen_ids: string[];
  needs: Record<string, number>;
  lon: number;
  lat: number;
  elderly_pct: number;
  altitude_m: number;
  hours_since_contact: number;
};

export type Situation = {
  clock_hour: number;
  event: {
    event_name: string;
    district: string;
    state: string;
    t0: string;
    hours: number[];
    brief: string;
  };
  settlements: GeoJSON.FeatureCollection;
  roads: GeoJSON.FeatureCollection;
  warehouses: GeoJSON.FeatureCollection;
  damage: GeoJSON.FeatureCollection;
  vehicles_geo: GeoJSON.FeatureCollection;
  ranked: Ranked[];
  missions: Mission[];
  inventory: { id: string; warehouse_id: string; sku: string; label: string; qty: number }[];
  vehicles: { id: string; name: string; kind: string; capacity_kits: number; status: string; base_warehouse_id: string }[];
  weather: { id: string; severity: string; headline: string; detail: string }[];
  briefing: string;
  last_run: { hour: number; isolated: number; proposed: number; replanned: number; ranked_top: string[] } | null;
  ledger_size?: number;
};
