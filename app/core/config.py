from dotenv import load_dotenv
import os

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "AI Meeting Agent")
    ENV = os.getenv("ENV", "development")

    # AI KEYS (SEPARATE & CLEAR)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # EMAIL CONFIG
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


settings = Settings()
