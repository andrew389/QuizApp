from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = Path(__file__).resolve().parents[2] / ".env.sample"


class DatabaseSettings(BaseSettings):
    """
    Configuration settings for PostgreSQL database.
    """

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

    @property
    def url(self):
        """
        Returns the PostgreSQL connection URL.
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self):
        """
        Returns the asynchronous PostgreSQL connection URL.
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def test_async_url(self):
        """
        Returns the asynchronous PostgreSQL connection URL for testing.
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """
    Configuration settings for Redis.
    """

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
        """
        Returns the Redis connection URL.
        """
        return f"redis://{self.host}:{self.port}"


class AuthSettings(BaseSettings):
    """
    Configuration settings for authentication.
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="allow",
    )

    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(alias="ALGORITHM")
    access_token_expire_minutes: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    domain: str = Field(alias="AUTH0_DOMAIN")
    audience: str = Field(alias="AUTH0_AUDIENCE")
    signing_key: str = Field(alias="SIGNING_KEY")

    @property
    def issuer(self):
        """
        Returns the issuer URL for authentication.
        """
        return f"https://{self.domain}/"


class Settings(BaseSettings):
    """
    Main settings class to aggregate database, Redis, and authentication configurations.
    """

    api_v1_prefix: str = "/api/v1"

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    auth: AuthSettings = AuthSettings()


settings = Settings()
