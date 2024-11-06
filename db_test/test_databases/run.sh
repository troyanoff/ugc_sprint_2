#!/usr/bin/env bash

while ! nc -z "elasticsearch" "9200"; do
      >&2 echo "elasticsearch is unavailable - sleeping"
      sleep 1
done

>&2 echo "elasticsearch are up - executing command"

python run.py

>&2 echo "elasticsearch"