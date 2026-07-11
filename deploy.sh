#!/bin/bash
set -e

echo "=== Start ==="

git pull origin master

docker compose -f docker-compose.prod.yaml up --build -d

docker compose -f docker-compose.prod.yaml exec -T backend python manage.py migrate

docker compose -f docker-compose.prod.yaml exec -T backend python manage.py collectstatic --noinput

echo "=== Done ==="
