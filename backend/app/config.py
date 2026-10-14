import os

APP_ENV = os.getenv("SEATFLOW_ENV", "development").strip().lower()
DATABASE_URL = os.getenv("SEATFLOW_DATABASE_URL", "sqlite:///./seatflow.db")
SECRET_KEY = os.getenv(
    "SEATFLOW_SECRET_KEY",
    "seatflow-development-secret-change-in-production",
)
JWT_ALGORITHM = os.getenv("SEATFLOW_JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("SEATFLOW_JWT_EXPIRE_MINUTES", "1440"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "SEATFLOW_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]


def validate_settings() -> None:
    """Validate settings that are required outside development."""
    if APP_ENV not in {"production", "prod"}:
        return

    configured_secret = os.getenv("SEATFLOW_SECRET_KEY", "")

    if not configured_secret:
        raise RuntimeError(
            "SEATFLOW_SECRET_KEY must be configured in production."
        )

    if configured_secret == "seatflow-development-secret-change-in-production":
        raise RuntimeError(
            "The development secret must not be used in production."
        )

    if len(configured_secret) < 32:
        raise RuntimeError(
            "SEATFLOW_SECRET_KEY must be at least 32 characters."
        )

    configured_origins = os.getenv("SEATFLOW_CORS_ORIGINS", "").strip()

    if not configured_origins or not CORS_ORIGINS:
        raise RuntimeError(
            "SEATFLOW_CORS_ORIGINS must be explicitly configured "
            "with at least one allowed origin in production."
        )
