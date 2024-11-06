import os
from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


env_file_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file_path, env_file_encoding="utf-8")
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field("UGC_project", alias="PROJECT_NAME")

    secret_key: str = Field(None, alias="SECRET_KEY")
    algorithm: str = Field(None, alias="ALGORITHM")

    mongo_connect: str = Field(None, alias="MONGO_CONNECT")
    mongo_db_name: str = Field(None, alias="MONGO_DB_NAME")


settings = Settings()
