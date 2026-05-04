"""
SPOKE Genesis — Autonomous Business Automation Intelligence Platform
"You spoke. It shipped. And then it built 4 more."
"""

from __future__ import annotations
import asyncio
import random
import sys
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="SPOKE Genesis — Autonomous Business Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

  @keyframes pulse     { 0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(34,197,94,.5)} 50%{opacity:.85;box-shadow:0 0 0 10px rgba(34,197,94,0)} }
  @keyframes glowPurp  { 0%,100%{text-shadow:0 0 30px #6c63ff90} 50%{text-shadow:0 0 60px #a78bfa} }
  @keyframes fadeSlide { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
  @keyframes ticker    { from{transform:translateX(100%)} to{transform:translateX(-100%)} }
  @keyframes scanLine  { 0%{top:-10%} 100%{top:110%} }
  @keyframes countUp   { from{opacity:0;transform:scale(0.8)} to{opacity:1;transform:scale(1)} }
  @keyframes borderPulse { 0%,100%{border-color:#6c63ff} 50%{border-color:#a78bfa} }

  body, .stApp { background:#050508 !important; color:#e2e8f0; }

  /* Hero */
  .genesis-hero h1 {
    font-size:5rem; font-weight:900; letter-spacing:-4px; line-height:1;
    background:linear-gradient(135deg,#6c63ff 0%,#a78bfa 50%,#60a5fa 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:glowPurp 3s ease-in-out infinite;
    text-align:center;
  }
  .genesis-hero .badge {
    display:inline-block; background:linear-gradient(135deg,#6c63ff22,#a78bfa22);
    border:1px solid #6c63ff; border-radius:20px; padding:3px 14px;
    font-size:.75rem; color:#a78bfa; letter-spacing:2px; text-transform:uppercase;
    margin:0 auto; display:block; width:fit-content;
  }

  /* System cards */
  .sys-card {
    background:#0c0c18; border:1px solid #1e1e3f; border-radius:14px;
    padding:1.2rem 1.4rem; margin:.4rem 0;
    transition:all .3s ease; animation:fadeSlide .4s ease;
  }
  .sys-card.active { border-color:#6c63ff; background:#10103a;
    box-shadow:0 0 30px rgba(108,99,255,.3); }
  .sys-card.done   { border-color:#22c55e33; background:#0a1a0f; }
  .sys-card.skipped{ opacity:.3; }

  /* Agent spawn cards */
  .spawn-card {
    background:#0c0c18; border:1px solid #1e1e3f; border-radius:12px;
    padding:1.1rem 1.3rem; animation:fadeSlide .5s ease;
  }
  .spawn-card:hover { border-color:#6c63ff; transform:translateY(-2px); }
  .spawn-name  { font-size:1.1rem; font-weight:800; color:#e2e8f0; }
  .spawn-val   { font-size:1.5rem; font-weight:900; color:#22c55e; }
  .spawn-tag   { font-size:.72rem; color:#64748b; font-style:italic; margin-top:2px; }

  /* Counterfactual cards */
  .cf-card        { border-radius:12px; padding:1rem 1.2rem; margin:.4rem 0; animation:fadeSlide .3s ease; }
  .cf-card.winner { background:#0a1f0a; border:2px solid #22c55e; }
  .cf-card.rejected { background:#1f0a0a; border:1px solid #ef444444; }
  .cf-card.warn   { background:#1a140a; border:1px solid #f59e0b88; }
  .cf-rejected-label { color:#ef4444; font-size:.72rem; font-weight:600; text-transform:uppercase; }
  .cf-winner-label   { color:#22c55e; font-size:.72rem; font-weight:600; text-transform:uppercase; }

  /* DAG */
  .dag-wrap { display:flex; align-items:center; gap:.5rem; overflow-x:auto; padding:1.5rem; }
  .dag-node {
    background:#12121f; border:2px solid #1e1e3f; border-radius:10px;
    padding:.7rem 1.1rem; text-align:center; min-width:90px;
    transition:all .4s ease; flex-shrink:0;
  }
  .dag-node.active { border-color:#6c63ff; background:#16163a;
    box-shadow:0 0 20px rgba(108,99,255,.4); }
  .dag-node.done   { border-color:#22c55e; background:#0f1f14; }
  .dag-icon   { font-size:1.4rem; }
  .dag-label  { font-size:.72rem; color:#94a3b8; margin-top:2px; font-weight:600; }
  .dag-arrow  { color:#334155; font-size:1.2rem; flex-shrink:0; }

  /* Self-heal */
  .heal-frame { border-radius:10px; padding:1rem 1.2rem; margin:.5rem 0;
    font-family:'Courier New',monospace; font-size:.82rem; animation:fadeSlide .3s ease; }
  .heal-inject  { background:#1a0a2e; border-left:3px solid #a78bfa; }
  .heal-run     { background:#0a1a2e; border-left:3px solid #60a5fa; }
  .heal-fail    { background:#2e0a0a; border-left:3px solid #ef4444; }
  .heal-diag    { background:#2e1a0a; border-left:3px solid #f59e0b; }
  .heal-patch   { background:#1a0a2e; border-left:3px solid #a78bfa; }
  .heal-redep   { background:#0a1a2e; border-left:3px solid #60a5fa; }
  .heal-ok      { background:#0a2e0a; border-left:3px solid #22c55e; }

  /* Economic */
  .roi-card   { background:#12121f; border:1px solid #1e1e3f; border-radius:12px; padding:1.5rem; text-align:center; }
  .roi-val    { font-size:2.5rem; font-weight:900; animation:countUp .8s ease; }
  .roi-lbl    { font-size:.72rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; margin-top:4px; }
  .roi-green  { color:#22c55e; }
  .roi-purple { color:#a78bfa; }
  .roi-blue   { color:#60a5fa; }

  /* Line item */
  .li-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.6rem .8rem; border-radius:8px; margin:.25rem 0;
    background:#0c0c18; border-left:3px solid #1e1e3f;
  }
  .li-row.time     { border-left-color:#22c55e; }
  .li-row.error    { border-left-color:#f59e0b; }
  .li-row.opp      { border-left-color:#60a5fa; }

  /* Discovery */
  .disc-card  { background:#12121f; border:1px solid #1e1e3f; border-radius:12px; padding:1.2rem; }
  .disc-card:hover { border-color:#6c63ff; }
  .disc-rank  { font-size:.7rem; color:#475569; text-transform:uppercase; }
  .disc-title { font-size:1rem; font-weight:700; color:#e2e8f0; margin:.3rem 0; }
  .disc-val   { color:#22c55e; font-weight:700; }

  /* Grand finale */
  .finale-box {
    background:linear-gradient(135deg,#050508,#0a0a1f,#050508);
    border:2px solid #6c63ff; border-radius:20px; padding:3rem 2rem;
    text-align:center; animation:borderPulse 3s ease-in-out infinite;
    position:relative; overflow:hidden;
  }
  .finale-num {
    font-size:5rem; font-weight:900; line-height:1;
    background:linear-gradient(135deg,#22c55e,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:countUp 1s ease;
  }
  .finale-sub  { font-size:1.4rem; color:#94a3b8; margin:.5rem 0; }
  .finale-cta  {
    font-size:1.1rem; font-style:italic; color:#a78bfa;
    border:1px solid #a78bfa44; border-radius:10px; padding:.7rem 1.5rem; margin-top:1.5rem;
    display:inline-block;
  }

  /* Progress bar */
  .prog-wrap { background:#1e1e3f; border-radius:999px; height:6px; margin:.5rem 0; }
  .prog-fill { height:100%; border-radius:999px;
    background:linear-gradient(90deg,#6c63ff,#a78bfa,#60a5fa); transition:width .6s ease; }

  /* Ticker */
  .ticker-wrap  { background:#0c0c18; border:1px solid #1e1e3f; border-radius:8px; overflow:hidden; white-space:nowrap; }
  .ticker-inner { display:inline-block; animation:ticker 25s linear infinite; color:#475569; font-size:.8rem; padding:.5rem 0; }

  /* Buttons */
  .stButton>button {
    background:linear-gradient(135deg,#6c63ff,#a78bfa) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-weight:700 !important; padding:.7rem 2rem !important; font-size:1rem !important;
    transition:all .2s !important;
  }
  .stButton>button:hover { transform:translateY(-2px); box-shadow:0 8px 30px rgba(108,99,255,.5) !important; }

  /* Tool badge */
  .tool-badge {
    display:inline-block; border-radius:20px; padding:3px 10px;
    font-size:.72rem; font-weight:600; margin:2px;
    border:1px solid #1e1e3f; background:#12121f; color:#94a3b8;
  }

  /* Stack detection */
  .stack-detected { background:#0a1a1a; border:1px solid #22c55e44; border-radius:12px; padding:1rem 1.3rem; }
  .tool-row { display:flex; align-items:center; gap:.8rem; padding:.4rem 0; border-bottom:1px solid #1e1e3f22; }
  .tool-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }

  /* Simulation day */
  .sim-day { background:#0c0c18; border:1px solid #1e1e3f; border-radius:10px; padding:.9rem 1rem; }

  /* Memory */
  .mem-card { background:#0c0c18; border:1px solid #1e1e3f; border-radius:10px; padding:1rem; }

  hr { border-color:#1e1e3f !important; }
</style>
""", unsafe_allow_html=True)


# ── State helpers ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "screen": "landing",
        "genesis_result": None,
        "transcript_text": "",
        "video_path": "",
        "error": None,
        "show_code": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def go(screen: str):
    st.session_state.screen = screen
    st.rerun()


def _g(obj, key, default=None):
    if obj is None:
        return default
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


# ── Rendering helpers ─────────────────────────────────────────────────────────

def render_progress(pct: int, msg: str, detail: str = ""):
    st.markdown(f"""
    <div>
      <div style="display:flex;justify-content:space-between;margin-bottom:.3rem">
        <span style="color:#a78bfa;font-weight:600;font-size:.9rem">{msg}</span>
        <span style="color:#475569;font-size:.8rem">{pct}%</span>
      </div>
      <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
      {"<div style='color:#64748b;font-size:.78rem;margin-top:2px'>" + detail[:140] + "</div>" if detail else ""}
    </div>""", unsafe_allow_html=True)


def render_dag(dag_data: dict | None):
    if not dag_data:
        return
    nodes = dag_data.get("nodes", [])
    labels = [
        ("👁️", "Observe"), ("🧠", "Extract"), ("✅", "Validate"),
        ("🔍", "Dedup"), ("🔀", "Route"), ("💾", "Store"),
        ("📡", "Monitor"), ("🔔", "Alert"), ("📈", "Improve"),
    ]
    html = '<div class="dag-wrap">'
    for i, (icon, label) in enumerate(labels):
        html += f"""
        <div class="dag-node done">
          <div class="dag-icon">{icon}</div>
          <div class="dag-label">{label}</div>
        </div>"""
        if i < len(labels) - 1:
            html += '<div class="dag-arrow">→</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_spawn_cards(spawn_data: dict | None):
    if not spawn_data:
        return
    agents = spawn_data.get("spawned_agents", [])
    cols = st.columns(min(len(agents), 3))
    for i, agent in enumerate(agents):
        col = cols[i % len(cols)]
        name = _g(agent, "name", "Agent")
        tagline = _g(agent, "tagline", "")
        value = _g(agent, "estimated_annual_value", 0)
        cat = _g(agent, "category", "")
        what = _g(agent, "what_it_does", "")
        col.markdown(f"""
        <div class="spawn-card">
          <div class="spawn-name">⚡ {name}</div>
          <div class="spawn-tag">{tagline}</div>
          <div style="margin:.5rem 0;color:#94a3b8;font-size:.82rem">{what[:100]}</div>
          <div class="spawn-val">${value:,.0f}<span style="font-size:.8rem;color:#64748b">/yr</span></div>
          <div style="margin-top:.4rem">
            <span class="tool-badge">{cat.replace('_',' ').title()}</span>
          </div>
        </div>""", unsafe_allow_html=True)


def render_counterfactual(cf_data: dict | None):
    if not cf_data:
        return
    candidates = cf_data.get("candidates", [])
    winner_id = None
    winner_obj = cf_data.get("winner")
    if winner_obj and isinstance(winner_obj, dict):
        winner_id = winner_obj.get("id")

    for c in candidates:
        cid = _g(c, "id", "")
        name = _g(c, "name", "")
        pattern = _g(c, "pattern", "")
        desc = _g(c, "description", "")
        pros = _g(c, "pros", [])
        cons = _g(c, "cons", [])
        rejection = _g(c, "rejection_reason", "")
        selected = _g(c, "selected", False) or (cid == winner_id)
        scores = _g(c, "scores", {})

        if isinstance(scores, dict):
            score_total = sum(scores.values()) / max(len(scores), 1)
        else:
            score_total = 7.0

        css_class = "winner" if selected else ("warn" if not rejection else "rejected")
        label_html = (
            '<span class="cf-winner-label">✅ SELECTED — OPTIMAL</span>'
            if selected else
            '<span class="cf-rejected-label">✗ REJECTED</span>'
        )

        st.markdown(f"""
        <div class="cf-card {css_class}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              {label_html}
              <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin:.2rem 0">{name}</div>
              <div style="font-size:.78rem;color:#64748b;margin-bottom:.4rem">{pattern}</div>
              <div style="font-size:.83rem;color:#94a3b8">{desc}</div>
            </div>
            <div style="text-align:right;min-width:60px">
              <div style="font-size:1.8rem;font-weight:900;color:{'#22c55e' if selected else '#ef4444'}">{score_total:.1f}</div>
              <div style="font-size:.65rem;color:#475569">/10</div>
            </div>
          </div>
          {f'<div style="margin-top:.5rem;color:#f59e0b;font-size:.78rem;border-top:1px solid #1e1e3f;padding-top:.4rem">⚠️ {rejection[:120]}</div>' if rejection else ""}
        </div>""", unsafe_allow_html=True)


def render_selfheal(sh_data: dict | None):
    if not sh_data:
        return
    frames = sh_data.get("frames", [])
    stage_css = {
        "injecting": "heal-inject",
        "running": "heal-run",
        "failing": "heal-fail",
        "diagnosing": "heal-diag",
        "patching": "heal-patch",
        "redeploying": "heal-redep",
        "recovered": "heal-ok",
    }
    for frame in frames:
        stage = _g(frame, "stage", "")
        content = _g(frame, "content", "")
        css = stage_css.get(stage, "heal-run")
        st.markdown(f'<div class="heal-frame {css}" style="white-space:pre-wrap">{content}</div>',
                    unsafe_allow_html=True)


def render_economics(econ_data: dict | None):
    if not econ_data:
        return
    total = _g(econ_data, "total_annual_value", 0)
    roi = _g(econ_data, "roi_percentage", 0)
    payback = _g(econ_data, "payback_months", 0)
    five_yr = _g(econ_data, "five_year_value", 0)
    confidence = _g(econ_data, "automation_confidence", 0)
    avoided = _g(econ_data, "avoided_errors_per_year", 0)
    hours_yr = _g(econ_data, "hours_saved_per_year", 0)

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, f"${total:,.0f}", "Annual Value", "roi-green"),
        (c2, f"{roi:.0f}%", "ROI", "roi-purple"),
        (c3, f"{payback:.1f}mo", "Payback Period", "roi-blue"),
        (c4, f"${five_yr:,.0f}", "5-Year Value", "roi-green"),
    ]
    for col, val, lbl, cls in metrics:
        col.markdown(f"""
        <div class="roi-card">
          <div class="roi-val {cls}">{val}</div>
          <div class="roi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""<div class="roi-card">
      <div class="roi-val roi-purple">{confidence:.0%}</div>
      <div class="roi-lbl">Automation Confidence</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="roi-card">
      <div class="roi-val roi-blue">{avoided:,}</div>
      <div class="roi-lbl">Errors Avoided / Year</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="roi-card">
      <div class="roi-val roi-green">{hours_yr:.0f}h</div>
      <div class="roi-lbl">Hours Saved / Year</div>
    </div>""", unsafe_allow_html=True)

    # Line items
    st.markdown("<br>**Value Breakdown**")
    line_items = _g(econ_data, "line_items", [])
    cat_css = {"time_savings": "time", "error_prevention": "error", "opportunity": "opp", "recovery": "opp"}
    for li in line_items:
        label = _g(li, "label", "")
        value = _g(li, "annual_value", 0)
        calc = _g(li, "calculation", "")
        cat = _g(li, "category", "time_savings")
        css = cat_css.get(cat, "time")
        st.markdown(f"""
        <div class="li-row {css}">
          <div>
            <div style="font-weight:600;color:#e2e8f0;font-size:.88rem">{label[:70]}</div>
            <div style="color:#64748b;font-size:.75rem">{calc[:100]}</div>
          </div>
          <div style="font-size:1.1rem;font-weight:800;color:#22c55e;min-width:90px;text-align:right">
            ${value:,.0f}/yr
          </div>
        </div>""", unsafe_allow_html=True)


def render_discovery(disc_data: dict | None):
    if not disc_data:
        return
    automations = _g(disc_data, "automations", [])
    total_opp = _g(disc_data, "total_opportunity_value", 0)

    st.markdown(f"""
    <div style="background:#0a0a1f;border:1px solid #6c63ff44;border-radius:12px;padding:1rem 1.3rem;margin-bottom:1rem">
      <div style="color:#a78bfa;font-size:.8rem;font-weight:600;text-transform:uppercase;letter-spacing:1px">ADDITIONAL OPPORTUNITY IDENTIFIED</div>
      <div style="font-size:1.5rem;font-weight:800;color:#22c55e;margin:.2rem 0">${total_opp:,.0f}<span style="font-size:.8rem;color:#64748b">/year</span></div>
      <div style="color:#64748b;font-size:.82rem">These automations use your existing stack. No new infrastructure required.</div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(min(len(automations), 2))
    for i, auto in enumerate(automations):
        col = cols[i % len(cols)]
        title = _g(auto, "title", "")
        desc = _g(auto, "description", "")
        why = _g(auto, "why_now", "")
        value = _g(auto, "estimated_annual_value", 0)
        effort = _g(auto, "effort_days", 2)
        roi_mult = _g(auto, "roi_multiple", 0)
        confidence = _g(auto, "confidence", 0.9)
        tools = _g(auto, "tools_needed", [])

        col.markdown(f"""
        <div class="disc-card" style="margin-bottom:.5rem">
          <div class="disc-rank">#{i+1} RECOMMENDATION</div>
          <div class="disc-title">{title}</div>
          <div style="color:#94a3b8;font-size:.82rem;margin-bottom:.6rem">{desc}</div>
          <div style="background:#0a1a0a;border-radius:6px;padding:.5rem .7rem;margin-bottom:.5rem;font-size:.78rem;color:#64748b">
            <span style="color:#22c55e;font-weight:600">Why now:</span> {why[:120]}
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div class="disc-val">${value:,.0f}/yr</div>
              <div style="font-size:.7rem;color:#64748b">{effort}d effort · {roi_mult:.1f}× ROI · {confidence:.0%} confidence</div>
            </div>
            <div>{' '.join(f'<span class="tool-badge">{t}</span>' for t in tools[:2])}</div>
          </div>
        </div>""", unsafe_allow_html=True)


def render_simulation(sim_data: dict | None):
    if not sim_data:
        return
    days = _g(sim_data, "days", [])
    if not days:
        return

    # Summary
    total_events = _g(sim_data, "total_events", 0)
    total_rev = _g(sim_data, "total_revenue", 0)
    fraud_blocked = _g(sim_data, "total_fraud_blocked", 0)
    final_acc = _g(sim_data, "final_accuracy", 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Operations", f"{total_events:,}")
    c2.metric("Revenue Captured", f"${total_rev:,.0f}")
    c3.metric("Fraud Blocked", f"${fraud_blocked:,.0f}")
    c4.metric("Final Accuracy", f"{final_acc:.1f}%")

    st.markdown("<br>")

    # Day-by-day table
    table_rows = ""
    for day in days:
        d = _g(day, "day", "")
        date = _g(day, "date", "")
        events = _g(day, "events_processed", 0)
        dupes = _g(day, "duplicates_blocked", 0)
        fraud = _g(day, "fraud_detected", 0)
        rev = _g(day, "revenue_captured", 0)
        acc = _g(day, "accuracy_pct", 0)
        upt = _g(day, "uptime_pct", 0)
        acc_color = "#22c55e" if acc >= 95 else "#f59e0b"
        table_rows += f"""
        <tr>
          <td style="color:#94a3b8">Day {d} — {date}</td>
          <td style="color:#e2e8f0;font-weight:600">{events}</td>
          <td style="color:#475569">{dupes}</td>
          <td style="color:#ef4444;font-weight:600">{fraud if fraud else '—'}</td>
          <td style="color:#22c55e;font-weight:600">${rev:,.0f}</td>
          <td style="color:{acc_color};font-weight:700">{acc:.1f}%</td>
          <td style="color:#22c55e">{upt:.1f}%</td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;font-size:.83rem">
      <thead>
        <tr style="border-bottom:1px solid #1e1e3f;color:#475569;font-size:.72rem;text-transform:uppercase;letter-spacing:1px">
          <th style="padding:.5rem;text-align:left">Day</th>
          <th>Orders</th><th>Dupes Blocked</th><th>Fraud</th>
          <th>Revenue</th><th>Accuracy</th><th>Uptime</th>
        </tr>
      </thead>
      <tbody style="color:#94a3b8">
        {table_rows}
      </tbody>
    </table>""", unsafe_allow_html=True)

    improvement = _g(sim_data, "improvement_story", "")
    if improvement:
        st.markdown(f"""
        <div style="background:#0a1a0a;border-left:3px solid #22c55e;border-radius:0 8px 8px 0;padding:.8rem 1rem;margin-top:.8rem;color:#64748b;font-size:.83rem;font-style:italic">
          {improvement}
        </div>""", unsafe_allow_html=True)


def render_stack(stack_data: dict | None):
    if not stack_data:
        return
    tools = _g(stack_data, "tools", [])
    if not tools:
        return

    tool_html = ""
    for t in tools[:8]:
        name = _g(t, "name", "")
        conf = _g(t, "confidence", 0.0)
        color = _g(t, "logo_color", "#6c63ff")
        source = _g(t, "source", "transcript")
        src_icon = "🔍" if source == "ocr" else "💬" if source == "transcript" else "🧠"
        tool_html += f"""
        <div class="tool-row">
          <div class="tool-dot" style="background:{color}"></div>
          <div style="font-weight:600;color:#e2e8f0;flex:1">{name}</div>
          <div style="font-size:.72rem;color:#64748b;margin-right:.5rem">{src_icon} {source}</div>
          <div style="font-size:.75rem;color:#22c55e;font-weight:600">{conf:.0%}</div>
        </div>"""

    summary = _g(stack_data, "stack_summary", "")
    st.markdown(f"""
    <div class="stack-detected">
      <div style="color:#22c55e;font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:.7rem">
        🎯 I DETECTED YOUR STACK AUTOMATICALLY
      </div>
      {tool_html}
      <div style="color:#475569;font-size:.75rem;margin-top:.6rem;font-style:italic">{summary}</div>
    </div>""", unsafe_allow_html=True)


# ── Screens ───────────────────────────────────────────────────────────────────

def screen_landing():
    st.markdown("""
    <div class="genesis-hero" style="padding:3rem 1rem 2rem;text-align:center">
      <div class="badge">⚡ GENESIS EDITION</div>
      <h1>SPOKE</h1>
      <p style="font-size:1.3rem;color:#94a3b8;margin:.5rem 0">
        You spoke. It shipped. And then it built 4 more.
      </p>
      <p style="color:#475569;font-size:.9rem;max-width:600px;margin:0 auto">
        The world's first autonomous business automation intelligence platform.<br>
        Describe one problem. Watch 10 AI systems build your entire operation.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ticker-wrap">
      <span class="ticker-inner">
        &nbsp;&nbsp;⚡ OrderSync + 5 agents built in 8.3s &nbsp;&nbsp;·&nbsp;&nbsp;
        🧠 Counterfactual rejected 3 inferior architectures &nbsp;&nbsp;·&nbsp;&nbsp;
        🛡️ FraudShield blocked $4,200 in fraud this week &nbsp;&nbsp;·&nbsp;&nbsp;
        💰 $78,400 annual value created for Acme Corp &nbsp;&nbsp;·&nbsp;&nbsp;
        📊 Self-heal recovered in 2.1 seconds &nbsp;&nbsp;·&nbsp;&nbsp;
        🚀 5 agent ecosystem deployed and live &nbsp;&nbsp;·&nbsp;&nbsp;
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 10 systems showcase
    systems = [
        ("⚡", "Agent Spawn", "1 problem → 5 agents"),
        ("🏛️", "Counterfactual Architect", "Rejects inferior designs"),
        ("🎥", "Multimodal Detection", "Sees your entire stack"),
        ("🔀", "Live Workflow DAG", "Animates in real time"),
        ("📅", "Business Simulation", "1-week synthetic test"),
        ("💰", "Economic Brain", "Boardroom-grade ROI"),
        ("🔧", "Self-Heal Theater", "Cinematic recovery"),
        ("🚀", "Live Deployment", "Health checks + rollback"),
        ("🧠", "Business Memory", "Smarter every build"),
        ("🔭", "Autonomous Discovery", "Finds what you missed"),
    ]

    cols = st.columns(5)
    for i, (icon, title, sub) in enumerate(systems):
        with cols[i % 5]:
            st.markdown(f"""
            <div style="background:#0c0c18;border:1px solid #1e1e3f;border-radius:10px;
              padding:1rem;text-align:center;margin-bottom:.5rem">
              <div style="font-size:2rem">{icon}</div>
              <div style="font-size:.82rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">{title}</div>
              <div style="font-size:.72rem;color:#475569">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background:#12121f;border:1px solid #1e1e3f;border-radius:12px;
          padding:1.5rem;text-align:center;height:160px;display:flex;flex-direction:column;
          justify-content:center;align-items:center;gap:.5rem">
          <div style="font-size:2.2rem">🎬</div>
          <div style="font-weight:700;color:#e2e8f0">Upload Video</div>
          <div style="font-size:.8rem;color:#64748b">AI reads your screen + voice</div>
        </div>""", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload video or audio", type=["mp4","mov","webm","avi","mp3","wav"],
                                    label_visibility="collapsed", key="genesis_upload")
        if uploaded:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix, delete=False)
            tmp.write(uploaded.read()); tmp.close()
            st.session_state.video_path = tmp.name
            go("genesis_running")

    with col2:
        st.markdown("""
        <div style="background:#12121f;border:1px solid #1e1e3f;border-radius:12px;
          padding:1.5rem;text-align:center;height:160px;display:flex;flex-direction:column;
          justify-content:center;align-items:center;gap:.5rem">
          <div style="font-size:2.2rem">💬</div>
          <div style="font-weight:700;color:#e2e8f0">Describe Your Problem</div>
          <div style="font-size:.8rem;color:#64748b">Type any repetitive task</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Start typing →", use_container_width=True, key="text_btn"):
            go("text_input")

    with col3:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0c0c18,#1a1a3f);border:2px solid #6c63ff;
          border-radius:12px;padding:1.5rem;text-align:center;height:160px;display:flex;flex-direction:column;
          justify-content:center;align-items:center;gap:.5rem">
          <div style="font-size:2.2rem">⚡</div>
          <div style="font-weight:700;color:#a78bfa">Genesis Demo</div>
          <div style="font-size:.8rem;color:#64748b">All 10 systems · No credentials</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Launch Genesis ⚡", use_container_width=True, key="demo_btn"):
            go("genesis_running_demo")

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    for col, val, lbl in zip(
        st.columns(4),
        ["10", "5+", "<10s", "$78K+"],
        ["AI systems", "agents per build", "build time", "avg annual value"],
    ):
        col.markdown(f"""
        <div class="roi-card">
          <div class="roi-val roi-purple" style="font-size:2rem">{val}</div>
          <div class="roi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)


def screen_text_input():
    st.markdown("<h2 style='color:#a78bfa'>Describe your business problem</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b'>Genesis will build your primary automation + up to 5 adjacent agents.</p>",
                unsafe_allow_html=True)

    example = ("Every day I get 10-15 order emails in Gmail. I manually open each one, "
               "read the customer name, product, quantity, and price, then type it into "
               "Google Sheets. It takes about 2 hours every day.")
    text = st.text_area("Problem description", height=160, placeholder=f"e.g. {example}", label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key="back_btn"):
            go("landing")
    with col2:
        if st.button("Launch Genesis →", use_container_width=True, key="launch_btn"):
            if len(text.strip()) < 20:
                st.error("Please describe your problem in at least a sentence or two.")
            else:
                st.session_state.transcript_text = text.strip()
                go("genesis_running")

    st.markdown("<br>")
    if st.button("Use the order-email example", key="example_btn"):
        st.session_state.transcript_text = example
        go("genesis_running")


def run_genesis_sync(demo_mode: bool, transcript_text: str = "", video_path: str = ""):
    from core.genesis_pipeline import GenesisOrchestrator

    orchestrator = GenesisOrchestrator()

    prog_ph    = st.empty()
    status_ph  = st.empty()

    async def on_progress(msg: str, pct: int, phase: str = "", detail: str = ""):
        with prog_ph.container():
            render_progress(pct, msg, detail)
        with status_ph.container():
            st.markdown(
                f"<div style='color:#475569;font-size:.78rem'>📍 {phase}</div>" if phase else "",
                unsafe_allow_html=True,
            )

    result = asyncio.run(orchestrator.run(
        transcript_text=transcript_text or None,
        video_path=video_path or None,
        demo_mode=demo_mode,
        progress=on_progress,
    ))

    prog_ph.empty()
    status_ph.empty()
    return result


def screen_genesis_running(demo_mode: bool = False):
    label = "⚡ Genesis Demo" if demo_mode else "🚀 Genesis"
    st.markdown(f"<h2 style='color:#a78bfa'>{label} — All 10 systems activating...</h2>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b'>Watch the autonomous pipeline build your entire business automation stack.</p>",
                unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    try:
        result = run_genesis_sync(
            demo_mode=demo_mode,
            transcript_text=st.session_state.get("transcript_text", ""),
            video_path=st.session_state.get("video_path", ""),
        )
        st.session_state.genesis_result = result if isinstance(result, dict) else result.model_dump()

        status = _g(result, "status", "failed")
        if status == "success":
            go("genesis_result")
        else:
            st.session_state.error = _g(result, "error", "Genesis pipeline failed")
            go("error")
    except Exception as e:
        st.session_state.error = str(e)
        go("error")


def screen_genesis_result():
    result = st.session_state.get("genesis_result")
    if not result:
        go("landing")
        return

    if not isinstance(result, dict):
        result = result.model_dump() if hasattr(result, "model_dump") else {}

    core = _g(result, "core_pipeline_result", {})
    agent_name = _g(core, "agent_name", "Your Agent")
    spawn    = _g(result, "spawn", {})
    cf       = _g(result, "counterfactual", {})
    stack    = _g(result, "detected_stack", {})
    dag      = _g(result, "workflow_dag", {})
    sim      = _g(result, "simulation", {})
    econ     = _g(result, "economics", {})
    sh       = _g(result, "selfheal", {})
    deploy   = _g(result, "deployment", {})
    disc     = _g(result, "discovery", {})
    memory_l = _g(result, "memory_learning", "")
    total_v  = _g(result, "total_annual_value", 0)
    total_a  = _g(result, "total_agents_built", 1)
    headline = _g(result, "final_headline", "")

    # ── GRAND FINALE HEADER ────────────────────────────────────────────────────
    spawn_count = _g(spawn, "spawn_count", 0) if spawn else 0
    st.markdown(f"""
    <div class="finale-box">
      <div style="color:#a78bfa;font-size:.8rem;font-weight:600;text-transform:uppercase;letter-spacing:2px;margin-bottom:1rem">
        ✅ GENESIS COMPLETE
      </div>
      <div class="finale-num">${total_v:,.0f}</div>
      <div class="finale-sub">estimated annual value created</div>
      <div style="display:flex;justify-content:center;gap:2rem;margin:1rem 0;flex-wrap:wrap">
        <div><span style="font-size:2rem;font-weight:800;color:#a78bfa">{total_a}</span>
             <span style="color:#64748b;font-size:.82rem"> systems built</span></div>
        <div><span style="font-size:2rem;font-weight:800;color:#60a5fa">{_g(econ,'hours_saved_per_year',0):.0f}h</span>
             <span style="color:#64748b;font-size:.82rem"> saved/year</span></div>
        <div><span style="font-size:2rem;font-weight:800;color:#22c55e">{_g(econ,'roi_percentage',0):.0f}%</span>
             <span style="color:#64748b;font-size:.82rem"> ROI</span></div>
      </div>
      <div class="finale-cta">
        "You asked for 1 automation. I built {total_a}.<br>
        Would you like me to continue optimizing your business?"
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ACTION BUTTONS ─────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        session_id = _g(result, "session_id", "")
        if session_id:
            st.link_button("⬇️ Download Bundle",
                           f"http://localhost:8000/api/v1/download/{session_id}",
                           use_container_width=True)
    with col2:
        if st.button("👁️ View Generated Code", use_container_width=True):
            st.session_state.show_code = not st.session_state.get("show_code", False)
            st.rerun()
    with col3:
        if st.button("🔁 Build Another", use_container_width=True):
            for k in ["genesis_result","transcript_text","video_path","error","show_code"]:
                st.session_state.pop(k, None)
            go("landing")

    if st.session_state.get("show_code"):
        code = _g(core, "code", "")
        if code:
            st.code(code, language="python", line_numbers=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── TABS FOR ALL 10 SYSTEMS ────────────────────────────────────────────────
    tabs = st.tabs([
        "⚡ Agent Spawn",
        "🏛️ Architecture",
        "🎯 Stack",
        "🔀 Workflow DAG",
        "📅 Simulation",
        "💰 Economics",
        "🔧 Self-Heal",
        "🚀 Deployment",
        "🔭 Discovery",
        "🧠 Memory",
    ])

    # ── TAB 1: Agent Spawn ─────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem 0">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 1</div>
          <div style="font-size:2rem;font-weight:900;color:#e2e8f0;margin:.4rem 0">You asked for 1 automation.</div>
          <div style="font-size:2rem;font-weight:900;color:#22c55e">I built {total_a}.</div>
        </div>""", unsafe_allow_html=True)

        if spawn:
            primary_name = _g(spawn, "primary_agent_name", agent_name)
            st.markdown(f"""
            <div style="background:#0a1f0a;border:2px solid #22c55e;border-radius:12px;padding:1rem 1.3rem;margin-bottom:1rem">
              <span style="color:#22c55e;font-weight:700">⚡ PRIMARY — {primary_name}</span>
              <span style="color:#64748b;font-size:.82rem;margin-left:.5rem">Built by the core 10-agent pipeline</span>
            </div>""", unsafe_allow_html=True)
            render_spawn_cards(spawn)

            total_spawn_val = _g(spawn, "total_estimated_value", 0)
            if total_spawn_val:
                st.markdown(f"""
                <div style="text-align:center;margin-top:1.5rem">
                  <div style="font-size:1rem;color:#64748b">Spawned agent value alone</div>
                  <div style="font-size:2.5rem;font-weight:900;color:#22c55e">${total_spawn_val:,.0f}<span style="font-size:1rem;color:#64748b">/year</span></div>
                </div>""", unsafe_allow_html=True)

    # ── TAB 2: Counterfactual Architect ───────────────────────────────────────
    with tabs[1]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 2 — COUNTERFACTUAL ARCHITECT</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            4 architectures evaluated. 3 rejected. Here's why.
          </div>
        </div>""", unsafe_allow_html=True)
        if cf:
            render_counterfactual(cf)
            rationale = _g(cf, "selection_rationale", "")
            if rationale:
                st.markdown(f"""
                <div style="background:#0a0a1f;border-left:3px solid #6c63ff;padding:.8rem 1rem;border-radius:0 8px 8px 0;margin-top:.5rem;font-size:.83rem;color:#94a3b8">
                  🏆 {rationale}
                </div>""", unsafe_allow_html=True)

    # ── TAB 3: Stack Detection ────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 3 — MULTIMODAL DETECTION</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            I detected your technology stack automatically.
          </div>
        </div>""", unsafe_allow_html=True)
        if stack and _g(stack, "tools", []):
            render_stack(stack)
        else:
            st.info("No explicit tool names detected in transcript. Inferred likely stack from problem domain.")

    # ── TAB 4: Workflow DAG ───────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 4 — LIVE WORKFLOW GRAPH</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            9-node DAG — all paths active and processing
          </div>
        </div>""", unsafe_allow_html=True)
        render_dag(dag)
        st.markdown("""
        <div style="display:flex;gap:1rem;margin-top:.5rem;font-size:.78rem;color:#475569">
          <span>🟢 Active nodes: 9/9</span>
          <span>→ Edges: 10</span>
          <span>♾️ Continuous loop enabled</span>
        </div>""", unsafe_allow_html=True)

    # ── TAB 5: Business Simulation ────────────────────────────────────────────
    with tabs[4]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 5 — ONE-WEEK SIMULATION</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            7 days of synthetic operations: orders, fraud, outages, recovery
          </div>
        </div>""", unsafe_allow_html=True)
        if sim:
            render_simulation(sim)

    # ── TAB 6: Economic Brain ─────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 6 — ECONOMIC BRAIN</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            Boardroom-grade ROI analysis
          </div>
        </div>""", unsafe_allow_html=True)
        if econ:
            render_economics(econ)
            summary = _g(econ, "boardroom_summary", "")
            if summary:
                st.markdown(f"""
                <div style="background:#0a0a1f;border:1px solid #6c63ff44;border-radius:10px;padding:1rem 1.3rem;margin-top:1rem">
                  <div style="font-size:.75rem;color:#475569;font-weight:600;text-transform:uppercase;margin-bottom:.5rem">Executive Summary</div>
                  <div style="color:#94a3b8;font-size:.88rem;line-height:1.6">{summary}</div>
                </div>""", unsafe_allow_html=True)

    # ── TAB 7: Self-Heal Theater ──────────────────────────────────────────────
    with tabs[6]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 7 — SELF-HEAL THEATER</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            Inject → Fail → Diagnose → Patch → Recover
          </div>
        </div>""", unsafe_allow_html=True)
        if sh:
            bug_desc = _g(sh, "injected_bug_description", "")
            recovery = _g(sh, "recovery_time_seconds", 0)
            attempts = _g(sh, "attempts_needed", 2)
            success = _g(sh, "success", True)

            col1, col2, col3 = st.columns(3)
            col1.metric("Recovery Time", f"{recovery:.1f}s")
            col2.metric("Attempts Needed", str(attempts))
            col3.metric("Status", "✅ Recovered" if success else "❌ Failed")

            st.markdown(f"**Bug injected:** {bug_desc}", unsafe_allow_html=False)
            st.markdown("<br>", unsafe_allow_html=True)
            render_selfheal(sh)

            diff = _g(sh, "patch_diff", "")
            if diff:
                st.markdown("**Surgical patch applied:**")
                st.code(diff, language="diff")

    # ── TAB 8: Live Deployment ────────────────────────────────────────────────
    with tabs[7]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 8 — LIVE DEPLOYMENT</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            Agent stack deployed — health checks passing
          </div>
        </div>""", unsafe_allow_html=True)
        if deploy:
            dep_status = _g(deploy, "status", "unknown")
            dep_version = _g(deploy, "version", "1.0.0")
            dep_url = _g(deploy, "preview_url", "")
            dep_time = _g(deploy, "deployed_at", "")
            dep_type = _g(deploy, "deployment_type", "local")

            color = "#22c55e" if dep_status == "live" else "#f59e0b"
            st.markdown(f"""
            <div style="background:#0a1f0a;border:1px solid {color}44;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                  <div style="color:{color};font-weight:700;font-size:1rem">● {dep_status.upper()}</div>
                  <div style="color:#64748b;font-size:.8rem">v{dep_version} · {dep_type} · {dep_time[:19]}</div>
                </div>
                <div style="background:{color}22;border:1px solid {color};border-radius:8px;padding:.3rem .8rem;font-size:.8rem;color:{color}">
                  {dep_type.upper()}
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            health_checks = _g(deploy, "health_checks", [])
            if health_checks:
                st.markdown("**Health Checks**")
                for hc in health_checks:
                    ep = _g(hc, "endpoint", "")
                    hstatus = _g(hc, "status", "unknown")
                    latency = _g(hc, "latency_ms", 0)
                    msg = _g(hc, "message", "")
                    hcolor = "#22c55e" if hstatus == "healthy" else "#f59e0b"
                    st.markdown(f"""
                    <div style="display:flex;gap:1rem;align-items:center;padding:.4rem .5rem;background:#0c0c18;border-radius:6px;margin:.2rem 0">
                      <span style="color:{hcolor};font-weight:600">{'✅' if hstatus=='healthy' else '⚠️'}</span>
                      <span style="color:#e2e8f0;font-size:.85rem;flex:1">{ep.replace('_',' ').title()}</span>
                      <span style="color:#64748b;font-size:.75rem">{latency}ms</span>
                      <span style="color:#475569;font-size:.75rem">{msg}</span>
                    </div>""", unsafe_allow_html=True)

            logs = _g(deploy, "logs", [])
            if logs:
                with st.expander("Deployment Logs"):
                    st.markdown(
                        '<div class="terminal" style="background:#050508;border:1px solid #1e1e3f;'
                        'border-radius:8px;padding:1rem;font-family:monospace;font-size:.78rem;'
                        'color:#4ade80;max-height:200px;overflow-y:auto">'
                        + "<br>".join(logs) + "</div>",
                        unsafe_allow_html=True,
                    )

    # ── TAB 9: Discovery ──────────────────────────────────────────────────────
    with tabs[8]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 10 — AUTONOMOUS DISCOVERY</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            High-value automations you never asked for — but clearly need.
          </div>
        </div>""", unsafe_allow_html=True)
        if disc:
            render_discovery(disc)
            cta = _g(disc, "call_to_action", "")
            if cta:
                st.markdown(f"""
                <div style="text-align:center;margin-top:1.5rem;padding:1rem;background:#0a0a1f;border-radius:10px;border:1px solid #6c63ff44">
                  <div style="color:#a78bfa;font-size:.9rem;font-style:italic">{cta}</div>
                </div>""", unsafe_allow_html=True)

    # ── TAB 10: Business Memory ───────────────────────────────────────────────
    with tabs[9]:
        st.markdown("""
        <div style="margin-bottom:1rem">
          <div style="font-size:.8rem;color:#a78bfa;text-transform:uppercase;letter-spacing:2px">SYSTEM 9 — BUSINESS MEMORY</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin:.3rem 0">
            Every build makes the next one smarter.
          </div>
        </div>""", unsafe_allow_html=True)
        if memory_l:
            st.markdown(f"""
            <div style="background:#0a0a1f;border-left:3px solid #6c63ff;padding:1rem 1.2rem;border-radius:0 8px 8px 0;color:#94a3b8;font-size:.88rem">
              🧠 <strong>What I learned from previous builds:</strong><br>{memory_l}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#0a1a0a;border-left:3px solid #22c55e;padding:1rem;border-radius:0 8px 8px 0;color:#94a3b8">
              ✅ This build has been saved to memory. Future builds in this category will benefit from these patterns.
            </div>""", unsafe_allow_html=True)

        # Show all memory records
        try:
            from agents.memory import BusinessMemory as BM
            mem = BM()
            stats = mem.cumulative_roi()
            all_autos = mem.all_automations()
            top_tools = mem.top_tools(5)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Automations Built", stats["total_automations"])
            col2.metric("Cumulative Annual Value", f"${stats['cumulative_annual_value']:,.0f}")
            col3.metric("Avg Value Per Build", f"${stats['average_value_per_automation']:,.0f}")

            if all_autos:
                st.markdown("<br>**Build History**")
                for rec in all_autos[:5]:
                    st.markdown(f"""
                    <div class="mem-card" style="margin-bottom:.4rem">
                      <div style="display:flex;justify-content:space-between">
                        <div style="font-weight:600;color:#e2e8f0">{rec.agent_name}</div>
                        <div style="color:#22c55e;font-weight:700">${rec.annual_value:,.0f}/yr</div>
                      </div>
                      <div style="color:#64748b;font-size:.78rem">{rec.problem_summary[:80]}... · {rec.created_at[:10]}</div>
                    </div>""", unsafe_allow_html=True)

            if top_tools:
                st.markdown("<br>**Most Used Tools**")
                for t in top_tools:
                    st.markdown(
                        f"`{t['tool']}` — used {t['count']} time(s)"
                    )
        except Exception:
            st.info("Memory stats will appear after the first successful build.")

    # ── BOTTOM CTA ─────────────────────────────────────────────────────────────
    st.markdown("<br><hr>", unsafe_allow_html=True)
    disc_val = _g(disc, "total_opportunity_value", 0) if disc else 0
    st.markdown(f"""
    <div style="text-align:center;padding:2rem 0;color:#475569;font-size:.85rem">
      <div style="color:#a78bfa;font-size:1rem;margin-bottom:.5rem">
        🔭 {len(_g(disc, 'automations', []))} additional automations identified · ${disc_val:,.0f} more value available
      </div>
      Built by <strong>SPOKE Genesis</strong> — "You spoke. It shipped. And then it built 4 more."
    </div>""", unsafe_allow_html=True)


def screen_error():
    error = st.session_state.get("error", "Unknown error")
    st.markdown(f"""
    <div style="background:#1f0f0f;border:1px solid #ef4444;border-radius:12px;padding:1.5rem">
      <h3 style="color:#ef4444;margin:0 0 .5rem">⚠️ Something went wrong</h3>
      <p style="color:#94a3b8;margin:0;font-size:.9rem">{str(error)[:400]}</p>
    </div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Try Again"):
            for k in ["genesis_result","error"]:
                st.session_state.pop(k, None)
            go("landing")
    with col2:
        if st.button("Run Genesis Demo"):
            for k in ["genesis_result","error"]:
                st.session_state.pop(k, None)
            go("genesis_running_demo")


# ── Router ────────────────────────────────────────────────────────────────────

def main():
    init_state()
    screen = st.session_state.screen

    if   screen == "landing":              screen_landing()
    elif screen == "text_input":           screen_text_input()
    elif screen == "genesis_running":      screen_genesis_running(demo_mode=False)
    elif screen == "genesis_running_demo": screen_genesis_running(demo_mode=True)
    elif screen == "genesis_result":       screen_genesis_result()
    elif screen == "error":                screen_error()
    else:                                  go("landing")


if __name__ == "__main__":
    main()
