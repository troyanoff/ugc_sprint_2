from http import HTTPStatus
from typing import Annotated, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from src.services.auth import get_jwt_with_roles
from src.services.film import FilmService, get_film_service
from src.settings import CACHED_RESPONSE_TTL

router = APIRouter()


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class RawPerson(BaseModel):
    uuid: str
    full_name: str


class Genre(BaseModel):
    uuid: str
    name: str


class FilmFull(Film):
    description: Optional[str]
    genre: List[Dict[str, str]]
    actors: List[Dict[str, str]]
    writers: List[Dict[str, str]]
    directors: List[Dict[str, str]]


@router.get("/search", response_model=List[Film])
@cache(expire=CACHED_RESPONSE_TTL)
async def search_films(
    user: Annotated[dict, Depends(get_jwt_with_roles(["Subscriber", "Admin"]))],
    query: str = Query(None),
    page_size: int = Query(50, description="Pagination page size", ge=1),
    page_number: int = Query(1, description="Pagination page number", ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> List[Film]:

    if query:
        films = await film_service.search_films(
            query=query, page_size=page_size, page_number=page_number
        )
        return [
            Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
            for film in films
        ]
    return []


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=FilmFull)
@cache(expire=CACHED_RESPONSE_TTL)
async def film_details(
    user: Annotated[dict, Depends(get_jwt_with_roles(["Subscriber", "Admin"]))],
    film_id: str,
    film_service: FilmService = Depends(get_film_service),
) -> FilmFull:

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    film.genres = [
        Genre(uuid=genre["id"], name=genre["name"]).model_dump()
        for genre in film.genres
    ]

    film.actors = [
        RawPerson(uuid=actor["id"], full_name=actor["name"]).model_dump()
        for actor in film.actors
    ]

    film.writers = [
        RawPerson(uuid=writer["id"], full_name=writer["name"]).model_dump()
        for writer in film.writers
    ]

    film.directors = [
        RawPerson(uuid=director["id"], full_name=director["name"]).model_dump()
        for director in film.directors
    ]

    return FilmFull(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


@router.get("/", response_model=List[Film])
@cache(expire=CACHED_RESPONSE_TTL)
async def popular_films(
    sort: str = Query(None),
    genre: str = Query(None),
    page_size: int = Query(50, description="Pagination page size", ge=1),
    page_number: int = Query(1, description="Pagination page number", ge=1),
    film_service: FilmService = Depends(get_film_service),
) -> List[Film]:

    descending = False
    if sort:
        descending = sort.startswith("-")
        sort = sort.lstrip("-")

    films = await film_service.get_popular_films(
        sort_param=sort,
        descending=descending,
        genre_filter=genre,
        page_size=page_size,
        page_number=page_number,
    )
    return [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
