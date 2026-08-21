# Verify the answer.
# Calculate the time difference.
# Create the EventDocument and save it to MongoDB.

from datetime import datetime
from bson import ObjectId
from app.models.domain import EventDocument
from app.schemas.quiz import AnswerSubmission, SubmissionResult
from fastapi import HTTPException

class QuizService:
    @staticmethod
    async def process_answer(db, user_id: str, submission: AnswerSubmission):
        """
        Logic: 
        1. Fetch the question from DB to get the 'true' correct answer.
        2. Calculate the duration between shown_time and submitted_time.
        3. Determine if the user's choice is correct.
        4. Capture ALL required event data for future analytics.
        """
        
        # 1. Fetch the static question data
        # We need this to get correct_option, exam_id, subject_id, and chapter_id
        question = await db.questions.find_one({"_id": submission.question_id})
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        # 2. Calculate Response Duration (in seconds)
        duration = (submission.answer_submitted_time - submission.question_shown_time).total_seconds()
        
        # Ensure duration isn't negative (edge case for system clock issues)
        duration = max(0, duration)

        # 3. Check correctness
        is_correct = (submission.selected_option == question["correct_option"])

        # 4. Construct the Event Document (As per PDF page 3 requirements)
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
            is_correct=is_correct
        )

        # 5. Save to the 'events' collection
        # .dict(by_alias=True) ensures we don't accidentally save internal Pydantic fields
        await db.events.insert_one(event_record.dict(exclude={"id"}))

        # 6. Return the result to the frontend
        return SubmissionResult(
            is_correct=is_correct,
            correct_option=question["correct_option"] # Optional: reveals answer after choice
        )

    @staticmethod
    async def get_quiz_score(db, quiz_id: str):
        """
        Logic: Summarizes the result for a specific sitting.
        Used for the 'Result' page in the UI flow.
        """
        cursor = db.events.find({"quiz_id": quiz_id})
        events = await cursor.to_list(length=100)
        
        total_questions = len(events)
        correct_answers = sum(1 for e in events if e["is_correct"])
        
        return {
            "total": total_questions,
            "score": correct_answers,
            "percentage": (correct_answers / total_questions * 100) if total_questions > 0 else 0
        }