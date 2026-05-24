import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(os.getenv("SITE_ROOT", str(BACKEND_ROOT.parent.parent))).resolve()
CMS_DATA = BACKEND_ROOT / "data"
UPLOADS_DIR = CMS_DATA / "uploads"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    secret_key: str = "dev-only-change-in-production-immediately"
    database_url: str = f"sqlite:///{(CMS_DATA / 'cms.db').as_posix()}"

    admin_email: str = "admin@seowithfaiz.com"
    admin_password: str = "ChangeThisBeforeDeploy123!"
    admin_name: str = "Site Administrator"

    access_token_minutes: int = 30
    refresh_token_days: int = 14
    cors_origins: str = "http://127.0.0.1:8780,http://localhost:8780"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    contact_notify_to: str = "md.faiz.ahmed62@gmail.com"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
