# Verify the answer.
# Calculate the time difference.
# Create the EventDocument and save it to MongoDB.

from datetime import datetime
from app.models.domain import EventDocument
from app.schemas.quiz import AnswerSubmission, SubmissionResult
from fastapi import HTTPException

class QuizService:
    @staticmethod
    async def process_answer(db, user_id: str, submission: AnswerSubmission):
        """
        1. Fetch the question from DB to get the 'true' correct answer.
        2. Calculate the duration between shown_time and submitted_time.
        3. Determine if the user's choice is correct.
        4. Capture ALL required event data for future analytics.
        """

        # 1. Fetch the static question data
        question = await db.questions.find_one({"_id": submission.question_id})

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        # 2. Calculate Response Duration (in seconds)
        duration = (submission.answer_submitted_time - submission.question_shown_time).total_seconds()

        # Ensure duration isn't negative (edge case for system clock issues)
        duration = max(0, duration)

        # 3. Check correctness
        is_correct = (submission.selected_option == question["correct_option"])

        # 4. Construct the Event Document
        event_record = EventDocument(
            user_id=user_id,
            quiz_id=submission.quiz_id,
            question_id=submission.question_id,
            exam_id=question["exam_id"],
            subject_id=question["subject_id"],
            chapter_id=question["chapter_id"],
            question_shown_time=submission.question_shown_time,
            answer_submitted_time=submission.answer_submitted_time,
            response_duration=duration,
            selected_option=submission.selected_option,
            is_correct=is_correct,
            marks=question["marks"]
        )

        # 5. Save to the 'events' collection
        await db.events.insert_one(event_record.model_dump(exclude={"id"}))

        # 6. Return the result to the frontend
        return SubmissionResult(
            is_correct=is_correct,
            correct_option=question["correct_option"]
        )

    @staticmethod
    async def get_quiz_score(db, quiz_id: str):
        """
        Aggregates all event records for a quiz session and returns the final score.
        """
        pipeline = [
            {"$match": {"quiz_id": quiz_id}},
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "score": {"$sum": {"$cond": ["$is_correct", "$marks", 0]}},
                    "total_marks": {"$sum": "$marks"}
                }
            }
        ]
        cursor = db.events.aggregate(pipeline)
        results = await cursor.to_list(length=1)

        if not results:
            return {"total": 0, "score": 0, "percentage": 0.0}

        r = results[0]
        return {
            "total": r["total"],
            "score": r["score"],
            "percentage": (r["score"] / r["total_marks"] * 100) if r["total_marks"] > 0 else 0.0
        }