from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(
        self,
        restaurant_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()
        self.connections[restaurant_id].add(websocket)

    def disconnect(
        self,
        restaurant_id: int,
        websocket: WebSocket,
    ):
        connections = self.connections.get(restaurant_id)

        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            self.connections.pop(restaurant_id, None)

    async def broadcast(
        self,
        restaurant_id: int,
        message: dict,
    ):
        connections = list(
            self.connections.get(
                restaurant_id,
                set(),
            )
        )

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(
                restaurant_id,
                websocket,
            )


manager = ConnectionManager()


async def broadcast_waitlist_update(
    restaurant_id: int,
    action: str,
    entry_id: int | None = None,
):
    await manager.broadcast(
        restaurant_id,
        {
            "type": "waitlist.updated",
            "action": action,
            "entry_id": entry_id,
        },
    )
