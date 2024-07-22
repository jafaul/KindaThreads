import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()


class Settings(BaseSettings):

    DB_USERNAME: str = os.environ.get("DB_USERNAME", "")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "")
    HOST: str = os.environ.get("HOST", "localhost")
    PORT: int = os.environ.get("PORT", 3000)

    DB_HOST: str = os.environ.get("DB_HOST", "localhost")
    DB_PORT: int = os.environ.get("DB_PORT", 5434)
    DB_NAME: str = os.environ.get("DB_NAME", "kinda_threads")
    DB_TEST_NAME: str = os.environ.get("DB_TEST_NAME", "test_kinda_threads")

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "")

    API_KEY: str = os.environ.get("AI_API_KEY")
    GENERATIVE_MODEL_NAME: str = os.environ.get("GENERATIVE_MODEL_NAME")

    class Config:
        env_file = ".env"


@lru_cache()
def get_config():
    return Settings()


config = get_config()
