from typing import Optional

from redis.asyncio import Redis

# наша сборка поддерживает версии питона ">=3.8.1,<3.11",
# поэтому синтаксис питона 3.10 в проекте не используется
# (а-ля redis: Redis | None = None)
redis_client: Optional[Redis] = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis_client  # type: ignore
