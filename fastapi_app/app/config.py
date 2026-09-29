from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    DATABASE_URL: str = "sqlite:///./taskboard.db"
    SECRET_KEY: str = "super-secret-benchmark-key-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15   

settings = Settings()