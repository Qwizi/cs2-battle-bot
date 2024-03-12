"""Bot settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    TOKEN: str = ""
    API_URL: str = ""
    API_TOKEN: str = ""
    TESTING: bool = False
    MIN_PLAYERS: int = 2
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    SENTRY_DSN: str = ""
    GUILD_ID: int
    LOBBY_CHANNEL_ID: int
    TEAM1_CHANNEL_ID: int
    TEAM2_CHANNEL_ID: int
    TEAM1_ROLE_ID: int
    TEAM2_ROLE_ID: int


settings = Settings()
