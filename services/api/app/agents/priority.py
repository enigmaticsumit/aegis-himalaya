from __future__ import annotations

from typing import Any

import networkx as nx

from ..graph_engine import annotate_settlements
from ..state import WorldState


def prioritize(world: WorldState, g: nx.Graph) -> list[dict[str, Any]]:
    ranked = annotate_settlements(world, g)
    world.ranked = ranked
    return ranked
