import logging

import sentry_sdk
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from src.api.v1 import films, genres, persons, service
from src.core.config import settings
from src.core.logger import LOGGING
from src.db import elastic, redis_db

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis_db.redis_client = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(hosts=[f"http://{settings.elastic_connect}"])
    FastAPICache.init(RedisBackend(redis_db.redis_client), prefix="fastapi-cache")


@app.on_event("shutdown")
async def shutdown():
    await redis_db.redis_client.close()
    await elastic.es.close()


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


app.include_router(service.router, tags=["service"])
app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
