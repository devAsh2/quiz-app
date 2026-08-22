from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


# --- Auth ---
class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(alias="_id")
    username: str
    email: str


# --- Hierarchy ---
class ChapterResponse(BaseModel):
    id: str
    name: str


class SubjectResponse(BaseModel):
    id: str
    name: str
    chapters: List[ChapterResponse]


class ExamResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(alias="_id")
    name: str
    subjects: List[SubjectResponse]


# --- Quiz ---
class QuestionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(alias="_id")
    text: str
    options: List[str]


class AnswerSubmission(BaseModel):
    quiz_id: str
    question_id: str
    selected_option: int
    question_shown_time: datetime
    answer_submitted_time: datetime


class SubmissionResult(BaseModel):
    is_correct: bool
    correct_option: Optional[int] = None


class QuizResult(BaseModel):
    total: int
    score: int
    percentage: float