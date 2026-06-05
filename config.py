import os
import sys
import configparser


def _load_settings_ini():
    """
    Load settings.ini from the same directory as the exe (or script).
    Injects values into os.environ so Config picks them up via os.environ.get().
    """
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    ini_path = os.path.join(base, 'settings.ini')
    if os.path.exists(ini_path):
        cfg = configparser.ConfigParser()
        cfg.read(ini_path)
        if cfg.has_section('settings'):
            for key, val in cfg.items('settings'):
                os.environ.setdefault(key.upper(), val)


_load_settings_ini()


class Config:
    """Application Configuration for Lab Inventory Management Tool"""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'lab-inventory-secret-key-2026')

    # ============================================================
    # SMTP Configuration - UPDATE WITH YOUR BOSCH SMTP DETAILS
    # ============================================================
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'rb-smtp.2mdc.net')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 25))
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'False').lower() == 'true'
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')

    # ============================================================
    # Email Recipients - UPDATE WITH ACTUAL BOSCH EMAIL IDs
    # ============================================================
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'mpi2cob@bosch.com')
    MANAGER_EMAIL = os.environ.get('MANAGER_EMAIL', 'mpi2cob@bosch.com')
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'lab-inventory-noreply@bosch.com')
    EMAIL_DOMAIN = os.environ.get('EMAIL_DOMAIN', '@bosch.com')

    # ============================================================
    # Admin Credentials - UPDATE WITH ACTUAL ADMIN NT ID
    # ============================================================
    ADMIN_NT_ID = os.environ.get('ADMIN_NT_ID', 'ADMIN')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@123')

    # Data file path — works in dev mode and as compiled exe
    # When frozen: stored next to the .exe so it is writable
    _base_dir = (
        os.path.dirname(sys.executable)
        if hasattr(sys, '_MEIPASS')
        else os.path.dirname(os.path.abspath(__file__))
    )
    DATA_FILE = os.path.join(_base_dir, 'data', 'inventory.json')

    # Application Host & Port
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
