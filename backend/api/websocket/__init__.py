"""WebSocket Progress Handler - Real-time training progress updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/progress")
async def websocket_progress(websocket: WebSocket):
    """WebSocket endpoint for training progress updates."""
    await manager.connect(websocket)

    # Get training service from app state
    training_service = websocket.app.state.training_service

    # Register callback for progress updates
    async def on_progress(data):
        try:
            # Send status update with proper type wrapper
            await websocket.send_json({
                'type': 'status',
                'data': data
            })
            # Also send logs if any new ones
            logs = training_service.get_logs(50)
            if logs:
                await websocket.send_json({
                    'type': 'logs',
                    'data': logs
                })
        except:
            pass

    # Get the current event loop for cross-thread scheduling
    loop = asyncio.get_running_loop()

    # Wrap async callback for sync training service (called from different thread)
    def sync_callback(data):
        try:
            asyncio.run_coroutine_threadsafe(on_progress(data), loop)
        except Exception:
            pass  # Silently ignore if loop is closed

    training_service.subscribe(sync_callback)

    try:
        # Send initial state
        await websocket.send_json({
            "type": "init",
            "data": training_service.get_progress()
        })
        # Send initial logs
        initial_logs = training_service.get_logs(100)
        if initial_logs:
            await websocket.send_json({
                "type": "logs",
                "data": initial_logs
            })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (ping/pong, commands, etc.)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )

                # Handle client messages
                try:
                    message = json.loads(data)

                    if message.get('type') == 'ping':
                        await websocket.send_json({'type': 'pong'})

                    elif message.get('type') == 'get_status':
                        await websocket.send_json({
                            'type': 'status',
                            'data': training_service.get_progress()
                        })

                    elif message.get('type') == 'get_logs':
                        limit = message.get('limit', 100)
                        await websocket.send_json({
                            'type': 'logs',
                            'data': training_service.get_logs(limit)
                        })

                except json.JSONDecodeError:
                    pass

            except asyncio.TimeoutError:
                # Send periodic status update
                await websocket.send_json({
                    'type': 'status',
                    'data': training_service.get_progress()
                })

    except WebSocketDisconnect:
        pass
    finally:
        training_service.unsubscribe(sync_callback)
        manager.disconnect(websocket)


@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for streaming logs."""
    await manager.connect(websocket)

    training_service = websocket.app.state.training_service
    last_log_count = 0

    try:
        while True:
            logs = training_service.get_logs()
            if len(logs) > last_log_count:
                # Send only new logs
                new_logs = logs[last_log_count:]
                await websocket.send_json({
                    'type': 'logs',
                    'data': new_logs
                })
                last_log_count = len(logs)

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
