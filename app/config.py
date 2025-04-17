from pydantic import BaseSettings


class Settings(BaseSettings):
    API_KEY: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    DATABASE_URL: str = "localhost:3306"

    class Config:
        env_file = ".env"


settings = Settings()
