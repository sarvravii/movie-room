from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    REDIS_URL: str
    TMDB_API_KEY: str
    SECRET_KEY: str

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Supabase (like Heroku) hands out "postgres://" URLs, but SQLAlchemy
        # 1.4+ only registers a "postgresql" dialect and raises
        # NoSuchModuleError on "postgres://" — rewrite it defensively so a
        # copy-pasted Supabase connection string just works.
        if value.startswith("postgres://"):
            return "postgresql://" + value[len("postgres://") :]
        return value


settings = Settings()
