"""Configuration management using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BrowserConfig(BaseSettings):
    """Browser configuration."""

    model_config = SettingsConfigDict(env_prefix="BROWSER_")

    name: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = True
    slow_mo: int = 0
    viewport_width: int = 1920
    viewport_height: int = 1080
    locale: str = "en-US"
    timezone_id: str = "UTC"
    permissions: list[str] = Field(default_factory=list)
    args: list[str] = Field(default_factory=lambda: ["--disable-dev-shm-usage", "--no-sandbox"])


class APIConfig(BaseSettings):
    """API client configuration."""

    model_config = SettingsConfigDict(env_prefix="API_")

    base_url: str = "https://jsonplaceholder.typicode.com"
    timeout: float = 30.0
    retries: int = 3
    backoff_factor: float = 0.5
    verify_ssl: bool = True


class UIConfig(BaseSettings):
    """UI client configuration."""

    model_config = SettingsConfigDict(env_prefix="UI_")

    base_url: str = "https://the-internet.herokuapp.com"
    timeout: float = 30.0


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    name: str = "testdb"
    pool_size: int = 5
    max_overflow: int = 10

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseSettings):
    """Redis configuration."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None

    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class TestConfig(BaseSettings):
    """Test execution configuration."""

    model_config = SettingsConfigDict(env_prefix="TEST_")

    parallel_workers: int = 0  # 0 = auto
    reruns: int = 2
    reruns_delay: float = 1.0
    screenshot_on_failure: bool = True
    video_on_failure: bool = False
    trace_on_failure: bool = True
    html_report: bool = True
    allure_report: bool = True


class Settings(BaseSettings):
    """Main settings aggregator."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: Literal["local", "ci", "staging", "prod"] = "local"
    log_level: str = "INFO"
    project_root: Path = Path(__file__).parent.parent.parent

    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    test: TestConfig = Field(default_factory=TestConfig)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()


