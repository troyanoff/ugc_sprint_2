from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

client = AsyncIOMotorClient("mongodb://" + settings.mongo_connect)
database = client[settings.mongo_db_name]


async def get_database():
    return database
