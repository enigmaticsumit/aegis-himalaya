from shapely.geometry import Point, shape


def point_in_any_polygon(lon: float, lat: float, polygons: list[dict]) -> list[dict]:
    pt = Point(lon, lat)
    hits: list[dict] = []
    for feat in polygons:
        geom = shape(feat["geometry"])
        if geom.contains(pt) or geom.distance(pt) < 0.02:
            hits.append(feat)
    return hits
