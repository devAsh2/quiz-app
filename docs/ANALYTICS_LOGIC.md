# Analytics Logic

All four analytics APIs use MongoDB aggregation pipelines over the `events` collection. No application-layer computation.

---

## 1. Learning Velocity Index

**Endpoint:** `GET /api/analytics/learning-velocity`

**Formula:**

```
LVI = (accuracy × 0.4) + (consistency × 0.3) + (speed × 0.3)
```

| Component   | Formula                         | Notes                         |
| ----------- | ------------------------------- | ----------------------------- |
| Accuracy    | `correct / total`               | 0.0 – 1.0                     |
| Consistency | `1 / (1 + stdDevPop(duration))` | 1.0 = perfectly consistent    |
| Speed       | `max(0, 1 - avg_duration / 60)` | 60s = slow (0), 0s = fast (1) |

**Pipeline stages:** `$group` → `$project` (intermediate) → `$project` (LVI) → `$sort`

**Assumptions:**

- 60s is the normalization cap for response time
- Weights (0.4/0.3/0.3) reflect accuracy as the primary measure
- Population std deviation used (events represent full history, not a sample)
- Cross-exam: LVI is computed across all exams for a user

---

## 2. Fatigue Analysis

**Endpoint:** `GET /api/analytics/fatigue/{user_id}/{quiz_id}`

Analyzes how a user's performance changes across a single quiz session.

**Segmentation:** Questions are divided into dynamic thirds based on submission order:

- Segment 1 = first ⌈n/3⌉ questions
- Segment 2 = next ⌈n/3⌉ questions
- Segment 3 = remaining questions

**Pipeline stages:** `$match` → `$setWindowFields` (rank + count) → `$project` (segment) → `$group` → `$sort`

**Key operator:** `$setWindowFields` with `$rank` assigns position numbers by submission time without collapsing documents (unlike `$group`).

**Output per segment:**

- `segment`: 1/2/3
- `accuracy`: avg correctness
- `avg_response_time`: avg seconds

---

## 3. Question Difficulty Index

**Endpoint:** `GET /api/analytics/question-difficulty`

**Formula:**

```
difficulty_score = (inverse_accuracy × 0.7) + (time_factor × 0.3)

inverse_accuracy = 100 - accuracy_percentage
time_factor      = min(avg_duration × 1.66, 100)
```

| Score range | Interpretation                      |
| ----------- | ----------------------------------- |
| 70 – 100    | Very hard (low accuracy, high time) |
| 40 – 70     | Moderate                            |
| 0 – 40      | Easy                                |

**Normalization:** `avg_duration × 1.66` maps 60s → 100, matching the 0–100 scale of accuracy. Capped at 100.

**Pipeline stages:** `$group` → `$project` (accuracy %) → `$project` (difficulty score) → `$sort`

---

## 4. Weak Area Analysis _(bonus)_

**Endpoint:** `GET /api/analytics/weak-areas/{user_id}`

Identifies which chapters a specific user should revisit, ranked by accuracy (lowest first).

**Pipeline stages:** `$match` (user) → `$group` (by chapter) → `$project` (accuracy) → `$sort`

**Output per chapter:**

- `chapter_id`, `subject_id`, `exam_id`
- `accuracy`: 0.0 – 1.0
- `quiz_sessions`: number of times the user has attempted this chapter's quiz
- `avg_response_time`

**Frontend color coding:**

- Red (`< 40%`) — needs urgent revision
- Orange (`40–70%`) — needs practice
- Green (`> 70%`) — performing well
