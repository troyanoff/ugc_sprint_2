from pydantic import BaseModel
from src.models.film import OrjsonMixin


class Genre(BaseModel, OrjsonMixin):
    id: str
    name: str
