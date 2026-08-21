import json
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Update this with your MongoDB URI if different
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "quiz_db"

async def seed_database():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # 1. Clean existing collections to start fresh
    print("🧹 Cleaning existing data...")
    await db.users.drop()
    await db.exams.drop()
    await db.questions.drop()
    await db.events.drop() # Clear old analytics data too

    # 2. Get path to JSON files (assumed to be in the same directory as seed.py)
    base_path = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    try:
        # 3. Load and Insert Users
        with open(os.path.join(base_path, 'users.json'), 'r') as f:
            users_data = json.load(f)
            # Ensure _id is handled if present as string in JSON
            for user in users_data:
                if "_id" in user: user["_id"] = ObjectId(user["_id"])
            await db.users.insert_many(users_data)
            print(f"✅ Inserted {len(users_data)} users.")

        # 4. Load and Insert Exams (Nested Hierarchy)
        with open(os.path.join(base_path, 'exam.json'), 'r') as f:
            exam_data = json.load(f)
            for exam in exam_data:
                if "_id" in exam: exam["_id"] = ObjectId(exam["_id"])
            await db.exams.insert_many(exam_data)
            print(f"✅ Inserted {len(exam_data)} exams (Hierarchy).")

        # 5. Load and Insert Questions
        with open(os.path.join(base_path, 'questions.json'), 'r') as f:
            questions_data = json.load(f)
            for q in questions_data:
                if "_id" in q: q["_id"] = ObjectId(q["_id"])
            await db.questions.insert_many(questions_data)
            print(f"✅ Inserted {len(questions_data)} questions.")

    except FileNotFoundError as e:
        print(f"❌ Error: Could not find JSON file - {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

    print("\n🚀 Database Seeding Completed Successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())