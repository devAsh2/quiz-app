import json
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "quiz_db")

async def seed_database():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print("🧹 Cleaning existing data...")
    await db.users.drop()
    await db.exams.drop()
    await db.questions.drop()
    await db.events.drop()

    base_path = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    try:
        with open(os.path.join(base_path, 'users.json'), 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            await db.users.insert_many(users_data)
            print(f"✅ Inserted {len(users_data)} users.")

        with open(os.path.join(base_path, 'exams.json'), 'r', encoding='utf-8') as f:
            exam_data = json.load(f)
            await db.exams.insert_many(exam_data)
            print(f"✅ Inserted {len(exam_data)} exams.")

        with open(os.path.join(base_path, 'questions.json'), 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
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