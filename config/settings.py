from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_KEY: str
    SQLSERVER_URL: str = "sqlite:///demo_database.db"  # Usar SQLite local por defecto
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    OPENSEARCH_ENDPOINT: str

    class Config:
        env_file = ".env"

settings = Settings()