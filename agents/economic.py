"""
System 6 — Economic Brain
Compute ROI, payback period, annual savings, opportunity gain, automation confidence,
and avoided errors. Produces a boardroom-grade economic dashboard.
"""

from __future__ import annotations
import math
from loguru import logger

from core.genesis_models import EconomicLineItem, EconomicReport, SpawnResult, SimulationResult
from core.models import ProblemGraph


HOURLY_RATE = 35.0          # $ per knowledge worker hour
WEEKS_PER_YEAR = 52
IMPLEMENTATION_COST = 5_000.0
MAINTENANCE_COST_ANNUAL = 600.0    # $50/month for hosting/maintenance
ERROR_COST_HOURS = 2.0             # hours to fix a typical manual error


def _roi(total_value: float, cost: float) -> float:
    if cost <= 0:
        return 0.0
    return round(((total_value - cost) / cost) * 100, 1)


def _payback_months(total_value: float, cost: float) -> float:
    monthly = total_value / 12
    if monthly <= 0:
        return 999.0
    return round(cost / monthly, 1)


class EconomicBrain:
    """
    System 6 — Computes the full economic value of the Genesis build.
    Uses real numbers from ProblemGraph + SpawnResult + SimulationResult.
    """

    def calculate(
        self,
        problem: ProblemGraph,
        spawn: SpawnResult | None = None,
        simulation: SimulationResult | None = None,
    ) -> EconomicReport:
        logger.info("EconomicBrain computing ROI and impact metrics...")

        line_items: list[EconomicLineItem] = []

        # ── Primary automation value ──────────────────────────────────────────
        hours_week = max(problem.estimated_hours_per_week, 2.0)
        primary_annual = hours_week * WEEKS_PER_YEAR * HOURLY_RATE
        line_items.append(EconomicLineItem(
            label=f"{problem.core_pain[:60]}... — automated",
            annual_value=round(primary_annual, 0),
            calculation=f"{hours_week:.0f}h/week × 52 weeks × ${HOURLY_RATE:.0f}/hr",
            agent="Primary Automation",
            category="time_savings",
        ))

        # ── Error prevention ──────────────────────────────────────────────────
        errors_per_week = max(1, int(hours_week * 0.15))  # ~15% of manual time is rework
        errors_annual = errors_per_week * WEEKS_PER_YEAR * ERROR_COST_HOURS * HOURLY_RATE
        line_items.append(EconomicLineItem(
            label="Human error elimination (rework & corrections)",
            annual_value=round(errors_annual, 0),
            calculation=f"{errors_per_week} errors/week × ${ERROR_COST_HOURS}h fix × 52 × ${HOURLY_RATE}/hr",
            agent="Primary Automation",
            category="error_prevention",
        ))

        # ── Spawned agents ────────────────────────────────────────────────────
        if spawn:
            for agent in spawn.spawned_agents:
                line_items.append(EconomicLineItem(
                    label=f"{agent.name} — {agent.tagline[:50]}",
                    annual_value=round(agent.estimated_annual_value, 0),
                    calculation=agent.value_description or f"Estimated from {agent.category} benchmarks",
                    agent=agent.name,
                    category="time_savings",
                ))

        # ── Simulation boost ──────────────────────────────────────────────────
        if simulation:
            fraud_annual = simulation.total_fraud_blocked * (WEEKS_PER_YEAR / 1)  # scale from 1 week
            if fraud_annual > 0:
                line_items.append(EconomicLineItem(
                    label="Fraud prevention (simulated baseline extrapolated)",
                    annual_value=round(fraud_annual, 0),
                    calculation=f"${simulation.total_fraud_blocked:,.0f} blocked in 1 week × 52",
                    agent="FraudShield",
                    category="error_prevention",
                ))

        # ── Opportunity gain (faster decisions) ───────────────────────────────
        opportunity_annual = max(5_000.0, primary_annual * 0.35)
        line_items.append(EconomicLineItem(
            label="Opportunity gain — faster decisions from real-time data",
            annual_value=round(opportunity_annual, 0),
            calculation="Real-time reporting enables 30% faster sales/ops decisions (industry benchmark)",
            agent="RevenueInsights",
            category="opportunity",
        ))

        # ── Total ─────────────────────────────────────────────────────────────
        total_annual = sum(li.annual_value for li in line_items)
        five_year = total_annual * 5 - IMPLEMENTATION_COST - (MAINTENANCE_COST_ANNUAL * 5)
        roi = _roi(total_annual, IMPLEMENTATION_COST)
        payback = _payback_months(total_annual, IMPLEMENTATION_COST)

        # Hours saved (all automations combined)
        total_hours_week = hours_week + sum(
            (a.estimated_annual_value / (HOURLY_RATE * WEEKS_PER_YEAR))
            for a in (spawn.spawned_agents if spawn else [])
        )

        # Errors avoided per year
        avoided_errors = int(errors_per_week * WEEKS_PER_YEAR + (total_hours_week * 0.1 * WEEKS_PER_YEAR))

        # Automation confidence (based on problem confidence + simulation accuracy)
        base_confidence = 0.88
        if simulation:
            base_confidence = max(0.80, simulation.final_accuracy / 100)
        automation_confidence = round(min(0.99, base_confidence * 1.05), 2)

        headline = (
            f"${total_annual:,.0f}/year in automated value · "
            f"{payback:.1f}-month payback · "
            f"{roi:.0f}% ROI"
        )

        boardroom_summary = (
            f"Deploying SPOKE Genesis delivers **${total_annual:,.0f} in annual value** across "
            f"{len(line_items)} value streams. Implementation cost of "
            f"${IMPLEMENTATION_COST:,.0f} recoups in {payback:.1f} months. "
            f"5-year cumulative value: **${five_year:,.0f}**. "
            f"Automation confidence: {automation_confidence:.0%}."
        )

        logger.success(f"Economic analysis complete: ${total_annual:,.0f}/year, {roi:.0f}% ROI")

        return EconomicReport(
            line_items=line_items,
            total_annual_value=round(total_annual, 2),
            implementation_cost=IMPLEMENTATION_COST,
            roi_percentage=roi,
            payback_months=payback,
            five_year_value=round(max(0, five_year), 2),
            automation_confidence=automation_confidence,
            avoided_errors_per_year=avoided_errors,
            hours_saved_per_year=round(total_hours_week * WEEKS_PER_YEAR, 1),
            headline=headline,
            boardroom_summary=boardroom_summary,
        )
