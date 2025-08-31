from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    sync_client: MongoClient = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db.sync_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    print("Connected to MongoDB")

async def close_mongo_connection():
    if db.client:
        db.client.close()
    if db.sync_client:
        db.sync_client.close()
    print("Disconnected from MongoDB")

def get_database():
    return db.client.recommendation_engine

def get_sync_database():
    return db.sync_client.recommendation_engine
