from functools import lru_cache
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from slugify import slugify
from src.db.elastic import get_elastic
from src.db.redis_db import get_redis
from src.models.film import Film, FilmFull
from src.services.genre import GenreService
from src.services.person import PersonService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis: Redis = redis
        self.elastic: AsyncElasticsearch = elastic
        self.genre_service = GenreService(redis, elastic)
        self.person_service = PersonService(redis, elastic)

    async def get_by_id(self, film_id: str) -> Optional[FilmFull]:
        film: Optional[FilmFull] = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[FilmFull]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
            doc = doc["_source"]

            genres = await self.genre_service.exact_search_by_full_name(
                genres=doc["genres"]
            )

            doc["genres"] = [genre.model_dump() for genre in genres if genre]

        except NotFoundError:
            return None
        return FilmFull(**doc)  # type: ignore

    async def _film_from_cache(self, film_id: str) -> Optional[FilmFull]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = FilmFull.model_validate_json(data)
        return film

    async def _put_film_to_cache(self, film: FilmFull):
        await self.redis.set(
            "film_" + slugify(film.title) + "_" + film.id,
            film.model_dump_json(),
            FILM_CACHE_EXPIRE_IN_SECONDS,
        )

    async def get_popular_films(
        self,
        sort_param: Optional[str],
        descending: bool,
        genre_filter: Optional[str],
        page_size: int,
        page_number: int,
    ) -> List[Film]:
        body: dict = {"query": {"match_all": {}}}
        if sort_param:
            body["sort"] = [{sort_param: {"order": "desc" if descending else "asc"}}]
        if genre_filter:
            genre = await self.genre_service.get_by_id(genre_id=genre_filter)
            if genre:
                body["query"] = {"bool": {"filter": [{"term": {"genres": genre.name}}]}}

        return await self.elastic_search(body, page_number, page_size)

    async def search_films(
        self, query: str, page_number: int, page_size: int
    ) -> List[Film]:
        body: dict = {
            "query": {"match": {"title": {"query": query, "fuzziness": "AUTO"}}},
            "sort": ["_score"],
        }

        return await self.elastic_search(body, page_number, page_size)

    async def elastic_search(
        self, body: dict, page_number: int, page_size: int
    ) -> List[Film]:
        results = await self.elastic.search(
            index="movies",
            body=body,
            from_=(page_number - 1) * page_size,
            size=page_size,
        )
        films_json = results.body["hits"]["hits"]
        return [Film(**film["_source"]) for film in films_json]


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
