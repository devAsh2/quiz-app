from app.schemas.analytics import UserVelocityMetrics
from typing import List
from app.schemas.analytics import FatigueAnalysisResponse, FatigueSegment
from app.schemas.analytics import QuestionDifficultyMetrics

class AnalyticsService:
    @staticmethod
    async def get_learning_velocity(db) -> List[UserVelocityMetrics]:
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
        results = await cursor.to_list(length=100)
        return results

    @staticmethod
    async def get_fatigue_analysis(db, user_id: str) -> FatigueAnalysisResponse:
        pipeline = [
            {
                # 1. Filter for the specific user
                "$match": {"user_id": user_id}
            },
            {
                # 2. Sort by quiz and time to establish the order of questions
                "$sort": {"quiz_id": 1, "answer_submitted_time": 1}
            },
            {
                # 3. Assign a sequence number (rank) to each question within its quiz
                "$setWindowFields": {
                    "partitionBy": "$quiz_id",
                    "sortBy": {"answer_submitted_time": 1},
                    "output": {
                        "question_rank": {"$rank": {}}
                    }
                }
            },
            {
                # 4. Group into segments (1-5, 6-10, 11-15)
                "$project": {
                    "is_correct": 1,
                    "response_duration": 1,
                    "segment": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lte": ["$question_rank", 5]}, "then": "1-5"},
                                {"case": {"$lte": ["$question_rank", 10]}, "then": "6-10"},
                                {"case": {"$lte": ["$question_rank", 15]}, "then": "11-15"}
                            ],
                            "default": "16+"
                        }
                    }
                }
            },
            {
                # 5. Calculate metrics per segment
                "$group": {
                    "_id": "$segment",
                    "accuracy": {"$avg": {"$cond": ["$is_correct", 1, 0]}},
                    "avg_response_time": {"$avg": "$response_duration"},
                    "segment_order": {"$min": "$question_rank"} # Used for sorting segments
                }
            },
            {
                # 6. Final sort so segments appear in order (1-5 first, etc.)
                "$sort": {"segment_order": 1}
            }
        ]

        cursor = db.events.aggregate(pipeline)
        results = await cursor.to_list(length=100)

        # Map to our Schema
        segments = [
            FatigueSegment(
                question_range=r["_id"],
                accuracy=round(r["accuracy"], 2),
                avg_response_time=round(r["avg_response_time"], 2)
            ) for r in results
        ]

        return FatigueAnalysisResponse(user_id=user_id, segments=segments)

    @staticmethod
    async def get_question_difficulty(db) -> List[QuestionDifficultyMetrics]:
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
                            # Higher score if time is high (capped at 60s for normalization)
                            {"$multiply": [{"$min": [{"$multiply": ["$avg_response_time", 1.66]}, 30]}, 0.3]}
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
        results = await cursor.to_list(length=500)
        return results