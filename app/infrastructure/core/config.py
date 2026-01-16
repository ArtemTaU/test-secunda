from datetime import date
from typing import Optional
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.parent / ".env"

DEFAULT_ALL_TIME_START = date(2025, 11, 1)


class Settings(BaseSettings):
    app_title: str | None = None
    root_path: str = ""

    summary: str | None = None
    description: str | None = None
    version: str | None = None
    default_all_time_start: date = DEFAULT_ALL_TIME_START

    log_level: str = "DEBUG"
    db_logs: bool = False

    debug: bool = False
    test_db: bool = False

    db_title: str = Field(default="sqlite", env="DB_TITLE")
    db_file: str = Field(default="./data/sqlite.db", env="DB_FILE")

    db_host: Optional[str] = Field(default=None, env="DB_HOST")
    db_user: Optional[str] = Field(default=None, env="DB_USER")
    db_name: Optional[str] = Field(default=None, env="DB_NAME")
    db_port: Optional[int] = Field(default=None, env="DB_PORT")
    db_pass: Optional[SecretStr] = Field(
        default=None,
        env="DB_PASS",
        json_schema_extra={"x-sensitive": True},
    )
    db_url: Optional[str] = Field(default=None, env="DB_URL")

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore",
    )


settings = Settings(
    version="0.0.0",
)
