import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    SECRET_KEY: str
    DATABASE_NAME: str = Field(..., env="DATABASE_NAME")
    DATABASE_USER: str = Field(..., env="DATABASE_USER")
    DATABASE_PASSWORD: str = Field("", env="DATABASE_PASSWORD")
    DATABASE_HOST: str = Field("127.0.0.1", env="DATABASE_HOST")
    DATABASE_HOST_DOCKER: str = Field(
        "host.docker.internal", env="DATABASE_HOST_DOCKER"
    )
    DATABASE_PORT: int = Field(3306, env="DATABASE_PORT")

    @property
    def DATABASE_URL(self):
        host = self.DATABASE_HOST
        if os.path.exists("/.dockerenv"):
            host = self.DATABASE_HOST_DOCKER
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{host}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
