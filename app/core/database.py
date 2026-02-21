from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

MONGO_URL = os.getenv("MONGO_URL","mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "chat_app")

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None


mongodb = MongoDB()

def connect_to_mongo() -> None:
    logger.info("Connecting to MongoDB...")
    mongodb.client = AsyncIOMotorClient(
        MONGO_URL,
        maxPoolSize=20,
        minPoolSize=5,
        serverSelectionTimeoutMS=5000,
    )


def close_mongo_connection() -> None:
    logger.info("Closing MongoDB connection...")
    if mongodb.client:
        mongodb.client.close()
        
def get_db():
    if mongodb.client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return mongodb.client[MONGO_DB_NAME]
