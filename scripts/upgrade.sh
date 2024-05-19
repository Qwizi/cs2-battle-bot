#!/bin/bash
## Do not modify this file. You will lose the ability to autoupdate!

VERSION="0.0.1"
CDN="https://raw.githubusercontent.com/Qwizi/cs2-battle-bot/master"

# If DEPLOY_COOLIFy is true, then use coolify files
if [ "$DEPLOY_COOLIFY" = "True" ]; then
    echo "Upgrading on Coolify"
    chmod +x upgrade.sh


    # Get app container name
    APP_CONTAINER_NAME=$(docker ps --filter ancestor=qwizii/cs2-battle-bot-api:latest --filter network=coolify_cs2-battle-bot-network --format "{{.Names}}")

    if [ -z "$APP_CONTAINER_NAME" ]; then
        echo "App container not found. Exiting..."
        exit 1
    fi

    # make migrations
    docker exec $APP_CONTAINER_NAME python manage.py makemigrations

    MAP_COUNT=$(docker exec  "$APP_CONTAINER_NAME" python manage.py shell -c "from matches.models import Map; print(Map.objects.all().count());")

    # Load map fixtures if there are no maps in the database
    if [ "$MAP_COUNT" = "0" ]; then
        docker exec  "$APP_CONTAINER_NAME" python manage.py loaddata maps
    fi

    SUPERUSER_COUNT=$(docker exec  "$APP_CONTAINER_NAME" -T app python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).count());")
    echo "Superuser count: $SUPERUSER_COUNT"
    if [ "$SUPERUSER_COUNT" = "0" ]; then
      SUPERUSER_PASSWORD=$(openssl rand -hex 16)
      docker docker exec  "$APP_CONTAINER_NAME" -T app python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(username='admin', password='$SUPERUSER_PASSWORD', email=None);"
      echo "Superuser admin created with password $SUPERUSER_PASSWORD"
  fi

else
  echo "Upgrading without Coolify"
  curl -fsSL $CDN/examples/without-ssl/docker-compose.yml -o cs2-battle-bot/docker-compose.yml
  curl -fsSL $CDN/examples/without-ssl/.env.example -o cs2-battle-bot/.env.example
  curl -fsSL $CDN/examples/without-ssl/default.conf -o cs2-battle-bot/default.conf
  curl -fsSL $CDN/scripts/upgrade.sh -o cs2-battle-bot/upgrade.sh
  curl -fsSL $CDN/scripts/uninstall.sh -o cs2-battle-bot/uninstall.sh

  chmod +x cs2-battle-bot/upgrade.sh
  chmod +x cs2-battle-bot/uninstall.sh


      # Check if SECRET_KEY is empty in cs2-battle-bot/.env
  if grep -q "SECRET_KEY=django-insecure" cs2-battle-bot/.env; then
    DJANGO_SECRET_KEY=$(openssl rand -hex 50)
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$DJANGO_SECRET_KEY|g" cs2-battle-bot/.env
  fi

        # Make sure cs2-battle-bot-network network exists
  docker network create --attachable cs2-battle-bot-network 2>/dev/null

  # Update containers
  docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml up -d --pull always --remove-orphans --force-recreate

  # Run app migrations
  docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml exec -T app python manage.py migrate

  # Check if there are any superusers in the database
  SUPERUSER_COUNT=$(docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml exec -T app python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).count());")

  # Create superuser if there are no superusers in the database
  if [ "$SUPERUSER_COUNT" = "0" ]; then
      API_URL=$(grep "API_URL=" cs2-battle-bot/.env | cut -d '=' -f2)
      SUPERUSER_PASSWORD=$(openssl rand -hex 16)
      docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml exec -T app python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(username='admin', password='$SUPERUSER_PASSWORD', email=None);"

      echo "Superuser admin created with password $SUPERUSER_PASSWORD"
      echo "Go to $API_URL/admin/password_change/ and login with the superuser to change the password"
  fi

  # Check if there any api keys in the database
  API_KEY_COUNT=$(docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml exec -T app python manage.py shell -c "from rest_framework_api_key.models import APIKey; print(APIKey.objects.all().count());")

  # Create API key if there are no api keys in the database and API_KEY is not set in .env
  if [ "$API_KEY_COUNT" = "0" ] && grep -q "API_KEY=$" cs2-battle-bot/.env; then
      API_KEY=$(docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml exec -T app python manage.py shell -c "from rest_framework_api_key.models import APIKey; api_key, key = APIKey.objects.create_key(name='cs2-battle-bot'); print(key);")
      # set API_KEY to env file
    sed -i "s|^API_KEY=.*|API_KEY=$API_KEY|g" cs2-battle-bot/.env
      # Update bot container
  fi

  # Check map count in database
  MAP_COUNT=$(docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml exec -T app python manage.py shell -c "from matches.models import Map; print(Map.objects.all().count());")
  # Load map fixtures if there are no maps in the database
  if [ "$MAP_COUNT" = "0" ]; then
      docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml exec -T app python manage.py loaddata maps
  fi

  # Merge .env and .env.production. New values will be added to .env
  sort -u -t '=' -k 1,1 cs2-battle-bot/.env cs2-battle-bot/.env.example | sed '/^$/d' >cs2-battle-bot/.env.temp && mv cs2-battle-bot/.env.temp cs2-battle-bot/.env
fi








echo "CS2 Battle BOT has been updated to the latest version!"
echo "Please check the logs to make sure everything is running fine."
