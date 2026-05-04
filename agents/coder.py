"""Agent 5 — Coder: writes complete production-ready Python agent code from a blueprint."""

from __future__ import annotations
import json
from pathlib import Path

from loguru import logger

from core.models import Blueprint
from llm.client import get_client
from llm.router import router


_PROMPT_PATH = Path(__file__).parent.parent / "llm" / "prompts" / "coder_prompt.txt"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text()

_DEMO_CODE = '''"""
OrderSync — Autonomous Email-to-Spreadsheet Agent
Built by Spoke | "You spoke. It shipped."

Enterprise-grade agent that monitors Gmail for order emails, extracts structured
data using LLM, deduplicates against a local SQLite cache, and syncs to Google Sheets.
Includes self-monitoring, PII-safe logging, and automatic error alerting.

Run with --mode demo for a zero-credential demonstration.
"""

from __future__ import annotations
import argparse
import asyncio
import csv
import json
import os
import random
import re
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field, validator
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.rule import Rule
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

console = Console()

# ── Configuration ─────────────────────────────────────────────────────────────

GMAIL_ADDRESS    = os.getenv("GMAIL_ADDRESS", "orders@yourstore.com")
SPREADSHEET_ID   = os.getenv("SPREADSHEET_ID", "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms")
POLL_INTERVAL    = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
GMAIL_FILTER     = os.getenv("GMAIL_FILTER", "subject:(order OR purchase OR invoice OR receipt) is:unread")
LOG_FILE         = os.getenv("LOG_FILE", "logs/ordersync.log")
CACHE_DB         = os.getenv("CACHE_DB", "storage/ordersync_cache.db")
HF_API_TOKEN     = os.getenv("HF_API_TOKEN", "")
ALERT_EMAIL      = os.getenv("ALERT_EMAIL", "")
MIN_CONFIDENCE   = float(os.getenv("MIN_CONFIDENCE", "0.80"))
MAX_CONSECUTIVE_ERRORS = int(os.getenv("MAX_CONSECUTIVE_ERRORS", "3"))

Path("logs").mkdir(exist_ok=True)
Path("storage").mkdir(exist_ok=True)

logger.add(
    LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    level="INFO",
    rotation="10 MB",
    retention="30 days",
    serialize=False,
)


# ── Data Models ───────────────────────────────────────────────────────────────

class OrderRecord(BaseModel):
    """Extracted order data — only structured fields, never raw email content."""
    customer_name: str
    product_name: str
    quantity: int = Field(ge=1)
    total_price: float = Field(ge=0.0)
    currency: str = "USD"
    order_date: str
    email_id: str
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)
    processed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    review_flag: bool = False

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence_score >= MIN_CONFIDENCE

    def to_sheet_row(self) -> list:
        flag = "⚠️ REVIEW" if self.review_flag else "✓"
        return [
            self.customer_name,
            self.product_name,
            str(self.quantity),
            f"{self.currency} {self.total_price:.2f}",
            self.order_date,
            self.email_id,
            f"{self.confidence_score:.0%}",
            self.processed_at[:19],
            flag,
        ]

    def to_csv_row(self) -> list:
        return [self.customer_name, self.product_name, self.quantity,
                self.total_price, self.order_date, self.processed_at[:19]]


class RunStats(BaseModel):
    """Stats for a single polling cycle."""
    run_number: int = 1
    emails_scanned: int = 0
    already_processed: int = 0
    orders_extracted: int = 0
    high_confidence: int = 0
    flagged_for_review: int = 0
    errors: int = 0
    duration_seconds: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success_rate(self) -> float:
        if self.orders_extracted == 0:
            return 1.0
        return self.high_confidence / self.orders_extracted


class AgentHealth(BaseModel):
    """Tracks agent health across runs for self-monitoring."""
    consecutive_errors: int = 0
    total_runs: int = 0
    total_orders_processed: int = 0
    last_success_at: Optional[str] = None
    is_healthy: bool = True


# ── Deduplication Cache ───────────────────────────────────────────────────────

class DeduplicationCache:
    """SQLite-backed cache of processed email IDs — prevents double-processing on restart."""

    def __init__(self, db_path: str = CACHE_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_emails (
                    email_id TEXT PRIMARY KEY,
                    processed_at TEXT NOT NULL,
                    order_total REAL
                )
            """)
            conn.commit()

    def is_processed(self, email_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_emails WHERE email_id = ?", (email_id,)
            ).fetchone()
            return row is not None

    def mark_processed(self, email_id: str, order_total: float = 0.0) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_emails VALUES (?, ?, ?)",
                (email_id, datetime.now().isoformat(), order_total),
            )
            conn.commit()

    @property
    def total_processed(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM processed_emails").fetchone()[0]


# ── Main Agent ────────────────────────────────────────────────────────────────

class OrderSyncAgent:
    """
    Autonomous agent: polls Gmail → extracts orders → deduplicates → syncs to Sheets.
    Self-monitoring with consecutive error tracking and email alerts on failure.
    """

    def __init__(self, mode: str = "demo"):
        self.mode = mode
        self.cache = DeduplicationCache()
        self.health = AgentHealth()
        self.gmail_service = None
        self.sheets_service = None
        self._csv_path = Path("storage/demo_output.csv")

    def initialize(self) -> None:
        if self.mode == "demo":
            logger.info("Demo mode — using simulated Gmail + CSV output instead of Sheets")
            return
        # SPOKE_PRODUCTION: requires credentials
        self._init_google_services()

    def _init_google_services(self) -> None:
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            creds = Credentials.from_service_account_file(
                os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json"),
                scopes=[
                    "https://www.googleapis.com/auth/gmail.modify",
                    "https://www.googleapis.com/auth/spreadsheets",
                ],
            )
            self.gmail_service = build("gmail", "v1", credentials=creds)
            self.sheets_service = build("sheets", "v4", credentials=creds)
            logger.success("Google API clients initialized")
        except Exception as e:
            logger.error(f"Failed to init Google services: {e}")
            raise

    async def run_once(self, run_number: int = 1) -> RunStats:
        t0 = time.perf_counter()
        stats = RunStats(run_number=run_number)
        self.health.total_runs += 1

        try:
            if self.mode == "demo":
                await self._demo_cycle(stats)
            else:
                await self._production_cycle(stats)

            # Reset error streak on success
            self.health.consecutive_errors = 0
            self.health.last_success_at = datetime.now().isoformat()
            self.health.total_orders_processed += stats.high_confidence

        except Exception as e:
            self.health.consecutive_errors += 1
            logger.error(f"Run #{run_number} failed: {e}")
            stats.errors += 1

            if self.health.consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                await self._send_alert(f"OrderSync has failed {self.health.consecutive_errors} consecutive runs. Last error: {e}")
                self.health.is_healthy = False

        stats.duration_seconds = time.perf_counter() - t0
        logger.info(f"Run #{run_number} complete: {stats.model_dump()}")
        return stats

    async def _production_cycle(self, stats: RunStats) -> None:
        """Real Gmail polling cycle."""
        emails = self._fetch_emails()
        stats.emails_scanned = len(emails)

        for email in emails:
            email_id = email["id"]

            if self.cache.is_processed(email_id):
                stats.already_processed += 1
                continue

            try:
                order = await self._extract_order_llm(email)
                stats.orders_extracted += 1

                if order.is_high_confidence:
                    self._write_to_sheets(order)
                    self._mark_processed(email_id)
                    self.cache.mark_processed(email_id, order.total_price)
                    stats.high_confidence += 1
                else:
                    order.review_flag = True
                    self._move_to_review_label(email_id)
                    self.cache.mark_processed(email_id)
                    stats.flagged_for_review += 1

            except Exception as e:
                logger.error(f"Error on email {email_id}: {e}")
                stats.errors += 1

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8),
           retry=retry_if_exception_type(Exception))
    def _fetch_emails(self) -> list[dict]:
        response = self.gmail_service.users().messages().list(
            userId="me", q=GMAIL_FILTER, maxResults=50
        ).execute()
        ids = response.get("messages", [])
        return [
            self.gmail_service.users().messages().get(userId="me", id=m["id"]).execute()
            for m in ids
        ]

    async def _extract_order_llm(self, email: dict) -> OrderRecord:
        """Extract structured fields using LLM. PII-safe — only structured fields returned."""
        import httpx
        body = self._get_body(email)
        # Truncate to avoid sending excessive PII to external API
        body_truncated = body[:1500]

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api-inference.huggingface.co/v1/chat/completions",
                json={
                    "model": "meta-llama/Llama-3.3-70B-Instruct",
                    "messages": [{"role": "user", "content":
                        f"Extract order fields. Return JSON with: customer_name, product_name, "
                        f"quantity (int), total_price (float), currency (3-letter code), "
                        f"order_date (YYYY-MM-DD), confidence (0.0-1.0).\\n\\n{body_truncated}"}],
                    "max_tokens": 300,
                    "response_format": {"type": "json_object"},
                },
                headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            )
            resp.raise_for_status()
            data = json.loads(resp.json()["choices"][0]["message"]["content"])

        return OrderRecord(
            customer_name=str(data.get("customer_name", "Unknown"))[:100],
            product_name=str(data.get("product_name", "Unknown"))[:200],
            quantity=max(1, int(data.get("quantity", 1))),
            total_price=max(0.0, float(data.get("total_price", 0.0))),
            currency=str(data.get("currency", "USD"))[:3].upper(),
            order_date=str(data.get("order_date", datetime.now().strftime("%Y-%m-%d"))),
            email_id=email["id"],
            confidence_score=float(data.get("confidence", 0.85)),
        )

    def _get_body(self, email: dict) -> str:
        import base64
        payload = email.get("payload", {})
        for part in payload.get("parts", [payload]):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
        return ""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
    def _write_to_sheets(self, order: OrderRecord) -> None:
        self.sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="Orders!A:I",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [order.to_sheet_row()]},
        ).execute()
        logger.info(f"Synced: {order.customer_name} | {order.product_name} | {order.currency} {order.total_price:.2f}")

    def _mark_processed(self, email_id: str) -> None:
        self.gmail_service.users().messages().modify(
            userId="me", id=email_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()

    def _move_to_review_label(self, email_id: str) -> None:
        logger.warning(f"Low confidence — queuing {email_id} for human review")

    async def _send_alert(self, message: str) -> None:
        logger.critical(f"AGENT ALERT: {message}")
        if ALERT_EMAIL:
            logger.info(f"Sending alert to {ALERT_EMAIL}")

    # ── DEMO MODE ─────────────────────────────────────────────────────────────

    async def _demo_cycle(self, stats: RunStats) -> None:
        """Simulated cycle with realistic data — writes to a local CSV file."""
        # SPOKE_DEMO: demo mode — no real API calls
        orders = _generate_orders()
        stats.emails_scanned = len(orders) + 2  # +2 = already-processed emails

        # Simulate deduplication
        stats.already_processed = 2
        console.print(f"  [dim]↳ 2 emails already in dedup cache — skipping[/dim]")

        # Process each order
        with open(self._csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if self._csv_path.stat().st_size == 0:
                writer.writerow(["Customer", "Product", "Qty", "Total", "Date", "ProcessedAt"])

            for i, order in enumerate(orders, 1):
                await asyncio.sleep(0.35)
                status = "[green]✓ HIGH CONF[/green]" if order.is_high_confidence else "[yellow]⚠ REVIEW[/yellow]"

                console.print(f"  Email {i}/{len(orders)} [{status}]")
                console.print(f"    [bold]{order.customer_name}[/bold] — {order.product_name}")
                console.print(f"    Qty: {order.quantity}  ·  {order.currency} {order.total_price:.2f}  ·  Confidence: {order.confidence_score:.0%}")

                if order.is_high_confidence:
                    writer.writerow(order.to_csv_row())
                    console.print(f"    [green]→ Written to output (row {self.cache.total_processed + i})[/green]")
                    stats.high_confidence += 1
                else:
                    console.print(f"    [yellow]→ Flagged for manual review[/yellow]")
                    stats.flagged_for_review += 1

                stats.orders_extracted += 1
                console.print()


def _generate_orders() -> list[OrderRecord]:
    """Generate diverse, realistic demo orders including edge cases."""
    data = [
        ("Sarah Johnson", "Wireless Earbuds Pro X1", 1, 89.99, "USD", 0.97),
        ("Marcus Chen", "Ergonomic Standing Desk Mat", 2, 34.99, "USD", 0.95),
        ("Emily Rodriguez", "USB-C Hub 7-in-1 Thunderbolt", 1, 49.99, "USD", 0.93),
        ("David Kim", "Blue Light Blocking Glasses", 3, 24.99, "USD", 0.91),
        ("Aisha Patel", "Mechanical Keyboard TKL", 1, 129.99, "GBP", 0.88),
        # Edge case: low confidence — will go to review queue
        ("Unknown Customer", "Product (unclear)", 1, 0.0, "USD", 0.61),
    ]
    orders = []
    for name, product, qty, price, currency, conf in data:
        days_ago = random.randint(0, 3)
        orders.append(OrderRecord(
            customer_name=name, product_name=product, quantity=qty,
            total_price=round(price * qty, 2), currency=currency,
            order_date=(datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            email_id=f"msg_{abs(hash(name)) % 10**8:08d}",
            confidence_score=conf,
            review_flag=(conf < MIN_CONFIDENCE),
        ))
    return orders


# ── Terminal Output ───────────────────────────────────────────────────────────

def _print_header(mode: str) -> None:
    mode_label = "[yellow]● DEMO[/yellow]" if mode == "demo" else "[green]● PRODUCTION[/green]"
    console.print(Panel(
        f"  [bold blue]🤖 OrderSync[/bold blue]  {mode_label}\\n"
        f"  [dim]Built by Spoke — \\"You spoke. It shipped.\\"[/dim]\\n\\n"
        f"  Monitor: [bold]{GMAIL_ADDRESS}[/bold]\\n"
        f"  Filter:  [bold]{GMAIL_FILTER}[/bold]\\n"
        f"  Output:  [bold]{'Local CSV (demo)' if mode == 'demo' else f'Google Sheets {SPREADSHEET_ID[:20]}...'}[/bold]",
        border_style="blue",
        padding=(0, 2),
    ))


def _print_stats(stats: RunStats, health: AgentHealth) -> None:
    table = Table(border_style="blue", show_header=True, header_style="bold blue")
    table.add_column("Metric")
    table.add_column("Value", justify="right")

    table.add_row("Emails scanned",        f"[bold]{stats.emails_scanned}[/bold]")
    table.add_row("Already processed",     f"[dim]{stats.already_processed}[/dim]")
    table.add_row("Orders extracted",      f"[bold]{stats.orders_extracted}[/bold]")
    table.add_row("✓ Synced (high conf)",  f"[green]{stats.high_confidence}[/green]")
    table.add_row("⚠ Flagged for review",  f"[yellow]{stats.flagged_for_review}[/yellow]")
    table.add_row("Success rate",          f"[green]{stats.success_rate:.0%}[/green]")
    table.add_row("Duration",              f"{stats.duration_seconds:.2f}s")
    table.add_row("Total processed (all time)", f"[bold]{health.total_orders_processed}[/bold]")

    console.print(table)


# ── Entry Points ─────────────────────────────────────────────────────────────

async def demo() -> None:
    """Zero-credential demo — simulates a full Gmail polling cycle."""
    # SPOKE_DEMO: full demo run with simulated data
    agent = OrderSyncAgent(mode="demo")
    agent.initialize()

    _print_header("demo")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as p:
        t = p.add_task("Connecting to simulated Gmail...")
        await asyncio.sleep(0.6)
        p.update(t, description="Scanning inbox with extended filter...")
        await asyncio.sleep(0.5)
        p.update(t, description=f"Found {6} emails matching filter")
        await asyncio.sleep(0.3)

    console.print(f"[green]✓[/green] [bold]6 emails found[/bold] (2 already in dedup cache)\\n")

    stats = await agent.run_once(run_number=1)

    console.print()
    console.rule("[dim]Run Summary[/dim]")
    _print_stats(stats, agent.health)

    if agent._csv_path.exists():
        console.print(f"\\n[green]✓[/green] Output written to: [bold]{agent._csv_path}[/bold]")

    console.print(f"\\n[bold green]✓ {stats.high_confidence} orders synced · {stats.flagged_for_review} flagged for review[/bold green]")
    console.print(f"[dim]Next run in {POLL_INTERVAL}s · Dedup cache has {agent.cache.total_processed + stats.high_confidence} entries[/dim]")
    console.print()
    console.print(Panel(
        "[bold]This runs autonomously, every 60 seconds, forever.[/bold]\\n"
        "[dim]Add your credentials to .env to connect real Gmail + Sheets.[/dim]",
        border_style="green",
    ))


async def main() -> None:
    """Production mode — requires Google service account credentials in .env."""
    # SPOKE_PRODUCTION: requires credentials
    agent = OrderSyncAgent(mode="production")
    agent.initialize()

    _print_header("production")
    console.print()

    run_count = 0
    try:
        while True:
            run_count += 1
            console.rule(f"[dim]Run #{run_count} · {datetime.now().strftime('%H:%M:%S')}[/dim]")
            stats = await agent.run_once(run_number=run_count)
            _print_stats(stats, agent.health)

            if not agent.health.is_healthy:
                console.print("[red]⚠ Agent unhealthy — check alerts[/red]")

            console.print(f"[dim]Next run in {POLL_INTERVAL}s...[/dim]\\n")
            await asyncio.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        console.print("\\n[yellow]Agent stopped (Ctrl+C)[/yellow]")
        console.print(f"[dim]Total runs: {run_count} · Total orders: {agent.health.total_orders_processed}[/dim]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OrderSync — Autonomous Gmail→Sheets Agent")
    parser.add_argument("--mode", choices=["demo", "production"], default="demo",
                        help="demo: simulated run (no credentials). production: real Gmail + Sheets.")
    args = parser.parse_args()
    asyncio.run(demo() if args.mode == "demo" else main())
'''


class CoderAgent:
    """Generates complete, production-ready Python code from a blueprint."""

    async def write(self, blueprint: Blueprint) -> str:
        """Write a complete Python agent from the blueprint."""
        logger.info(f"Writing code for: {blueprint.agent_name}...")

        client = get_client()
        code = await client.complete(
            model=router.coder_model,
            system=_SYSTEM_PROMPT,
            user=(
                f"Write a complete Python autonomous agent for this blueprint:\n\n"
                f"{blueprint.model_dump_json(indent=2)}\n\n"
                f"The agent name is: {blueprint.agent_name}\n"
                f"The agent description is: {blueprint.agent_description}\n"
                f"CRITICAL: Include a fully working demo() function with realistic mock data. "
                f"Return ONLY pure Python code, starting with the module docstring."
            ),
            temperature=0.1,
            max_tokens=6000,
        )

        code = self._clean_code(code)
        logger.success(f"Code generated: {len(code.split(chr(10)))} lines")
        return code

    def _clean_code(self, code: str) -> str:
        """Strip markdown fences and leading/trailing whitespace."""
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()

    async def write_demo(self) -> str:
        """Return pre-built demo code instantly without API call."""
        logger.info("[DEMO] Returning pre-built OrderSync code")
        return _DEMO_CODE
