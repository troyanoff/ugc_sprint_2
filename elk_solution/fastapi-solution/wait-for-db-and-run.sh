#!/bin/bash
# Файл ожидания доступности баз данных

set -e

ELASTICSEARCH_HOST=$(echo "${ELASTIC_CONNECT}" | cut -d: -f1)
ELASTICSEARCH_PORT=$(echo "${ELASTIC_CONNECT}" | cut -d: -f2)
until ncat -z "${ELASTICSEARCH_HOST}" "${ELASTICSEARCH_PORT}"; do
  >&2 echo "Elasticsearch is unavailable - sleeping"
  sleep 1
done

until ncat -z "${REDIS_HOST}" "${REDIS_PORT}"; do
  >&2 echo "Redis is unavailable - sleeping"
  sleep 1
done

>&2 echo "Elasticsearch and Redis are up - executing command"

# запускаем как модуль, так универсальнее работают импорты

# и мы продолжаем использовать увикорн, потому что его сервить будет nginx теперь.
# В данной ситуации оптимальным решением является масштабирование на одном из
# уровней архитектуры (либо на уровне реплик приложения - k8s/nginx,
# либо на уровне ядер через гуникорн). Дока фастАпи также рекомендует из-под nginx
# раздавать увикорн: https://www.uvicorn.org/deployment/#running-behind-nginx
# Такое же мнение мы получили от наших обоих наставников, цитирую одного из них
# (краткая часть обсуждения): "Если речь про докер, то запускать gunicorn можно,
# но лучше uvicorn, это следует из самой концепции докера: один контейнер -
# один процесс"
poetry run python -m src.main
