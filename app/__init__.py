import os
import sys
from datetime import timedelta

from flask import Flask
from config import Config


def create_app():
    """Flask application factory."""
    # When running as a PyInstaller frozen exe, bundled resources live in
    # sys._MEIPASS. Point Flask to those absolute paths so templates/static
    # are found correctly.
    if hasattr(sys, '_MEIPASS'):
        template_folder = os.path.join(sys._MEIPASS, 'app', 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'app', 'static')
    else:
        template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config.from_object(Config)

    # Session timeout: auto-logout after 30 minutes of inactivity
    app.permanent_session_lifetime = timedelta(minutes=30)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
