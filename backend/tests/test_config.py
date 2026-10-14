import pytest

from app import config


def configure_valid_production(monkeypatch):
    secret = "test-production-secret-" + ("x" * 32)
    origins = "https://seatflow.example.com"

    monkeypatch.setattr(config, "APP_ENV", "production")
    monkeypatch.setattr(config, "SECRET_KEY", secret)
    monkeypatch.setattr(config, "CORS_ORIGINS", [origins])
    monkeypatch.setenv("SEATFLOW_SECRET_KEY", secret)
    monkeypatch.setenv("SEATFLOW_CORS_ORIGINS", origins)


def test_development_settings_do_not_require_production_secrets(monkeypatch):
    monkeypatch.setattr(config, "APP_ENV", "development")
    monkeypatch.delenv("SEATFLOW_SECRET_KEY", raising=False)
    monkeypatch.delenv("SEATFLOW_CORS_ORIGINS", raising=False)

    config.validate_settings()


def test_production_rejects_missing_secret(monkeypatch):
    configure_valid_production(monkeypatch)
    monkeypatch.delenv("SEATFLOW_SECRET_KEY")

    with pytest.raises(RuntimeError, match="must be configured"):
        config.validate_settings()


def test_production_rejects_development_secret(monkeypatch):
    configure_valid_production(monkeypatch)
    development_secret = (
        "seatflow-development-secret-change-in-production"
    )
    monkeypatch.setenv("SEATFLOW_SECRET_KEY", development_secret)
    monkeypatch.setattr(config, "SECRET_KEY", development_secret)

    with pytest.raises(RuntimeError, match="development secret"):
        config.validate_settings()


def test_production_rejects_short_secret(monkeypatch):
    configure_valid_production(monkeypatch)
    monkeypatch.setenv("SEATFLOW_SECRET_KEY", "too-short")
    monkeypatch.setattr(config, "SECRET_KEY", "too-short")

    with pytest.raises(RuntimeError, match="at least 32 characters"):
        config.validate_settings()


def test_production_requires_explicit_cors_origins(monkeypatch):
    configure_valid_production(monkeypatch)
    monkeypatch.delenv("SEATFLOW_CORS_ORIGINS")

    with pytest.raises(RuntimeError, match="SEATFLOW_CORS_ORIGINS"):
        config.validate_settings()


def test_production_accepts_explicit_valid_settings(monkeypatch):
    configure_valid_production(monkeypatch)

    config.validate_settings()
