"""FastAPI REST endpoints for the Spoke pipeline."""

from __future__ import annotations
import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.config import settings
from core.pipeline import SpokePipeline
from core.state import SessionState

router = APIRouter()
_pipeline = SpokePipeline()
_state = SessionState()


# ── Request / Response models ─────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str
    demo_mode: bool = False


class ResumeRequest(BaseModel):
    session_id: str
    answers: dict[str, str]


class PipelineStatusResponse(BaseModel):
    session_id: str
    status: str
    updated_at: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/pipeline/run/text")
async def run_from_text(body: TextInput):
    """Start pipeline from raw transcript text (useful for testing)."""
    result = await _pipeline.run(
        transcript_text=body.text,
        demo_mode=body.demo_mode,
    )
    return result.model_dump()


@router.post("/pipeline/run/video")
async def run_from_video(
    file: UploadFile = File(...),
    demo_mode: bool = Form(default=False),
):
    """Upload a video and start the pipeline."""
    allowed = {".mp4", ".mov", ".webm", ".avi", ".mp3", ".wav", ".m4a"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {allowed}")

    upload_path = settings.storage_dir / f"upload_{uuid.uuid4().hex[:8]}{ext}"
    async with aiofiles.open(upload_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    result = await _pipeline.run(
        video_path=str(upload_path),
        demo_mode=demo_mode,
    )
    return result.model_dump()


@router.post("/pipeline/demo")
async def run_demo():
    """Run the full pipeline in demo mode — zero credentials required."""
    result = await _pipeline.run(demo_mode=True)
    return result.model_dump()


@router.post("/pipeline/resume")
async def resume_pipeline(body: ResumeRequest):
    """Resume a pipeline that was paused for clarification answers."""
    result = await _pipeline.resume(
        session_id=body.session_id,
        clarification_answers=body.answers,
    )
    return result.model_dump()


@router.get("/sessions")
async def list_sessions():
    """List recent pipeline sessions."""
    return await _state.list_sessions()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get details of a specific session."""
    session = await _state.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Session {session_id} not found")
    return session


@router.get("/download/{session_id}")
async def download_agent(session_id: str):
    """Download the generated agent ZIP package."""
    zip_dir = settings.generated_dir / session_id
    zips = list(zip_dir.glob("*.zip")) if zip_dir.exists() else []
    if not zips:
        raise HTTPException(404, f"No deployment package found for session {session_id}")
    return FileResponse(
        str(zips[0]),
        media_type="application/zip",
        filename=zips[0].name,
    )


@router.get("/health")
async def health():
    """Health check endpoint."""
    from llm.client import get_usage
    usage = get_usage()
    return {
        "status": "ok",
        "has_hf": settings.has_hf,
        "has_anthropic": settings.has_anthropic,
        "sandbox_type": settings.sandbox_type,
        "token_usage": {"prompt": getattr(usage, "prompt_tokens", 0), "completion": getattr(usage, "completion_tokens", 0)},
    }
