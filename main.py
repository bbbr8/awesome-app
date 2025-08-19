"""
Awesome App
============

This module defines a small FastAPI application that exposes a simple REST
endpoint for listing and creating tasks and a websocket endpoint for
broadcasting task updates in real‑time. The service stores tasks in
memory and pushes notifications to all connected websocket clients when a
task is added.

The architecture is deliberately minimal yet demonstrates asynchronous
programming, REST endpoints and websockets all living together in a
single, self‑contained FastAPI service.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict


app = FastAPI()


class ConnectionManager:
    """Manage websocket connections and broadcast messages."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a websocket connection and add it to the pool."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a websocket from the pool when it disconnects."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        """Send a message to all connected websockets."""
        disconnected = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)


# A global connection manager to keep track of websocket clients
manager = ConnectionManager()

# In‑memory store for tasks; in a real system this would be a database
tasks: List[Dict[str, str]] = []


@app.get("/")
async def serve_frontend() -> HTMLResponse:
    """Serve the static HTML page for the front‑end."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/tasks")
async def get_tasks() -> Dict[str, List[Dict[str, str]]]:
    """Return all tasks as JSON."""
    return {"tasks": tasks}


@app.post("/tasks")
async def add_task(task: Dict[str, str]) -> Dict[str, str]:
    """Add a task via REST and broadcast it to all websocket clients."""
    tasks.append(task)
    await manager.broadcast(f"new_task:{task}")
    return {"status": "task_added"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle websocket connections for real‑time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Support simple commands prefixed by a tag
            if data.startswith("add_task:"):
                content = data[len("add_task:"):].strip()
                if content:
                    task = {"id": str(len(tasks)), "content": content}
                    tasks.append(task)
                    await manager.broadcast(f"new_task:{task}")
            else:
                # Echo unrecognised messages to all clients
                await manager.broadcast(f"message:{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected")
