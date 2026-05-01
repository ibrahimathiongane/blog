import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    # Upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    # Blog meta
    BLOG_TITLE = os.environ.get("BLOG_TITLE", "nexatech-sn")
    BLOG_DESCRIPTION = os.environ.get(
        "BLOG_DESCRIPTION",
        "Articles techniques, projets et réflexions sur le développement logiciel.",
    )
    BLOG_AUTHOR = os.environ.get("BLOG_AUTHOR", "Ibrahima Thiongane")
    BLOG_URL = os.environ.get("BLOG_URL", "https://blog.nexatech-sn.online")
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///blog_dev.db"
    )
    CACHE_TYPE = "SimpleCache"


class ProductionConfig(Config):
    DEBUG = False
    database_url = os.environ.get("DATABASE_URL", "")
    # Railway injecte postgresql:// mais SQLAlchemy 1.4+ nécessite postgresql+psycopg2://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    SQLALCHEMY_DATABASE_URI = database_url
    CACHE_TYPE = "SimpleCache"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
