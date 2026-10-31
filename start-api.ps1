python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r services\api\requirements.txt
uvicorn app.main:app --app-dir services\api --reload --port 8000
