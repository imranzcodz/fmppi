"""Tests for config and database."""
from app.config import Settings, get_settings, settings


class TestConfig:
    def test_settings_defaults_not_from_env(self):
        s = Settings()
        # Values not present in .env should be defaults
        assert s.APP_NAME == "FMPPI Backend API"
        assert s.APP_VERSION == "1.0.0"
        assert s.DEBUG is False
        assert s.ALGORITHM == "HS256"

    def test_get_settings_cached(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_settings_singleton(self):
        assert settings is not None
        assert settings.APP_NAME == "FMPPI Backend API"
