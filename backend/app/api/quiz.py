from fastapi import APIRouter, Depends, Header, HTTPException
from typing import List
from app.core.database import get_db
from app.schemas.quiz import UserResponse, ExamResponse, QuestionResponse, AnswerSubmission, SubmissionResult, QuizResult
from app.services.quiz_services import QuizService

router = APIRouter()

# --- Dummy Auth ---
# Returns predefined users for the login screen
@router.get("/users", response_model=List[UserResponse])
async def get_users(db = Depends(get_db)):
    cursor = db.users.find()
    return await cursor.to_list(length=None)

# --- Hierarchy ---
# Returns full nested structure: Exam -> Subject -> Chapter
@router.get("/exams", response_model=List[ExamResponse])
async def get_exams(db = Depends(get_db)):
    cursor = db.exams.find()
    return await cursor.to_list(length=None)

# --- Quiz ---
# Returns all questions for a chapter (correct_option excluded by schema)
@router.get("/questions/{chapter_id}", response_model=List[QuestionResponse])
async def get_questions(chapter_id: str, db = Depends(get_db)):
    cursor = db.questions.find({"chapter_id": chapter_id})
    questions = await cursor.to_list(length=None)

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this chapter")

    return questions

# --- Submit Answer ---
# Verifies answer, captures event for analytics, returns result to frontend
@router.post("/submit", response_model=SubmissionResult)
async def submit_answer(
    submission: AnswerSubmission,
    x_user_id: str = Header(...),  # user selected on login screen
    db = Depends(get_db)
):
    return await QuizService.process_answer(db, x_user_id, submission)

# --- Result ---
# Returns final score for a completed quiz session
@router.get("/result/{quiz_id}", response_model=QuizResult)
async def get_quiz_result(quiz_id: str, db = Depends(get_db)):
    return await QuizService.get_quiz_score(db, quiz_id)