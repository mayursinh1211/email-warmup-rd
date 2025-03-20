from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from ..core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.DATABASE_NAME]
        print("Connected to MongoDB.")

    @classmethod
    async def close_database_connection(cls):
        if cls.client is not None:
            cls.client.close()
            print("MongoDB connection closed.")
