from fastapi import APIRouter, Depends  # type: ignore[reportMissingImports]
from app.core.database import get_db
from app.services.analytics_services import AnalyticsService
from app.schemas.analytics import UserVelocityMetrics, FatigueAnalysisResponse, QuestionDifficultyMetrics
from typing import List

router = APIRouter()

@router.get("/learning-velocity", response_model=List[UserVelocityMetrics])
async def learning_velocity(db = Depends(get_db)):
    return await AnalyticsService.get_learning_velocity(db)

@router.get("/fatigue/{user_id}", response_model=FatigueAnalysisResponse)
async def fatigue_analysis(user_id: str, db = Depends(get_db)):
    return await AnalyticsService.get_fatigue_analysis(db, user_id)

@router.get("/question-difficulty", response_model=List[QuestionDifficultyMetrics])
async def question_difficulty(db = Depends(get_db)):
    return await AnalyticsService.get_question_difficulty(db)