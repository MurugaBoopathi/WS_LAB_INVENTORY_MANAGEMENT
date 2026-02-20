from datetime import timedelta

from flask import Flask
from config import Config


def create_app():
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Session timeout: auto-logout after 30 minutes of inactivity
    app.permanent_session_lifetime = timedelta(minutes=30)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
