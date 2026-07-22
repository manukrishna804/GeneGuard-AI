from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "GeneGuard API"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()