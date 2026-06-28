from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    
    MONGODB_URL: str
    MONGODB_DATABASE_NAME: str
        
    class Config:
        env_file = ".env"
        
def get_settings():
    return Settings()