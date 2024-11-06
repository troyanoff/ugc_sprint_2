from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Review(BaseModel):
    user_id: str
    text: str
    rating: Optional[int] = None
    date: datetime = Field(default_factory=datetime.now)


class User(BaseModel):
    user_id: str
    bookmarks: List[str] = []


class Movie(BaseModel):
    movie_id: str
    likes: List[int] = []
    reviews: List[Review] = []
