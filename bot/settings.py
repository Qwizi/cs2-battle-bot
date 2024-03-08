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


settings = Settings()
