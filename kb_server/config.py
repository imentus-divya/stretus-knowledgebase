from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="KB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0", description="Bind address")
    port: int = Field(default=8080, ge=1, le=65535)
    content_path: Path = Field(default=Path("./content"))
    db_path: Path = Field(default=Path("./data/kb.db"))
    debug: bool = False
    snippet_length: int = Field(default=240, ge=32, le=2000)
    default_search_limit: int = Field(default=20, ge=1, le=100)
    max_search_limit: int = Field(default=100, ge=1, le=500)
    reindex_on_startup: bool = Field(
        default=True,
        description="If true, full rebuild on boot; if false, incremental by mtime+size.",
    )

    @field_validator("content_path", "db_path", mode="before")
    @classmethod
    def coerce_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser()
