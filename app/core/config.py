from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Path to the .env file
env_file = Path(__file__).resolve().parents[2] / ".env"


class DatabaseSettings(BaseSettings):
    """
    Configuration settings for the PostgreSQL database.

    Attributes:
        user (str): The username for the PostgreSQL database.
        password (str): The password for the PostgreSQL database.
        host (str): The host of the PostgreSQL database.
        port (str): The port of the PostgreSQL database.
        name (str): The name of the PostgreSQL database.
        test_name (str): The name of the test PostgreSQL database.
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
    test_name: str = Field(alias="POSTGRES_DB_TEST_NAME")

    @property
    def url(self) -> str:
        """
        Get the database connection URL for synchronous PostgreSQL.

        Returns:
            str: The connection URL.
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def async_url(self) -> str:
        """
        Get the database connection URL for asynchronous PostgreSQL.

        Returns:
            str: The connection URL.
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def test_async_url(self) -> str:
        """
        Get the database connection URL for the test asynchronous PostgreSQL database.

        Returns:
            str: The connection URL.
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.test_name}"


class RedisSettings(BaseSettings):
    """
    Configuration settings for the Redis database.

    Attributes:
        host (str): The host of the Redis database.
        port (int): The port of the Redis database.
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
    def url(self) -> str:
        """
        Get the Redis connection URL.

        Returns:
            str: The connection URL.
        """
        return f"redis://{self.host}:{self.port}"


class AuthSettings(BaseSettings):
    """
    Configuration settings for authentication.

    Attributes:
        secret_key (str): The secret key for encoding JWT tokens.
        algorithm (str): The algorithm used for encoding JWT tokens.
        access_token_expire_minutes (int): The expiration time in minutes for access tokens.
        domain (str): The Auth0 domain.
        audience (str): The Auth0 audience.
        signing_key (str): The key used to sign JWT tokens.
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
    def issuer(self) -> str:
        """
        Get the issuer URL for JWT tokens.

        Returns:
            str: The issuer URL.
        """
        return f"https://{self.domain}/"


class Settings(BaseSettings):
    """
    Main settings class that aggregates other configuration settings.

    Attributes:
        api_v1_prefix (str): The API version prefix.
        database (DatabaseSettings): Database configuration settings.
        redis (RedisSettings): Redis configuration settings.
        auth (AuthSettings): Authentication configuration settings.
    """

    api_v1_prefix: str = "/api/v1"

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    auth: AuthSettings = AuthSettings()


# Instantiate the settings object
settings = Settings()
