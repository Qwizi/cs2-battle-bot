#!/bin/bash
# This script is only to help on dev environment

# shellcheck disable=SC2164
cd src

# Run containers
docker compose up -d --build

# Run migrations
docker compose exec app sh -c "cd src && python manage.py migrate"

# Check if superuser not exists
SUPERUSER_COUNT=$(docker compose exec -T app sh -c "cd src && python manage.py shell -c 'from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).count());'")

echo "Superusers count: $SUPERUSER_COUNT"

if [ "$SUPERUSER_COUNT" = "0" ]; then
  echo "Creating superuser"
    # Create superuser
docker compose exec -T app sh -c "cd src && python manage.py shell -c 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(username=\"admin\", password=\"admin\", email=None)'"
echo "Superuser admin with password admin created"
fi

API_KEY_COUNT=$(docker compose exec -T app sh -c "cd src && python manage.py shell -c 'from rest_framework_api_key.models import APIKey; print(APIKey.objects.all().count());'")

echo "API keys count: $API_KEY_COUNT"

if [ "$API_KEY_COUNT" = "0" ]; then
  echo "Creating API key"
  API_KEY=$(docker compose exec -T app sh -c "cd src && python manage.py shell -c 'from rest_framework_api_key.models import APIKey; api_key, key = APIKey.objects.create_key(name=\"cs2-battle-bot\"); print(key);'")
  echo "API key created with value $API_KEY"
  sed -i "s|^API_KEY=.*|API_KEY=$API_KEY|g" ../.env
fi

MAP_COUNT=$(docker compose exec -T app sh -c "cd src && python manage.py shell -c 'from matches.models import Map; print(Map.objects.all().count());'")


if [ "$MAP_COUNT" = "0" ]; then
      docker compose exec -T app sh -c "cd src && python manage.py loaddata maps"
fi

MAP_POOL_COUNT=$(docker compose exec -T app sh -c "cd src && python manage.py shell -c 'from matches.models import MapPool; print(MapPool.objects.all().count());'")

if [ "$MAP_POOL_COUNT" = "0" ]; then
      docker compose exec -T app sh -c "cd src && python manage.py loaddata map_pools"
fi

MATCH_CONFIG_COUNT=$(docker compose exec -T app sh -c "cd src && python manage.py shell -c 'from matches.models import MatchConfig; print(MatchConfig.objects.all().count());'")

if [ "$MATCH_CONFIG_COUNT" = "0" ]; then
      docker compose exec -T app sh -c "cd src && python manage.py loaddata match_configs"
fi

PLAYERS_COUNT=$(docker compose exec -T app sh -c "cd src && python manage.py shell -c 'from players.models import Player; print(Player.objects.all().count());'")

if [ "$PLAYERS_COUNT" = "0" ]; then
      docker compose exec -T app sh -c "cd src && python manage.py loaddata players"
fi

echo "Upgrade finished"