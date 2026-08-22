from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from typing import List, Optional, Annotated
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v))]


# --- USER ---
class UserDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(default=None, alias="_id")
    username: str
    email: str


# --- HIERARCHY (nested inside EXAM) ---
class ChapterDocument(BaseModel):
    id: str
    name: str


class SubjectDocument(BaseModel):
    id: str
    name: str
    chapters: List[ChapterDocument]


class ExamDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    subjects: List[SubjectDocument]


# --- QUESTION ---
class QuestionDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(default=None, alias="_id")
    exam_id: str
    subject_id: str
    chapter_id: str
    text: str
    options: List[str]
    correct_option: int
    marks: int = 1


# --- EVENT (analytics engine) ---
class EventDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    quiz_id: str
    question_id: str
    exam_id: str
    subject_id: str
    chapter_id: str
    question_shown_time: datetime
    answer_submitted_time: datetime
    response_duration: float
    selected_option: int
    is_correct: bool
    marks: int
