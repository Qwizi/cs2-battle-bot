FROM ghcr.io/coollabsio/coolify-helper:latest
RUN apk update && apk add openssl

# Download upgrade script

RUN sh -c "curl -fsSL https://raw.githubusercontent.com/Qwizi/cs2-battle-bot/master/scripts/upgrade.sh?token=$(date +%s%N) -o upgrade.sh"

RUN chmod +x upgrade.sh