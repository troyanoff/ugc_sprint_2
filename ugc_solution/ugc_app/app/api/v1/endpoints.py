from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app import models, schemas
from app.crud import (
    add_bookmark,
    add_like,
    add_review,
    delete_bookmark,
    delete_like,
    delete_review,
    edit_review,
    get_movie_likes,
    get_user_bookmarks,
    get_user_likes,
)
from app.database import get_database
from app.service_functions import security_jwt

router = APIRouter()


@router.post("/movies/like")
async def like_movie(
    like: schemas.Like,
    db=Depends(get_database),
    user: dict = Depends(security_jwt),
):

    result = await add_like(db, like.movie_id, user["user_id"], like.rating)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Movie is aleady liked"
        )
    return {"message": "Like added"}


@router.delete("/movies/{movie_id}/like")
async def unlike_movie(
    movie_id: str,
    db=Depends(get_database),
    user: dict = Depends(security_jwt),
):
    result = await delete_like(db, movie_id, user["user_id"])
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Like not found")
    return {"message": "Like deleted"}


@router.post("/movies/review")
async def review_movie(
    review: schemas.Review,
    db=Depends(get_database),
    user: dict = Depends(security_jwt),
):

    model_review = models.Review(**review.model_dump() | {"user_id": user["user_id"]})

    result = await add_review(db, review.movie_id, model_review)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")
    return {"message": "Review added"}


@router.put("/movies/review/{review_id}")
async def update_review(
    review_id: str,
    updated_review: schemas.Review,
    db=Depends(get_database),
    user: dict = Depends(security_jwt),
):

    model_review = models.Review(
        **updated_review.model_dump() | {"user_id": user["user_id"]}
    )

    result = await edit_review(db, updated_review.movie_id, review_id, model_review)
    if not result:
        raise HTTPException(status_code=404, detail="Review or movie not found")
    return {"message": "Review updated"}


@router.delete("/movies/{movie_id}/review/{review_id}")
async def remove_review(
    movie_id: str,
    review_id: str,
    db=Depends(get_database),
    user: dict = Depends(security_jwt),
):
    result = await delete_review(db, movie_id, review_id)
    if not result:
        raise HTTPException(status_code=404, detail="Review or movie not found")
    return {"message": "Review deleted"}


@router.post("/users/bookmark")
async def bookmark_movie(
    bookmark: schemas.Bookmark,
    db=Depends(get_database),
    user: dict = Depends(security_jwt),
):
    result = await add_bookmark(db, user["user_id"], bookmark.movie_id)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Already bookmarked"
        )
    return {"message": "Movie bookmarked"}


@router.delete("/users/bookmark/{movie_id}")
async def remove_bookmark(
    movie_id: str,
    db=Depends(get_database),
    user: dict = Depends(security_jwt),
):
    result = await delete_bookmark(db, user["user_id"], movie_id)
    if not result:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"message": "Bookmark deleted"}


@router.get("/movies/{movie_id}/likes")
async def get_likes(
    movie_id: str, db=Depends(get_database), user: dict = Depends(security_jwt)
):
    likes = await get_movie_likes(db, movie_id)
    return likes


@router.get("/users/me/bookmarks")
async def get_my_bookmarks(
    db=Depends(get_database), user: dict = Depends(security_jwt)
):
    bookmarks = await get_user_bookmarks(db, user["user_id"])
    return bookmarks


@router.get("/users/me/likes")
async def get_my_likes(db=Depends(get_database), user: dict = Depends(security_jwt)):
    likes = await get_user_likes(db, user["user_id"])
    return likes
