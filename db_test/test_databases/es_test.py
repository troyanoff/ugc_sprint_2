from uuid import uuid4
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from random import choices, randint
from time import time
from datetime import datetime
from faker import Faker

import config as cnf


def bulk_update_likes(client: Elasticsearch, films: list) -> float:
    result_time: float = 0.0
    for _ in range(1000):
        bulk_data = []
        data = [{
            'user_id': str(uuid4()),
            'filmwork_id': choices(films)[0],
            'estimation': randint(0, 10),
        } for _ in range(1000)]
        for elem in data:
            bulk_data.append({
                '_index': 'likes',
                '_id': str(uuid4()),
                '_source': elem
            })
        start = time()
        bulk(client, bulk_data)
        end = time() - start
        result_time += end
    return result_time


def bulk_update_reviews(client: Elasticsearch, films: list) -> float:
    result_time: float = 0.0
    fake = Faker('ru_RU')
    for _ in range(1000):
        bulk_data = []
        data = [{
            'user_id': str(uuid4()),
            'filmwork_id': choices(films)[0],
            'datetime': datetime.now(),
            'like_id': str(uuid4()),
            'text': fake.text(300)
        } for _ in range(1000)]
        for elem in data:
            bulk_data.append({
                '_index': 'reviews',
                '_id': str(uuid4()),
                '_source': elem
            })
        start = time()
        bulk(client, bulk_data)
        end = time() - start
        result_time += end
    return result_time


def bulk_update_bookmarks(client: Elasticsearch, films: list) -> float:
    result_time: float = 0.0
    for _ in range(1000):
        bulk_data = []
        data = [{
            'user_id': str(uuid4()),
            'filmwork_id': choices(films)[0],
        } for _ in range(1000)]
        for elem in data:
            bulk_data.append({
                '_index': 'bookmarks',
                '_id': str(uuid4()),
                '_source': elem
            })
        start = time()
        bulk(client, bulk_data)
        end = time() - start
        result_time += end
    return result_time


def average_estimation(client: Elasticsearch) -> float:
    query = {
        "aggs": {
            "group_by_ids": {
                "terms": {"field": "filmwork_id"},
                "aggs": {
                    "avg_estimation": {
                        "avg": {"field": "estimation"}
                    }
                }
            }
        }
    }
    start = time()
    response = client.search(index='likes', body=query)
    end = time() - start
    print(response['aggregations'])
    return end


def main():
    print('Проверка ElasticSearch.')
    # client = Elasticsearch('http://localhost:9200')
    client = Elasticsearch('http://elasticsearch:9200')

    if not client.indices.exists(index='likes'):
        client.indices.create(
            index='likes', mappings=cnf.es_mapping_likes,
            settings=cnf.es_setting)

    if not client.indices.exists(index='reviews'):
        client.indices.create(
            index='reviews', mappings=cnf.es_mapping_reviews,
            settings=cnf.es_setting)

    if not client.indices.exists(index='bookmarks'):
        client.indices.create(
            index='bookmarks', mappings=cnf.es_mapping_bookmarks,
            settings=cnf.es_setting)

    filmwork_ids = [str(uuid4()) for _ in range(1000)]

    result = bulk_update_likes(client, filmwork_ids)
    print(f'Время загрузки лайков: {result:.2f}')

    result = bulk_update_reviews(client, filmwork_ids)
    print(f'Время загрузки рецензий: {result:.2f}')

    result = bulk_update_bookmarks(client, filmwork_ids)
    print(f'Время загрузки закладок: {result:.2f}')

    average_time = average_estimation(client)
    print(f'Время подсчета среднего значения оценки: {average_time:.7f}')


if __name__ == '__main__':
    main()
