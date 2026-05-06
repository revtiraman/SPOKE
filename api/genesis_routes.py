"""FastAPI routes for SPOKE Genesis — the 10-system upgrade."""

from __future__ import annotations
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import BaseModel

from core.config import settings
from core.genesis_pipeline import GenesisOrchestrator
from agents.memory import BusinessMemory

router = APIRouter()
_genesis = GenesisOrchestrator()
_memory = BusinessMemory()


class GenesisTextRequest(BaseModel):
    text: str
    demo_mode: bool = False


class GenesisResumeRequest(BaseModel):
    session_id: str
    answers: dict[str, str]


@router.post("/genesis/demo")
async def genesis_demo():
    """Run the full Genesis pipeline in demo mode — zero credentials required."""
    result = await _genesis.run(demo_mode=True)
    return result.model_dump()


@router.post("/genesis/run/text")
async def genesis_from_text(body: GenesisTextRequest):
    """Run Genesis from a typed transcript."""
    result = await _genesis.run(
        transcript_text=body.text,
        demo_mode=body.demo_mode,
    )
    return result.model_dump()


@router.post("/genesis/run/video")
async def genesis_from_video(
    file: UploadFile = File(...),
    demo_mode: bool = Form(default=False),
):
    """Upload a video and run the full Genesis pipeline."""
    allowed = {".mp4", ".mov", ".webm", ".avi", ".mp3", ".wav", ".m4a"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported format: {ext}")

    upload_path = settings.storage_dir / f"genesis_upload_{uuid.uuid4().hex[:8]}{ext}"
    async with aiofiles.open(upload_path, "wb") as f:
        await f.write(await file.read())

    result = await _genesis.run(
        video_path=str(upload_path),
        demo_mode=demo_mode,
    )
    return result.model_dump()


@router.post("/genesis/resume")
async def genesis_resume(body: GenesisResumeRequest):
    """Resume a Genesis run paused for clarification."""
    result = await _genesis.resume(
        session_id=body.session_id,
        clarification_answers=body.answers,
    )
    return result.model_dump()


@router.get("/genesis/memory")
async def get_memory():
    """Get all stored automations from business memory."""
    return {
        "automations": [r.model_dump() for r in _memory.all_automations()],
        "cumulative": _memory.cumulative_roi(),
        "top_tools": _memory.top_tools(),
    }


@router.get("/genesis/memory/stats")
async def get_memory_stats():
    """Get aggregate business memory statistics."""
    return {
        "cumulative": _memory.cumulative_roi(),
        "top_tools": _memory.top_tools(5),
    }
