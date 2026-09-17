import os


APP_ENV = os.getenv(
    "SEATFLOW_ENV",
    "development",
).strip().lower()


DATABASE_URL = os.getenv(
    "SEATFLOW_DATABASE_URL",
    "sqlite:///./seatflow.db",
)


SECRET_KEY = os.getenv(
    "SEATFLOW_SECRET_KEY",
    "seatflow-development-secret-change-in-production",
)


JWT_ALGORITHM = os.getenv(
    "SEATFLOW_JWT_ALGORITHM",
    "HS256",
)


JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "SEATFLOW_JWT_EXPIRE_MINUTES",
        "1440",
    )
)


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

    if APP_ENV in {"production", "prod"}:
        if not os.getenv("SEATFLOW_SECRET_KEY"):
            raise RuntimeError(
                "SEATFLOW_SECRET_KEY must be configured in production."
            )

        if len(SECRET_KEY) < 32:
            raise RuntimeError(
                "SEATFLOW_SECRET_KEY must be at least 32 characters."
            )

        if not CORS_ORIGINS:
            raise RuntimeError(
                "SEATFLOW_CORS_ORIGINS must be configured in production."
            )