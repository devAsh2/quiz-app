from pydantic import BaseModel
from typing import List


# --- Learning Velocity ---
class UserVelocityMetrics(BaseModel):
    user_id: str
    accuracy: float
    avg_response_time: float
    consistency_score: float
    learning_velocity_index: float


# --- Fatigue Analysis ---
class FatigueSegment(BaseModel):
    segment: int  # 1 = first third, 2 = middle third, 3 = last third
    accuracy: float
    avg_response_time: float


class FatigueAnalysisResponse(BaseModel):
    user_id: str
    quiz_id: str
    segments: List[FatigueSegment]


# --- Question Difficulty ---
class QuestionDifficultyMetrics(BaseModel):
    question_id: str
    total_attempts: int
    accuracy_percentage: float
    avg_response_time: float
    difficulty_score: float


# --- Weak Area Analysis ---
class WeakAreaMetrics(BaseModel):
    chapter_id: str
    subject_id: str
    exam_id: str
    total_attempts: int
    accuracy: float
    avg_response_time: float