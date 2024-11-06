import uuid

from app import models


async def add_like(db, movie_id, user_id, rating):
    is_already_liked = await db.movies.find_one(
        {"movie_id": movie_id, f"likes.{user_id}": {"$exists": True}}
    )
    if is_already_liked:
        return False

    if not await _movie_exists(db, movie_id):
        await _add_movie(db, movie_id)

    if not await _user_exists(db, user_id):
        await _add_user(db, user_id)

    result = await db.movies.update_one(
        {"movie_id": movie_id, f"likes.{user_id}": {"$exists": False}},
        {"$set": {f"likes.{user_id}": rating}, "$inc": {"likes_count": 1}},
    )

    if result.modified_count > 0:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {f"likes.{movie_id}": rating}},
        )

    return True


async def delete_like(db, movie_id, user_id):
    result = await db.movies.update_one(
        {"movie_id": movie_id, f"likes.{user_id}": {"$exists": True}},
        {"$unset": {f"likes.{user_id}": ""}, "$inc": {"likes_count": -1}},
    )

    if result.modified_count > 0:
        await db.users.update_one(
            {"user_id": user_id, f"likes.{movie_id}": {"$exists": True}},
            {"$unset": {f"likes.{movie_id}": ""}},
        )
        return True
    else:
        return False


async def add_review(db, movie_id, review: models.Review):

    if not await _movie_exists(db, movie_id):
        await _add_movie(db, movie_id)

    if not await _user_exists(db, review.user_id):
        await _add_user(db, review.user_id)

    await db.movies.update_one(
        {"movie_id": movie_id},
        {"$set": {f"reviews.{uuid.uuid4()}": review.model_dump()}},
    )
    return True


async def edit_review(db, movie_id, review_id, updated_review: models.Review):
    if not await _movie_exists(db, movie_id):
        return False

    if not await _review_exists(db, movie_id, review_id):
        return False

    await db.movies.update_one(
        {"movie_id": movie_id},
        {"$set": {f"reviews.{review_id}": updated_review.model_dump()}},
    )
    return True


async def delete_review(db, movie_id, review_id):
    result = await db.movies.update_one(
        {"movie_id": movie_id}, {"$unset": {f"reviews.{review_id}": ""}}
    )
    return result.modified_count > 0


async def add_bookmark(db, user_id, movie_id):
    if not await _movie_exists(db, movie_id):
        await _add_movie(db, movie_id)

    if not await _user_exists(db, user_id):
        await _add_user(db, user_id)

    is_already_bookmarked = await db.users.find_one(
        {"user_id": user_id, "bookmarks": movie_id}
    )
    if is_already_bookmarked:
        return False

    await db.users.update_one({"user_id": user_id}, {"$push": {"bookmarks": movie_id}})
    return True


async def delete_bookmark(db, user_id, movie_id):
    result = await db.users.update_one(
        {"user_id": user_id}, {"$pull": {"bookmarks": movie_id}}
    )
    return result.modified_count > 0


async def get_movie_likes(db, movie_id):
    movie = await db.movies.find_one({"movie_id": movie_id}, {"likes_count": 1})
    if movie:
        return {"likes_count": movie.get("likes_count", 0)}
    return {"likes_count": 0}


async def get_user_bookmarks(db, user_id):
    user = await db.users.find_one({"user_id": user_id}, {"bookmarks": 1})
    if user:
        return {"bookmarks": user["bookmarks"]}
    return {"bookmarks": []}


async def get_user_likes(db, user_id):
    user = await db.users.find_one({"user_id": user_id}, {"likes": 1})
    if user:
        return {"likes": user["likes"]}
    return {"likes": []}


async def _add_movie(db, movie_id):
    await db.movies.insert_one({"movie_id": movie_id, "likes": {}, "reviews": {}})


async def _add_user(db, user_id):
    await db.users.insert_one({"user_id": user_id, "bookmarks": [], "likes": {}})


async def _movie_exists(db, movie_id):
    return bool(await db.movies.find_one({"movie_id": movie_id}, {"_id": 1}))


async def _user_exists(db, user_id):
    return bool(await db.users.find_one({"user_id": user_id}, {"_id": 1}))


async def _review_exists(db, movie_id, review_id):
    return bool(
        await db.movies.find_one(
            {"movie_id": movie_id, f"reviews.{review_id}": {"$exists": True}},
            {"_id": 1},
        )
    )
