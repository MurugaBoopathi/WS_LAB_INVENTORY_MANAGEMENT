import json
import os
import re
import threading
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash


class AuthManager:
    """Manage registered users stored in a JSON file."""

    _lock = threading.Lock()
    NT_ID_PATTERN = re.compile(r'^[A-Z]{3}\d[A-Z]{3}$')
    EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    PHONE_PATTERN = re.compile(r'^\+?[0-9\-\s]{7,20}$')

    def __init__(self, users_file):
        self.users_file = users_file
        self._ensure_users_file()

    def _ensure_users_file(self):
        """Create the users file if it does not exist."""
        if not os.path.exists(self.users_file):
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            self._save_users({'users': {}})

    def _load_users(self):
        """Load users from disk."""
        with open(self.users_file, 'r', encoding='utf-8') as file_handle:
            return json.load(file_handle)

    def _save_users(self, data):
        """Save users to disk."""
        with open(self.users_file, 'w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, indent=2, ensure_ascii=False)

    @classmethod
    def normalize_nt_id(cls, nt_id):
        """Normalize NT_ID input to uppercase without extra spaces."""
        return (nt_id or '').strip().upper()

    @classmethod
    def is_valid_nt_id(cls, nt_id):
        """Validate NT_ID format like KNA1COB."""
        return bool(cls.NT_ID_PATTERN.fullmatch(cls.normalize_nt_id(nt_id)))

    @classmethod
    def is_valid_email(cls, email):
        """Validate email format."""
        return bool(cls.EMAIL_PATTERN.fullmatch((email or '').strip()))

    @classmethod
    def is_valid_phone(cls, phone):
        """Validate phone number format."""
        return bool(cls.PHONE_PATTERN.fullmatch((phone or '').strip()))

    def user_exists(self, nt_id):
        """Check whether a user already exists."""
        normalized_nt_id = self.normalize_nt_id(nt_id)
        with self._lock:
            data = self._load_users()
            return normalized_nt_id in data.get('users', {})

    def register_user(self, nt_id, name, email, phone, password):
        """Register a new user with hashed password storage."""
        normalized_nt_id = self.normalize_nt_id(nt_id)
        cleaned_name = (name or '').strip()
        cleaned_email = (email or '').strip().lower()
        cleaned_phone = (phone or '').strip()

        with self._lock:
            data = self._load_users()
            users = data.setdefault('users', {})
            if normalized_nt_id in users:
                return False

            users[normalized_nt_id] = {
                'nt_id': normalized_nt_id,
                'name': cleaned_name,
                'email': cleaned_email,
                'phone': cleaned_phone,
                'password_hash': generate_password_hash(password),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            self._save_users(data)
            return True

    def authenticate_user(self, nt_id, password):
        """Authenticate a registered user with NT_ID and password."""
        normalized_nt_id = self.normalize_nt_id(nt_id)
        with self._lock:
            data = self._load_users()
            user = data.get('users', {}).get(normalized_nt_id)

        if not user:
            return None

        if not check_password_hash(user['password_hash'], password or ''):
            return None

        return {
            'nt_id': user['nt_id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone'],
        }