from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def heuristic_briefing(facts: dict[str, Any]) -> str:
    names = facts.get("isolated_names") or "none"
    return (
        f"T+{facts['hour']}h · {facts['isolated']} isolated settlements ({names}). "
        f"{facts['weather'].rstrip('.')}. Proposed {facts['proposed']} new mission(s); "
        f"replanned {facts['replanned']} authorized mission(s). "
        "Human authorization is required before any stock leaves a warehouse."
    )


def summarize_briefing(facts: dict[str, Any]) -> str:
    fallback = heuristic_briefing(facts)
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return fallback
    body = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a district emergency operations briefer. "
                    "Write 2 tight sentences citing the fused facts. Do not invent sources."
                ),
            },
            {"role": "user", "content": json.dumps(facts)},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        text = payload["choices"][0]["message"]["content"].strip()
        return text or fallback
    except (urllib.error.URLError, KeyError, IndexError, TimeoutError, json.JSONDecodeError):
        return fallback
