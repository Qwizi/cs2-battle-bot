"""Bot settings."""
import httpx
from cs2_battle_bot_api_client import AuthenticatedClient
from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.logger import logger


class Settings(BaseSettings):
    """Bot settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DISCORD_BOT_TOKEN: str = ""
    API_URL: str = ""
    API_KEY: str = ""
    DEBUG: bool = False
    MIN_PLAYERS: int = 2
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""


settings = Settings()


async def log_request(request: httpx.Request) -> None:
    """
    Log request event hook.

    Args:
    ----
        request (httpx.Request): Request object.

    Returns:
    -------
        None

    """
    logger.debug(f"Request event hook: {request.method} {request.url}")


async def log_response(response: httpx.Response) -> None:
    """
    Log response event hook.

    Args:
    ----
        response (httpx.Response): Response object.

    Returns:
    -------
        None

    """
    request = response.request
    logger.debug(
        f"Response event hook: {request.method} {request.url} - Status {response.status_code}"
    )


api_client = AuthenticatedClient(
    base_url=settings.API_URL,
    token=settings.API_KEY,
    headers={"Content-Type": "application/json"},
    raise_on_unexpected_status=True,
    httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}},
)
