from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

# Helper to handle MongoDB ObjectId as string
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)

# --- USER MODEL ---
class UserDocument(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: str

# --- HIERARCHY MODEL (Nested) ---
class ChapterDocument(BaseModel):
    id: str # Internal UUID/String
    name: str

class SubjectDocument(BaseModel):
    id: str
    name: str
    chapters: List[ChapterDocument]

class ExamDocument(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    subjects: List[SubjectDocument]

# --- QUESTION MODEL (Referenced) ---
class QuestionDocument(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    exam_id: str
    subject_id: str
    chapter_id: str
    text: str
    options: List[str]
    correct_option: int # Internal truth
    marks: int = 1

# --- EVENT TRACKING MODEL (The Analytics Engine) ---
class EventDocument(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    quiz_id: str
    question_id: str
    exam_id: str
    subject_id: str
    chapter_id: str
    
    question_shown_time: datetime
    answer_submitted_time: datetime
    response_duration: float # Calculated (seconds)
    
    selected_option: int
    is_correct: bool # Calculated (bool)

    class Config:
        populate_by_name = True