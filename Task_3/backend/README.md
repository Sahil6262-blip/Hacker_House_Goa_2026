# Backend

Requires Python 3.10+. Create a virtual environment, install dependencies, and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item ..\.env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

The API uses `multipart/form-data` for `POST /api/face/analyze` and `POST /api/search`; all other write routes use JSON. OpenAPI is at `/docs`.

Run checks:

```powershell
python -m pytest
python -m ruff check app tests
python -m mypy app
```

The default `LocalLedger` is a persistent JSON hash chain for local development. It is not an Ethereum network and should not be described as public-chain notarization.

