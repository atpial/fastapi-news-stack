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
    DATABASE_PORT: int = Field(3306, env="DATABASE_PORT")

    @property
    def DATABASE_URL(self):
        return (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
