"""FastAPI application for the VEKTOR Logistics Brain."""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import database
from .planner import build_mission_plan
from .routing import LocationNotFoundError, RoutingError

DisasterType = Literal["flood", "earthquake", "wildfire", "cyclone", "landslide"]
STATIC_FILE = Path(__file__).with_name("static") / "index.html"

app = FastAPI(
    title="VEKTOR Logistics Brain",
    description="Starter relief-supply recommendations and map routes.",
    version="1.0.0",
)


class PlanRequest(BaseModel):
    location: str = Field(min_length=2, max_length=200)
    disaster_type: DisasterType


class SupplyRecommendation(BaseModel):
    item_id: str
    name: str
    quantity: int
    requested_quantity: int
    available_quantity: int
    shortage: int
    unit: str


class Coordinate(BaseModel):
    latitude: float
    longitude: float


class Destination(Coordinate):
    name: str


class Route(BaseModel):
    origin: Coordinate
    distance_m: float
    duration_s: float
    geometry: list[list[float]]


class PlanResponse(BaseModel):
    id: int
    location: str
    disaster_type: DisasterType
    destination: Destination
    route: Route
    recommended_supplies: list[SupplyRecommendation]
    mission_summary: str
    created_at: str


@app.on_event("startup")
def startup() -> None:
    database.initialize_database()


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_FILE)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/plan", response_model=PlanResponse)
def create_plan(request: PlanRequest) -> dict:
    if not request.location.strip():
        raise HTTPException(status_code=422, detail="Location cannot be blank.")
    try:
        mission = build_mission_plan(request.location, request.disaster_type)
    except LocationNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RoutingError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    mission_id, created_at = database.save_mission(mission)
    return {"id": mission_id, **mission, "created_at": created_at}
