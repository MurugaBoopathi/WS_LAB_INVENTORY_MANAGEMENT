import os


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

    # Data file path (JSON-based, no database)
    DATA_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app', 'data', 'inventory.json'
    )

    # Application Host & Port
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
