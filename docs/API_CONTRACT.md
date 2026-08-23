# API Contract

Base URL: `http://localhost:8000/api`

All responses are JSON. All timestamps are ISO 8601.

---

## Quiz Flow

### `GET /users`

Returns all predefined users for the login screen.

**Response:**

```json
[{ "id": "user_01", "username": "arjun_s", "email": "arjun.sharma@email.com" }]
```

---

### `GET /exams`

Returns the full nested hierarchy.

**Response:**

```json
[
	{
		"id": "exam_1",
		"name": "JEE",
		"subjects": [
			{
				"id": "sub_01",
				"name": "Physics",
				"chapters": [{ "id": "ch_01", "name": "Mechanics" }]
			}
		]
	}
]
```

---

### `GET /questions/{chapter_id}`

Returns all questions for a chapter. `correct_option` is intentionally excluded.

**Response:**

```json
[
	{
		"id": "q_001",
		"text": "The SI unit of force is:",
		"options": ["Joule", "Watt", "Newton", "Pascal"]
	}
]
```

**Error:** `404` if no questions found for the chapter.

---

### `POST /submit`

Submits an answer. Verifies correctness server-side and stores the event.

**Header:** `X-User-Id: user_01`

**Request body:**

```json
{
	"quiz_id": "uuid-string",
	"question_id": "q_001",
	"selected_option": 2,
	"question_shown_time": "2026-08-22T10:00:00Z",
	"answer_submitted_time": "2026-08-22T10:00:12Z"
}
```

**Response:**

```json
{
	"is_correct": true,
	"correct_option": 2
}
```

---

### `GET /result/{quiz_id}`

Returns the final score for a completed quiz session.

**Response:**

```json
{
	"total": 17,
	"score": 12,
	"percentage": 70.6
}
```

---

## Analytics

### `GET /analytics/learning-velocity`

Returns all users ranked by Learning Velocity Index (highest first).

**Response:**

```json
[
	{
		"user_id": "user_01",
		"accuracy": 0.82,
		"avg_response_time": 18.4,
		"consistency_score": 0.76,
		"learning_velocity_index": 0.71
	}
]
```

---

### `GET /analytics/fatigue/{user_id}/{quiz_id}`

Returns performance breakdown across session thirds.

**Response:**

```json
{
	"user_id": "user_01",
	"quiz_id": "uuid-string",
	"segments": [
		{ "segment": 1, "accuracy": 0.83, "avg_response_time": 14.2 },
		{ "segment": 2, "accuracy": 0.67, "avg_response_time": 21.5 },
		{ "segment": 3, "accuracy": 0.5, "avg_response_time": 31.0 }
	]
}
```

`segment` values: `1` = start, `2` = middle, `3` = end

---

### `GET /analytics/question-difficulty`

Returns all questions ranked from hardest to easiest.

**Response:**

```json
[
	{
		"question_id": "q_042",
		"total_attempts": 23,
		"accuracy_percentage": 17.4,
		"avg_response_time": 48.2,
		"difficulty_score": 72.6
	}
]
```

---

### `GET /analytics/weak-areas/{user_id}` _(bonus)_

Returns chapters ranked by the user's accuracy (lowest first).

**Response:**

```json
[
	{
		"chapter_id": "ch_07",
		"subject_id": "sub_03",
		"exam_id": "exam_1",
		"quiz_sessions": 2,
		"accuracy": 0.24,
		"avg_response_time": 38.1
	}
]
```
