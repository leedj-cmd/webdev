from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_KEY: str = ""
    
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_SECRET: str = "admin_secret_change_me"
    FRONTEND_URL: str = "http://localhost:5173"
    EMAIL_FROM: str = "no-reply@techbridge.local"
    EMAIL_FROM_NAME: str = "TechBridge"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    WORKNET_API_KEY: str = ""
    WORKNET_API_URL: str = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"
    KIPRIS_API_KEY: str = ""
    KIPRIS_IDEA_API_URL: str = "http://plus.kipris.or.kr/openapi/rest/IdeaDBInfoService/ideaDBInfo"

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = False

settings = Settings()
