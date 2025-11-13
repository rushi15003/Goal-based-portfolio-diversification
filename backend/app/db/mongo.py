from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings

_mongo_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db

async def connect_to_mongo() -> None:
    global _mongo_client, _db
    _mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _mongo_client[settings.mongodb_db]

async def close_mongo_connection() -> None:
    global _mongo_client, _db
    if _mongo_client:
        _mongo_client.close()
    _mongo_client = None
    _db = None