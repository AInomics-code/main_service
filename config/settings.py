from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_KEY: str
    PG_URL: str

    class Config:
        env_file = ".env"

settings = Settings()