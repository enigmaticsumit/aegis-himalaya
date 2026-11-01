# VEKTOR Logistics Brain

A beginner-friendly FastAPI starter module for relief-supply planning. It keeps a
fixed inventory and mission history in SQLite, selects supplies using small
disaster-specific rules, and uses OpenStreetMap Nominatim plus OSRM for a basic
geocoded driving route to the nearest example relief hub. A Leaflet page displays
the route and endpoints.

> **Starter only:** inventory quantities and relief hubs are examples, not
> operational guidance. Verify inventory, hub locations, route conditions, and
> supply needs with qualified local responders before dispatch.

## Requirements

- Python 3.10 or newer
- Internet access for the public OpenStreetMap geocoder, OSRM router, map tiles,
  and Leaflet CDN

## Setup on Windows (PowerShell)

From the repository root:

```powershell
Set-Location .\vektor
py -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

This uses the virtual environment directly, so PowerShell script activation and
execution-policy changes are not needed. For running the API without its tests,
install `requirements.txt` instead.

## Run

```powershell
& .\.venv\Scripts\python.exe -m uvicorn logistics.main:app --host 127.0.0.1 --port 8000 --reload
```

Open <http://127.0.0.1:8000/> for the Leaflet map or
<http://127.0.0.1:8000/docs> for interactive API documentation.

Run the command above from the `vektor` directory. From the repository root, use:

```powershell
& .\vektor\.venv\Scripts\python.exe -m uvicorn logistics.main:app --app-dir .\vektor --host 127.0.0.1 --port 8000 --reload
```

The SQLite database is created as `logistics/vektor.db` on first startup.
Set `VEKTOR_DB_PATH` to use another database file. Set `VEKTOR_USER_AGENT` to a
descriptive application identifier when using the public geocoder.

## API example

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/plan `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"location":"New Delhi, India","disaster_type":"flood"}'
```

Supported `disaster_type` values are `flood`, `earthquake`, `wildfire`,
`cyclone`, and `landslide`. The response includes recommended quantities,
requested quantities and any stock shortages, the chosen destination, route
geometry and distance/time estimates, and a mission summary. Successful plans
are saved in SQLite.

The hubs in `logistics/inventory.py` are illustrative coordinates and should be
replaced with verified operating locations. Public Nominatim and OSRM services
have usage policies, rate limits, and no availability guarantee; use appropriate
hosted services for production or high-volume use.

## Run tests

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The API tests mock external map services, so they do not need internet access.
