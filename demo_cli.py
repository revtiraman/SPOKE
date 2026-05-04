"""
Spoke — CLI demo runner.
Run the full 8-agent pipeline in demo mode from the terminal.
No credentials required. No UI needed.

Usage:  python demo_cli.py
        python demo_cli.py --transcript "I manually copy invoices into QuickBooks every day"
"""

from __future__ import annotations
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich import print as rprint

from core.models import PipelineStatus
from core.pipeline import SpokePipeline

console = Console()

AGENT_LABELS = [
    ("🎙️", "Transcriber",  "Converting speech to text"),
    ("🧠", "Analyst",      "Extracting problem structure"),
    ("❓", "Clarifier",    "Checking for gaps"),
    ("📐", "Architect",    "Designing the solution"),
    ("💻", "Coder",        "Writing production code"),
    ("🚀", "Executor",     "Testing the agent"),
    ("🔧", "Debugger",     "Self-healing bugs"),
    ("📦", "Deployer",     "Packaging for deployment"),
]

STAGE_TO_IDX = {
    PipelineStatus.TRANSCRIBING:  0,
    PipelineStatus.ANALYSING:     1,
    PipelineStatus.CLARIFYING:    2,
    PipelineStatus.ARCHITECTING:  3,
    PipelineStatus.CODING:        4,
    PipelineStatus.EXECUTING:     5,
    PipelineStatus.DEBUGGING:     6,
    PipelineStatus.DEPLOYING:     7,
}


async def run(transcript_text: str | None = None) -> None:
    console.print(Panel(
        "[bold blue]🎙️  SPOKE[/bold blue]\n"
        "[dim]You spoke. It shipped.[/dim]\n\n"
        "[green]8-agent autonomous pipeline[/green] | Zero credentials required",
        border_style="blue",
        padding=(1, 6),
        title="[bold]Hackathon Demo[/bold]",
    ))

    console.print()

    pipeline = SpokePipeline()
    done: set[int] = set()

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("Initialising...", total=100)

        async def on_progress(msg: str, pct: int, status: PipelineStatus, detail: str = ""):
            idx = STAGE_TO_IDX.get(status, -1)
            if idx > 0:
                for i in range(idx):
                    done.add(i)

            icon, label, _ = AGENT_LABELS[max(0, idx)] if idx >= 0 else ("⚡", "Pipeline", "")
            progress.update(task, completed=pct, description=f"{icon}  {label}: {msg}")
            if detail:
                console.print(f"   [dim]{detail[:80]}[/dim]")

        result = await pipeline.run(
            demo_mode=True,
            transcript_text=transcript_text,
            progress=on_progress,
        )

        progress.update(task, completed=100, description="✅  Done!")

    console.print()

    if result.status != PipelineStatus.SUCCESS:
        console.print(f"[red]Pipeline failed: {result.error}[/red]")
        return

    # Result
    console.print(Panel(
        f"[bold green]✅ {result.agent_name} is ready![/bold green]\n"
        f"[dim]{result.blueprint.agent_description if result.blueprint else ''}[/dim]",
        border_style="green",
        padding=(1, 4),
    ))

    # Metrics
    table = Table(title="Impact Summary", border_style="blue", show_header=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="green")
    table.add_row("Hours saved per week", f"{result.time_saved_hours_per_week:.0f} hrs")
    table.add_row("Hours saved per year", f"{result.hours_per_year:.0f} hrs")
    table.add_row("Annual value (@ $35/hr)", result.cost_saved_per_year)
    table.add_row("Code lines generated", str(len(result.code.splitlines())))
    table.add_row("Build time", f"{result.total_duration_seconds:.1f}s")
    console.print(table)

    # Output
    if result.execution_preview:
        console.print("\n[bold]🖥️  Live Agent Output:[/bold]")
        console.print(Panel(
            result.execution_preview[:1200],
            border_style="dim",
            padding=(0, 1),
        ))

    # Deployment
    if result.deployment and result.deployment.zip_path:
        console.print(f"\n[green]📦 Agent package:[/green] {result.deployment.zip_path}")
        console.print(f"[dim]Run it with: python agent.py --mode demo[/dim]")

    console.print()
    console.print("[bold blue]One video. One problem. One working agent. That's Spoke.[/bold blue]")
    console.print("[dim]Start the UI: streamlit run frontend/app.py[/dim]")


def main():
    parser = argparse.ArgumentParser(description="Spoke CLI Demo")
    parser.add_argument(
        "--transcript",
        type=str,
        default=None,
        help="Custom transcript text to use instead of default demo",
    )
    args = parser.parse_args()
    asyncio.run(run(transcript_text=args.transcript))


if __name__ == "__main__":
    main()
