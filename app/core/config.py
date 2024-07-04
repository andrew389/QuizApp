from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False, env_file=env_file, env_file_encoding="utf-8"
    )

    redis_db_host: str
    redis_db_port: str

    postgres_db_user: str
    postgres_db_password: str
    postgres_db_host: str
    postgres_db_port: str
    postgres_db_name: str
    postgres_db_test_name: str

    @property
    def redis_db_url(self):
        return f"redis://{self.redis_db_host}:{self.redis_db_port}"

    @property
    def postgres_db_url(self):
        return f"postgresql://{self.postgres_db_user}:{self.postgres_db_password}@{self.postgres_db_host}:{self.postgres_db_port}/{self.postgres_db_name}"

    @property
    def postgres_db_async_url(self):
        return f"postgresql+asyncpg://{self.postgres_db_user}:{self.postgres_db_password}@{self.postgres_db_host}:{self.postgres_db_port}/{self.postgres_db_name}"

    @property
    def postgres_db_test_async_url(self):
        return f"postgresql+asyncpg://{self.postgres_db_user}:{self.postgres_db_password}@{self.postgres_db_host}:{self.postgres_db_port}/{self.postgres_db_test_name}"


settings = Settings()
