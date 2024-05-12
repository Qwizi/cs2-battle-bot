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
fi
#
#if grep -q "PUSHER_APP_KEY=$" /data/coolify/source/.env; then
#    sed -i "s|PUSHER_APP_KEY=.*|PUSHER_APP_KEY=$(openssl rand -hex 32)|g" /data/coolify/source/.env
#fi
#
#if grep -q "PUSHER_APP_SECRET=$" /data/coolify/source/.env; then
#    sed -i "s|PUSHER_APP_SECRET=.*|PUSHER_APP_SECRET=$(openssl rand -hex 32)|g" /data/coolify/source/.env
#fi

# Make sure cs2-battle-bot-network network exists
docker network create --attachable cs2-battle-bot-network 2>/dev/null
# docker network create --attachable --driver=overlay coolify-overlay 2>/dev/null

#if [ -f /data/coolify/source/docker-compose.custom.yml ]; then
#    echo "docker-compose.custom.yml detected."
#    docker run -v /data/coolify/source:/data/coolify/source -v /var/run/docker.sock:/var/run/docker.sock --rm ghcr.io/coollabsio/coolify-helper bash -c "LATEST_IMAGE=${1:-} docker compose --env-file /data/coolify/source/.env -f /data/coolify/source/docker-compose.yml -f /data/coolify/source/docker-compose.prod.yml -f /data/coolify/source/docker-compose.custom.yml up -d --pull always --remove-orphans --force-recreate"
#else
#    docker run -v /data/coolify/source:/data/coolify/source -v /var/run/docker.sock:/var/run/docker.sock --rm ghcr.io/coollabsio/coolify-helper bash -c "LATEST_IMAGE=${1:-} docker compose --env-file /data/coolify/source/.env -f /data/coolify/source/docker-compose.yml -f /data/coolify/source/docker-compose.prod.yml up -d --pull always --remove-orphans --force-recreate"
#fi

docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml up -d --pull always --remove-orphans --force-recreate