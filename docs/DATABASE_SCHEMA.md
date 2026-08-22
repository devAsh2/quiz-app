# Database Schema

## Collections

### `users`

Pre-seeded user list for dummy authentication.

```json
{
	"_id": "user_01",
	"username": "arjun_s",
	"email": "arjun.sharma@email.com"
}
```

---

### `exams`

Fully nested — subjects and chapters are embedded documents, not separate collections. One query returns the complete hierarchy.

```json
{
	"_id": "exam_1",
	"name": "JEE",
	"subjects": [
		{
			"id": "sub_01",
			"name": "Physics",
			"chapters": [
				{ "id": "ch_01", "name": "Mechanics" },
				{ "id": "ch_02", "name": "Thermodynamics" }
			]
		}
	]
}
```

**Why nested?** The exam selection flow always needs the full tree at once. Embedding avoids multiple round-trips.

---

### `questions`

Flat collection, referenced by `chapter_id`. `correct_option` is never returned to the frontend.

```json
{
	"_id": "q_001",
	"exam_id": "exam_1",
	"subject_id": "sub_01",
	"chapter_id": "ch_01",
	"text": "The SI unit of force is:",
	"options": ["Joule", "Watt", "Newton", "Pascal"],
	"correct_option": 2,
	"marks": 1
}
```

**Index:** `chapter_id` (ascending) for quiz question fetch.

---

### `events`

The analytics engine. Every answer attempt is stored as a self-contained snapshot. No joins needed.

```json
{
  "_id": ObjectId,
  "user_id": "user_01",
  "quiz_id": "uuid-generated-by-frontend",
  "question_id": "q_001",
  "exam_id": "exam_1",
  "subject_id": "sub_01",
  "chapter_id": "ch_01",
  "question_shown_time": "2026-08-22T10:00:00Z",
  "answer_submitted_time": "2026-08-22T10:00:12Z",
  "response_duration": 12.3,
  "selected_option": 2,
  "is_correct": true,
  "marks": 1
}
```

**Indexes:**

| Index                                       | Purpose                              |
| ------------------------------------------- | ------------------------------------ |
| `user_id`                                   | Learning velocity, weak area lookups |
| `question_id`                               | Question difficulty aggregation      |
| `quiz_id`                                   | Result and fatigue lookups           |
| `(user_id, quiz_id, answer_submitted_time)` | Fatigue analysis pipeline            |
| `(question_id, is_correct)`                 | Difficulty aggregation optimization  |
| `(user_id, chapter_id)`                     | Weak area analysis                   |

**Why self-contained?** Marks and hierarchy IDs are copied from the question at submission time. This ensures historical analytics remain accurate even if question data changes.
