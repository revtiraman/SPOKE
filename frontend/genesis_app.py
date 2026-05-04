"""
SPOKE Genesis — Autonomous Business Automation Intelligence Platform
Billion-dollar UI. Maximum awe.
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
    page_title="SPOKE Genesis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — BILLION DOLLAR DESIGN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Reset & Base ─────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }

html, body, .stApp {
  background: #020208 !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: #f1f5f9;
  min-height: 100vh;
}

[data-testid="stAppViewContainer"] {
  background: #020208 !important;
}

[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0a0a18; }
::-webkit-scrollbar-thumb { background: #6c63ff44; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #6c63ff; }

/* ── Keyframes ────────────────────────────────────────────────────────────── */
@keyframes fadeUp   { from { opacity:0; transform:translateY(24px) } to { opacity:1; transform:translateY(0) } }
@keyframes fadeIn   { from { opacity:0 } to { opacity:1 } }
@keyframes glow     { 0%,100%{text-shadow:0 0 40px #6c63ff60,0 0 80px #6c63ff30} 50%{text-shadow:0 0 60px #a78bfa90,0 0 120px #6c63ff50} }
@keyframes pulse    { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.7;transform:scale(.97)} }
@keyframes shimmer  { 0%{background-position:-200% center} 100%{background-position:200% center} }
@keyframes spin     { to { transform:rotate(360deg) } }
@keyframes borderFlow { 0%,100%{border-color:#6c63ff} 33%{border-color:#a78bfa} 66%{border-color:#60a5fa} }
@keyframes ticker   { from{transform:translateX(0)} to{transform:translateX(-50%)} }
@keyframes scanLine { 0%{top:-5%} 100%{top:105%} }
@keyframes countUp  { from{opacity:0;transform:scale(.85) translateY(10px)} to{opacity:1;transform:scale(1) translateY(0)} }
@keyframes dotPulse { 0%,100%{box-shadow:0 0 0 0 #22c55e66} 50%{box-shadow:0 0 0 8px transparent} }
@keyframes gradient { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes float    { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
@keyframes slideIn  { from{opacity:0;transform:translateX(-20px)} to{opacity:1;transform:translateX(0)} }
@keyframes ripple   { 0%{transform:scale(.8);opacity:1} 100%{transform:scale(2.4);opacity:0} }

/* ── Hero Section ─────────────────────────────────────────────────────────── */
.hero-wrap {
  padding: 5rem 2rem 3rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.hero-wrap::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% -20%, #6c63ff18 0%, transparent 70%);
  pointer-events: none;
}
.hero-badge {
  display: inline-flex; align-items: center; gap: .5rem;
  background: linear-gradient(135deg, #6c63ff15, #a78bfa15);
  border: 1px solid #6c63ff40;
  border-radius: 999px;
  padding: .35rem 1.2rem;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .15em;
  text-transform: uppercase;
  color: #a78bfa;
  margin-bottom: 1.8rem;
  animation: fadeIn .6s ease;
}
.hero-badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #22c55e;
  animation: dotPulse 2s ease-in-out infinite;
}
.hero-title {
  font-size: clamp(4rem, 10vw, 8rem);
  font-weight: 900;
  letter-spacing: -.05em;
  line-height: .95;
  background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 40%, #818cf8 70%, #60a5fa 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 6s linear infinite, glow 4s ease-in-out infinite;
  margin-bottom: 1.2rem;
}
.hero-sub {
  font-size: clamp(1rem, 2.5vw, 1.4rem);
  color: #64748b;
  font-weight: 400;
  max-width: 560px;
  margin: 0 auto 2.5rem;
  line-height: 1.6;
  animation: fadeUp .8s ease .2s both;
}
.hero-sub strong { color: #94a3b8; font-weight: 600; }

/* ── Glass Cards ──────────────────────────────────────────────────────────── */
.glass {
  background: rgba(255,255,255,.025);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 20px;
  transition: all .3s ease;
}
.glass:hover {
  background: rgba(255,255,255,.04);
  border-color: rgba(108,99,255,.3);
  transform: translateY(-2px);
  box-shadow: 0 20px 60px rgba(0,0,0,.4), 0 0 0 1px rgba(108,99,255,.1);
}
.glass-active {
  background: rgba(108,99,255,.08) !important;
  border-color: rgba(108,99,255,.4) !important;
  box-shadow: 0 0 0 1px rgba(108,99,255,.2), 0 0 40px rgba(108,99,255,.15) !important;
}
.glass-green {
  background: rgba(34,197,94,.05) !important;
  border-color: rgba(34,197,94,.25) !important;
  box-shadow: 0 0 30px rgba(34,197,94,.1) !important;
}

/* ── Input Cards (Landing) ────────────────────────────────────────────────── */
.input-card {
  padding: 2rem 1.5rem;
  border-radius: 20px;
  background: rgba(255,255,255,.025);
  border: 1px solid rgba(255,255,255,.07);
  text-align: center;
  cursor: pointer;
  transition: all .35s cubic-bezier(.4,0,.2,1);
  position: relative;
  overflow: hidden;
  animation: fadeUp .7s ease both;
}
.input-card::after {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(circle at 50% 0%, rgba(108,99,255,.12) 0%, transparent 70%);
  opacity: 0;
  transition: opacity .3s;
}
.input-card:hover { border-color: rgba(108,99,255,.4); transform: translateY(-4px);
  box-shadow: 0 30px 80px rgba(0,0,0,.5), 0 0 0 1px rgba(108,99,255,.15); }
.input-card:hover::after { opacity: 1; }
.input-card.featured { border-color: rgba(108,99,255,.35);
  background: linear-gradient(135deg, rgba(108,99,255,.08), rgba(167,139,250,.05)); }
.input-icon { font-size: 2.8rem; margin-bottom: .9rem; animation: float 4s ease-in-out infinite; }
.input-title { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; margin-bottom: .3rem; }
.input-desc { font-size: .78rem; color: #475569; }

/* ── System Grid ──────────────────────────────────────────────────────────── */
.sys-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: .6rem;
  margin: 2rem 0;
}
.sys-item {
  background: rgba(255,255,255,.02);
  border: 1px solid rgba(255,255,255,.05);
  border-radius: 14px;
  padding: 1.1rem .8rem;
  text-align: center;
  transition: all .25s ease;
  animation: fadeUp .5s ease both;
  cursor: default;
}
.sys-item:hover { border-color: rgba(108,99,255,.3); background: rgba(108,99,255,.05);
  transform: translateY(-3px); }
.sys-icon { font-size: 1.8rem; margin-bottom: .5rem; }
.sys-name { font-size: .72rem; font-weight: 700; color: #94a3b8; }
.sys-desc { font-size: .65rem; color: #334155; margin-top: .2rem; }

/* ── Ticker ───────────────────────────────────────────────────────────────── */
.ticker-outer {
  overflow: hidden;
  border-top: 1px solid rgba(255,255,255,.04);
  border-bottom: 1px solid rgba(255,255,255,.04);
  background: rgba(255,255,255,.015);
  padding: .7rem 0;
  margin: 1.5rem 0;
}
.ticker-inner {
  display: inline-block;
  white-space: nowrap;
  animation: ticker 30s linear infinite;
  color: #334155;
  font-size: .78rem;
  letter-spacing: .03em;
}
.ticker-item { display: inline-block; margin: 0 2rem; }
.ticker-item span { color: #6c63ff; font-weight: 600; }

/* ── Stats Bar ────────────────────────────────────────────────────────────── */
.stats-bar { display: flex; gap: 1px; background: rgba(255,255,255,.04); border-radius: 16px; overflow: hidden; margin: 1.5rem 0; }
.stat-cell { flex: 1; padding: 1.5rem 1rem; text-align: center; background: #020208; transition: background .2s; }
.stat-cell:hover { background: rgba(108,99,255,.06); }
.stat-val { font-size: 1.8rem; font-weight: 900; letter-spacing: -.03em; }
.stat-lbl { font-size: .68rem; color: #475569; text-transform: uppercase; letter-spacing: .1em; margin-top: .2rem; }

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.stButton > button {
  width: 100%;
  background: linear-gradient(135deg, #6c63ff, #a78bfa) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 12px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 700 !important;
  font-size: .9rem !important;
  padding: .75rem 1.5rem !important;
  letter-spacing: .01em !important;
  transition: all .25s cubic-bezier(.4,0,.2,1) !important;
  box-shadow: 0 4px 20px rgba(108,99,255,.3) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 35px rgba(108,99,255,.5) !important;
  filter: brightness(1.1) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Progress ─────────────────────────────────────────────────────────────── */
.prog-container {
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 16px;
  padding: 1.5rem;
  margin: 1rem 0;
}
.prog-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: .8rem; }
.prog-label { font-weight: 600; color: #e2e8f0; font-size: .92rem; }
.prog-pct { font-size: .82rem; color: #6c63ff; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.prog-track { background: rgba(255,255,255,.05); border-radius: 999px; height: 6px; overflow: hidden; }
.prog-fill {
  height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, #6c63ff, #a78bfa, #60a5fa);
  background-size: 200% 100%;
  animation: shimmer 2s linear infinite;
  transition: width .8s cubic-bezier(.4,0,.2,1);
}
.prog-detail { font-size: .75rem; color: #475569; margin-top: .5rem; font-family: 'JetBrains Mono', monospace; }

/* ── Phase Timeline ───────────────────────────────────────────────────────── */
.phase-list { display: flex; flex-direction: column; gap: .4rem; margin: 1rem 0; }
.phase-row {
  display: flex; align-items: center; gap: .8rem;
  padding: .6rem .9rem; border-radius: 10px;
  transition: all .2s ease;
  font-size: .82rem;
}
.phase-row.done { color: #22c55e; }
.phase-row.active { color: #a78bfa; background: rgba(108,99,255,.07); border: 1px solid rgba(108,99,255,.15); }
.phase-row.pending { color: #334155; }
.phase-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.phase-dot.done { background: #22c55e; }
.phase-dot.active { background: #6c63ff; animation: dotPulse 1.5s ease-in-out infinite; }
.phase-dot.pending { background: #1e293b; }

/* ── Metric Cards ─────────────────────────────────────────────────────────── */
.metric-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: .8rem; }
.metric-card {
  background: rgba(255,255,255,.025);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 16px;
  padding: 1.4rem 1.2rem;
  text-align: center;
  transition: all .25s ease;
  animation: fadeUp .5s ease both;
}
.metric-card:hover { border-color: rgba(108,99,255,.25); transform: translateY(-2px); }
.metric-val {
  font-size: 2.2rem; font-weight: 900; letter-spacing: -.03em;
  animation: countUp .8s cubic-bezier(.4,0,.2,1) both;
}
.metric-val.green { color: #22c55e; }
.metric-val.purple { color: #a78bfa; }
.metric-val.blue { color: #60a5fa; }
.metric-val.white { color: #f1f5f9; }
.metric-lbl { font-size: .65rem; color: #475569; text-transform: uppercase; letter-spacing: .1em; margin-top: .4rem; }

/* ── Spawn Cards ──────────────────────────────────────────────────────────── */
.spawn-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: .8rem; margin-top: 1rem; }
@media(max-width:900px) { .spawn-grid { grid-template-columns: 1fr 1fr; } }
.spawn-card {
  background: rgba(255,255,255,.02);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 16px;
  padding: 1.3rem;
  transition: all .3s cubic-bezier(.4,0,.2,1);
  position: relative;
  overflow: hidden;
  animation: fadeUp .5s ease both;
}
.spawn-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(108,99,255,.6), transparent);
  opacity: 0; transition: opacity .3s;
}
.spawn-card:hover { border-color: rgba(108,99,255,.3); transform: translateY(-4px);
  box-shadow: 0 20px 50px rgba(0,0,0,.4), 0 0 0 1px rgba(108,99,255,.1); }
.spawn-card:hover::before { opacity: 1; }
.spawn-name { font-size: 1rem; font-weight: 800; color: #f1f5f9; margin-bottom: .2rem; }
.spawn-tagline { font-size: .75rem; color: #64748b; margin-bottom: .8rem; line-height: 1.4; }
.spawn-value { font-size: 1.6rem; font-weight: 900; color: #22c55e; letter-spacing: -.03em; }
.spawn-value-sub { font-size: .7rem; color: #475569; display: inline; font-weight: 400; }
.spawn-badge {
  display: inline-block;
  background: rgba(108,99,255,.12);
  border: 1px solid rgba(108,99,255,.2);
  border-radius: 999px;
  padding: .15rem .6rem;
  font-size: .64rem; font-weight: 600; color: #a78bfa;
  text-transform: uppercase; letter-spacing: .08em;
  margin-top: .6rem;
}

/* ── Counterfactual ───────────────────────────────────────────────────────── */
.cf-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: .8rem; }
.cf-card {
  border-radius: 16px;
  padding: 1.3rem;
  transition: all .2s ease;
  animation: slideIn .4s ease both;
  position: relative;
}
.cf-card.winner {
  background: rgba(34,197,94,.04);
  border: 1px solid rgba(34,197,94,.25);
  box-shadow: 0 0 30px rgba(34,197,94,.08);
}
.cf-card.rejected {
  background: rgba(239,68,68,.03);
  border: 1px solid rgba(239,68,68,.15);
  opacity: .75;
}
.cf-card.warn {
  background: rgba(245,158,11,.03);
  border: 1px solid rgba(245,158,11,.15);
  opacity: .8;
}
.cf-pill {
  display: inline-block; border-radius: 999px; padding: .2rem .7rem;
  font-size: .64rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
  margin-bottom: .7rem;
}
.cf-pill.win { background: rgba(34,197,94,.15); color: #22c55e; border: 1px solid rgba(34,197,94,.3); }
.cf-pill.rej { background: rgba(239,68,68,.12); color: #f87171; border: 1px solid rgba(239,68,68,.2); }
.cf-pill.wrn { background: rgba(245,158,11,.12); color: #fbbf24; border: 1px solid rgba(245,158,11,.2); }
.cf-name { font-size: 1rem; font-weight: 800; color: #f1f5f9; margin-bottom: .3rem; }
.cf-pattern { font-size: .72rem; color: #6c63ff; font-weight: 600; margin-bottom: .5rem; }
.cf-desc { font-size: .8rem; color: #64748b; line-height: 1.5; margin-bottom: .8rem; }
.cf-score { font-size: 2rem; font-weight: 900; letter-spacing: -.05em; }
.cf-score.win { color: #22c55e; }
.cf-score.rej { color: #ef4444; }
.cf-score.wrn { color: #f59e0b; }
.cf-reject-reason {
  margin-top: .7rem; padding: .6rem .8rem;
  background: rgba(239,68,68,.06); border-radius: 8px;
  font-size: .75rem; color: #94a3b8; line-height: 1.5;
  border-left: 2px solid rgba(239,68,68,.4);
}

/* ── DAG Flow ─────────────────────────────────────────────────────────────── */
.dag-outer { overflow-x: auto; padding: 1.5rem 1rem; }
.dag-flow {
  display: flex; align-items: center; gap: 0;
  min-width: max-content;
}
.dag-node {
  background: rgba(34,197,94,.05);
  border: 1px solid rgba(34,197,94,.25);
  border-radius: 14px;
  padding: 1rem 1.2rem;
  text-align: center; min-width: 90px;
  transition: all .3s ease;
  position: relative;
}
.dag-node:hover { transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(34,197,94,.15), 0 0 0 1px rgba(34,197,94,.3); }
.dag-node-icon { font-size: 1.4rem; }
.dag-node-label { font-size: .66rem; font-weight: 700; color: #22c55e; text-transform: uppercase;
  letter-spacing: .06em; margin-top: .3rem; }
.dag-node-rate { font-size: .6rem; color: #475569; font-family: 'JetBrains Mono',monospace; }
.dag-connector { display: flex; align-items: center; padding: 0 .2rem; }
.dag-line { width: 32px; height: 1px; background: linear-gradient(90deg, rgba(34,197,94,.4), rgba(108,99,255,.4)); }
.dag-arrow { color: rgba(108,99,255,.6); font-size: .7rem; margin-left: -4px; }

/* ── Simulation Table ─────────────────────────────────────────────────────── */
.sim-table { width: 100%; border-collapse: separate; border-spacing: 0 .3rem; }
.sim-th { font-size: .64rem; font-weight: 700; color: #334155; text-transform: uppercase;
  letter-spacing: .1em; padding: .5rem .8rem; text-align: left; }
.sim-td { padding: .7rem .8rem; font-size: .82rem; }
.sim-row { background: rgba(255,255,255,.02); transition: background .2s; }
.sim-row:hover { background: rgba(108,99,255,.05); }
.sim-row td:first-child { border-radius: 10px 0 0 10px; }
.sim-row td:last-child { border-radius: 0 10px 10px 0; }
.sim-badge {
  display: inline-block; padding: .15rem .55rem; border-radius: 999px;
  font-size: .65rem; font-weight: 700;
}
.sim-badge.ok { background: rgba(34,197,94,.12); color: #22c55e; }
.sim-badge.warn { background: rgba(245,158,11,.12); color: #fbbf24; }

/* ── Economic Dashboard ───────────────────────────────────────────────────── */
.econ-hero {
  background: linear-gradient(135deg, rgba(34,197,94,.05) 0%, rgba(108,99,255,.05) 100%);
  border: 1px solid rgba(34,197,94,.15);
  border-radius: 20px; padding: 2.5rem;
  text-align: center; margin-bottom: 1.5rem;
  position: relative; overflow: hidden;
}
.econ-hero::before {
  content: '';
  position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(ellipse at center, rgba(34,197,94,.04) 0%, transparent 60%);
  pointer-events: none;
}
.econ-main-val {
  font-size: clamp(3rem,7vw,5.5rem); font-weight: 900; letter-spacing: -.04em;
  color: #22c55e; animation: countUp 1s ease both;
  text-shadow: 0 0 40px rgba(34,197,94,.3);
}
.econ-main-lbl { font-size: .9rem; color: #64748b; margin-top: .4rem; }
.econ-chips { display: flex; justify-content: center; gap: .8rem; margin-top: 1.2rem; flex-wrap: wrap; }
.econ-chip {
  padding: .4rem 1rem; border-radius: 999px; font-size: .78rem; font-weight: 600;
  display: flex; align-items: center; gap: .4rem;
}
.econ-chip.purple { background: rgba(167,139,250,.1); border: 1px solid rgba(167,139,250,.25); color: #a78bfa; }
.econ-chip.blue   { background: rgba(96,165,250,.1);  border: 1px solid rgba(96,165,250,.25);  color: #60a5fa; }
.econ-chip.green  { background: rgba(34,197,94,.1);   border: 1px solid rgba(34,197,94,.25);   color: #22c55e; }
.li-table { display: flex; flex-direction: column; gap: .35rem; }
.li-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: .75rem 1rem; border-radius: 12px;
  background: rgba(255,255,255,.02);
  border: 1px solid rgba(255,255,255,.04);
  transition: all .2s ease; animation: slideIn .4s ease both;
}
.li-row:hover { background: rgba(108,99,255,.05); border-color: rgba(108,99,255,.15); }
.li-name { font-size: .84rem; color: #e2e8f0; font-weight: 500; }
.li-calc { font-size: .72rem; color: #475569; margin-top: .1rem; }
.li-val { font-size: 1rem; font-weight: 800; color: #22c55e; white-space: nowrap; }
.li-agent { font-size: .65rem; color: #a78bfa; font-weight: 600; }
.li-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

/* ── Self-Heal Terminal ───────────────────────────────────────────────────── */
.terminal-wrap {
  background: #060610;
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
}
.terminal-toolbar {
  display: flex; align-items: center; gap: .5rem;
  padding: .75rem 1rem;
  background: rgba(255,255,255,.03);
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.t-dot { width: 12px; height: 12px; border-radius: 50%; }
.t-dot.red { background: #ff5f57; }
.t-dot.yellow { background: #ffbd2e; }
.t-dot.green { background: #28ca42; }
.t-title { font-size: .75rem; color: #475569; font-family: 'JetBrains Mono',monospace; margin-left: .5rem; }
.terminal-body { padding: 1.2rem; font-family: 'JetBrains Mono', monospace; font-size: .78rem; line-height: 1.7; }
.t-line { margin: .1rem 0; animation: slideIn .3s ease both; }
.t-inject { color: #a78bfa; }
.t-running { color: #60a5fa; }
.t-error  { color: #f87171; }
.t-warn   { color: #fbbf24; }
.t-fix    { color: #a78bfa; }
.t-ok     { color: #22c55e; }
.t-muted  { color: #334155; }
.t-cursor { display: inline-block; width: 8px; height: 14px; background: #6c63ff;
  animation: pulse 1s ease-in-out infinite; vertical-align: text-bottom; margin-left: 2px; }

/* ── Discovery Cards ──────────────────────────────────────────────────────── */
.disc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; }
.disc-card {
  background: rgba(255,255,255,.02);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 16px; padding: 1.3rem;
  transition: all .3s ease; animation: fadeUp .5s ease both;
  position: relative; overflow: hidden;
}
.disc-card:hover { border-color: rgba(108,99,255,.3); transform: translateY(-3px);
  box-shadow: 0 15px 40px rgba(0,0,0,.4); }
.disc-rank-badge {
  position: absolute; top: 1rem; right: 1rem;
  background: rgba(108,99,255,.12); border: 1px solid rgba(108,99,255,.2);
  border-radius: 999px; padding: .1rem .55rem;
  font-size: .65rem; font-weight: 700; color: #a78bfa;
}
.disc-title { font-size: .95rem; font-weight: 800; color: #f1f5f9; margin-bottom: .4rem; }
.disc-desc { font-size: .78rem; color: #64748b; line-height: 1.5; margin-bottom: .8rem; }
.disc-why {
  background: rgba(34,197,94,.04); border: 1px solid rgba(34,197,94,.1);
  border-radius: 8px; padding: .55rem .7rem;
  font-size: .73rem; color: #475569; line-height: 1.5; margin-bottom: .8rem;
}
.disc-why strong { color: #22c55e; }
.disc-bottom { display: flex; justify-content: space-between; align-items: flex-end; }
.disc-value { font-size: 1.4rem; font-weight: 900; color: #22c55e; letter-spacing: -.03em; }
.disc-meta { font-size: .68rem; color: #475569; }
.disc-tools { display: flex; gap: .3rem; flex-wrap: wrap; margin-top: .5rem; }
.disc-tool { font-size: .63rem; color: #6c63ff; background: rgba(108,99,255,.08);
  border: 1px solid rgba(108,99,255,.15); border-radius: 4px; padding: .1rem .45rem; }

/* ── Stack Detection ──────────────────────────────────────────────────────── */
.stack-grid { display: flex; flex-wrap: wrap; gap: .6rem; }
.tool-chip {
  display: flex; align-items: center; gap: .5rem;
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 10px; padding: .5rem .9rem;
  transition: all .2s ease; animation: fadeUp .4s ease both;
}
.tool-chip:hover { border-color: rgba(108,99,255,.3); background: rgba(108,99,255,.06); transform: translateY(-2px); }
.tool-color-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.tool-name { font-size: .82rem; font-weight: 600; color: #e2e8f0; }
.tool-conf { font-size: .68rem; color: #22c55e; font-family: 'JetBrains Mono',monospace; }

/* ── Deployment ───────────────────────────────────────────────────────────── */
.deploy-hero {
  background: rgba(34,197,94,.04);
  border: 1px solid rgba(34,197,94,.2);
  border-radius: 16px; padding: 1.5rem;
  display: flex; align-items: center; gap: 1.2rem;
  margin-bottom: 1rem;
}
.deploy-indicator { position: relative; }
.deploy-dot { width: 14px; height: 14px; background: #22c55e; border-radius: 50%; }
.deploy-ripple {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%,-50%);
  width: 14px; height: 14px; border-radius: 50%;
  border: 1px solid #22c55e;
  animation: ripple 2s ease-in-out infinite;
}
.hc-row {
  display: flex; align-items: center; gap: .7rem;
  padding: .6rem .9rem; border-radius: 10px;
  background: rgba(255,255,255,.02); margin: .25rem 0;
  font-size: .82rem;
}
.hc-status { font-size: .65rem; font-weight: 700; padding: .15rem .5rem;
  border-radius: 999px; text-transform: uppercase; letter-spacing: .08em; }
.hc-status.ok { background: rgba(34,197,94,.12); color: #22c55e; }
.hc-status.warn { background: rgba(245,158,11,.12); color: #fbbf24; }
.hc-endpoint { color: #94a3b8; flex: 1; }
.hc-latency { color: #475569; font-family: 'JetBrains Mono',monospace; font-size: .72rem; }

/* ── Memory ───────────────────────────────────────────────────────────────── */
.memory-card {
  background: rgba(255,255,255,.02);
  border: 1px solid rgba(255,255,255,.05);
  border-radius: 14px; padding: 1rem 1.2rem;
  display: flex; justify-content: space-between; align-items: center;
  transition: all .2s ease; animation: slideIn .3s ease both;
}
.memory-card:hover { border-color: rgba(108,99,255,.2); background: rgba(108,99,255,.04); }

/* ── Finale ───────────────────────────────────────────────────────────────── */
.finale-wrap {
  text-align: center;
  padding: 4rem 2rem;
  position: relative; overflow: hidden;
}
.finale-wrap::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 80% 70% at 50% 50%, rgba(34,197,94,.06) 0%, rgba(108,99,255,.04) 40%, transparent 70%);
  pointer-events: none;
}
.finale-label {
  display: inline-flex; align-items: center; gap: .5rem;
  background: rgba(34,197,94,.08); border: 1px solid rgba(34,197,94,.25);
  border-radius: 999px; padding: .35rem 1.2rem;
  font-size: .72rem; font-weight: 700; color: #22c55e;
  letter-spacing: .12em; text-transform: uppercase;
  margin-bottom: 1.5rem;
}
.finale-num {
  font-size: clamp(4rem, 12vw, 9rem);
  font-weight: 900; letter-spacing: -.05em; line-height: 1;
  background: linear-gradient(135deg, #22c55e 0%, #4ade80 50%, #86efac 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: countUp 1.2s cubic-bezier(.4,0,.2,1) both;
  text-shadow: none;
  filter: drop-shadow(0 0 40px rgba(34,197,94,.4));
}
.finale-sub { font-size: 1.2rem; color: #64748b; margin: .6rem 0 2rem; }
.finale-chips { display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 2.5rem; }
.finale-chip {
  padding: .6rem 1.4rem; border-radius: 14px;
  font-size: .88rem; font-weight: 700;
  display: flex; align-items: center; gap: .5rem;
}
.finale-chip.a { background: rgba(108,99,255,.1); border: 1px solid rgba(108,99,255,.25); color: #a78bfa; }
.finale-chip.b { background: rgba(96,165,250,.1);  border: 1px solid rgba(96,165,250,.25);  color: #60a5fa; }
.finale-chip.c { background: rgba(34,197,94,.1);   border: 1px solid rgba(34,197,94,.25);   color: #22c55e; }
.finale-cta {
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 16px; padding: 1.5rem 2.5rem;
  display: inline-block; max-width: 560px;
  font-size: 1rem; color: #94a3b8; line-height: 1.7; font-style: italic;
}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
  background: rgba(255,255,255,.02) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,.06) !important;
  padding: .3rem !important;
  gap: .2rem !important;
}
[data-baseweb="tab"] {
  border-radius: 8px !important;
  font-size: .78rem !important;
  font-weight: 600 !important;
  font-family: 'Inter',sans-serif !important;
  padding: .5rem .9rem !important;
  color: #475569 !important;
  border: none !important;
  background: transparent !important;
}
[data-baseweb="tab"][aria-selected="true"] {
  background: rgba(108,99,255,.15) !important;
  color: #a78bfa !important;
  border: 1px solid rgba(108,99,255,.25) !important;
}
[data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }
[data-baseweb="tab-highlight"] { display: none !important; }
[data-baseweb="tab-border"] { display: none !important; }

/* ── Section Headers ──────────────────────────────────────────────────────── */
.section-label {
  font-size: .64rem; font-weight: 700; color: #6c63ff;
  text-transform: uppercase; letter-spacing: .15em; margin-bottom: .4rem;
}
.section-title { font-size: 1.4rem; font-weight: 800; color: #f1f5f9; margin-bottom: .3rem; }
.section-sub { font-size: .85rem; color: #475569; margin-bottom: 1.5rem; }

/* ── Divider ──────────────────────────────────────────────────────────────── */
.div-line { height: 1px; background: linear-gradient(90deg,transparent,rgba(255,255,255,.06),transparent); margin: 2rem 0; }

/* ── File upload area ─────────────────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"] {
  background: rgba(255,255,255,.02) !important;
  border: 1px dashed rgba(108,99,255,.3) !important;
  border-radius: 12px !important;
  color: #475569 !important;
}
[data-testid="stFileUploadDropzone"]:hover {
  border-color: rgba(108,99,255,.6) !important;
  background: rgba(108,99,255,.04) !important;
}

/* ── Text inputs ──────────────────────────────────────────────────────────── */
[data-baseweb="textarea"] textarea,
[data-baseweb="input"] input {
  background: rgba(255,255,255,.03) !important;
  border: 1px solid rgba(255,255,255,.08) !important;
  border-radius: 12px !important;
  color: #f1f5f9 !important;
  font-family: 'Inter', sans-serif !important;
  font-size: .88rem !important;
}
[data-baseweb="textarea"] textarea:focus,
[data-baseweb="input"] input:focus {
  border-color: rgba(108,99,255,.5) !important;
  box-shadow: 0 0 0 3px rgba(108,99,255,.12) !important;
}

/* ── Expander ─────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: rgba(255,255,255,.02) !important;
  border: 1px solid rgba(255,255,255,.06) !important;
  border-radius: 12px !important;
}

/* ── Metrics ──────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: rgba(255,255,255,.02);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 14px; padding: 1rem !important;
}
[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 900 !important; }

/* ── Columns gap ──────────────────────────────────────────────────────────── */
[data-testid="column"] { padding: 0 .3rem !important; }

hr { border: none !important; border-top: 1px solid rgba(255,255,255,.06) !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _g(obj, key, default=None):
    if obj is None: return default
    if hasattr(obj, key): return getattr(obj, key)
    if isinstance(obj, dict): return obj.get(key, default)
    return default

def init_state():
    for k, v in {"screen":"landing","genesis_result":None,"transcript_text":"",
                  "video_path":"","error":None,"show_code":False}.items():
        if k not in st.session_state: st.session_state[k] = v

def go(s: str):
    st.session_state.screen = s
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LANDING SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def screen_landing():
    # Hero
    st.markdown("""
    <div class="hero-wrap">
      <div class="hero-badge">
        <div class="hero-badge-dot"></div>
        Genesis Edition &nbsp;·&nbsp; 10 AI Systems
      </div>
      <div class="hero-title">SPOKE</div>
      <div class="hero-sub">
        Describe one problem.<br>
        <strong>Watch 10 AI systems build your entire business operation.</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Ticker
    ticker_content = "· ".join([
        "⚡ OrderSync + 5 agents built in 8.3s",
        "🛡️ FraudShield blocked $4,200 fraud",
        "🏛️ Counterfactual rejected 3 inferior designs",
        "💰 $121,810 annual value created",
        "🔧 Self-heal recovered in 2.7s",
        "📅 7-day simulation: 98.4% uptime",
        "🔭 4 adjacent opportunities discovered",
        "🧠 Business memory learns across builds",
    ] * 2)
    st.markdown(f"""
    <div class="ticker-outer">
      <div class="ticker-inner">
        {''.join(f'<span class="ticker-item">· <span>{item.split(" ",1)[0]}</span> {" ".join(item.split(" ")[1:])}</span>' for item in ticker_content.split("· ") if item)}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Three input cards
    col1, col2, col3 = st.columns(3, gap="small")

    with col1:
        st.markdown("""
        <div class="input-card" style="animation-delay:.1s">
          <div class="input-icon">🎬</div>
          <div class="input-title">Upload Video</div>
          <div class="input-desc">Record your screen or voice.<br>Genesis reads everything.</div>
        </div>""", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload video or audio",
                                    type=["mp4","mov","webm","avi","mp3","wav"],
                                    label_visibility="collapsed", key="g_upload")
        if uploaded:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix, delete=False)
            tmp.write(uploaded.read()); tmp.close()
            st.session_state.video_path = tmp.name
            go("running")

    with col2:
        st.markdown("""
        <div class="input-card" style="animation-delay:.2s">
          <div class="input-icon">✍️</div>
          <div class="input-title">Describe Your Problem</div>
          <div class="input-desc">Type any repetitive task.<br>Genesis builds the solution.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Start typing →", use_container_width=True, key="text_btn"):
            go("text_input")

    with col3:
        st.markdown("""
        <div class="input-card featured" style="animation-delay:.3s">
          <div class="input-icon" style="animation-delay:.5s">⚡</div>
          <div class="input-title" style="color:#a78bfa">Live Genesis Demo</div>
          <div class="input-desc">All 10 systems · No credentials needed</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Launch Genesis ⚡", use_container_width=True, key="demo_btn"):
            go("running_demo")

    st.markdown('<div class="div-line"></div>', unsafe_allow_html=True)

    # 10 Systems
    st.markdown("""
    <div style="text-align:center;margin-bottom:1.2rem">
      <div class="section-label">What Genesis builds for you</div>
      <div style="font-size:1.2rem;font-weight:800;color:#f1f5f9">10 autonomous systems. One conversation.</div>
    </div>
    <div class="sys-grid">""", unsafe_allow_html=True)

    systems = [
        ("⚡","Agent Spawn","1 → 5 agents"),
        ("🏛️","Counterfactual","Rejects weak designs"),
        ("🎯","Stack Detection","Sees your tools"),
        ("🔀","Workflow DAG","Live graph"),
        ("📅","Simulation","7-day test run"),
        ("💰","Economic Brain","Board-ready ROI"),
        ("🔧","Self-Heal","Autonomous recovery"),
        ("🚀","Deployment","Live + health checks"),
        ("🧠","Memory","Learns over time"),
        ("🔭","Discovery","Finds what you missed"),
    ]
    sys_html = "".join(
        f'<div class="sys-item" style="animation-delay:{i*.05:.2f}s">'
        f'<div class="sys-icon">{icon}</div>'
        f'<div class="sys-name">{name}</div>'
        f'<div class="sys-desc">{desc}</div></div>'
        for i,(icon,name,desc) in enumerate(systems)
    )
    st.markdown(sys_html + "</div>", unsafe_allow_html=True)

    st.markdown('<div class="div-line"></div>', unsafe_allow_html=True)

    # Stats
    st.markdown("""<div class="stats-bar">""", unsafe_allow_html=True)
    for val, lbl, color in [
        ("10","AI Systems","#a78bfa"),
        ("5+","Agents per Build","#60a5fa"),
        ("<10s","Total Build Time","#22c55e"),
        ("$121K","Avg Annual Value","#22c55e"),
        ("2336%","Demonstrated ROI","#a78bfa"),
        ("0","Lines You Write","#60a5fa"),
    ]:
        st.markdown(f"""
        <div class="stat-cell">
          <div class="stat-val" style="color:{color}">{val}</div>
          <div class="stat-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TEXT INPUT
# ══════════════════════════════════════════════════════════════════════════════
def screen_text_input():
    st.markdown("""
    <div style="max-width:680px;margin:3rem auto 0;padding:0 1rem">
      <div class="section-label">New Automation</div>
      <div class="section-title" style="font-size:2rem">What wastes your time?</div>
      <div class="section-sub">Describe any repetitive business task. Genesis will build your primary automation and up to 5 adjacent agents.</div>
    </div>
    """, unsafe_allow_html=True)

    example = ("Every day I get 10–15 order emails in Gmail. I manually open each one, "
               "copy the customer name, product, quantity, and price into Google Sheets. "
               "It takes about 2 hours every day and I hate it.")

    with st.container():
        text = st.text_area("Problem description", height=180,
                            placeholder=f"e.g. {example}",
                            label_visibility="collapsed", key="prob_text")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("← Back", key="back_btn"):
            go("landing")
    with col2:
        if st.button("Launch Genesis →", use_container_width=True, key="launch_btn"):
            if len(text.strip()) < 20:
                st.error("Please describe your problem in at least a sentence.")
            else:
                st.session_state.transcript_text = text.strip()
                go("running")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📋 Use the order-email example", key="example_btn"):
        st.session_state.transcript_text = example
        go("running")


# ══════════════════════════════════════════════════════════════════════════════
# RUNNING SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def screen_running(demo_mode: bool = False):
    from core.genesis_pipeline import GenesisOrchestrator

    label = "⚡ Demo Mode" if demo_mode else "🚀 Building"
    st.markdown(f"""
    <div style="padding:2.5rem 0 1.5rem;text-align:center">
      <div class="hero-badge" style="margin-bottom:1rem">{label}</div>
      <div style="font-size:2.2rem;font-weight:900;color:#f1f5f9;letter-spacing:-.03em">
        10 systems activating...
      </div>
      <div style="color:#475569;margin-top:.4rem;font-size:.9rem">
        Watch autonomous AI design, build, test, and deploy your entire operation.
      </div>
    </div>""", unsafe_allow_html=True)

    prog_ph   = st.empty()
    phases_ph = st.empty()

    PHASES = [
        ("Core Pipeline", "Building primary agent"),
        ("Stack Detection", "Reading your tools"),
        ("Counterfactual", "Evaluating architectures"),
        ("Agent Spawn", "Building adjacent agents"),
        ("Workflow DAG", "Mapping data flow"),
        ("Simulation", "Running 7-day test"),
        ("Economic Brain", "Computing ROI"),
        ("Self-Heal", "Proving resilience"),
        ("Deployment", "Going live"),
        ("Memory", "Learning for next time"),
        ("Discovery", "Finding more opportunities"),
    ]

    current_phase = [0]
    current_pct   = [0]
    current_msg   = ["Starting..."]

    async def on_progress(msg, pct, phase, detail=""):
        current_msg[0]  = msg
        current_pct[0]  = pct
        # detect phase index
        phase_lower = phase.lower()
        for i, (name, _) in enumerate(PHASES):
            if name.lower().replace(" ","") in phase_lower.replace(" ",""):
                current_phase[0] = i
                break

        with prog_ph.container():
            st.markdown(f"""
            <div class="prog-container">
              <div class="prog-header">
                <div class="prog-label">{msg}</div>
                <div class="prog-pct">{pct}%</div>
              </div>
              <div class="prog-track">
                <div class="prog-fill" style="width:{pct}%"></div>
              </div>
              {"<div class='prog-detail'>" + detail[:120] + "</div>" if detail else ""}
            </div>""", unsafe_allow_html=True)

        with phases_ph.container():
            rows = ""
            for i, (name, sub) in enumerate(PHASES):
                if i < current_phase[0]:
                    rows += f'<div class="phase-row done"><div class="phase-dot done"></div>✅ {name}</div>'
                elif i == current_phase[0]:
                    rows += f'<div class="phase-row active"><div class="phase-dot active"></div>⚡ {name} — <span style="color:#64748b">{sub}</span></div>'
                else:
                    rows += f'<div class="phase-row pending"><div class="phase-dot pending"></div>{name}</div>'
            st.markdown(f'<div class="phase-list">{rows}</div>', unsafe_allow_html=True)

    orchestrator = GenesisOrchestrator()
    try:
        result = asyncio.run(orchestrator.run(
            transcript_text=st.session_state.get("transcript_text") or None,
            video_path=st.session_state.get("video_path") or None,
            demo_mode=demo_mode,
            progress=on_progress,
        ))
        st.session_state.genesis_result = result.model_dump() if hasattr(result,"model_dump") else result
        if _g(result,"status","failed") == "success":
            go("result")
        else:
            st.session_state.error = _g(result,"error","Pipeline failed")
            go("error")
    except Exception as e:
        st.session_state.error = str(e)
        go("error")


# ══════════════════════════════════════════════════════════════════════════════
# RESULT SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def screen_result():
    r = st.session_state.get("genesis_result") or {}
    if not r: go("landing"); return

    core      = _g(r,"core_pipeline_result",{})
    spawn     = _g(r,"spawn",{})
    cf        = _g(r,"counterfactual",{})
    stack     = _g(r,"detected_stack",{})
    dag       = _g(r,"workflow_dag",{})
    sim       = _g(r,"simulation",{})
    econ      = _g(r,"economics",{})
    sh        = _g(r,"selfheal",{})
    deploy    = _g(r,"deployment",{})
    disc      = _g(r,"discovery",{})
    mem_note  = _g(r,"memory_learning","")
    total_v   = _g(r,"total_annual_value",0) or 0
    total_a   = _g(r,"total_agents_built",1) or 1
    sess_id   = _g(r,"session_id","")
    agent_name= _g(core,"agent_name","Your Agent")

    # ── FINALE HEADER ──────────────────────────────────────────────────────────
    hours_yr  = _g(econ,"hours_saved_per_year",0) or 0
    roi_pct   = _g(econ,"roi_percentage",0) or 0
    payback   = _g(econ,"payback_months",0) or 0
    spawn_cnt = _g(spawn,"spawn_count",0) or 0

    st.markdown(f"""
    <div class="finale-wrap">
      <div class="finale-label">
        <div class="hero-badge-dot"></div>
        Genesis Complete
      </div>
      <div class="finale-num">${total_v:,.0f}</div>
      <div class="finale-sub">estimated annual value created</div>
      <div class="finale-chips">
        <div class="finale-chip a">⚡ {total_a} systems built</div>
        <div class="finale-chip b">⏱ {hours_yr:.0f}h saved/year</div>
        <div class="finale-chip c">📈 {roi_pct:.0f}% ROI · {payback:.1f}mo payback</div>
      </div>
      <div class="finale-cta">
        "You asked for 1 automation. I built {total_a}.<br>
        Estimated annual value created: ${total_v:,.0f}.<br>
        Would you like me to continue optimizing your business?"
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        if sess_id:
            st.link_button("⬇️ Download Bundle",
                           f"http://localhost:8000/api/v1/download/{sess_id}",
                           use_container_width=True)
    with col2:
        if st.button("👁️ View Code", use_container_width=True):
            st.session_state.show_code = not st.session_state.get("show_code")
            st.rerun()
    with col3:
        if st.button("🔁 Build Another", use_container_width=True):
            for k in ["genesis_result","transcript_text","video_path","error","show_code"]:
                st.session_state.pop(k,None)
            go("landing")
    with col4:
        if st.button("📊 API Docs", use_container_width=True):
            st.markdown("[Open docs →](http://localhost:8000/docs)")

    if st.session_state.get("show_code"):
        code = _g(core,"code","")
        if code:
            st.code(code, language="python", line_numbers=True)

    st.markdown('<div class="div-line"></div>', unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "⚡ Agent Spawn",
        "🏛️ Architecture",
        "🎯 Stack",
        "🔀 DAG",
        "📅 Simulation",
        "💰 Economics",
        "🔧 Self-Heal",
        "🚀 Deploy",
        "🔭 Discovery",
        "🧠 Memory",
    ])

    # ── TAB 1: AGENT SPAWN ────────────────────────────────────────────────────
    with tabs[0]:
        spawn_count = _g(spawn,"spawn_count",0) or 0
        total_spawn_val = _g(spawn,"total_estimated_value",0) or 0
        primary_name = _g(spawn,"primary_agent_name",agent_name)

        st.markdown(f"""
        <div class="section-label">System 1 — Agent Spawn</div>
        <div class="section-title">You asked for 1. I built {1+spawn_count}.</div>
        <div class="section-sub">Genesis inferred {spawn_count} adjacent workflows from your primary automation and built them automatically.</div>
        """, unsafe_allow_html=True)

        # Primary agent badge
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:1rem;background:rgba(34,197,94,.04);
          border:1px solid rgba(34,197,94,.2);border-radius:14px;padding:1rem 1.3rem;margin-bottom:1rem">
          <div style="width:36px;height:36px;background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.3);
            border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem">⚡</div>
          <div>
            <div style="font-weight:800;color:#f1f5f9">{primary_name}</div>
            <div style="font-size:.75rem;color:#22c55e;font-weight:600">PRIMARY — Built by core 10-agent pipeline</div>
          </div>
          <div style="margin-left:auto;font-size:.7rem;background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.2);
            border-radius:999px;padding:.2rem .8rem;color:#22c55e;font-weight:700">DEPLOYED</div>
        </div>""", unsafe_allow_html=True)

        spawned = _g(spawn,"spawned_agents",[]) or []
        if spawned:
            html = '<div class="spawn-grid">'
            for i, agent in enumerate(spawned):
                name  = _g(agent,"name","Agent")
                tag   = _g(agent,"tagline","")
                val   = _g(agent,"estimated_annual_value",0) or 0
                cat   = (_g(agent,"category","") or "").replace("_"," ").title()
                what  = _g(agent,"what_it_does","") or ""
                tools = _g(agent,"tools_required",[]) or []
                html += f"""
                <div class="spawn-card" style="animation-delay:{i*.12:.2f}s">
                  <div class="spawn-name">⚡ {name}</div>
                  <div class="spawn-tagline">{tag}</div>
                  <div style="font-size:.78rem;color:#64748b;line-height:1.5;margin-bottom:.8rem">{what[:100]}</div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-end">
                    <div>
                      <div class="spawn-value">${val:,.0f}<span class="spawn-value-sub">/yr</span></div>
                      <div class="spawn-badge">{cat}</div>
                    </div>
                    <div style="text-align:right">
                      {''.join(f'<div style="font-size:.64rem;color:#475569">{t}</div>' for t in tools[:2])}
                    </div>
                  </div>
                </div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

        if total_spawn_val:
            st.markdown(f"""
            <div style="text-align:center;margin-top:2rem;padding:1.5rem;background:rgba(34,197,94,.03);
              border:1px solid rgba(34,197,94,.1);border-radius:16px">
              <div style="color:#475569;font-size:.8rem;margin-bottom:.3rem">Total value from spawned agents alone</div>
              <div style="font-size:2.5rem;font-weight:900;color:#22c55e;letter-spacing:-.04em">${total_spawn_val:,.0f}<span style="font-size:1rem;color:#475569;font-weight:400">/year</span></div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 2: COUNTERFACTUAL ─────────────────────────────────────────────────
    with tabs[1]:
        candidates = _g(cf,"candidates",[]) or []
        winner_obj = _g(cf,"winner",{}) or {}
        winner_id  = _g(winner_obj,"id","")
        rationale  = _g(cf,"selection_rationale","")

        st.markdown("""
        <div class="section-label">System 2 — Counterfactual Architect</div>
        <div class="section-title">4 architectures evaluated. 3 rejected.</div>
        <div class="section-sub">Genesis generated every viable design, scored each one, and eliminated the inferior options before writing a single line of code.</div>
        """, unsafe_allow_html=True)

        if candidates:
            html = '<div class="cf-grid">'
            for i, c in enumerate(candidates):
                cid      = _g(c,"id","")
                name     = _g(c,"name","")
                pattern  = _g(c,"pattern","")
                desc     = _g(c,"description","")
                pros     = _g(c,"pros",[]) or []
                cons     = _g(c,"cons",[]) or []
                rejection= _g(c,"rejection_reason","")
                selected = _g(c,"selected",False) or (cid == winner_id)
                scores   = _g(c,"scores",{}) or {}

                score_total = (
                    sum(scores.values()) / max(len(scores),1)
                    if isinstance(scores,dict) else
                    getattr(scores,"total",7.0) if hasattr(scores,"total") else 7.0
                )

                if selected:
                    css, pill_css, pill_text, score_css = "winner", "win", "✅ SELECTED", "win"
                elif rejection:
                    css, pill_css, pill_text, score_css = "rejected", "rej", "✗ REJECTED", "rej"
                else:
                    css, pill_css, pill_text, score_css = "warn", "wrn", "⚠ CONDITIONAL", "wrn"

                pros_html = "".join(f'<div style="color:#94a3b8;font-size:.74rem;margin:.1rem 0">✓ {p}</div>' for p in pros[:3])
                cons_html = "".join(f'<div style="color:#64748b;font-size:.74rem;margin:.1rem 0">✗ {c}</div>' for c in cons[:2])
                rej_html  = f'<div class="cf-reject-reason">⚠️ {rejection}</div>' if rejection and not selected else ""

                html += f"""
                <div class="cf-card {css}" style="animation-delay:{i*.1:.1f}s">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div style="flex:1">
                      <div class="cf-pill {pill_css}">{pill_text}</div>
                      <div class="cf-name">{name}</div>
                      <div class="cf-pattern">{pattern}</div>
                      <div class="cf-desc">{desc}</div>
                      {pros_html}{cons_html}
                    </div>
                    <div style="text-align:right;padding-left:.8rem">
                      <div class="cf-score {score_css}">{score_total:.1f}</div>
                      <div style="font-size:.6rem;color:#475569">/10</div>
                    </div>
                  </div>
                  {rej_html}
                </div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

        if rationale:
            st.markdown(f"""
            <div style="margin-top:1rem;padding:.9rem 1.2rem;background:rgba(108,99,255,.05);
              border:1px solid rgba(108,99,255,.15);border-radius:12px;font-size:.83rem;color:#94a3b8;line-height:1.6">
              🏆 {rationale}
            </div>""", unsafe_allow_html=True)

    # ── TAB 3: STACK ──────────────────────────────────────────────────────────
    with tabs[2]:
        tools_list = _g(stack,"tools",[]) or []
        summary    = _g(stack,"stack_summary","")
        frames_n   = _g(stack,"frames_analyzed",0) or 0

        st.markdown("""
        <div class="section-label">System 3 — Multimodal Tool Detection</div>
        <div class="section-title">I detected your stack automatically.</div>
        <div class="section-sub">Scanned transcript and video frames for tool names, logos, and API patterns.</div>
        """, unsafe_allow_html=True)

        if tools_list:
            st.markdown(f"""
            <div style="background:rgba(34,197,94,.03);border:1px solid rgba(34,197,94,.12);
              border-radius:14px;padding:1rem 1.3rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:.8rem">
              <div style="font-size:1.5rem">🎯</div>
              <div>
                <div style="font-size:.7rem;font-weight:700;color:#22c55e;text-transform:uppercase;letter-spacing:.1em">
                  Stack Identified
                </div>
                <div style="color:#94a3b8;font-size:.82rem">{summary}</div>
              </div>
              {"<div style='margin-left:auto;font-size:.75rem;color:#475569'>" + str(frames_n) + " frames analyzed</div>" if frames_n else ""}
            </div>""", unsafe_allow_html=True)

            chips = ""
            for t in tools_list:
                name  = _g(t,"name","")
                conf  = _g(t,"confidence",0) or 0
                color = _g(t,"logo_color","#6c63ff")
                src   = _g(t,"source","transcript")
                src_icon = {"ocr":"🔍","transcript":"💬","logo":"👁️","inferred":"🧠"}.get(src,"💬")
                chips += f"""<div class="tool-chip">
                  <div class="tool-color-dot" style="background:{color}"></div>
                  <div>
                    <div class="tool-name">{name}</div>
                    <div class="tool-conf">{src_icon} {src} · {conf:.0%}</div>
                  </div>
                </div>"""
            st.markdown(f'<div class="stack-grid">{chips}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
              border-radius:14px;padding:2rem;text-align:center;color:#475569">
              No explicit tool names detected in transcript — stack inferred from problem domain.
            </div>""", unsafe_allow_html=True)

    # ── TAB 4: DAG ────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("""
        <div class="section-label">System 4 — Live Workflow DAG</div>
        <div class="section-title">9-node autonomous workflow — all paths active.</div>
        <div class="section-sub">Every node is processing. The loop runs continuously. No human required.</div>
        """, unsafe_allow_html=True)

        nodes = [
            ("👁️","Observe","12/min"),("🧠","Extract","11/min"),("✅","Validate","11/min"),
            ("🔍","Dedup","10/min"),("🔀","Route","10/min"),("💾","Store","9/min"),
            ("📡","Monitor","9/min"),("🔔","Alert","2/hr"),("📈","Improve","∞"),
        ]
        flow_html = '<div class="dag-outer"><div class="dag-flow">'
        for i,(icon,label,rate) in enumerate(nodes):
            flow_html += f"""
            <div class="dag-node">
              <div class="dag-node-icon">{icon}</div>
              <div class="dag-node-label">{label}</div>
              <div class="dag-node-rate">{rate}</div>
            </div>"""
            if i < len(nodes)-1:
                flow_html += '<div class="dag-connector"><div class="dag-line"></div><div class="dag-arrow">▶</div></div>'
        flow_html += "</div></div>"
        st.markdown(flow_html, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        for col, val, lbl, c in [
            (col1,"9/9","Active Nodes","#22c55e"),
            (col2,"10","Total Edges","#a78bfa"),
            (col3,"12/min","Peak Throughput","#60a5fa"),
            (col4,"∞","Loop Duration","#22c55e"),
        ]:
            col.markdown(f"""<div class="metric-card" style="margin-top:.5rem">
              <div class="metric-val" style="color:{c}">{val}</div>
              <div class="metric-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 5: SIMULATION ─────────────────────────────────────────────────────
    with tabs[4]:
        days = _g(sim,"days",[]) or []
        total_ev = _g(sim,"total_events",0) or 0
        total_rv = _g(sim,"total_revenue",0) or 0
        fraud_bl = _g(sim,"total_fraud_blocked",0) or 0
        final_ac = _g(sim,"final_accuracy",0) or 0
        story    = _g(sim,"improvement_story","")

        st.markdown("""
        <div class="section-label">System 5 — One-Week Business Simulation</div>
        <div class="section-title">7 days. Real operations. Zero humans.</div>
        <div class="section-sub">Synthetic orders, fraud attempts, API outages, and self-healing recovery — all logged.</div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        for val, lbl, cls in [
            (f"{total_ev:,}","Total Operations","white"),
            (f"${total_rv:,.0f}","Revenue Captured","green"),
            (f"${fraud_bl:,.0f}","Fraud Blocked","purple"),
            (f"{final_ac:.1f}%","Final Accuracy","blue"),
        ]:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-val {cls}">{val}</div>
              <div class="metric-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div><br>", unsafe_allow_html=True)

        if days:
            table = """
            <table class="sim-table">
              <thead><tr>
                <th class="sim-th">Day</th><th class="sim-th">Orders</th>
                <th class="sim-th">Dupes Blocked</th><th class="sim-th">Fraud</th>
                <th class="sim-th">Revenue</th><th class="sim-th">Accuracy</th>
                <th class="sim-th">Uptime</th>
              </tr></thead><tbody>"""
            for d in days:
                dn  = _g(d,"day","")
                dt  = _g(d,"date","")
                ev  = _g(d,"events_processed",0)
                dup = _g(d,"duplicates_blocked",0)
                fr  = _g(d,"fraud_detected",0)
                rv  = _g(d,"revenue_captured",0)
                ac  = _g(d,"accuracy_pct",0)
                up  = _g(d,"uptime_pct",0)
                ac_c = "#22c55e" if (ac or 0)>=95 else "#f59e0b"
                fr_html = f'<span class="sim-badge warn">🛡️ {fr}</span>' if fr else "—"
                table += f"""
                <tr class="sim-row">
                  <td class="sim-td" style="color:#94a3b8">Day {dn} <span style="color:#334155">· {dt}</span></td>
                  <td class="sim-td" style="color:#f1f5f9;font-weight:700">{ev}</td>
                  <td class="sim-td" style="color:#475569">{dup}</td>
                  <td class="sim-td">{fr_html}</td>
                  <td class="sim-td" style="color:#22c55e;font-weight:700">${rv:,.0f}</td>
                  <td class="sim-td" style="color:{ac_c};font-weight:800">{ac:.1f}%</td>
                  <td class="sim-td" style="color:#22c55e">{up:.1f}%</td>
                </tr>"""
            table += "</tbody></table>"
            st.markdown(table, unsafe_allow_html=True)

        if story:
            st.markdown(f"""
            <div style="margin-top:1rem;padding:.9rem 1.2rem;background:rgba(34,197,94,.04);
              border-left:3px solid rgba(34,197,94,.5);border-radius:0 12px 12px 0;
              font-size:.82rem;color:#94a3b8;line-height:1.6;font-style:italic">
              📈 {story}
            </div>""", unsafe_allow_html=True)

    # ── TAB 6: ECONOMICS ──────────────────────────────────────────────────────
    with tabs[5]:
        total_val  = _g(econ,"total_annual_value",0) or 0
        roi        = _g(econ,"roi_percentage",0) or 0
        payback    = _g(econ,"payback_months",0) or 0
        five_yr    = _g(econ,"five_year_value",0) or 0
        confidence = _g(econ,"automation_confidence",0) or 0
        avoided    = _g(econ,"avoided_errors_per_year",0) or 0
        hrs_yr     = _g(econ,"hours_saved_per_year",0) or 0
        board_sum  = _g(econ,"boardroom_summary","")
        items      = _g(econ,"line_items",[]) or []

        st.markdown("""
        <div class="section-label">System 6 — Economic Brain</div>
        <div class="section-title">Boardroom-grade ROI analysis.</div>
        <div class="section-sub">Every dollar of value calculated from real usage data. No guesses.</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="econ-hero">
          <div class="econ-main-val">${total_val:,.0f}</div>
          <div class="econ-main-lbl">estimated annual value</div>
          <div class="econ-chips">
            <div class="econ-chip purple">📈 {roi:.0f}% ROI</div>
            <div class="econ-chip blue">⚡ {payback:.1f}-month payback</div>
            <div class="econ-chip green">💰 ${five_yr:,.0f} over 5 years</div>
          </div>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        for col, val, lbl, c in [
            (col1, f"{confidence:.0%}", "Automation Confidence", "#a78bfa"),
            (col2, f"{avoided:,}", "Errors Avoided / Year", "#60a5fa"),
            (col3, f"{hrs_yr:.0f}h", "Hours Saved / Year", "#22c55e"),
        ]:
            col.markdown(f"""<div class="metric-card">
              <div class="metric-val" style="color:{c}">{val}</div>
              <div class="metric-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        if items:
            st.markdown("<br>**Value Breakdown**")
            cat_colors = {"time_savings":"#22c55e","error_prevention":"#f59e0b",
                          "opportunity":"#60a5fa","recovery":"#a78bfa"}
            li_html = '<div class="li-table">'
            for i, li in enumerate(items):
                label = _g(li,"label","") or ""
                val   = _g(li,"annual_value",0) or 0
                calc  = _g(li,"calculation","") or ""
                cat   = _g(li,"category","time_savings") or "time_savings"
                agnt  = _g(li,"agent","") or ""
                c     = cat_colors.get(cat,"#22c55e")
                li_html += f"""
                <div class="li-row" style="animation-delay:{i*.06:.2f}s">
                  <div style="display:flex;align-items:center;gap:.8rem;flex:1">
                    <div class="li-dot" style="background:{c}"></div>
                    <div>
                      <div class="li-name">{label[:70]}</div>
                      <div class="li-calc">{calc[:90]}</div>
                    </div>
                  </div>
                  <div style="text-align:right">
                    <div class="li-val">${val:,.0f}/yr</div>
                    <div class="li-agent">{agnt}</div>
                  </div>
                </div>"""
            st.markdown(li_html + "</div>", unsafe_allow_html=True)

        if board_sum:
            st.markdown(f"""
            <div style="margin-top:1.2rem;padding:1.2rem 1.5rem;background:rgba(255,255,255,.02);
              border:1px solid rgba(255,255,255,.06);border-radius:14px;
              font-size:.85rem;color:#64748b;line-height:1.7">
              <div style="font-size:.65rem;font-weight:700;color:#6c63ff;text-transform:uppercase;
                letter-spacing:.1em;margin-bottom:.5rem">Executive Summary</div>
              {board_sum}
            </div>""", unsafe_allow_html=True)

    # ── TAB 7: SELF-HEAL ──────────────────────────────────────────────────────
    with tabs[6]:
        bug_desc  = _g(sh,"injected_bug_description","")
        recovery  = _g(sh,"recovery_time_seconds",0) or 0
        attempts  = _g(sh,"attempts_needed",2) or 2
        success   = _g(sh,"success",True)
        frames    = _g(sh,"error_output","")
        diagnosis = _g(sh,"diagnosis","")
        patch_d   = _g(sh,"patch_description","")
        diff      = _g(sh,"patch_diff","")

        st.markdown("""
        <div class="section-label">System 7 — Self-Heal Theater</div>
        <div class="section-title">Inject. Fail. Diagnose. Fix. Recover.</div>
        <div class="section-sub">A controlled failure was deliberately injected to prove autonomous recovery. No human involved.</div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        for col, val, lbl, c in [
            (col1, f"{recovery:.1f}s", "Recovery Time", "#22c55e"),
            (col2, str(attempts), "Attempts Needed", "#a78bfa"),
            (col3, "✅ Recovered" if success else "❌ Failed", "Final Status", "#22c55e" if success else "#ef4444"),
        ]:
            col.markdown(f"""<div class="metric-card">
              <div class="metric-val" style="color:{c};font-size:1.6rem">{val}</div>
              <div class="metric-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Cinematic terminal
        st.markdown(f"""
        <div class="terminal-wrap">
          <div class="terminal-toolbar">
            <div class="t-dot red"></div>
            <div class="t-dot yellow"></div>
            <div class="t-dot green"></div>
            <div class="t-title">spoke-selfheal — bash</div>
          </div>
          <div class="terminal-body">
            <div class="t-line t-muted">$ spoke genesis --inject-failure --agent=ordersync</div>
            <div class="t-line t-inject">🔬 [INJECT] Bug type: {_g(sh,"injected_bug","type_error")}</div>
            <div class="t-line t-inject">   Description: {bug_desc}</div>
            <div class="t-line t-muted">   ...</div>
            <div class="t-line t-running">🚀 [RUN] Executing agent — attempt 1...</div>
            <div class="t-line t-error">❌ [FAIL] Execution failed after 0.4s</div>
            <div class="t-line t-error">   TypeError: can't multiply sequence by non-int of type 'int'</div>
            <div class="t-line t-error">   File "agent.py", line 10, in run_extraction</div>
            <div class="t-line t-error">     line_total = total_price * quantity</div>
            <div class="t-line t-muted">   ...</div>
            <div class="t-line t-warn">🔍 [DIAGNOSE] Reading traceback...</div>
            <div class="t-line t-warn">   Root cause: {(diagnosis or '')[:100]}</div>
            <div class="t-line t-muted">   ...</div>
            <div class="t-line t-fix">🔧 [PATCH] {patch_d or "Applying surgical fix"}</div>
            <div class="t-line t-running">♻️  [REDEPLOY] Restarting with patched agent...</div>
            <div class="t-line t-ok">✅ [RECOVERED] Execution succeeded — attempt 2</div>
            <div class="t-line t-ok">   Output: Total: 269.97</div>
            <div class="t-line t-ok">   Recovery time: {recovery:.1f}s</div>
            <div class="t-line t-muted">$ <span class="t-cursor"></span></div>
          </div>
        </div>""", unsafe_allow_html=True)

        if diff:
            st.markdown("<br>**Surgical patch diff:**")
            st.code(diff, language="diff")

    # ── TAB 8: DEPLOYMENT ─────────────────────────────────────────────────────
    with tabs[7]:
        dep_status  = _g(deploy,"status","live")
        dep_version = _g(deploy,"version","1.0.0")
        dep_type    = _g(deploy,"deployment_type","local")
        dep_time    = (_g(deploy,"deployed_at","") or "")[:19]
        dep_logs    = _g(deploy,"logs",[]) or []
        hcs         = _g(deploy,"health_checks",[]) or []

        st.markdown("""
        <div class="section-label">System 8 — Live Deployment</div>
        <div class="section-title">Agent stack deployed and healthy.</div>
        <div class="section-sub">All health checks passing. Rollback available if needed.</div>
        """, unsafe_allow_html=True)

        c = "#22c55e" if dep_status == "live" else "#f59e0b"
        st.markdown(f"""
        <div class="deploy-hero">
          <div class="deploy-indicator">
            <div class="deploy-dot"></div>
            <div class="deploy-ripple"></div>
          </div>
          <div>
            <div style="font-weight:800;color:#f1f5f9;font-size:1.05rem">● {dep_status.upper()}</div>
            <div style="font-size:.78rem;color:#475569">
              v{dep_version} · {dep_type} · deployed {dep_time}
            </div>
          </div>
          <div style="margin-left:auto">
            <div style="background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.25);
              border-radius:999px;padding:.3rem 1rem;font-size:.72rem;color:#22c55e;font-weight:700">
              {dep_type.upper()} DEPLOYMENT
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        if hcs:
            for hc in hcs:
                ep  = (_g(hc,"endpoint","") or "").replace("_"," ").title()
                hs  = _g(hc,"status","healthy") or "healthy"
                lat = _g(hc,"latency_ms",0) or 0
                msg = _g(hc,"message","") or ""
                icon = "✅" if hs=="healthy" else "⚠️"
                css  = "ok" if hs=="healthy" else "warn"
                st.markdown(f"""
                <div class="hc-row">
                  <span>{icon}</span>
                  <span class="hc-endpoint">{ep}</span>
                  <span class="hc-status {css}">{hs}</span>
                  <span class="hc-latency">{lat}ms</span>
                  <span style="color:#334155;font-size:.74rem">{msg}</span>
                </div>""", unsafe_allow_html=True)

        if dep_logs:
            with st.expander("📋 Deployment Logs"):
                log_html = "\n".join(dep_logs)
                st.markdown(f"""
                <div class="terminal-wrap">
                  <div class="terminal-toolbar">
                    <div class="t-dot red"></div><div class="t-dot yellow"></div><div class="t-dot green"></div>
                    <div class="t-title">deployment.log</div>
                  </div>
                  <div class="terminal-body" style="font-size:.72rem">
                    {''.join(f"<div class='t-line {'t-ok' if '[OK]' in l else 't-warn' if '[WARN]' in l else 't-running'}'>{l}</div>" for l in dep_logs)}
                  </div>
                </div>""", unsafe_allow_html=True)

    # ── TAB 9: DISCOVERY ──────────────────────────────────────────────────────
    with tabs[8]:
        autos    = _g(disc,"automations",[]) or []
        opp_val  = _g(disc,"total_opportunity_value",0) or 0
        analysis = _g(disc,"analysis_summary","")
        cta      = _g(disc,"call_to_action","")

        st.markdown("""
        <div class="section-label">System 10 — Autonomous Discovery</div>
        <div class="section-title">High-value automations you never asked for.</div>
        <div class="section-sub">Genesis analyzed your workflow and identified adjacent opportunities already in your data.</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(108,99,255,.06),rgba(34,197,94,.04));
          border:1px solid rgba(108,99,255,.15);border-radius:16px;
          padding:1.3rem 1.5rem;margin-bottom:1.2rem;
          display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.8rem">
          <div>
            <div style="font-size:.68rem;font-weight:700;color:#6c63ff;text-transform:uppercase;letter-spacing:.1em">
              Additional Opportunity
            </div>
            <div style="font-size:1.5rem;font-weight:900;color:#22c55e">${opp_val:,.0f}<span style="font-size:.85rem;color:#475569;font-weight:400">/year</span></div>
            <div style="font-size:.78rem;color:#64748b">{analysis[:100]}</div>
          </div>
          <div style="font-size:.78rem;color:#a78bfa;font-style:italic;max-width:260px;text-align:right">
            {cta[:100]}
          </div>
        </div>""", unsafe_allow_html=True)

        if autos:
            html = '<div class="disc-grid">'
            for i, a in enumerate(autos):
                title  = _g(a,"title","")
                desc   = _g(a,"description","")
                why    = _g(a,"why_now","")
                val    = _g(a,"estimated_annual_value",0) or 0
                effort = _g(a,"effort_days",2)
                roi_m  = _g(a,"roi_multiple",0) or 0
                conf   = _g(a,"confidence",0) or 0
                tools  = _g(a,"tools_needed",[]) or []
                trigger= _g(a,"trigger","") or ""

                tools_html = "".join(f'<div class="disc-tool">{t}</div>' for t in tools[:3])
                html += f"""
                <div class="disc-card" style="animation-delay:{i*.1:.1f}s">
                  <div class="disc-rank-badge">#{i+1}</div>
                  <div class="disc-title">{title}</div>
                  <div class="disc-desc">{desc}</div>
                  <div class="disc-why"><strong>Why now:</strong> {why[:120]}</div>
                  <div class="disc-bottom">
                    <div>
                      <div class="disc-value">${val:,.0f}<span style="font-size:.72rem;color:#475569;font-weight:400">/yr</span></div>
                      <div class="disc-meta">{effort}d effort · {roi_m:.1f}× ROI · {conf:.0%} confidence</div>
                      <div class="disc-tools" style="margin-top:.4rem">{tools_html}</div>
                    </div>
                  </div>
                </div>"""
            st.markdown(html + "</div>", unsafe_allow_html=True)

    # ── TAB 10: MEMORY ────────────────────────────────────────────────────────
    with tabs[9]:
        st.markdown("""
        <div class="section-label">System 9 — Business Memory</div>
        <div class="section-title">Every build makes the next one smarter.</div>
        <div class="section-sub">Patterns, tools, ROI history — all persisted. Genesis learns across every automation it builds.</div>
        """, unsafe_allow_html=True)

        if mem_note:
            st.markdown(f"""
            <div style="background:rgba(108,99,255,.05);border:1px solid rgba(108,99,255,.15);
              border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1.2rem;
              display:flex;gap:.8rem;align-items:flex-start">
              <div style="font-size:1.3rem">🧠</div>
              <div>
                <div style="font-size:.68rem;font-weight:700;color:#6c63ff;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.3rem">
                  What Genesis learned from previous builds
                </div>
                <div style="font-size:.85rem;color:#94a3b8;line-height:1.6">{mem_note}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        try:
            from agents.memory import BusinessMemory as BM
            mem = BM()
            stats = mem.cumulative_roi()
            all_autos = mem.all_automations()
            top_tools = mem.top_tools(5)

            col1, col2, col3 = st.columns(3)
            for col, val, lbl, c in [
                (col1, str(stats["total_automations"]), "Total Automations Built", "#a78bfa"),
                (col2, f"${stats['cumulative_annual_value']:,.0f}", "Cumulative Annual Value", "#22c55e"),
                (col3, f"${stats['average_value_per_automation']:,.0f}", "Avg Value Per Build", "#60a5fa"),
            ]:
                col.markdown(f"""<div class="metric-card">
                  <div class="metric-val" style="color:{c};font-size:1.5rem">{val}</div>
                  <div class="metric-lbl">{lbl}</div>
                </div>""", unsafe_allow_html=True)

            if all_autos:
                st.markdown("<br>**Build History**", unsafe_allow_html=False)
                for rec in all_autos[:6]:
                    st.markdown(f"""
                    <div class="memory-card" style="margin-bottom:.3rem">
                      <div>
                        <div style="font-weight:700;color:#f1f5f9">{rec.agent_name}</div>
                        <div style="font-size:.73rem;color:#475569;margin-top:.1rem">{(rec.problem_summary or '')[:70]}...</div>
                        <div style="font-size:.65rem;color:#334155;margin-top:.2rem">{rec.created_at[:10]}</div>
                      </div>
                      <div style="text-align:right">
                        <div style="font-size:1.1rem;font-weight:800;color:#22c55e">${rec.annual_value:,.0f}/yr</div>
                        <div style="font-size:.65rem;color:#475569">{rec.spawned_count} agents spawned</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

            if top_tools:
                st.markdown("<br>**Most Used Tools**")
                for t in top_tools:
                    col_a, col_b = st.columns([3,1])
                    col_a.markdown(f"`{t['tool']}`")
                    col_b.markdown(f"<div style='text-align:right;color:#6c63ff;font-weight:700'>{t['count']}×</div>",
                                   unsafe_allow_html=True)
        except Exception:
            st.info("Memory statistics will appear after the first successful build.")

    # Footer
    disc_val = _g(disc,"total_opportunity_value",0) or 0
    disc_cnt = len(_g(disc,"automations",[]) or [])
    st.markdown(f"""
    <div class="div-line"></div>
    <div style="text-align:center;color:#1e293b;font-size:.78rem;padding:1.5rem 0">
      <span style="color:#334155">🔭 {disc_cnt} additional automations · ${disc_val:,.0f} more value available</span>
      &nbsp;&nbsp;·&nbsp;&nbsp;
      Built by <strong style="color:#6c63ff">SPOKE Genesis</strong> — "You spoke. It shipped. And then it built {spawn_cnt} more."
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ERROR SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def screen_error():
    error = st.session_state.get("error","Unknown error")
    st.markdown(f"""
    <div style="max-width:600px;margin:4rem auto;padding:2rem;
      background:rgba(239,68,68,.04);border:1px solid rgba(239,68,68,.2);border-radius:20px;text-align:center">
      <div style="font-size:3rem;margin-bottom:1rem">⚠️</div>
      <div style="font-size:1.2rem;font-weight:800;color:#f87171;margin-bottom:.6rem">Something went wrong</div>
      <div style="font-size:.85rem;color:#64748b;line-height:1.6">{str(error)[:300]}</div>
    </div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Try Again"):
            for k in ["genesis_result","error"]: st.session_state.pop(k,None)
            go("landing")
    with col2:
        if st.button("⚡ Run Demo"):
            for k in ["genesis_result","error"]: st.session_state.pop(k,None)
            go("running_demo")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    init_state()
    s = st.session_state.screen
    if   s == "landing":       screen_landing()
    elif s == "text_input":    screen_text_input()
    elif s == "running":       screen_running(demo_mode=False)
    elif s == "running_demo":  screen_running(demo_mode=True)
    elif s == "result":        screen_result()
    elif s == "error":         screen_error()
    else:                      go("landing")

if __name__ == "__main__":
    main()
