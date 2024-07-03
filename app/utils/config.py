from pydantic_settings import BaseSettings
from pydantic import Field
import dotenv

env_file = dotenv.find_dotenv('.env')



class Settings(BaseSettings):
    postgres_db_user: str = Field(env='POSTGRES_DB_USER')
    postgres_db_password: str = Field(env='POSTGRES_DB_PASSWORD')
    postgres_db_host: str = Field(env='POSTGRES_DB_HOST')
    postgres_db_port: str = Field(env='POSTGRES_DB_PORT')
    postgres_db_name: str = Field(env='POSTGRES_DB_NAME')

    redis_db_host: str = Field(env='REDIS_DB_HOST')
    redis_db_port: str = Field(env='REDIS_DB_PORT')

settings = Settings(_env_file=env_file, _env_file_encoding='utf-8')

postgres_db_url = f"postgresql://{settings.postgres_db_user}:{settings.postgres_db_password}@{settings.postgres_db_host}:{settings.postgres_db_port}/{settings.postgres_db_name}"
postgres_db_async_url = f"postgresql+asyncpg://{settings.postgres_db_user}:{settings.postgres_db_password}@{settings.postgres_db_host}:{settings.postgres_db_port}/{settings.postgres_db_name}"

redis_db_url = f"redis://{settings.redis_db_host}:{settings.redis_db_port}"
