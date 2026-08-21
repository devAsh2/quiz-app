from pydantic import BaseModel
from typing import List

# 1. Learning Velocity Index
class UserVelocityMetrics(BaseModel):
    user_id: str
    accuracy: float
    avg_response_time: float
    consistency_score: float
    learning_velocity_index: float

# 2. Fatigue Analysis
class FatigueSegment(BaseModel):
    question_range: str # e.g., "1-5"
    accuracy: float
    avg_response_time: float

class FatigueAnalysisResponse(BaseModel):
    user_id: str
    segments: List[FatigueSegment]

# 3. Question Difficulty Index
class QuestionDifficultyMetrics(BaseModel):
    question_id: str
    total_attempts: int
    accuracy_percentage: float
    avg_response_time: float
    difficulty_score: float