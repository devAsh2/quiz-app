from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- UI Flow Schemas ---
class ChapterResponse(BaseModel):
    id: str
    name: str

class SubjectResponse(BaseModel):
    id: str
    name: str
    chapters: List[ChapterResponse]

class ExamResponse(BaseModel):
    id: str
    name: str
    subjects: List[SubjectResponse]

# --- Quiz Schemas ---
class QuestionRequest(BaseModel):
    """Used for fetching a question"""
    id: str
    text: str
    options: List[str]
    # correct_option is ABSENT for security

class AnswerSubmission(BaseModel):
    """Data sent by frontend when user clicks 'Next'"""
    quiz_id: str
    question_id: str
    selected_option: int
    question_shown_time: datetime
    answer_submitted_time: datetime

class SubmissionResult(BaseModel):
    """Data sent back to frontend after 'Next'"""
    is_correct: bool
    correct_option: Optional[int] = None # Optional: show correct answer after click