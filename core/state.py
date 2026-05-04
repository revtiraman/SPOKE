"""Session state management using SQLite."""

import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosqlite
from loguru import logger

from core.config import settings


class SessionState:
    """Async SQLite-backed session state for pipeline runs."""

    def __init__(self):
        self.db_path = str(settings.db_path)
        self._initialized = False
        self._lock = asyncio.Lock()

    async def _ensure_init(self) -> None:
        if self._initialized:
            return
        async with self._lock:
            if self._initialized:
                return
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        data TEXT DEFAULT '{}'
                    )
                """)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS session_artifacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        UNIQUE(session_id, key)
                    )
                """)
                await db.commit()
            self._initialized = True

    async def create_session(self) -> str:
        await self._ensure_init()
        session_id = str(uuid.uuid4())[:8].upper()
        now = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO sessions (id, created_at, updated_at) VALUES (?, ?, ?)",
                (session_id, now, now)
            )
            await db.commit()
        logger.info(f"Session created: {session_id}")
        return session_id

    async def save(self, session_id: str, key: str, value: Any) -> None:
        await self._ensure_init()
        now = datetime.now().isoformat()
        serialized = json.dumps(value if not hasattr(value, "model_dump") else value.model_dump())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO session_artifacts (session_id, key, value, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id, key) DO UPDATE SET value=excluded.value, created_at=excluded.created_at
            """, (session_id, key, serialized, now))
            await db.execute(
                "UPDATE sessions SET updated_at=?, status=? WHERE id=?",
                (now, key, session_id)
            )
            await db.commit()

    async def load(self, session_id: str, key: str) -> Any | None:
        await self._ensure_init()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT value FROM session_artifacts WHERE session_id=? AND key=?",
                (session_id, key)
            ) as cursor:
                row = await cursor.fetchone()
                return json.loads(row[0]) if row else None

    async def get_session(self, session_id: str) -> dict | None:
        await self._ensure_init()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, created_at, updated_at, status FROM sessions WHERE id=?",
                (session_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                return {"id": row[0], "created_at": row[1], "updated_at": row[2], "status": row[3]}

    async def list_sessions(self, limit: int = 20) -> list[dict]:
        await self._ensure_init()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, created_at, updated_at, status FROM sessions ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [{"id": r[0], "created_at": r[1], "updated_at": r[2], "status": r[3]} for r in rows]
