"""WebSocket endpoint for real-time pipeline progress streaming."""

from __future__ import annotations
import asyncio
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from core.models import PipelineStatus, ProgressUpdate
from core.pipeline import SpokePipeline


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[session_id] = ws
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str) -> None:
        self._connections.pop(session_id, None)
        logger.info(f"WebSocket disconnected: {session_id}")

    async def send(self, session_id: str, data: dict) -> None:
        ws = self._connections.get(session_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data))
            except Exception as e:
                logger.warning(f"WebSocket send error for {session_id}: {e}")
                self.disconnect(session_id)


manager = ConnectionManager()


async def websocket_pipeline_endpoint(
    websocket: WebSocket,
    session_id: str,
    mode: str = "demo",
) -> None:
    """WebSocket handler: runs pipeline and streams progress to client."""
    await manager.connect(session_id, websocket)

    pipeline = SpokePipeline()
    is_demo = mode == "demo"

    async def send_progress(
        message: str,
        percent: int,
        status: PipelineStatus,
        detail: str = "",
    ) -> None:
        update = ProgressUpdate(
            message=message,
            percent=percent,
            status=status,
            detail=detail,
        )
        await manager.send(session_id, {
            "type": "progress",
            "data": update.model_dump(),
        })

    try:
        # Receive initial config from client
        init_data_raw = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
        init_data: dict = json.loads(init_data_raw)
    except (asyncio.TimeoutError, json.JSONDecodeError):
        init_data = {}

    video_path = init_data.get("video_path")
    transcript_text = init_data.get("transcript_text")
    clarification_answers = init_data.get("clarification_answers")

    try:
        result = await pipeline.run(
            video_path=video_path,
            transcript_text=transcript_text,
            clarification_answers=clarification_answers,
            session_id=session_id,
            progress=send_progress,
            demo_mode=is_demo,
        )

        await manager.send(session_id, {
            "type": "complete",
            "data": result.model_dump(exclude={"code", "deployment"}),
            "preview": result.execution_preview[:2000] if result.execution_preview else "",
            "agent_name": result.agent_name,
            "hours_saved": result.time_saved_hours_per_week,
            "session_id": session_id,
            "status": result.status,
            "error": result.error,
        })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected during pipeline: {session_id}")
    except Exception as e:
        logger.exception(f"Pipeline error for session {session_id}: {e}")
        await manager.send(session_id, {
            "type": "error",
            "message": str(e),
        })
    finally:
        manager.disconnect(session_id)
