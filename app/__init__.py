from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
bcrypt = Bcrypt()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name="default"):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config[config_name])

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # Login config
    login_manager.login_view = "admin_bp.login"
    login_manager.login_message = "Connectez-vous pour accéder à cette page."
    login_manager.login_message_category = "warning"

    # Ensure upload folder exists
    os.makedirs(app.config.get("UPLOAD_FOLDER", "static/uploads"), exist_ok=True)

    # Register blueprints
    from app.routes import main_bp
    from app.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            "blog_title": app.config["BLOG_TITLE"],
            "blog_description": app.config["BLOG_DESCRIPTION"],
            "blog_author": app.config["BLOG_AUTHOR"],
        }

    return app
