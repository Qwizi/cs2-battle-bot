#!/bin/bash
## Do not modify this file. You will lose the ability to install and auto-update!

set -e # Exit immediately if a command exits with a non-zero status
## $1 could be empty, so we need to disable this check
#set -u # Treat unset variables as an error and exit
set -o pipefail # Cause a pipeline to return the status of the last command that exited with a non-zero status

VERSION="0.0.3"
CDN="https://raw.githubusercontent.com/Qwizi/cs2-battle-bot/master"
OS_TYPE=$(grep -w "ID" /etc/os-release | cut -d "=" -f 2 | tr -d '"')

# Check if the OS is manjaro, if so, change it to arch
if [ "$OS_TYPE" = "manjaro" ]; then
    OS_TYPE="arch"
fi

if [ "$OS_TYPE" = "arch" ]; then
    OS_VERSION="rolling"
else
    OS_VERSION=$(grep -w "VERSION_ID" /etc/os-release | cut -d "=" -f 2 | tr -d '"')
fi

# Install xargs on Amazon Linux 2023 - lol
if [ "$OS_TYPE" = 'amzn' ]; then
    dnf install -y findutils >/dev/null 2>&1
fi

#LATEST_VERSION=$(curl --silent $CDN/versions.json | grep -i version | xargs | awk '{print $2}' | tr -d ',')
DATE=$(date +"%Y%m%d-%H%M%S")

#if [ $EUID != 0 ]; then
#    echo "Please run as root"
#    exit
#fi

#case "$OS_TYPE" in
#arch | ubuntu | debian | raspbian | centos | fedora | rhel | ol | rocky | sles | opensuse-leap | opensuse-tumbleweed | almalinux | amzn) ;;
#*)
#    echo "This script only supports Debian, Redhat, Arch Linux, or SLES based operating systems for now."
#    exit
#    ;;
#esac

echo -e "-------------"
echo -e "Welcome to CS2 Battle BOT installer!"
echo -e "This script will install everything for you."
#echo -e "(Source code: https://github.com/coollabsio/coolify/blob/main/scripts/install.sh)\n"
echo -e "-------------"

echo "OS: $OS_TYPE $OS_VERSION"

echo -e "Creating directories..."

mkdir -p cs2-battle-bot/

echo "Downloading required files from CDN..."
curl -fsSL $CDN/examples/without-ssl/docker-compose.yml -o cs2-battle-bot/docker-compose.yml
curl -fsSL $CDN/examples/without-ssl/.env.example -o cs2-battle-bot/.env.example
curl -fsSL $CDN/examples/without-ssl/default.conf -o cs2-battle-bot/default.conf
curl -fsSL $CDN/scripts/upgrade.sh -o cs2-battle-bot/upgrade.sh
curl -fsSL $CDN/scripts/uninstall.sh -o cs2-battle-bot/uninstall.sh

chmod +x cs2-battle-bot/upgrade.sh
chmod +x cs2-battle-bot/uninstall.sh




# Copy .env.example if .env does not exist
if [ ! -f cs2-battle-bot/.env ]; then
    cp cs2-battle-bot/.env.example cs2-battle-bot/.env

    DJANGO_SECRET_KEY=$(openssl rand -hex 50)
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$DJANGO_SECRET_KEY|g" cs2-battle-bot/.env

    API_URL=$1
    sed -i "s|API_URL=.*|API_URL=$API_URL|g" cs2-battle-bot/.env
    sed -i "s|CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=$API_URL|g" cs2-battle-bot/.env

    STEAM_API_KEY=$2
    sed -i "s|STEAM_API_KEY=.*|STEAM_API_KEY=$STEAM_API_KEY|g" cs2-battle-bot/.env

    DISCORD_CLIENT_ID=$3
    sed -i "s|DISCORD_CLIENT_ID=.*|DISCORD_CLIENT_ID=$DISCORD_CLIENT_ID|g" cs2-battle-bot/.env

    DISCORD_CLIENT_SECRET=$4
    sed -i "s|DISCORD_CLIENT_SECRET=.*|DISCORD_CLIENT_SECRET=$DISCORD_CLIENT_SECRET|g" cs2-battle-bot/.env

    DISCORD_BOT_TOKEN=$5
    sed -i "s|DISCORD_BOT_TOKEN=.*|DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN|g" cs2-battle-bot/.env
fi

# Merge .env and .env.production. New values will be added to .env
sort -u -t '=' -k 1,1 cs2-battle-bot/.env cs2-battle-bot/.env.example | sed '/^$/d' >cs2-battle-bot/.env.temp && mv cs2-battle-bot/.env.temp cs2-battle-bot/.env


bash cs2-battle-bot/upgrade.sh

echo -e "\nCongratulations! Your CS2 Battle Bot instance is ready to use.\n"
echo "Please visit $API_URL/admin/ to get started."
