from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = Path(__file__).resolve().parents[2] / ".env"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="allow",
    )
    user: str = Field(alias="POSTGRES_DB_USER")
    password: str = Field(alias="POSTGRES_DB_PASSWORD")
    host: str = Field(alias="POSTGRES_DB_HOST")
    port: str = Field(alias="POSTGRES_DB_PORT")
    name: str = Field(alias="POSTGRES_DB_NAME")
    test_name: str = Field(alias="POSTGRES_DB_TEST_NAME")

    @property
    def url(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def test_async_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.test_name}"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="allow",
    )

    host: str = Field(alias="REDIS_DB_HOST")
    port: int = Field(alias="REDIS_DB_PORT")

    @property
    def url(self):
        return f"redis://{self.host}:{self.port}"


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
