import os
from logging import config as logging_config
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.logger import LOGGING, logger

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


env_file_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file_path, env_file_encoding="utf-8")
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field("movies", alias="PROJECT_NAME")
    # Настройки Redis
    redis_host: str = Field("127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    # Настройки Elasticsearch
    elastic_connect: str = Field("localhost:9200", alias="ELASTIC_CONNECT")

    auth_service_host: str = Field("localhost", alias="AUTH_SERVICE_HOST")
    auth_service_port: int = Field(8002, alias="AUTH_SERVICE_PORT")

    secret_key: str = Field("", alias="SECRET_KEY")
    algorithm: str = Field("", alias="ALGORITHM")
    access_token_ttl_in_minutes: Optional[int] = Field(None, alias="ACCESS_TOKEN_TTL")
    refresh_token_ttl: Optional[int] = Field(None, alias="REFRESH_TOKEN_TTL")

    sentry_dsn: Optional[str] = Field(None, alias="SENTRY_DSN")

    auth_check_is_on: bool = Field(True, alias="AUTH_CHECK_IS_ON")


settings = Settings()

logger.info(f"{settings.auth_check_is_on=}")
