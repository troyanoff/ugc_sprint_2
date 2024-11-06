from uuid import uuid4
from pymongo import MongoClient
from pymongo.collection import Collection
from random import choices, randint
from time import time
from datetime import datetime
from faker import Faker


def insert_many_document(*, collection: Collection, data: list[dict]) -> list:
    res = collection.insert_many(data)
    result_id = res.inserted_ids
    return result_id


def insert_likes(collection: Collection, films: list) -> tuple[list, float]:
    result = []
    result_time: float = 0.0
    for _ in range(1000):
        data = [
            {
                "user_id": str(uuid4()),
                "filmwork_id": choices(films)[0],
                "estimation": randint(0, 10),
            }
            for _ in range(1000)
        ]
        start = time()
        ids = insert_many_document(collection=collection, data=data)
        end = time() - start
        result_time += end
        result += ids
    return result, result_time


def insert_reviews(
    collection: Collection, films: list, likes: list, fake: Faker
) -> tuple[list, float]:
    result = []
    result_time: float = 0.0
    for _ in range(1000):
        data = [
            {
                "user_id": str(uuid4()),
                "filmwork_id": choices(films)[0],
                "datetime": datetime.now(),
                "like_id": choices(likes)[0],
                "text": fake.text(300),
            }
            for _ in range(1000)
        ]
        start = time()
        ids = insert_many_document(collection=collection, data=data)
        end = time() - start
        result_time += end
        result += ids
    return result, result_time


def insert_bookmarks(collection: Collection, films: list) -> tuple[list, float]:
    result = []
    result_time: float = 0.0
    for _ in range(1000):
        data = [
            {
                "user_id": str(uuid4()),
                "filmwork_id": choices(films)[0],
            }
            for _ in range(1000)
        ]
        start = time()
        ids = insert_many_document(collection=collection, data=data)
        end = time() - start
        result_time += end
        result += ids
    return result, result_time


def average_estimation(collection: Collection) -> float:
    pipeline = [
        {
            "$group": {
                "_id": "$filmwork_id",
                "average_estimation": {"$avg": "$estimation"},
            }
        }
    ]
    start = time()
    results = collection.aggregate(pipeline)
    end = time() - start
    print(list(results)[:10])
    return end


def main():
    client = MongoClient("mongodb", 27017)
    db = client["TestDB"]

    fake = Faker("ru_RU")

    filmwork_ids = [str(uuid4()) for _ in range(1000)]

    like_ids, likes_time = insert_likes(db.likes, filmwork_ids)
    print(f"Время загрузки лайков: {likes_time:.2f}")

    _, reviews_time = insert_reviews(db.reviews, filmwork_ids, like_ids, fake)
    print(f"Время загрузки рецензий: {reviews_time:.2f}")

    _, bookmark_time = insert_bookmarks(db.bookmark, filmwork_ids)
    print(f"Время загрузки закладок: {bookmark_time:.2f}")

    average_time = average_estimation(db.likes)
    print(f"Время подсчета среднего значения оценки: {average_time:.7f}")


if __name__ == "__main__":
    main()
