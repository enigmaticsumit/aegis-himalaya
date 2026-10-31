from typing import Any, Literal

from pydantic import BaseModel, Field

MissionStatus = Literal["proposed", "authorized", "rejected", "in_transit", "replanned"]
RoadStatus = Literal["open", "degraded", "blocked"]


class Evidence(BaseModel):
    source_id: str
    role: str
    snippet: str = ""


class LedgerEntry(BaseModel):
    record_id: str
    source_id: str
    source_type: str
    observed_at: str
    confidence: float
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ClockBody(BaseModel):
    hour: int = Field(ge=0, le=72)


class AuthorizeBody(BaseModel):
    decision: Literal["authorized", "rejected"]
    actor: str = "District Magistrate (demo)"
    reason: str = ""


class MissionNeed(BaseModel):
    sku: str
    qty: int


class Mission(BaseModel):
    id: str
    settlement_id: str
    settlement_name: str
    warehouse_id: str | None
    warehouse_name: str | None
    vehicle_id: str | None
    vehicle_name: str | None
    mode: Literal["road", "airdrop"]
    status: MissionStatus
    needs: list[MissionNeed]
    path: list[str]
    road_ids: list[str]
    distance_km: float
    priority_score: float
    evidence: list[Evidence]
    rationale: str
    created_at_hour: int
    parent_id: str | None = None
    authorization: dict[str, Any] | None = None


class SituationResponse(BaseModel):
    clock_hour: int
    event: dict[str, Any]
    settlements: dict[str, Any]
    roads: dict[str, Any]
    warehouses: dict[str, Any]
    damage: dict[str, Any]
    ranked: list[dict[str, Any]]
    missions: list[Mission]
    inventory: list[dict[str, Any]]
    vehicles: list[dict[str, Any]]
    weather: list[dict[str, Any]]
    briefing: str
    last_run: dict[str, Any] | None
