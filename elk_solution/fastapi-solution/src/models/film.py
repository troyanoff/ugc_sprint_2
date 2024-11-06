from typing import Dict, List, Optional

import orjson
# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class OrjsonMixin:
    # Заменяем стандартную работу с json на более быструю
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Film(BaseModel, OrjsonMixin):
    id: str
    title: str
    imdb_rating: float


class FilmFull(Film):
    description: Optional[str]
    genres: List[Dict[str, str]]
    actors: List[Dict[str, str]]
    writers: List[Dict[str, str]]
    directors: List[Dict[str, str]]
