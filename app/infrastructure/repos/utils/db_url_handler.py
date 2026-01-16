from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


def build_db_url(settings: BaseSettings) -> str:
    driver = (settings.db_title or "sqlite").lower()

    match driver:
        case "sqlite":
            if settings.test_db:
                return "sqlite+aiosqlite:///:memory:"
            db_path = Path(settings.db_file)
            return f"sqlite+aiosqlite:///{db_path.as_posix()}"

        case "postgres":
            if settings.test_db:
                raise RuntimeError(f"{settings.db_title!r} does not support test (in-memory) mode.")

            required = {
                "DB_HOST": settings.db_host,
                "DB_USER": settings.db_user,
                "DB_NAME": settings.db_name,
                "DB_PORT": settings.db_port,
                "DB_PASS": settings.db_pass,
            }

            missing = [k for k, v in required.items() if v in (None, "")]
            if missing:
                raise RuntimeError(
                    f"Postgres config is missing required var(s): {', '.join(missing)}"
                )

            password = settings.db_pass.get_secret_value()
            return (
                "postgresql+asyncpg://"
                f"{quote_plus(settings.db_user)}:{quote_plus(password)}"
                f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
            )

        case _:
            raise RuntimeError(f"Unsupported DB_TITLE: {driver!r}")
