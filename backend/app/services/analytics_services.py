from app.schemas.analytics import UserVelocityMetrics
from typing import List
from app.schemas.analytics import FatigueAnalysisResponse, FatigueSegment
from app.schemas.analytics import QuestionDifficultyMetrics, WeakAreaMetrics

class AnalyticsService:
    @staticmethod
    async def get_learning_velocity(db) -> List[UserVelocityMetrics]:
        """
        Calculates a Learning Velocity Index for every user based on
        accuracy, average response time, and consistency of response time.
        Returns users ranked from highest to lowest index.
        """
        pipeline = [
            {
                # 1. Group by user and calculate raw metrics
                "$group": {
                    "_id": "$user_id",
                    "total_attempts": {"$sum": 1},
                    "correct_count": {"$sum": {"$cond": ["$is_correct", 1, 0]}},
                    "avg_response_time": {"$avg": "$response_duration"},
                    "std_dev_time": {"$stdDevPop": "$response_duration"}
                }
            },
            {
                # 2. Calculate intermediate scores
                "$project": {
                    "user_id": "$_id",
                    "accuracy": {"$divide": ["$correct_count", "$total_attempts"]},
                    "avg_response_time": 1,
                    # Consistency: 1 / (1 + std_dev). If std_dev is 0, score is 1 (perfect)
                    "consistency_score": {
                        "$divide": [1, {"$add": [1, "$std_dev_time"]}]
                    }
                }
            },
            {
                # 3. Calculate Final Index (Weighted)
                # Formula: (Acc * 0.4) + (Consistency * 0.3) + (NormalizedSpeed * 0.3)
                # Note: For Speed, we assume 60s is slow (0) and 0s is fast (1)
                "$project": {
                    "user_id": 1,
                    "accuracy": 1,
                    "avg_response_time": 1,
                    "consistency_score": 1,
                    "learning_velocity_index": {
                        "$add": [
                            {"$multiply": ["$accuracy", 0.4]},
                            {"$multiply": ["$consistency_score", 0.3]},
                            {"$multiply": [
                                {"$max": [0, {"$subtract": [1, {"$divide": ["$avg_response_time", 60]}]}]}, 
                                0.3
                            ]}
                        ]
                    }
                }
            },
            {
                # 4. Rank users by the index
                "$sort": {"learning_velocity_index": -1}
            }
        ]

        cursor = db.events.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return results

    @staticmethod
    async def get_fatigue_analysis(db, user_id: str, quiz_id: str) -> FatigueAnalysisResponse:
        """
        Analyzes how a user's accuracy and response time change across
        the start, middle, and end thirds of a specific quiz session.
        """
        pipeline = [
            {
                # 1. Filter for the specific user and quiz session
                "$match": {"user_id": user_id, "quiz_id": quiz_id}
            },
            {
                # 2. Assign rank and total count per session for dynamic segment calculation
                "$setWindowFields": {
                    "partitionBy": "$quiz_id",
                    "sortBy": {"answer_submitted_time": 1},
                    "output": {
                        "question_rank": {"$rank": {}},
                        "total_questions": {"$count": {}}
                    }
                }
            },
            {
                # 3. Assign segment label based on thirds
                "$project": {
                    "is_correct": 1,
                    "response_duration": 1,
                    "question_rank": 1,
                    "segment": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lte": ["$question_rank", {"$ceil": {"$divide": ["$total_questions", 3]}}]}, "then": 1},
                                {"case": {"$lte": ["$question_rank", {"$ceil": {"$multiply": [{"$divide": ["$total_questions", 3]}, 2]}}]}, "then": 2}
                            ],
                            "default": 3
                        }
                    }
                }
            },
            {
                # 4. Calculate metrics per segment
                "$group": {
                    "_id": "$segment",
                    "accuracy": {"$avg": {"$cond": ["$is_correct", 1, 0]}},
                    "avg_response_time": {"$avg": "$response_duration"}
                }
            },
            {
                # 5. Sort so segment 1 → 2 → 3
                "$sort": {"_id": 1}
            }
        ]

        cursor = db.events.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        segments = [
            FatigueSegment(
                segment=r["_id"],
                accuracy=round(r["accuracy"], 2),
                avg_response_time=round(r["avg_response_time"], 2)
            ) for r in results
        ]

        return FatigueAnalysisResponse(user_id=user_id, quiz_id=quiz_id, segments=segments)

    @staticmethod
    async def get_question_difficulty(db) -> List[QuestionDifficultyMetrics]:
        """
        Derives a difficulty score for every question using inverse accuracy
        and average response time. Returns questions ranked hardest to easiest.
        """
        pipeline = [
            {
                # 1. Group by question_id and aggregate raw attempt data
                "$group": {
                    "_id": "$question_id",
                    "total_attempts": {"$sum": 1},
                    "correct_count": {"$sum": {"$cond": ["$is_correct", 1, 0]}},
                    "avg_response_time": {"$avg": "$response_duration"}
                }
            },
            {
                # 2. Calculate Accuracy Percentage
                "$project": {
                    "question_id": "$_id",
                    "total_attempts": 1,
                    "avg_response_time": 1,
                    "accuracy_percentage": {
                        "$multiply": [{"$divide": ["$correct_count", "$total_attempts"]}, 100]
                    }
                }
            },
            {
                # 3. Derive Difficulty Score
                # Logic: (Inverse of Accuracy * 0.7) + (Response Time factor * 0.3)
                # We cap the Response Time factor at 60 seconds.
                "$project": {
                    "question_id": 1,
                    "total_attempts": 1,
                    "accuracy_percentage": 1,
                    "avg_response_time": 1,
                    "difficulty_score": {
                        "$add": [
                            # Higher score if accuracy is low
                            {"$multiply": [{"$subtract": [100, "$accuracy_percentage"]}, 0.7]},
                            # Higher score if time is high (capped at 60s → mapped to 0-100)
                            {"$multiply": [{"$min": [{"$multiply": ["$avg_response_time", 1.66]}, 100]}, 0.3]}
                        ]
                    }
                }
            },
            {
                # 4. Rank from Hardest (High Score) to Easiest (Low Score)
                "$sort": {"difficulty_score": -1}
            }
        ]

        cursor = db.events.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return results

    @staticmethod
    async def get_weak_areas(db, user_id: str) -> List[WeakAreaMetrics]:
        """
        Groups all of a user's events by chapter and ranks by accuracy (lowest first).
        Identifies which chapters the user should revisit.
        """
        pipeline = [
            {
                # 1. Filter events for this user only
                "$match": {"user_id": user_id}
            },
            {
                # 2. Group by chapter, carry subject and exam, compute metrics
                "$group": {
                    "_id": "$chapter_id",
                    "subject_id": {"$first": "$subject_id"},
                    "exam_id": {"$first": "$exam_id"},
                    "total_attempts": {"$sum": 1},
                    "correct_count": {"$sum": {"$cond": ["$is_correct", 1, 0]}},
                    "avg_response_time": {"$avg": "$response_duration"}
                }
            },
            {
                # 3. Calculate accuracy per chapter
                "$project": {
                    "chapter_id": "$_id",
                    "subject_id": 1,
                    "exam_id": 1,
                    "total_attempts": 1,
                    "avg_response_time": 1,
                    "accuracy": {"$divide": ["$correct_count", "$total_attempts"]}
                }
            },
            {
                # 4. Sort by accuracy ascending (weakest chapters first)
                "$sort": {"accuracy": 1}
            }
        ]

        cursor = db.events.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return results