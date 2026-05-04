"""
System 9 — Business Memory
Persist tools, workflows, pain points, ROI history, and previous automations.
Every future build becomes smarter because of what came before.
"""

from __future__ import annotations
import json
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from loguru import logger

from core.genesis_models import MemoryRecord, MemoryQueryResult
from core.models import ProblemGraph
from core.config import settings


_DB_PATH = settings.db_path.parent / "business_memory.db"


def _keyword_overlap(text_a: str, text_b: str) -> float:
    """Simple keyword similarity for memory retrieval (no ML deps needed)."""
    words_a = set(re.findall(r"\b\w{4,}\b", text_a.lower()))
    words_b = set(re.findall(r"\b\w{4,}\b", text_b.lower()))
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)   # Jaccard similarity


class BusinessMemory:
    """
    System 9 — SQLite-backed memory store for the SPOKE Genesis platform.
    Stores every automation, extracts patterns, and surfaced relevant history
    to improve future builds.
    """

    def __init__(self, db_path: Path = _DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS automations (
                    id          TEXT PRIMARY KEY,
                    session_id  TEXT NOT NULL,
                    agent_name  TEXT NOT NULL,
                    problem_summary TEXT NOT NULL,
                    tools_used  TEXT NOT NULL,     -- JSON array
                    category    TEXT NOT NULL,
                    annual_value REAL DEFAULT 0,
                    hours_saved_weekly REAL DEFAULT 0,
                    created_at  TEXT NOT NULL,
                    tags        TEXT DEFAULT '[]', -- JSON array
                    spawned_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_usage (
                    tool_name   TEXT NOT NULL,
                    category    TEXT NOT NULL,
                    count       INTEGER DEFAULT 0,
                    PRIMARY KEY (tool_name)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS roi_history (
                    id          TEXT PRIMARY KEY,
                    session_id  TEXT NOT NULL,
                    total_value REAL NOT NULL,
                    payback_months REAL NOT NULL,
                    recorded_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save(
        self,
        problem: ProblemGraph,
        session_id: str,
        agent_name: str,
        annual_value: float = 0.0,
        hours_saved_weekly: float = 0.0,
        spawned_count: int = 0,
        tools: list[str] | None = None,
    ) -> MemoryRecord:
        record_id = str(uuid.uuid4())[:8].upper()
        tools_used = tools or (problem.tools_mentioned + problem.tools_implied)
        tags = [problem.category.value if hasattr(problem.category, "value") else str(problem.category)]

        record = MemoryRecord(
            id=record_id,
            session_id=session_id,
            agent_name=agent_name,
            problem_summary=problem.core_pain[:500],
            tools_used=tools_used,
            category=tags[0],
            annual_value=annual_value,
            hours_saved_weekly=hours_saved_weekly,
            created_at=datetime.now().isoformat(),
            tags=tags,
            spawned_count=spawned_count,
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO automations
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.id, record.session_id, record.agent_name,
                    record.problem_summary, json.dumps(record.tools_used),
                    record.category, record.annual_value, record.hours_saved_weekly,
                    record.created_at, json.dumps(record.tags), record.spawned_count,
                ),
            )
            for tool in tools_used:
                conn.execute(
                    """INSERT INTO tool_usage (tool_name, category, count) VALUES (?, ?, 1)
                       ON CONFLICT(tool_name) DO UPDATE SET count = count + 1""",
                    (tool, tags[0]),
                )
            conn.commit()

        logger.success(f"Memory saved: {agent_name} (${annual_value:,.0f}/year) — ID: {record_id}")
        return record

    def query_similar(self, problem: ProblemGraph, top_k: int = 3) -> MemoryQueryResult:
        """Find previous automations similar to the current problem."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, session_id, agent_name, problem_summary, tools_used, "
                "category, annual_value, hours_saved_weekly, created_at, tags, spawned_count "
                "FROM automations ORDER BY created_at DESC LIMIT 50"
            ).fetchall()

        if not rows:
            return MemoryQueryResult(records=[], similar_found=False, similarity_score=0.0)

        scored: list[tuple[float, MemoryRecord]] = []
        query_text = f"{problem.core_pain} {' '.join(problem.tools_mentioned)}"

        for row in rows:
            rec = MemoryRecord(
                id=row[0], session_id=row[1], agent_name=row[2],
                problem_summary=row[3], tools_used=json.loads(row[4]),
                category=row[5], annual_value=row[6], hours_saved_weekly=row[7],
                created_at=row[8], tags=json.loads(row[9]), spawned_count=row[10],
            )
            sim = _keyword_overlap(query_text, rec.problem_summary)
            # Boost by shared category
            cat_match = (rec.category == (
                problem.category.value if hasattr(problem.category, "value") else str(problem.category)
            ))
            if cat_match:
                sim = min(1.0, sim + 0.2)
            scored.append((sim, rec))

        scored.sort(key=lambda x: -x[0])
        top = scored[:top_k]

        top_sim = top[0][0] if top else 0.0
        records = [rec for _, rec in top if _ > 0.1]

        learning = ""
        if records:
            past = records[0]
            learning = (
                f"Similar past build: '{past.agent_name}' (${past.annual_value:,.0f}/year, "
                f"{past.hours_saved_weekly:.0f}h/week saved). "
                f"Applied tools: {', '.join(past.tools_used[:3])}. "
                f"Spawned {past.spawned_count} adjacent agents previously."
            )

        return MemoryQueryResult(
            records=records,
            similar_found=bool(records),
            similarity_score=round(top_sim, 2),
            learning=learning,
        )

    def save_roi(self, session_id: str, total_value: float, payback_months: float) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO roi_history VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4())[:8], session_id, total_value, payback_months,
                 datetime.now().isoformat()),
            )

    def top_tools(self, limit: int = 10) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT tool_name, category, count FROM tool_usage ORDER BY count DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [{"tool": r[0], "category": r[1], "count": r[2]} for r in rows]

    def all_automations(self) -> list[MemoryRecord]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, session_id, agent_name, problem_summary, tools_used, "
                "category, annual_value, hours_saved_weekly, created_at, tags, spawned_count "
                "FROM automations ORDER BY created_at DESC"
            ).fetchall()
        return [
            MemoryRecord(
                id=r[0], session_id=r[1], agent_name=r[2],
                problem_summary=r[3], tools_used=json.loads(r[4]),
                category=r[5], annual_value=r[6], hours_saved_weekly=r[7],
                created_at=r[8], tags=json.loads(r[9]), spawned_count=r[10],
            )
            for r in rows
        ]

    def cumulative_roi(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT SUM(annual_value), COUNT(*) FROM automations"
            ).fetchone()
        total_value = rows[0] or 0.0
        count = rows[1] or 0
        return {
            "total_automations": count,
            "cumulative_annual_value": total_value,
            "average_value_per_automation": (total_value / count) if count else 0.0,
        }
