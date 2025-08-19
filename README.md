# Awesome App

This repository contains a compact yet expressive demonstration of how to
build a real‑time web application with Python using [FastAPI](https://fastapi.tiangolo.com/).

## Features

- **REST and WebSockets**: Exposes a `/tasks` REST endpoint for listing and
  creating tasks and a `/ws` websocket endpoint for broadcasting updates
  when new tasks are added.
- **In‑memory storage**: Keeps task data in memory to avoid external
  dependencies. The patterns used here easily extend to a database.
- **Minimal front‑end**: Provides a simple HTML page (`static/index.html`) to
  demonstrate interacting with the API and receiving live updates.

## Running the App

1. Install the dependencies (it is recommended to use a virtualenv):

   ```bash
   pip install -r requirements.txt
   ```

2. Run the server using [uvicorn](https://www.uvicorn.org/):

   ```bash
   uvicorn main:app --reload
   ```

3. Open your browser at [`http://localhost:8000`](http://localhost:8000) to
   load the front‑end. In another browser tab or window, load the same
   URL. Adding tasks in one window will propagate to all connected clients
   in real time via websockets.

## Notes

This application stores all data in memory. If you restart the server,
the tasks list will be reset. To persist data across restarts you can
swap the in‑memory list with a database or external storage.
