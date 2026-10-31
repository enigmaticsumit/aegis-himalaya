from __future__ import annotations

from typing import Any

from .models import LedgerEntry


def stamp(
    *,
    record_id: str,
    source_id: str,
    source_type: str,
    observed_at: str,
    confidence: float,
    summary: str,
    payload: dict[str, Any] | None = None,
) -> LedgerEntry:
    return LedgerEntry(
        record_id=record_id,
        source_id=source_id,
        source_type=source_type,
        observed_at=observed_at,
        confidence=confidence,
        summary=summary,
        payload=payload or {},
    )
