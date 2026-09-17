import jwt

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth import ALGORITHM, SECRET_KEY
from app.services.websocket import manager


router = APIRouter(
    tags=["WebSocket"],
)


def authenticate_websocket(
    token: str,
    db: Session,
) -> User | None:

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        user = db.get(
            User,
            int(user_id),
        )

        if user is None:
            return None

        if not user.is_active:
            return None

        token_restaurant_id = payload.get(
            "restaurant_id"
        )

        if token_restaurant_id is None:
            return None

        if int(token_restaurant_id) != user.restaurant_id:
            return None

        return user

    except (
        jwt.InvalidTokenError,
        TypeError,
        ValueError,
    ):
        return None


@router.websocket("/ws/waitlist")
async def waitlist_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    token = websocket.query_params.get("token")

    if token is None or not token.strip():
        await websocket.close(
            code=1008,
            reason="Authentication required",
        )
        return

    token = token.strip()

    user = authenticate_websocket(
        token,
        db,
    )

    if user is None:
        await websocket.close(
            code=1008,
            reason="Invalid authentication token",
        )
        return

    restaurant_id = user.restaurant_id

    await manager.connect(
        restaurant_id,
        websocket,
    )

    await websocket.send_json(
        {
            "type": "connected",
            "restaurant_id": restaurant_id,
            "user_id": user.id,
        }
    )

    try:
        while True:
            message = await websocket.receive_text()

            if message == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                    }
                )

    except WebSocketDisconnect:
        pass

    finally:
        manager.disconnect(
            restaurant_id,
            websocket,
        )
