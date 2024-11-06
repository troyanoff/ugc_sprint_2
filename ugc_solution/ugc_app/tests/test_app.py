# tests/test_app.py

from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "UP"}


@pytest.mark.asyncio
async def test_add_like(client, db):
    like_data = {"movie_id": "movie123", "rating": 7}
    response = await client.post("/api/v1/movies/like", json=like_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Like added"}


@pytest.mark.asyncio
async def test_delete_like(client, db):
    await db.movies.insert_one(
        {"movie_id": "movie123", "likes": {"kimkanovsky": 7}, "likes_count": 1}
    )
    response = await client.delete("/api/v1/movies/movie123/like")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Like deleted"}


@pytest.mark.asyncio
async def test_add_review(client, db):
    review_data = {"movie_id": "movie123", "text": "Great movie!", "rating": 9}
    response = await client.post(
        "/api/v1/movies/review",
        json=review_data,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Review added"}


@pytest.mark.asyncio
async def test_edit_review(client, db):
    review_data = {"movie_id": "movie123", "text": "Updated review text.", "rating": 7}
    await db.movies.insert_one(
        {
            "movie_id": "movie123",
            "reviews": {
                "05706134-22ea-4cd5-9bcc-5fdbee547316": {
                    "user_id": "kimkanovsky",
                    "text": "Great movie!",
                    "rating": 9,
                }
            },
        }
    )
    response = await client.put(
        "/api/v1/movies/review/05706134-22ea-4cd5-9bcc-5fdbee547316",
        json=review_data,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Review updated"}


@pytest.mark.asyncio
async def test_delete_review(client, db):
    await db.movies.insert_one(
        {
            "movie_id": "movie123",
            "reviews": {
                "05706134-22ea-4cd5-9bcc-5fdbee547316": {
                    "user_id": "kimkanovsky",
                    "text": "Great movie!",
                    "rating": 9,
                }
            },
        }
    )
    response = await client.delete(
        "/api/v1/movies/movie123/review/05706134-22ea-4cd5-9bcc-5fdbee547316",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Review deleted"}


@pytest.mark.asyncio
async def test_add_bookmark(client, db):
    bookmark_data = {"movie_id": "movie123"}
    response = await client.post(
        "/api/v1/users/bookmark",
        json=bookmark_data,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Movie bookmarked"}


@pytest.mark.asyncio
async def test_delete_bookmark(client, db):
    await db.users.insert_one({"user_id": "kimkanovsky", "bookmarks": ["movie123"]})
    response = await client.delete(
        "/api/v1/users/bookmark/movie123",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Bookmark deleted"}


@pytest.mark.asyncio
async def test_get_movie_likes(client, db):
    await db.movies.insert_one({"movie_id": "movie123", "likes_count": 10})
    response = await client.get(
        "/api/v1/movies/movie123/likes",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"likes_count": 10}


@pytest.mark.asyncio
async def test_get_user_bookmarks(client, db):
    await db.users.insert_one(
        {"user_id": "kimkanovsky", "bookmarks": ["movie123", "movie456"]}
    )
    response = await client.get(
        "/api/v1/users/me/bookmarks",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"bookmarks": ["movie123", "movie456"]}


@pytest.mark.asyncio
async def test_get_user_likes(client, db):
    await db.users.insert_one(
        {"user_id": "kimkanovsky", "likes": {"movie123": 7, "movie456": 8}}
    )
    response = await client.get(
        "/api/v1/users/me/likes",
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"likes": {"movie123": 7, "movie456": 8}}
