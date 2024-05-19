FROM ghcr.io/coollabsio/coolify-helper:latest

# Download upgrade script

RUN sh -c "curl -fsSL https://raw.githubusercontent.com/Qwizi/cs2-battle-bot/master/scripts/upgrade.sh?$(date +%s%N) -o upgrade.sh"

RUN chmod +x upgrade.sh