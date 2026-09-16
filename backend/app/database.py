import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


if os.getenv("SEATFLOW_TESTING") == "1":
    DATABASE_URL = "sqlite:///./seatflow_test.db"
else:
    DATABASE_URL = "sqlite:///./seatflow.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
