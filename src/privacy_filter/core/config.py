from pydantic_settings import BaseSettings


class Env(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    MASTER_KEY: str = "sk-default"
    MODEL_ID: str = "openai/privacy-filter"

    # Logging
    LOG_JSON: bool = False  # Set to True for GKE deployment
    LOGURU_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/mlpa.log"
    LOG_ROTATION: str = "500 MB"
    LOG_COMPRESSION: str = "zip"
    HTTPX_LOGGING: bool = True
    ASYNCPG_LOGGING: bool = True


env = Env()
