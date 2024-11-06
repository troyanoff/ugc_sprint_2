import pickle
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from slugify import slugify
from src.db.elastic import get_elastic
from src.db.redis_db import get_redis
from src.models.film import Film
from src.models.person import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis: Redis = redis
        self.elastic: AsyncElasticsearch = elastic

    def _get_query_for_person_films(self, person_ids: List[str]) -> dict:
        return {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"terms": {"actors.id": person_ids}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"terms": {"directors.id": person_ids}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"terms": {"writers.id": person_ids}},
                            }
                        },
                    ]
                }
            }
        }

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person: Optional[Person] = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc: ObjectApiResponse[Any] = await self.elastic.get(
                index="persons",
                id=person_id,
            )
            person_films = await self._get_person_film_roles_from_elastic(
                [person_id],
            )
            [film.pop("person_id", None) for film in person_films]

            data: dict = doc["_source"]
            data["films"] = person_films

        except NotFoundError:
            return None
        return Person(**data)

    async def _get_person_film_roles_from_elastic(
        self, person_ids: List[str]
    ) -> List[Dict[str, Union[UUID, List[str]]]]:
        try:
            dsl_query = self._get_query_for_person_films(person_ids)

            films_response: ObjectApiResponse[Any] = await self.elastic.search(
                index="movies",
                body=dsl_query,
                size=1000,
            )

            films_list: List[dict] = [
                film["_source"] for film in films_response.body["hits"]["hits"]
            ]

            films_field: List[Dict[str, Union[UUID, List[str]]]] = []
            for film in films_list:
                for person_id in person_ids:
                    roles = []
                    role_fields: dict[str, str] = {
                        "directors": "director",
                        "actors": "actor",
                        "writers": "writer",
                    }

                    for role_field, role_name in role_fields.items():
                        ids: set = {person["id"] for person in film[role_field]}
                        if person_id in ids:
                            roles.append(role_name)

                    if roles:
                        films_field.append(
                            {
                                "person_id": UUID(person_id),
                                "uuid": UUID(film["id"]),
                                "roles": sorted(roles),
                            }
                        )

        except NotFoundError:
            return []
        return films_field

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person: Person = Person.model_validate_json(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(
            "person_" + slugify(person.full_name) + "_" + person.id,
            person.model_dump_json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS,
        )

    async def get_films_by_person_id(
        self,
        person_id: str,
    ) -> Optional[Union[list, List[Film]]]:
        films = await self._person_films_from_cache(person_id)
        if not films:
            films = await self._get_person_films_from_elastic(person_id)
            if not films:
                return []

        await self._put_person_films_to_cache(person_id, films)
        return films

    async def _get_person_films_from_elastic(
        self, person_id: str
    ) -> Union[list, List[Film]]:
        try:
            dsl_query = self._get_query_for_person_films(
                [
                    person_id,
                ]
            )
            films_response: ObjectApiResponse[Any] = await self.elastic.search(
                index="movies", body=dsl_query, size=1000
            )
            films_list: List[Film] = [
                Film(**film["_source"]) for film in films_response.body["hits"]["hits"]
            ]

        except NotFoundError:
            return []
        return films_list

    async def _person_films_from_cache(self, person_id: str):
        data: bytes = await self.redis.get(person_id + "_films")  # type: ignore
        if not data:
            return None

        films_data: list = pickle.loads(data)
        return films_data

    async def _put_person_films_to_cache(
        self, person_id: str, films: Union[list, List[dict]]
    ):
        await self.redis.set(
            person_id + "_films", pickle.dumps(films), PERSON_CACHE_EXPIRE_IN_SECONDS
        )

    async def search_by_full_name(
        self, query: str, page_number: int, page_size: int
    ) -> Union[list, List[Person]]:
        must_queries = []
        for stem in query.split():
            must_query = {"match": {"full_name": {"query": stem, "fuzziness": "AUTO"}}}
            must_queries.append(must_query)

        dsl_query = {"bool": {"must": must_queries}}

        search_result: ObjectApiResponse[Any] = await self.elastic.search(
            index="persons",
            query=dsl_query,
            from_=(page_number - 1) * page_size,
            size=page_size,
        )

        persons_data = search_result.body["hits"]["hits"]

        persons: Union[list, List[Person]] = []
        person_ids_to_get_film_roles: Union[list, List[str]] = []

        for person in persons_data:
            person_id: str = person["_source"]["id"]

            person_from_cache: Optional[Person] = await self._person_from_cache(
                person_id
            )
            if not person_from_cache:
                person_source = person["_source"]

                person_obj = Person(
                    id=person_source["id"],
                    full_name=person_source["full_name"],
                    films=None,
                )

                # append to persons to keep _score-based ordering of persons
                persons.append(person_obj)
                person_ids_to_get_film_roles.append(person_obj.id)
            else:
                persons.append(person_from_cache)

        person_films = await self._get_person_film_roles_from_elastic(
            person_ids_to_get_film_roles
        )

        films_dict: Dict[str, List[Dict[str, Union[UUID, List[str]]]]] = {}
        for film in person_films:
            films_dict.setdefault(str(film["person_id"]), []).append(
                {"uuid": film["uuid"], "roles": film["roles"]}
            )

        for person in persons:
            if person.films is None:
                person.films = films_dict.get(person.id, [])
                await self._put_person_to_cache(person)

        return persons


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
