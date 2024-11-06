from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from src.services.auth import get_jwt_with_roles
from src.services.genre import GenreService, get_genre_service
from src.settings import CACHED_RESPONSE_TTL

router = APIRouter()


class Genre(BaseModel):
    uuid: str
    name: str


@router.get("/")
@cache(expire=CACHED_RESPONSE_TTL)
async def genre_list(
    user: Annotated[dict, Depends(get_jwt_with_roles(["Subscriber", "Admin"]))],
    genre_service: GenreService = Depends(get_genre_service),
) -> List[Genre]:
    genres = await genre_service.get_all_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genres not found")

    return list(map(lambda genre: Genre(uuid=genre.id, name=genre.name), genres))  # type: ignore


@router.get("/{genre_id}", response_model=Genre)
@cache(expire=CACHED_RESPONSE_TTL)
async def genre_details(
    user: Annotated[dict, Depends(get_jwt_with_roles(["Subscriber", "Admin"]))],
    genre_id: str,
    genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Genre(uuid=genre.id, name=genre.name)
