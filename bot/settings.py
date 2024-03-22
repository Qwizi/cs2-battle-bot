"""Bot settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DISCORD_BOT_TOKEN: str = ""
    HOST_URL: str = ""
    API_KEY: str = ""
    DEBUG: bool = False
    MIN_PLAYERS: int = 2
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    GUILD_ID: int
    LOBBY_CHANNEL_ID: int
    TEAM1_CHANNEL_ID: int
    TEAM2_CHANNEL_ID: int


settings = Settings()
