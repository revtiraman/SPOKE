"""SPOKE Genesis — FastAPI application entrypoint."""

from __future__ import annotations
import uuid

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from core.config import settings
from api.routes import router as api_router
from api.genesis_routes import router as genesis_router
from api.websocket import websocket_pipeline_endpoint


def create_app() -> FastAPI:
    app = FastAPI(
        title="SPOKE Genesis API",
        description="Autonomous Business Automation Intelligence Platform — You spoke. It shipped. And then it built 4 more.",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")
    app.include_router(genesis_router, prefix="/api/v1")

    @app.websocket("/ws/{session_id}")
    async def ws_endpoint(websocket: WebSocket, session_id: str, mode: str = "demo"):
        await websocket_pipeline_endpoint(websocket, session_id, mode=mode)

    @app.websocket("/ws/demo")
    async def ws_demo(websocket: WebSocket):
        session_id = str(uuid.uuid4())[:8].upper()
        await websocket_pipeline_endpoint(websocket, session_id, mode="demo")

    @app.on_event("startup")
    async def startup():
        logger.info(f"SPOKE Genesis API v2.0 starting on {settings.app_host}:{settings.app_port}")
        logger.info(f"HF API: {'✓' if settings.has_hf else '✗ (demo only)'}")
        logger.info(f"Anthropic: {'✓' if settings.has_anthropic else '✗'}")
        logger.info(f"Sandbox: {settings.sandbox_type}")
        logger.info("Genesis systems: AgentSpawn · Counterfactual · Multimodal · Simulator · Economic · SelfHeal · Deployment · Memory · Discovery")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
