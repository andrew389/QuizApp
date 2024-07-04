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
    postgres_db_user: str = Field(env="POSTGRES_DB_USER")
    postgres_db_password: str = Field(env="POSTGRES_DB_PASSWORD")
    postgres_db_host: str = Field(env="POSTGRES_DB_HOST")
    postgres_db_port: str = Field(env="POSTGRES_DB_PORT")
    postgres_db_name: str = Field(env="POSTGRES_DB_NAME")
    postgres_db_test_name: str = Field(env="POSTGRES_DB_TEST_NAME")

    @property
    def postgres_db_url(self):
        return f"postgresql://{self.postgres_db_user}:{self.postgres_db_password}@{self.postgres_db_host}:{self.postgres_db_port}/{self.postgres_db_name}"

    @property
    def postgres_db_async_url(self):
        return f"postgresql+asyncpg://{self.postgres_db_user}:{self.postgres_db_password}@{self.postgres_db_host}:{self.postgres_db_port}/{self.postgres_db_name}"

    @property
    def postgres_db_test_async_url(self):
        return f"postgresql+asyncpg://{self.postgres_db_user}:{self.postgres_db_password}@{self.postgres_db_host}:{self.postgres_db_port}/{self.postgres_db_test_name}"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="allow",
    )

    redis_db_host: str = Field(env="REDIS_DB_HOST")
    redis_db_port: str = Field(env="REDIS_DB_PORT")

    @property
    def redis_db_url(self):
        return f"redis://{self.redis_db_host}:{self.redis_db_port}"


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
