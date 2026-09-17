from fastapi import FastAPI

from app.database import Base, engine

# Register all SQLAlchemy models.
from app.models import Restaurant, User, WaitlistEntry  # noqa: F401

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.waitlist import router as waitlist_router
from app.api.websocket import router as websocket_router
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SeatFlow Restaurant Waitlist API",
    version="2.2.0",
    description=(
        "SaaS-ready multi-tenant restaurant "
        "waitlist management system."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(waitlist_router)
app.include_router(websocket_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "seatflow-api",
    }
