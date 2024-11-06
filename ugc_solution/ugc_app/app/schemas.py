from typing import List, Optional

from pydantic import BaseModel


class Like(BaseModel):
    movie_id: str
    rating: int


class Bookmark(BaseModel):
    movie_id: str


class Review(BaseModel):
    movie_id: str
    text: str
    rating: Optional[int] = None


class User(BaseModel):
    user_id: str
    bookmarks: List[str] = []


class Movie(BaseModel):
    movie_id: str
    likes: List[int] = []
    reviews: List[Review] = []
