from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_KEY: str
    PG_URL: str
    MYSQL_URL: str
    SQLSERVER_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()