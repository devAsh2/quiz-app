# Quiz App — WhatsApp-Style Quiz Application

A full-stack quiz application built with React, FastAPI, and MongoDB. Features a WhatsApp-inspired chat interface for quiz-taking and analytics APIs for performance insights.

## Architecture

```
quiz-app/
├── backend/          FastAPI + Motor (async MongoDB)
│   └── app/
│       ├── api/           Route handlers (quiz.py, analytics.py)
│       ├── core/          Database connection + indexes
│       ├── models/        MongoDB document models (Pydantic)
│       ├── schemas/       Request/Response DTOs
│       ├── services/      Business logic + aggregation pipelines
│       ├── scripts/       Database seeder
│       └── data/          JSON seed files (users, exams, questions)
├── frontend/         React + Vite
│   └── src/
│       ├── components/    LoginScreen, SelectionScreen, QuizScreen, AnalyticsScreen
│       └── api.js         API service layer
└── README.md
```

## Database Design

**Collections:**

| Collection  | Description                                 |
| ----------- | ------------------------------------------- |
| `users`     | 50 predefined users (dummy auth)            |
| `exams`     | 3 exams with nested subjects and chapters   |
| `questions` | 500 MCQs referenced by chapter_id           |
| `events`    | Every answer attempt — powers all analytics |

**Key Design Decisions:**

- Exams use nested documents (subjects → chapters) for single-query hierarchy fetch
- Questions are flat with `chapter_id` reference for indexed lookup
- Events are self-contained snapshots — no joins needed for analytics

## Analytics Implementation

### 1. Learning Velocity Index

Ranks users by a weighted composite score:

- Accuracy (40%) — correct answers / total attempts
- Consistency (30%) — `1 / (1 + std_dev_of_response_time)`
- Speed (30%) — normalized against 60s cap

### 2. Fatigue Analysis

Analyzes performance change within a single quiz session:

- Divides questions into dynamic thirds (start/middle/end)
- Reports accuracy and avg response time per segment
- Uses `$setWindowFields` with `$rank` for position tracking

### 3. Question Difficulty Index

Scores each question from hardest to easiest:

- Inverse accuracy contributes 70%
- Avg response time contributes 30% (capped at 60s, normalized to 0-100)

## API Endpoints

### Quiz Flow

| Method | Endpoint                      | Description                                       |
| ------ | ----------------------------- | ------------------------------------------------- |
| GET    | `/api/users`                  | List all users (dummy auth)                       |
| GET    | `/api/exams`                  | Full exam → subject → chapter tree                |
| GET    | `/api/questions/{chapter_id}` | Questions for a chapter (correct_option excluded) |
| POST   | `/api/submit`                 | Submit an answer (Header: X-User-Id)              |
| GET    | `/api/result/{quiz_id}`       | Final score for a quiz session                    |

### Analytics

| Method | Endpoint                                     | Description                        |
| ------ | -------------------------------------------- | ---------------------------------- |
| GET    | `/api/analytics/learning-velocity`           | All users ranked by LVI            |
| GET    | `/api/analytics/fatigue/{user_id}/{quiz_id}` | Fatigue breakdown for a session    |
| GET    | `/api/analytics/question-difficulty`         | All questions ranked by difficulty |

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (running locally on port 27017)

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

Seed the database:

```bash
py -m app.scripts.seed
```

Start the server:

```bash
py -m uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000/api
```

Start the dev server:

```bash
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Application Flow

```
Login (select user) → Exam → Subject → Chapter → Quiz (chat-style) → Result
```

- Questions are displayed one at a time as chat bubbles
- User cannot revisit previous questions
- Each answer is submitted immediately and tracked as an event
- Result page shows score + fatigue analysis

## Assumptions

1. 60 seconds is the normalization cap for response time
2. LVI weights: Accuracy 0.4, Consistency 0.3, Speed 0.3
3. Difficulty weights: Inverse Accuracy 0.7, Response Time 0.3
4. Fatigue segments are dynamic thirds based on total questions per session
5. All quiz attempts feed into analytics (no filtering by latest only)
6. Population std deviation used for consistency calculation

## Tech Stack

- **Frontend:** React 19, Vite
- **Backend:** FastAPI, Motor (async MongoDB driver), Pydantic v2
- **Database:** MongoDB
