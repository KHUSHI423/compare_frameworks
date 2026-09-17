from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./taskboard.db"
    SECRET_KEY: str = "super-secret-benchmark-key-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    class Config:
        env_file = ".env"

settings = Settings()