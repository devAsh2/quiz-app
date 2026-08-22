# Quiz App — WhatsApp-Style Quiz Application

A full-stack quiz application built with **React**, **FastAPI**, and **MongoDB**. Designed around a WhatsApp-style chat interface where each quiz question appears as a message bubble.

## Architecture

```mermaid
graph TD
    A[React Frontend\nChat UI] -->|REST API| B[FastAPI Backend]
    B --> C[(MongoDB)]

    C --> D[users]
    C --> E[exams]
    C --> F[questions]
    C --> G[events]

    G -->|aggregation| H[Learning Velocity API]
    G -->|aggregation| I[Fatigue Analysis API]
    G -->|aggregation| J[Question Difficulty API]

    style A fill:#005c4b,color:#fff
    style B fill:#1f2c34,color:#fff
    style C fill:#00a884,color:#fff
    style G fill:#2a3942,color:#fff
    style H fill:#1f2c34,color:#aaa
    style I fill:#1f2c34,color:#aaa
    style J fill:#1f2c34,color:#aaa
```

**Key design decisions:**

- Exams embed subjects and chapters — one query fetches the full hierarchy
- Questions are flat, indexed by `chapter_id`
- Every answer attempt is stored as an `event` — all 3 analytics pipelines read from this single collection

→ See [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for full schema details  
→ See [docs/ANALYTICS_LOGIC.md](docs/ANALYTICS_LOGIC.md) for pipeline breakdowns  
→ See [docs/API_CONTRACT.md](docs/API_CONTRACT.md) for all API contracts

---

## Setup

### Prerequisites

- Python 3.11+, Node.js 18+, MongoDB running on port 27017

### Backend

```bash
cd backend
py -m pip install -r requirements.txt
```

Create `backend/.env`:

```
MONGODB_URL=mongodb://localhost:27017
DB_NAME=quiz_db
```

```bash
py -m app.scripts.seed          # populate the database
py -m uvicorn app.main:app --reload
```

API runs at `http://localhost:8000` · Swagger docs at `/docs`

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000/api
```

```bash
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## How to Use

1. **Login** — type a name in the search bar and select a user (e.g. `arjun_s`)
2. **Pick an Exam** — choose from JEE, NEET, or UPSC
3. **Pick a Subject** → then a **Chapter**
4. **Quiz** — questions appear as chat bubbles one at a time; tap an option to answer
5. **Result** — see your score, accuracy, and a fatigue breakdown (Start / Middle / End performance)
6. **Analytics** — tap the Analytics button on the exam screen to see:
   - **Velocity** — all users ranked by Learning Velocity Index
   - **Difficulty** — all questions ranked from hardest to easiest

---

## Tech Stack

| Layer    | Technology                   |
| -------- | ---------------------------- |
| Frontend | React 19, Vite               |
| Backend  | FastAPI, Pydantic v2         |
| Database | MongoDB (Motor async driver) |
