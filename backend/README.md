# AI-Powered Mock Interview & Readiness Platform (Backend)

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and update values.
4. Run the server:
   - `uvicorn app.main:app --reload`

## API Base

- Base URL: `http://127.0.0.1:8000`
- API prefix: `/api/v1`
- Docs: `/docs`

## Frontend (React + Vite)

The frontend is in the sibling folder `../frontend`.

1. In `frontend`, copy `.env.example` to `.env`.
2. Install frontend dependencies:
   - `npm install`
3. Start frontend dev server:
   - `npm run dev`

The frontend expects backend API at:

- `http://127.0.0.1:8000/api/v1`

## Integration Smoke Test

Run a local API smoke test that covers signup, role selection, interview answer evaluation, and dashboard:

- `python -m app.scripts.smoke_test`
- `python scripts/smoke_test.py`
