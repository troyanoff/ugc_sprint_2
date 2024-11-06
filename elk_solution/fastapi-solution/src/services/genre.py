from functools import lru_cache
from typing import Any, List, Optional

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from slugify import slugify
from src.db.elastic import get_elastic
from src.db.redis_db import get_redis
from src.models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis: Redis = redis
        self.elastic: AsyncElasticsearch = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre: Optional[Genre] = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc: ObjectApiResponse[Any] = await self.elastic.get(
                index="genres", id=genre_id
            )
        except NotFoundError:
            return None
        return Genre(**doc["_source"])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None

        genre = Genre.model_validate_json(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(
            "genre_" + slugify(genre.name) + "_" + genre.id,
            genre.model_dump_json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS,
        )

    async def get_all_genres(self) -> Optional[Genre]:
        genres = await self._get_all_genres_from_elastic()
        if not genres:
            return None

        return genres

    async def exact_search_by_full_name(self, genres: List[str]):
        dsl_query = {"query": {"terms": {"name": genres}}}

        search_result = await self.elastic.search(
            index="genres",
            body=dsl_query,
        )

        genres = search_result.body["hits"]["hits"]
        return [Genre(**genre["_source"]) for genre in genres]  # type: ignore

    async def _get_all_genres_from_elastic(self):
        try:
            docs: ObjectApiResponse[Any] = await self.elastic.search(  # type: ignore
                index="genres", size=1000
            )
            docs = list(
                map(
                    lambda doc: Genre(**doc["_source"]),
                    [doc for doc in docs["hits"]["hits"]],
                )
            )
        except NotFoundError:
            return None

        return docs


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
