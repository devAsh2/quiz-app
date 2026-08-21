# backend/app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_db():
    return db.client.quiz_db # quiz_db is the database name

async def create_indexes():
    # Get the collections
    db_name = db.client.quiz_db
    
    # 1. Index for fetching questions by chapter
    await db_name.questions.create_index([("chapter_id", 1)])
    
    # 2. Indexes for Analytics (Critical for 50% weightage)
    await db_name.events.create_index([("user_id", 1)])
    await db_name.events.create_index([("question_id", 1)])
    await db_name.events.create_index([("quiz_id", 1)])
    
    # 3. Compound Index for Fatigue Analysis (Optimizes sorting by time)
    await db_name.events.create_index([("user_id", 1), ("answer_submitted_time", 1)])
    
    print("🚀 Database Indexes Created Successfully")