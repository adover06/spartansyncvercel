"""
Test configuration for the LMS application.
"""

import os


class TestConfig:
    """Test configuration class."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key-for-testing-only"
    SESSION_PROTECTION = None
    WERKZEUG_PASSWORD_HASH_METHOD = 'pbkdf2:sha256'
