from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db, AsyncIOMotorClient
import os
from dotenv import load_dotenv
from app.api.quiz import router as quiz_router
from app.api.analytics import router as analytics_router

load_dotenv()

app = FastAPI(title="WhatsApp Style Quiz API")

# Allow Frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db.client = AsyncIOMotorClient(mongo_url)
    
    # Call the indexing function here
    from app.core.database import create_indexes
    await create_indexes()
    
    print("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    db.client.close()
    print("Disconnected from MongoDB")

# Placeholder for future routes
@app.get("/")
async def root():
    return {"message": "Quiz API is running"}

# Next Step: app.include_router(quiz.router)
app.include_router(quiz_router, prefix="/api", tags=["Quiz Flow"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])