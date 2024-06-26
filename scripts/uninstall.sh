#!/bin/bash
echo -e "-------------"
echo -e "Welcome to CS2 Battle BOT uninstaller!"
echo -e "This script will uninstall everything for you."
echo -e "-------------"

echo -e "Stopping and removing containers..."
# Uninstall the bot
docker compose --env-file cs2-battle-bot/.env -f cs2-battle-bot/docker-compose.yml down -v
echo -e "-------------"

# Remove the network
echo -e "Removing network..."
docker network rm cs2-battle-bot-network
echo -e "-------------"


# Remove the directory
echo -e "Removing directories..."
rm -rf cs2-battle-bot/
echo -e "-------------"

echo "CS2 Battle BOT has been uninstalled."