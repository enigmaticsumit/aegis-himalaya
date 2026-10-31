from __future__ import annotations

from typing import Any


def _point_in_ring(lon: float, lat: float, ring: list[list[float]]) -> bool:
    inside = False
    n = len(ring)
    if n < 4:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        intersects = ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi)
        if intersects:
            inside = not inside
        j = i
    return inside


def _geom_hits(lon: float, lat: float, geom: dict[str, Any]) -> bool:
    gtype = geom.get("type")
    coords = geom.get("coordinates")
    if gtype == "Polygon" and coords:
        return _point_in_ring(lon, lat, coords[0])
    if gtype == "MultiPolygon" and coords:
        return any(_point_in_ring(lon, lat, poly[0]) for poly in coords if poly)
    return False


def _min_distance_deg(lon: float, lat: float, geom: dict[str, Any]) -> float:
    pts: list[list[float]] = []

    def walk(node: Any) -> None:
        if not node:
            return
        if isinstance(node[0], (int, float)):
            pts.append(node)  # type: ignore[arg-type]
            return
        for child in node:
            walk(child)

    walk(geom.get("coordinates"))
    best = 1e9
    for p in pts:
        d = ((p[0] - lon) ** 2 + (p[1] - lat) ** 2) ** 0.5
        if d < best:
            best = d
    return best


def point_in_any_polygon(lon: float, lat: float, polygons: list[dict]) -> list[dict]:
    hits: list[dict] = []
    for feat in polygons:
        geom = feat["geometry"]
        try:
            from shapely.geometry import Point, shape

            pt = Point(lon, lat)
            shp = shape(geom)
            if shp.contains(pt) or shp.distance(pt) < 0.02:
                hits.append(feat)
                continue
        except Exception:
            if _geom_hits(lon, lat, geom) or _min_distance_deg(lon, lat, geom) < 0.02:
                hits.append(feat)
    return hits
