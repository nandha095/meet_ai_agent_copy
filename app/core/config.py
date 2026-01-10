from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "AI Meeting Agent")
    ENV = os.getenv("ENV", "development")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # =========================
    # GOOGLE OAUTH CONFIG ✅
    # =========================
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

    # =========================
    # AI KEYS
    # =========================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # =========================
    # EMAIL CONFIG
    # =========================
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


settings = Settings()
