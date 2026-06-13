from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuTest AI API"
    API_V1_STR: str = "/api/v1"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
