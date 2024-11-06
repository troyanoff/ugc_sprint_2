from http import HTTPStatus
from typing import Annotated, Dict, List, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from src.services.auth import get_jwt_with_roles
from src.services.person import PersonService, get_person_service
from src.settings import CACHED_RESPONSE_TTL

router = APIRouter()


class Person(BaseModel):
    uuid: UUID
    full_name: str
    # наша сборка поддерживает версии питона ">=3.8.1,<3.11",
    # поэтому синтаксис питона 3.10 в проекте не используется
    # (а-ля redis: Redis | None = None)
    films: List[Dict[str, Union[UUID, List[str]]]]


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


@router.get("/search")
@cache(expire=CACHED_RESPONSE_TTL)
async def person_search(
    user: Annotated[dict, Depends(get_jwt_with_roles(["Subscriber", "Admin"]))],
    query: str,
    page_size: int = Query(50, description="Pagination page size", ge=1),
    page_number: int = Query(1, description="Pagination page number", ge=1),
    person_service: PersonService = Depends(get_person_service),
) -> List[Person]:

    persons = await person_service.search_by_full_name(query, page_number, page_size)

    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return [
        Person(uuid=person.id, full_name=person.full_name, films=person.films)
        for person in persons
    ]


@router.get("/{person_id}", response_model=Person)
@cache(expire=CACHED_RESPONSE_TTL)
async def person_details(
    user: Annotated[dict, Depends(get_jwt_with_roles(["Subscriber", "Admin"]))],
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return Person(uuid=person.id, full_name=person.full_name, films=person.films)


@router.get("/{person_id}/film")
@cache(expire=CACHED_RESPONSE_TTL)
async def person_film_list(
    user: Annotated[dict, Depends(get_jwt_with_roles(["Subscriber", "Admin"]))],
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
) -> list[Film]:
    films = await person_service.get_films_by_person_id(person_id)

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
