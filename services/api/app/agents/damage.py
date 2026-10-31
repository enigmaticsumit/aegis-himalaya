from __future__ import annotations

import networkx as nx

from ..graph_engine import build_graph, persist_graph, reachable_from_warehouses
from ..state import WorldState


def assess_damage(world: WorldState) -> nx.Graph:
    """Mark blocked roads, persist the knowledge graph, compute isolation."""
    g = build_graph(world)
    persist_graph(g)
    reachable = reachable_from_warehouses(g, world)
    world.isolated_ids = {
        f["properties"]["id"]
        for f in world.settlements_fc["features"]
        if f["properties"]["id"] not in reachable
    }
    return g
