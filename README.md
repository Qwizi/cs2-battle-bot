## CS2 Battle Discord Bot
The CS2 Battle Discord Bot is your go-to solution for seamlessly organizing and enjoying 5v5 matches with your friends directly on your Discord server.

## Features
- **Match Creation:** Effortlessly create matches with members from your Discord server. Simply initiate the command, and the bot handles the rest by assembling two teams and randomly assigning members to each team.
- **B01/B03 Support:** Enjoy both best-of-one (B01) and best-of-three (B03) match formats, complete with map bans and picks for added excitement and strategy.
- **Automatic Channel Management:** The bot takes care of channel assignments for players throughout the match lifecycle. It automatically connects users to the lobby channel upon match initiation, transitions them to team channels as the match begins, and returns them to the lobby channel after each map concludes.
- **User Stats Updates:** Stay informed with timely updates on user statistics at the end of each round, keeping everyone engaged and competitive throughout the match. 
- At the moment, the bot is only functional for a single guild and cs2 server.

With the CS2 Battle Discord Bot, you can elevate your Discord server into a dynamic gaming hub where thrilling 5v5 matches await with just a few simple commands. Enjoy the camaraderie and competition as you and your friends embark on epic gaming adventures together!


## Requirements
1. [Backend server](https://github.com/Qwizi/cs2-battle-bot-api)
2. CS2 server with plugin [MatchZy](https://github.com/shobhit-pathak/MatchZy)


## Showcase
![](https://i.imgur.com/jUuywHe.png)
![](https://i.imgur.com/4MOxuyt.png)
## Installation
1. **Setting Up Docker**
Create a Docker network for the CS2 Battle Bot:
```shell
docker network create cs2-battle-bot-network
```
2. **Docker Compose Configuration**
Create a docker-compose.yml file with the following configuration:

```yaml
services:
  app:
    container_name: cs2_battle_bot_api
    image: qwizii/cs2-battle-bot-api:latest
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8003:8000"
    environment:
      - SECRET_KEY=django-insecure-#
      - DB_ENGINE=django.db.backends.postgresql
      - DB_HOST=db
      - DB_NAME=cs2_db
      - DB_USER=cs2_user
      - DB_PASSWORD=cs2_password
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - HOST_URL=http://localhost:8003
      - DISCORD_CLIENT_ID=
      - DISCORD_CLIENT_SECRET=
      - DISCORD_REDIRECT_URI=http://localhost:8003/accounts/discord/callback
      - STEAM_API_KEY=
      - STEAM_REDIRECT_URI=https://localhost:8003/accounts/steam/callback
      - RCON_HOST=
      - RCON_PORT=
      - RCON_PASSWORD=
      - API_KEY=
    restart: always
    depends_on:
      - db
    networks:
      - cs2-battle-bot-network
  db:
    image: postgres:15.1
    container_name: cs2_battle_bot_db
    environment:
      - POSTGRES_DB=cs2_db
      - POSTGRES_USER=cs2_user
      - POSTGRES_PASSWORD=cs2_password
    restart: always
    expose:
      - "5435:5432"
    networks:
      - cs2-battle-bot-network
  redis:
    image: "redis:alpine"
    container_name: cs2_battle_bot_redis
    restart: always
    expose:
      - "6379:6379"
    networks:
      - cs2-battle-bot-network
    bot:
    image: qwizii/cs2-battle-bot:v0.0.5
    container_name: cs2_battle_bot
    env_file:
      - .env
    networks:
      -  cs2-battle-bot-network
  bot:
    image: qwizii/cs2-battle-bot:latest
    container_name: cs2_battle_bot
    environment:
      ## Discord BOT token
      - TOKEN=
      ## BACKEND SERVER URL
      - API_URL=http://app:8000
      ## API TOKEN from installation section
      - API_TOKEN=
      - TESTING=False
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
      - REDIS_PASSWORD=
      ## SENTRY DSN
      - SENTRY_DSN=
      ## Your guild id
      - GUILD_ID=
      - LOBBY_CHANNEL_ID=
      - TEAM1_CHANNEL_ID=
      - TEAM2_CHANNEL_ID=
      - TEAM1_ROLE_ID=
      - TEAM2_ROLE_ID=
    networks:
      -  cs2-battle-bot-network
networks:
  cs2-battle-bot-network:
    external: true
```
3. **Building and Running Containers**
Build and run the containers:
```shell
docker compose up -d --build
```
4. **Running Migrations**
Run migrations:
```shell
docker compose exec app python manage.py migrate
```
5. **Creating Super User**
Create a superuser:
```shell
docker compose exec app python manage.py createsuperuser
```
6. **Creating API Key**
   1. Access the admin panel at http://localhost:8003/admin/ using the superuser credentials.
   2. Navigate to the API Keys section.
   3. Click on the "Add" button to create a new API key, providing a name and expiration date.
   4. Save the API key.
   5. After completing the previous steps, you will see a message similar to the following in the admin panel:
   ![Api token](https://i.imgur.com/RrfuGNH.png)
   6. Update the API_KEY and API_TOKEN environment  variablein your docker-compose.yml file with the new key.
   7. Rebuild the containers:
   ```shell
   docker compose up -d --build
   ```
7. **Add maps**:
Run fixture with maps
```shell
docker compose exec app python manage.py loaddata maps
```
