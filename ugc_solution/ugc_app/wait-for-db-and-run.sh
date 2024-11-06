#!/bin/bash
# Файл ожидания доступности MongoDB

set -e

MONGO_HOST=$(echo "${MONGO_CONNECT}" | cut -d: -f1)
MONGO_PORT=$(echo "${MONGO_CONNECT}" | cut -d: -f2)
until ncat -z "${MONGO_HOST}" "${MONGO_PORT}"; do
  >&2 echo "MongoDB is unavailable - sleeping"
  sleep 1
done

>&2 echo "MongoDB is up - executing command"

# запускаем как модуль, так универсальнее работают импорты

poetry run python -m app.main
