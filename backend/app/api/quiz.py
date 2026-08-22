from fastapi import APIRouter, Depends, Header, HTTPException
from typing import List
from app.core.database import get_db
from app.schemas.quiz import ExamResponse, QuestionRequest, AnswerSubmission, SubmissionResult
from app.services.quiz_services import QuizService
from app.models.domain import UserDocument

router = APIRouter()

# --- 1. DUMMY AUTH: GET USERS ---
# Requirement: "A simple login screen where the user selects a predefined user"
@router.get("/users", response_model=List[UserDocument])
async def get_users(db = Depends(get_db)):
    cursor = db.users.find()
    return await cursor.to_list(length=100)

# --- 2. HIERARCHY: GET EXAMS/SUBJECTS/CHAPTERS ---
# Requirement: Flow is Exam -> Subject -> Chapter
@router.get("/exams", response_model=List[ExamResponse])
async def get_exams(db = Depends(get_db)):
    # Returns the nested structure defined in your model
    cursor = db.exams.find()
    return await cursor.to_list(length=10)

# --- 3. QUIZ: GET QUESTIONS BY CHAPTER ---
# Requirement: "Display one question at a time" (Frontend handles the 'one at a time' logic)
@router.get("/questions/{chapter_id}", response_model=List[QuestionRequest])
async def get_questions(chapter_id: str, db = Depends(get_db)):
    cursor = db.questions.find({"chapter_id": chapter_id})
    questions = await cursor.to_list(length=100)
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this chapter")
    
    # QuestionRequest schema automatically removes 'correct_option' for security
    return questions

# --- 4. SUBMIT: POST ANSWER ---
# Requirement: Capture all Event Tracking data
@router.post("/submit", response_model=SubmissionResult)
async def submit_answer(
    submission: AnswerSubmission, 
    x_user_id: str = Header(...), # We pass the selected User ID in the header
    db = Depends(get_db)
):
    return await QuizService.process_answer(db, x_user_id, submission)

# --- 5. RESULT: GET FINAL SCORE ---
# Requirement: "Show final score after quiz completion"
@router.get("/result/{quiz_id}")
async def get_quiz_result(quiz_id: str, db = Depends(get_db)):
    return await QuizService.get_quiz_score(db, quiz_id)