# AI-Powered Mock Interview & Readiness Platform

A full-stack web app to simulate realistic interview practice with AI-generated questions, answer evaluation, and role-wise readiness tracking.

## Features

- User signup and login with JWT authentication
- Multi-role selection per user profile
- AI-powered interview sessions by role
- Interview question categories:
  - HR / Behavioral
  - Technical (conceptual, non-coding)
  - Situational
  - Project-based
- AI feedback for each answer:
  - Score (0-10)
  - Strengths
  - Weaknesses
  - Missing points
  - Ideal answer example
- Role-wise readiness scoring and weak-area tracking
- Dashboard with trend visuals:
  - Readiness breakdown
  - Timeline sparkline
  - Category performance bars

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: React + Vite
- AI: OpenAI API
- Auth: JWT + password hashing (passlib)

## Project Structure

- `backend/` FastAPI API, models, services, smoke test
- `frontend/` React app with interview flow and dashboard

## Prerequisites

- Python 3.11+ (project currently runs on local virtual environment)
- Node.js 18+
- npm

## Setup

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` from example:

```bash
copy .env.example .env
```

Update values in `.env`:

- `SECRET_KEY`
- `OPENAI_API_KEY` (optional for live AI responses)

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend URLs:

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
```

Create `.env` from example:

```bash
copy .env.example .env
```

Run frontend:

```bash
npm run dev
```

Frontend URL:

- App: `http://127.0.0.1:5173`

## API Overview

Base prefix: `/api/v1`

- Auth
  - `POST /auth/signup`
  - `POST /auth/login`
- Roles
  - `GET /roles/`
  - `GET /roles/selected`
  - `POST /roles/select`
- Interview
  - `POST /interview/sessions/start`
  - `POST /interview/sessions/{session_id}/answer`
  - `POST /interview/sessions/{session_id}/next-question`
- Dashboard
  - `GET /dashboard/me`
  - `GET /dashboard/role-history/{role_id}`

## Readiness Score Logic

Readiness per role is calculated as:

- 60%: average answer quality
- 20%: consistency (practice sessions)
- 20%: coverage (question category diversity)

Weak areas are identified from low-scoring categories.

## Local Verification

Run backend smoke test:

```bash
cd backend
python scripts/smoke_test.py
```

This validates:

- signup/login
- role selection
- interview flow
- AI evaluation response
- dashboard and role-history endpoints

## Notes

- Question generation explicitly avoids coding questions.
- If OpenAI API key is not configured, deterministic fallback responses are used for local testing.
