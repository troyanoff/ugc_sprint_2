# tests/conftest.py

import os
import sys

import pytest
import pytest_asyncio
from httpx import AsyncClient

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__))))
)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )
)


@pytest.fixture(scope="session", autouse=True)
def set_env_vars():
    os.environ["MONGO_DB_NAME"] = "test_db"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        base_url="http://nginx:80",
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJraW1rYW5vdnNreSIsInJvbGUiOltdLCJpcF9hZGRyZXNzIjoiMTI3LjAuMC4xIiwidXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChYMTE7IExpbnV4IHg4Nl82NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyNS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwidHlwZSI6ImFjY2VzcyIsImV4cCI6MjcxOTI2MjEwN30.7xNUV2OnHl50rF6GPh1X9wQplxtzFFkxaA3GcXD_EEg"
        },
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def db():
    # Создание подключения к тестовой базе данных
    from motor.motor_asyncio import AsyncIOMotorClient

    # client = AsyncIOMotorClient("mongodb://localhost:27017")
    client = AsyncIOMotorClient("mongodb://mongodb:27017")
    db = client.test_db
    yield db
    await client.drop_database("test_db")
