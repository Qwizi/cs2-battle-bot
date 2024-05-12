#!/bin/bash
## Do not modify this file. You will lose the ability to autoupdate!

VERSION="0.0.1"
CDN="https://raw.githubusercontent.com/Qwizi/cs2-battle-bot/master"

curl -fsSL $CDN/examples/without-ssl/docker-compose.yml -o cs2-battle-bot/docker-compose.yml
curl -fsSL $CDN/examples/without-ssl/.env.example -o cs2-battle-bot/.env.example
curl -fsSL $CDN/examples/without-ssl/default.conf -o cs2-battle-bot/default.conf
curl -fsSL $CDN/scripts/upgrade.sh -o cs2-battle-bot/upgrade.sh

# Merge .env and .env.production. New values will be added to .env
sort -u -t '=' -k 1,1 cs2-battle-bot/.env cs2-battle-bot/.env.example | sed '/^$/d' >cs2-battle-bot/.env.temp && mv cs2-battle-bot/.env.temp cs2-battle-bot/.env

# Check if PUSHER_APP_ID or PUSHER_APP_KEY or PUSHER_APP_SECRET is empty in /data/coolify/source/.env
if grep -q "SECRET_KEY=$" cs2-battle-bot/.env; then
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 32)|g" cs2-battle-bot/.env
    sed -i "s|DJANGO_SUPERUSER_PASSWORD=.*|API_KEY=$(openssl rand -hex 32)|g" cs2-battle-bot/.env
fi

# Make sure cs2-battle-bot-network network exists
docker network create --attachable cs2-battle-bot-network 2>/dev/null

# Update containers
docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml up -d --pull always --remove-orphans --force-recreate

# Run app migrations
docker compose exec app python manage.py migrate

# Check if there are any superusers in the database
SUPERUSER_COUNT=$(docker compose exec app python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).count());")

# Create superuser if there are no superusers in the database
if [ "$SUPERUSER_COUNT" -eq 0 ]; then
    docker compose exec app python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME"
    echo "Superuser $DJANGO_SUPERUSER_USERNAME created with password $DJANGO_SUPERUSER_PASSWORD"
    echo "Please change the password after the first login."

    # set DJANGO_SUPERUSER_PASSWORD to empty string
    sed -i "s|DJANGO_SUPERUSER_PASSWORD=.*|DJANGO_SUPERUSER_PASSWORD=|g" cs2-battle-bot/.env
fi

# Check if there any api keys in the database
API_KEY_COUNT=$(docker compose exec app python manage.py shell -c "from rest_framework_api_key.models import APIKey; print(APIKey.objects.all().count());")

# Create API key if there are no api keys in the database
if [ "$API_KEY_COUNT" -eq 0 ]; then
    API_KEY=$(docker compose exec app python manage.py shell -c "from rest_framework_api_key.models import APIKey; api_key, key = APIKey.objects.create_key(name='cs2-battle-bot'); print(key);")
    echo "Api key created: $API_KEY."

    # set API_KEY to env file
    sed -i "s|API_KEY=.*|API_KEY=$API_KEY|g" cs2-battle-bot/.env

    # Update bot container
fi

# Check map count in database
MAP_COUNT=$(python manage.py shell -c "from matches.models import Map; print(Map.objects.all().count());")

# Load map fixtures if there are no maps in the database
if [ "$MAP_COUNT" -eq 0 ]; then
    docker compose exec app python manage.py loaddata maps
fi

docker compose exec app python manage.py loaddata maps
echo "CS2 Battle BOT has been updated to the latest version!"
echo "Please check the logs to make sure everything is running fine."
