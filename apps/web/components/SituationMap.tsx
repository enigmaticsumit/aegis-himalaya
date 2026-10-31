"use client";

import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Mission, Situation } from "@/lib/types";

type Props = {
  data: Situation;
  selectedId: string | null;
  onSelect: (id: string) => void;
};

export default function SituationMap({ data, selectedId, onSelect }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  useEffect(() => {
    if (!ref.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: ref.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap",
          },
        },
        layers: [{ id: "osm", type: "raster", source: "osm" }],
      },
      center: [78.5, 30.82],
      zoom: 9,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const apply = () => {
      const ensure = (id: string, source: maplibregl.GeoJSONSourceSpecification, layers: maplibregl.LayerSpecification[]) => {
        if (map.getSource(id)) {
          (map.getSource(id) as maplibregl.GeoJSONSource).setData(source.data as GeoJSON.GeoJSON);
        } else {
          map.addSource(id, source);
          for (const layer of layers) map.addLayer(layer);
        }
      };

      ensure(
        "damage",
        { type: "geojson", data: data.damage },
        [
          {
            id: "damage-fill",
            type: "fill",
            source: "damage",
            paint: { "fill-color": "#ef4444", "fill-opacity": 0.22 },
          },
          {
            id: "damage-line",
            type: "line",
            source: "damage",
            paint: { "line-color": "#fca5a5", "line-width": 1.5 },
          },
        ],
      );

      ensure(
        "roads",
        { type: "geojson", data: data.roads },
        [
          {
            id: "roads-line",
            type: "line",
            source: "roads",
            paint: {
              "line-color": [
                "match",
                ["get", "status"],
                "blocked",
                "#ef4444",
                "degraded",
                "#f59e0b",
                "#67e8f9",
              ],
              "line-width": ["match", ["get", "status"], "blocked", 4, 3],
            },
          },
        ],
      );

      const selectedMission = data.missions.find((m) => m.id === selectedId);
      const route = routeFeature(data, selectedMission);
      ensure(
        "route",
        { type: "geojson", data: route },
        [
          {
            id: "route-line",
            type: "line",
            source: "route",
            paint: { "line-color": "#34d399", "line-width": 5, "line-opacity": 0.9 },
          },
        ],
      );

      ensure(
        "settlements",
        { type: "geojson", data: data.settlements },
        [
          {
            id: "settlements-circle",
            type: "circle",
            source: "settlements",
            paint: {
              "circle-radius": ["interpolate", ["linear"], ["get", "priority_score"], 10, 5, 90, 14],
              "circle-color": [
                "case",
                ["get", "isolated"],
                "#fb7185",
                ["interpolate", ["linear"], ["get", "priority_score"], 20, "#22d3ee", 60, "#fbbf24", 85, "#f97316"],
              ],
              "circle-stroke-width": 2,
              "circle-stroke-color": "#071018",
            },
          },
          {
            id: "settlements-label",
            type: "symbol",
            source: "settlements",
            layout: { "text-field": ["get", "name"], "text-size": 11, "text-offset": [0, 1.2] },
            paint: { "text-color": "#e7f1f6", "text-halo-color": "#071018", "text-halo-width": 1 },
          },
        ],
      );

      ensure(
        "warehouses",
        { type: "geojson", data: data.warehouses },
        [
          {
            id: "wh-circle",
            type: "circle",
            source: "warehouses",
            paint: {
              "circle-radius": 8,
              "circle-color": "#a3e635",
              "circle-stroke-width": 2,
              "circle-stroke-color": "#14532d",
            },
          },
        ],
      );

      const click = (e: maplibregl.MapLayerMouseEvent) => {
        const id = e.features?.[0]?.properties?.id as string | undefined;
        if (id) onSelectRef.current(id);
      };
      if (!(map as unknown as { _aegisBound?: boolean })._aegisBound) {
        map.on("click", "settlements-circle", click);
        map.on("click", "wh-circle", click);
        (map as unknown as { _aegisBound?: boolean })._aegisBound = true;
      }
    };

    if (map.isStyleLoaded()) apply();
    else map.once("load", apply);
  }, [data, selectedId]);

  return (
    <>
      <div ref={ref} className="map-el" />
      <div className="legend">
        <div><span className="swatch" style={{ background: "#fb7185" }} /> Isolated settlement</div>
        <div><span className="swatch" style={{ background: "#fbbf24" }} /> High priority</div>
        <div><span className="swatch" style={{ background: "#a3e635" }} /> Warehouse</div>
        <div><span className="swatch" style={{ background: "#ef4444", borderRadius: 2 }} /> Blocked road</div>
        <div><span className="swatch" style={{ background: "#34d399", borderRadius: 2 }} /> Selected mission route</div>
      </div>
    </>
  );
}

function routeFeature(data: Situation, mission?: Mission): GeoJSON.FeatureCollection {
  if (!mission || mission.road_ids.length === 0) {
    return { type: "FeatureCollection", features: [] };
  }
  const features = data.roads.features.filter((f) => mission.road_ids.includes(String(f.properties?.id)));
  return { type: "FeatureCollection", features };
}
