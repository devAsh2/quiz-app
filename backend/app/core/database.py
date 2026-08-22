from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_db():
    return db.client[os.getenv("DB_NAME", "quiz_db")]

async def create_indexes():
    database = db.client[os.getenv("DB_NAME", "quiz_db")]

    # 1. Index for fetching questions by chapter
    await database.questions.create_index([("chapter_id", 1)])

    # 2. Indexes for Analytics
    await database.events.create_index([("user_id", 1)])
    await database.events.create_index([("question_id", 1)])
    await database.events.create_index([("quiz_id", 1)])

    # 3. Compound index for Fatigue Analysis (user + quiz session, sorted by time)
    await database.events.create_index([("user_id", 1), ("quiz_id", 1), ("answer_submitted_time", 1)])

    print("🚀 Database Indexes Created Successfully")