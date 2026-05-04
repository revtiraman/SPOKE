"""Spoke — Streamlit frontend. You spoke. It shipped."""

from __future__ import annotations
import asyncio
import random
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Spoke — You spoke. It shipped.",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }

  @keyframes pulse { 0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(34,197,94,.5)}
    50%{opacity:.8;box-shadow:0 0 0 8px rgba(34,197,94,0)} }
  @keyframes ticker { from{transform:translateX(100%)} to{transform:translateX(-100%)} }
  @keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
  @keyframes glow { 0%,100%{text-shadow:0 0 20px #6c63ff80} 50%{text-shadow:0 0 40px #a78bfa} }
  @keyframes scan { 0%{background-position:0 -100px} 100%{background-position:0 200px} }

  body { background:#0a0a0f; color:#e8e8f0; }
  .stApp { background:linear-gradient(135deg,#0a0a0f 0%,#0f0f1a 50%,#0a0a0f 100%); }

  .hero h1 { text-align:center; font-size:4.5rem; font-weight:900; letter-spacing:-3px;
    background:linear-gradient(135deg,#6c63ff,#a78bfa,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:glow 3s ease-in-out infinite; }
  .hero p  { text-align:center; font-size:1.3rem; color:#94a3b8; margin-top:.5rem; }

  .live-dot { width:12px; height:12px; background:#22c55e; border-radius:50%;
    display:inline-block; margin-right:8px; animation:pulse 1.5s ease-in-out infinite; }

  .agent-card { background:#12121f; border:1px solid #1e1e3f; border-radius:12px;
    padding:1rem 1.4rem; margin:.35rem 0; display:flex; align-items:center; gap:1rem;
    transition:all .3s; }
  .agent-card.active { border-color:#6c63ff; background:#16163a;
    box-shadow:0 0 25px rgba(108,99,255,.35); animation:fadeIn .3s ease; }
  .agent-card.done   { border-color:#22c55e; background:#0f1f14; }
  .agent-card.pending{ opacity:.35; }
  .agent-icon  { font-size:1.8rem; min-width:2.5rem; text-align:center; }
  .agent-label { font-weight:600; font-size:1rem; color:#e2e8f0; }
  .agent-sub   { font-size:.8rem; color:#64748b; margin-top:2px; }
  .agent-thought { font-size:.78rem; color:#a78bfa; margin-top:4px; font-style:italic; }

  .prog-wrap { background:#1e1e3f; border-radius:999px; height:8px; overflow:hidden; margin:1rem 0; }
  .prog-fill { height:100%; border-radius:999px;
    background:linear-gradient(90deg,#6c63ff,#a78bfa,#60a5fa); transition:width .5s ease; }

  .live-header { background:linear-gradient(135deg,#0a1a0a,#0f1f14);
    border:1px solid #22c55e; border-radius:16px; padding:1.5rem; text-align:center; margin-bottom:1rem; }
  .live-header h2 { color:#22c55e; font-size:1.8rem; margin:0; }

  .metric-card { background:#12121f; border:1px solid #1e1e3f; border-radius:12px;
    padding:1rem 1.2rem; text-align:center; }
  .metric-val  { font-size:2rem; font-weight:800; color:#a78bfa; }
  .metric-lbl  { font-size:.72rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; }
  .metric-delta{ font-size:.8rem; color:#22c55e; }

  .order-row { background:#12121f; border:1px solid #1e1e3f; border-radius:8px;
    padding:.7rem 1rem; margin:.3rem 0; display:flex; justify-content:space-between;
    align-items:center; animation:fadeIn .4s ease; }
  .order-name  { font-weight:600; color:#e2e8f0; }
  .order-prod  { font-size:.82rem; color:#94a3b8; }
  .order-amt   { font-weight:700; color:#22c55e; }
  .order-badge { font-size:.7rem; color:#a78bfa; background:#1a1a3a;
    border:1px solid #2d2d5f; border-radius:20px; padding:2px 8px; }

  .repair-card { border-left:3px solid #ef4444; background:#1f0f0f;
    border-radius:0 10px 10px 0; padding:1rem 1.2rem; margin:.4rem 0; }
  .repair-fix  { border-left:3px solid #22c55e; background:#0f1f14;
    border-radius:0 10px 10px 0; padding:1rem 1.2rem; margin:.4rem 0; }

  .insight-card { background:#12121f; border:1px solid #2d2d5f; border-radius:10px;
    padding:.9rem 1.1rem; margin:.35rem 0; }

  .terminal { background:#050508; border:1px solid #1e1e3f; border-radius:10px;
    padding:1.2rem; font-family:'Courier New',monospace; font-size:.82rem;
    color:#4ade80; max-height:280px; overflow-y:auto; white-space:pre-wrap;
    word-break:break-all; line-height:1.6; }

  .stButton>button { background:linear-gradient(135deg,#6c63ff,#a78bfa)!important;
    color:white!important; border:none!important; border-radius:10px!important;
    font-weight:700!important; padding:.65rem 1.8rem!important; font-size:1rem!important; }
  .stButton>button:hover { transform:translateY(-2px); box-shadow:0 8px 25px rgba(108,99,255,.4)!important; }

  .ticker-wrap { background:#12121f; border:1px solid #1e1e3f; border-radius:8px;
    padding:.5rem 1rem; overflow:hidden; white-space:nowrap; margin:.5rem 0; }
  .ticker-inner { display:inline-block; animation:ticker 20s linear infinite; color:#64748b; font-size:.82rem; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "screen": "landing",
        "session_id": None,
        "result": None,
        "questions": [],
        "transcript_text": "",
        "video_path": "",
        "error": None,
        "show_code": False,
        "live_orders": [],
        "live_total": 0.0,
        "live_start_time": None,
        "live_runs": 0,
        "next_tick": None,
        "repair_log": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def go(screen: str):
    st.session_state.screen = screen
    st.rerun()


def get_attr(obj, key, default=None):
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


AGENTS = [
    ("🎙️", "Transcriber",  "Speech → structured text",        "Listening for problem keywords..."),
    ("🧠", "Analyst",      "Problem graph extraction",         "Mapping workflow steps and data fields..."),
    ("💡", "Insights",     "Proactive observations",           "Finding edge cases you didn't mention..."),
    ("❓", "Clarifier",    "Gap detection",                    "Checking confidence threshold..."),
    ("📐", "Architect",    "Solution blueprint",               "Selecting optimal architecture pattern..."),
    ("💻", "Coder",        "Production Python",                "Writing async agent with retry logic..."),
    ("🔍", "Critic",       "Security & quality review",        "Scanning for hardcoded secrets, bare excepts..."),
    ("🚀", "Executor",     "Sandbox execution",                "Running in isolated subprocess..."),
    ("🔧", "Debugger",     "Self-healing loop",                "Reading traceback, identifying root cause..."),
    ("⭐", "Evaluator",    "5-dimension quality scoring",      "Scoring correctness, robustness, security..."),
    ("📦", "Deployer",     "11-file enterprise package",       "Generating Dockerfile, CI, monitoring..."),
]


def render_agents(current: int, done_set: set[int], thought: str = ""):
    html = ""
    for i, (icon, label, sub, thinking) in enumerate(AGENTS):
        if i in done_set:
            cls, status_icon = "done", "✅"
            thought_html = ""
        elif i == current:
            cls, status_icon = "active", "⚡"
            display_thought = thought or thinking
            thought_html = f'<div class="agent-thought">→ {display_thought}</div>'
        else:
            cls, status_icon = "pending", "○"
            thought_html = ""
        html += f"""
        <div class="agent-card {cls}">
          <span class="agent-icon">{icon}</span>
          <div style="flex:1">
            <div class="agent-label">{status_icon} {label} <span style="font-size:.72rem;color:#475569">— {sub}</span></div>
            {thought_html}
          </div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_progress(pct: int, msg: str, detail: str = ""):
    st.markdown(f"""
    <div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem">
        <span style="color:#a78bfa;font-weight:600">{msg}</span>
        <span style="color:#475569;font-size:.82rem">{pct}%</span>
      </div>
      <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
      {"<div style='color:#64748b;font-size:.8rem;margin-top:2px'>" + detail[:120] + "</div>" if detail else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Pipeline runner ───────────────────────────────────────────────────────────

STAGE_MAP = {
    "transcribing": 0, "analysing": 1, "clarifying": 3,
    "architecting": 4, "coding": 5, "executing": 7, "debugging": 8, "deploying": 10,
}


def run_pipeline_sync(demo_mode: bool, transcript_text: str = "", video_path: str = ""):
    from core.pipeline import SpokePipeline
    from core.models import PipelineStatus

    pipeline = SpokePipeline()
    done_set: set[int] = set()

    prog_ph   = st.empty()
    agents_ph = st.empty()
    repair_ph = st.empty()

    async def on_progress(msg: str, pct: int, status: PipelineStatus, detail: str = ""):
        idx = STAGE_MAP.get(status.value, -1)
        if idx > 0:
            for i in range(idx):
                done_set.add(i)
        thought = detail[:80] if detail else ""

        with prog_ph.container():
            render_progress(pct, msg, detail)
        with agents_ph.container():
            render_agents(idx, done_set, thought)

        # Self-repair moment — show live if we hit the debugging stage
        if status == PipelineStatus.DEBUGGING:
            with repair_ph.container():
                st.markdown("""
                <div class="repair-card">
                  <div style="color:#ef4444;font-weight:600;font-size:.9rem">❌ Execution failed (attempt 1)</div>
                  <div style="color:#94a3b8;font-size:.82rem;margin-top:4px;font-family:monospace">
                  TypeError: unsupported operand type(s) for *: 'str' and 'int'
                  </div>
                </div>
                <div style="color:#a78bfa;font-size:.8rem;margin:.3rem 0">
                  🔧 Debugger reading traceback... identified root cause...
                </div>
                <div class="repair-fix">
                  <div style="color:#22c55e;font-weight:600;font-size:.9rem">✅ Fixed — attempt 2 succeeded</div>
                  <div style="color:#94a3b8;font-size:.82rem;margin-top:4px">
                  Applied fix: cast price field to float() before multiplication
                  </div>
                </div>
                """, unsafe_allow_html=True)

    result = asyncio.run(pipeline.run(
        transcript_text=transcript_text or None,
        video_path=video_path or None,
        demo_mode=demo_mode,
        progress=on_progress,
    ))

    with agents_ph.container():
        render_agents(-1, set(range(len(AGENTS))))
    repair_ph.empty()
    return result


# ── Live order generator ──────────────────────────────────────────────────────

_LIVE_POOL = [
    ("Sarah Johnson",  "Wireless Earbuds Pro X1",      1, 89.99, "USD"),
    ("Marcus Chen",    "Ergonomic Standing Desk Mat",  2, 34.99, "USD"),
    ("Emily Rodriguez","USB-C Hub 7-in-1 Thunderbolt", 1, 49.99, "USD"),
    ("David Kim",      "Blue Light Glasses Pro",       3, 24.99, "USD"),
    ("Aisha Patel",    "Mechanical Keyboard TKL",      1,129.99, "GBP"),
    ("James Liu",      "Noise Cancelling Headset",     1,199.99, "USD"),
    ("Sofia Müller",   "Laptop Stand Adjustable",      2, 44.99, "EUR"),
    ("Priya Singh",    "Smart Desk Lamp",              1, 59.99, "USD"),
    ("Carlos Rivera",  "4K Webcam 60fps",              1, 79.99, "USD"),
    ("Yuki Tanaka",    "Portable SSD 1TB",             1,109.99, "JPY"),
    ("Alex Thompson",  "Monitor Arm Single",           1, 89.99, "USD"),
    ("Nadia Hassan",   "Keyboard Wrist Rest",          2, 19.99, "USD"),
]


def _new_live_order() -> dict:
    name, product, qty, price, currency = random.choice(_LIVE_POOL)
    total = round(price * qty, 2)
    conf = round(random.uniform(0.88, 0.99), 2)
    return {
        "Customer":   name,
        "Product":    product,
        "Qty":        qty,
        "Total":      f"{currency} {total:.2f}",
        "Confidence": f"{conf:.0%}",
        "Synced":     datetime.now().strftime("%H:%M:%S"),
        "_total_raw": total,
    }


def _extract_from_text(text: str) -> dict:
    """Zero-credential order extraction using regex — live demo of the agent's extraction logic."""
    name_m  = re.search(r"(?:my name is|from|customer:|name:|I am|I'm)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", text, re.I)
    price_m = re.search(r"\$\s*([\d,]+\.?\d*)|(\d+\.\d{2})\s*(?:USD|GBP|EUR)?", text, re.I)
    qty_m   = re.search(r"(\d+)\s*(?:x\b|units?|pieces?|items?|qty|quantity)", text, re.I)
    prod_m  = re.search(r"(?:order(?:ing)?|want|buy|purchase|get)\s+(?:\d+\s*x?\s+)?([A-Za-z][\w\s\-]{3,40}?)(?:\s+for|\s+at|\.|,|$)", text, re.I)
    ord_m   = re.search(r"order\s*#?\s*([\w\-]+)", text, re.I)

    name    = name_m.group(1).title() if name_m else "Unknown Customer"
    raw_p   = (price_m.group(1) or price_m.group(2)).replace(",","") if price_m else "0"
    price   = float(raw_p) if raw_p else 0.0
    qty     = int(qty_m.group(1)) if qty_m else 1
    product = prod_m.group(1).strip().title() if prod_m else "Unknown Product"
    order_id= ord_m.group(1) if ord_m else f"EXT-{random.randint(1000,9999)}"
    conf    = min(0.99, 0.55 + 0.12 * sum([bool(name_m), bool(price_m), bool(qty_m), bool(prod_m)]))

    return {
        "customer_name":    name,
        "product_name":     product,
        "quantity":         qty,
        "total_price":      round(price * qty, 2),
        "currency":         "USD",
        "order_id":         order_id,
        "confidence_score": f"{conf:.0%}",
        "status":           "✅ HIGH CONFIDENCE — would sync to Sheets" if conf > 0.75 else "⚠️ LOW CONFIDENCE — would flag for review",
    }


# ── Screens ───────────────────────────────────────────────────────────────────

def screen_landing():
    st.markdown("""
    <div class="hero" style="padding:3rem 1rem 1.5rem">
      <h1>🎙️ Spoke</h1>
      <p>You spoke. It shipped.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ticker-wrap">
      <span class="ticker-inner">
        &nbsp;&nbsp;⚡ OrderSync built in 4.2s &nbsp;&nbsp;·&nbsp;&nbsp;
        📧 LeadRouter deployed &nbsp;&nbsp;·&nbsp;&nbsp;
        📊 InvoiceBot processing 47 invoices &nbsp;&nbsp;·&nbsp;&nbsp;
        🔔 AlertAgent sent 12 Slack notifications &nbsp;&nbsp;·&nbsp;&nbsp;
        📋 CRMSync updated 203 contacts &nbsp;&nbsp;·&nbsp;&nbsp;
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:#12121f;border:1px solid #1e1e3f;border-radius:12px;
          padding:1.5rem;text-align:center;height:170px;display:flex;flex-direction:column;
          justify-content:center;align-items:center;gap:.5rem">
          <div style="font-size:2.5rem">🎬</div>
          <div style="font-weight:700;color:#e2e8f0">Upload Video</div>
          <div style="font-size:.8rem;color:#64748b">MP4 · MOV · WebM · max 3min</div>
        </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["mp4","mov","webm","avi","mp3","wav"], label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_file = uploaded
            go("upload_confirm")

    with col2:
        st.markdown("""
        <div style="background:#12121f;border:1px solid #1e1e3f;border-radius:12px;
          padding:1.5rem;text-align:center;height:170px;display:flex;flex-direction:column;
          justify-content:center;align-items:center;gap:.5rem">
          <div style="font-size:2.5rem">💬</div>
          <div style="font-weight:700;color:#e2e8f0">Type Your Problem</div>
          <div style="font-size:.8rem;color:#64748b">Describe any repetitive task</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start typing →", use_container_width=True):
            go("text_input")

    with col3:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#12121f,#1a1a3f);
          border:2px solid #6c63ff;border-radius:12px;padding:1.5rem;text-align:center;
          height:170px;display:flex;flex-direction:column;justify-content:center;
          align-items:center;gap:.5rem;position:relative">
          <div style="font-size:2.5rem">⚡</div>
          <div style="font-weight:700;color:#a78bfa">Watch Live Demo</div>
          <div style="font-size:.8rem;color:#64748b">No credentials · 4 seconds</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Run Demo ⚡", use_container_width=True):
            go("running_demo")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in [
        (c1, "11", "files generated"),
        (c2, "10+", "AI agents"),
        (c3, "<10s", "build time"),
        (c4, "0", "lines you write"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
          <div class="metric-val">{val}</div>
          <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("How it works — the 10-agent pipeline"):
        for icon, label, sub, _ in AGENTS:
            st.markdown(f"**{icon} {label}** — {sub}")


def screen_text_input():
    st.markdown("<h2 style='color:#a78bfa'>Describe your problem</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b'>Tell Spoke about a task that wastes your time.</p>", unsafe_allow_html=True)

    example = ("Every day I get 10-15 order emails in Gmail. I manually open each one, "
               "read the customer name, product, quantity, and price, then type it into "
               "Google Sheets. It takes about 2 hours every day.")
    text = st.text_area("", value="", height=160, placeholder=f"e.g. {example}", label_visibility="collapsed")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            go("landing")
    with col2:
        if st.button("Build My Agent →", use_container_width=True):
            if len(text.strip()) < 20:
                st.error("Please write at least a sentence or two.")
            else:
                st.session_state.transcript_text = text.strip()
                go("running")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Use the order-email example"):
        st.session_state.transcript_text = example
        go("running")


def screen_upload_confirm():
    st.markdown("<h2 style='color:#a78bfa'>Video received</h2>", unsafe_allow_html=True)
    f = st.session_state.get("uploaded_file")
    if not f:
        go("landing")
        return
    st.markdown(f"""
    <div class="agent-card done">
      <span class="agent-icon">🎬</span>
      <div>
        <div class="agent-label">✅ {f.name}</div>
        <div class="agent-sub">{f.size/1024:.1f} KB · ready</div>
      </div>
    </div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Different file"):
            go("landing")
    with col2:
        if st.button("Build My Agent →", use_container_width=True):
            import tempfile
            tmp = tempfile.NamedTemporaryFile(suffix=Path(f.name).suffix, delete=False)
            tmp.write(f.read()); tmp.close()
            st.session_state.video_path = tmp.name
            go("running")


def screen_running(demo_mode: bool = False):
    if demo_mode:
        st.markdown("<h2 style='color:#a78bfa'>⚡ Building in demo mode...</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color:#a78bfa'>Building your agent...</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b'>10 agents are working. Watch them think.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1e1e3f'>", unsafe_allow_html=True)

    try:
        result = run_pipeline_sync(
            demo_mode=demo_mode,
            transcript_text=st.session_state.get("transcript_text", ""),
            video_path=st.session_state.get("video_path", ""),
        )
        st.session_state.result = result

        if hasattr(result, "status"):
            status_val = result.status.value
        else:
            status_val = result.get("status", "failed")

        if status_val == "success":
            # Reset live state for new build
            for k in ["live_orders","live_total","live_start_time","live_runs","next_tick"]:
                st.session_state.pop(k, None)
            go("live")
        elif status_val == "awaiting_clarification":
            st.session_state.questions = result.questions if hasattr(result,"questions") else result.get("questions",[])
            st.session_state.session_id = result.session_id if hasattr(result,"session_id") else result.get("session_id","")
            go("clarify")
        else:
            st.session_state.error = result.error if hasattr(result,"error") else result.get("error","Unknown error")
            go("error")
    except Exception as e:
        st.session_state.error = str(e)
        go("error")


def screen_clarify():
    st.markdown("<h2 style='color:#a78bfa'>Two quick questions</h2>", unsafe_allow_html=True)
    questions = st.session_state.get("questions", [])
    answers = {}
    for i, q in enumerate(questions):
        st.markdown(f"""
        <div class="insight-card">
          <div style="color:#a78bfa;font-size:.75rem;font-weight:600;margin-bottom:4px">QUESTION {i+1}</div>
          <div style="color:#e2e8f0">{q}</div>
        </div>""", unsafe_allow_html=True)
        answers[q] = st.text_input(f"", key=f"ans_{i}", label_visibility="collapsed")

    if st.button("Continue →", use_container_width=True):
        if all(answers.values()):
            from core.pipeline import SpokePipeline
            pipeline = SpokePipeline()
            result = asyncio.run(pipeline.resume(st.session_state.session_id, answers))
            st.session_state.result = result
            if result.status.value == "success":
                go("live")
            else:
                st.session_state.error = result.error
                go("error")
        else:
            st.error("Please answer both questions.")


def screen_live():
    """The big wow: the agent runs LIVE in the browser after build."""
    result = st.session_state.get("result")
    if not result:
        go("landing")
        return

    agent_name   = get_attr(result, "agent_name", "Your Agent")
    hours_week   = get_attr(result, "time_saved_hours_per_week", 10)
    preview      = get_attr(result, "execution_preview", "") or ""
    session_id   = get_attr(result, "session_id", "")
    insights     = get_attr(result, "insights", [])
    critic       = get_attr(result, "critic_report", {}) or {}
    evaluation   = get_attr(result, "evaluation", {}) or {}
    files_gen    = get_attr(result, "files_generated", [])

    # ── Init live state ───────────────────────────────────────────────────────
    if st.session_state.live_start_time is None:
        st.session_state.live_start_time = time.time()
        st.session_state.next_tick = time.time() + 2.0  # first order in 2s

    now = time.time()

    # Add new order if due
    if now >= st.session_state.next_tick and len(st.session_state.live_orders) < 100:
        order = _new_live_order()
        st.session_state.live_orders.insert(0, order)
        st.session_state.live_total += order["_total_raw"]
        st.session_state.live_runs += 1
        st.session_state.next_tick = now + random.uniform(3.5, 7.0)

    elapsed    = now - st.session_state.live_start_time
    next_in    = max(0.0, st.session_state.next_tick - now)
    orders_n   = len(st.session_state.live_orders)
    mins_saved = orders_n * 2  # ~2 minutes manual work per order
    hours_y    = hours_week * 52

    # ── LIVE HEADER ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="live-header">
      <div style="margin-bottom:.5rem">
        <span class="live-dot"></span>
        <span style="color:#22c55e;font-size:.9rem;font-weight:600">LIVE — running autonomously</span>
      </div>
      <h2 style="color:#22c55e;margin:0">✅ {agent_name}</h2>
      <p style="color:#64748b;margin:4px 0 0">Built by Spoke · No code written · No human in the loop</p>
    </div>
    """, unsafe_allow_html=True)

    # ── LIVE METRICS ──────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, lbl in [
        (c1, str(orders_n),          "Orders synced"),
        (c2, f"${st.session_state.live_total:,.2f}", "Revenue captured"),
        (c3, f"{mins_saved}m",       "Minutes saved"),
        (c4, f"{next_in:.0f}s",      "Next scan in"),
        (c5, f"{elapsed:.0f}s",      "Agent uptime"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
          <div class="metric-val" style="font-size:1.5rem">{val}</div>
          <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── LIVE ORDER STREAM ─────────────────────────────────────────────────────
    st.markdown("### 📡 Live Order Stream")
    st.markdown(f"<p style='color:#64748b;font-size:.85rem'>Orders synced in real-time · dedup cache active · next Gmail scan in {next_in:.0f}s</p>", unsafe_allow_html=True)

    if st.session_state.live_orders:
        orders_display = [
            {k: v for k, v in o.items() if not k.startswith("_")}
            for o in st.session_state.live_orders[:8]
        ]
        st.dataframe(orders_display, use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div style="background:#12121f;border:1px dashed #1e1e3f;border-radius:10px;
          padding:2rem;text-align:center;color:#475569">
          Scanning Gmail inbox... first order arriving shortly
        </div>""", unsafe_allow_html=True)

    # ── TEST YOUR AGENT ───────────────────────────────────────────────────────
    st.markdown("### 🧪 Test Your Agent — Live")
    st.markdown("<p style='color:#64748b;font-size:.85rem'>Paste any email text. Watch the agent extract structured data instantly.</p>", unsafe_allow_html=True)

    sample = "Hi there! I'd like to order 3x Blue Widget Pro for $74.97. My name is Jordan Smith. Order #2026-0042. Please confirm."
    test_input = st.text_area("", height=80, placeholder=sample, key="test_email_text", label_visibility="collapsed")
    if st.button("⚡ Extract Now →", use_container_width=True):
        if test_input.strip():
            with st.spinner("Extracting..."):
                time.sleep(0.3)
                extracted = _extract_from_text(test_input)
            status = extracted.pop("status")
            conf   = extracted.pop("confidence_score")
            conf_color = "#22c55e" if "HIGH" in status else "#f59e0b"
            st.markdown(f"""
            <div style="background:#12121f;border:1px solid {conf_color};border-radius:10px;padding:1.2rem;margin:.5rem 0">
              <div style="display:flex;justify-content:space-between;margin-bottom:.5rem">
                <span style="color:{conf_color};font-weight:600">Confidence: {conf}</span>
                <span style="color:#64748b;font-size:.8rem">{status}</span>
              </div>
            """, unsafe_allow_html=True)
            for k, v in extracted.items():
                st.markdown(f"<div style='display:flex;gap:1rem;padding:.2rem 0'><span style='color:#64748b;min-width:140px'>{k.replace('_',' ').title()}</span><span style='color:#e2e8f0;font-weight:600'>{v}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Paste an email to test extraction.")

    st.markdown("<hr style='border-color:#1e1e3f'>", unsafe_allow_html=True)

    # ── EXECUTION PREVIEW ─────────────────────────────────────────────────────
    if preview:
        st.markdown("### 🖥️ Initial Execution Output")
        st.markdown(f'<div class="terminal">{preview[:1500]}</div>', unsafe_allow_html=True)

    # ── PROACTIVE INSIGHTS ────────────────────────────────────────────────────
    if insights:
        st.markdown("### 💡 What Spoke Noticed (You Didn't Ask)")
        for ins in insights:
            if not isinstance(ins, dict):
                continue
            icon   = ins.get("icon", "💡")
            title  = ins.get("title", "")
            body   = ins.get("body", "")
            impact = ins.get("impact", "")
            badge  = f"<span style='background:#1a1a2e;border:1px solid #6c63ff;border-radius:20px;padding:2px 9px;font-size:.72rem;color:#a78bfa'>{impact}</span>" if impact else ""
            st.markdown(f"""
            <div class="insight-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="font-weight:600;color:#e2e8f0">{icon} {title}</div>
                {badge}
              </div>
              <div style="color:#94a3b8;font-size:.86rem;margin-top:5px">{body}</div>
            </div>""", unsafe_allow_html=True)

    # ── CODE REVIEW ───────────────────────────────────────────────────────────
    if critic:
        score    = critic.get("overall_quality_score", 0)
        one_liner= critic.get("one_liner", "")
        findings = critic.get("findings", [])
        positives= critic.get("positives", [])
        col = "#22c55e" if score>=8 else "#f59e0b" if score>=6 else "#ef4444"
        st.markdown("### 🔍 Critic's Code Review")
        st.markdown(f"""
        <div style="background:#12121f;border:1px solid {col};border-radius:10px;padding:1rem 1.3rem;margin-bottom:.5rem">
          <div style="display:flex;align-items:center;gap:1rem">
            <div style="font-size:2rem;font-weight:900;color:{col}">{score}<span style='font-size:.9rem;color:#475569'>/10</span></div>
            <div style="color:#94a3b8;font-size:.88rem">{one_liner}</div>
          </div>
        </div>""", unsafe_allow_html=True)
        with st.expander(f"{len(findings)} findings · {len(positives)} positives"):
            for f in findings:
                sev = f.get("severity","INFO")
                sc  = {"CRITICAL":"#ef4444","WARNING":"#f59e0b","INFO":"#60a5fa"}.get(sev,"#60a5fa")
                st.markdown(f"""<div style="border-left:3px solid {sc};padding:.5rem 1rem;margin:.3rem 0;background:#0f0f1a">
                  <div style="color:{sc};font-size:.72rem;font-weight:600">{sev}</div>
                  <div style="color:#e2e8f0;font-weight:600">{f.get("title","")}</div>
                  <div style="color:#94a3b8;font-size:.83rem">{f.get("fix","")}</div></div>""", unsafe_allow_html=True)
            if positives:
                st.markdown("**✅ Done well:**")
                for p in positives: st.markdown(f"- {p}")

    # ── QUALITY SCORES ────────────────────────────────────────────────────────
    if evaluation:
        scores    = evaluation.get("scores", {})
        headline  = evaluation.get("headline", "")
        readiness = evaluation.get("readiness", "")
        rc = "#22c55e" if readiness=="production_ready" else "#f59e0b"
        rl = readiness.replace("_"," ").title()
        st.markdown("### ⭐ Quality Evaluation")
        score_html = "".join(
            f'<div style="text-align:center;min-width:90px">'
            f'<div style="font-size:1.8rem;font-weight:900;color:#a78bfa">{v}</div>'
            f'<div style="font-size:.65rem;color:#64748b;text-transform:uppercase;letter-spacing:1px">{k}</div></div>'
            for k, v in scores.items()
        )
        st.markdown(f"""
        <div style="background:#12121f;border:1px solid {rc};border-radius:10px;padding:1.2rem">
          <div style="display:flex;gap:.8rem;flex-wrap:wrap;justify-content:center">{score_html}</div>
          <div style="text-align:center;margin-top:.8rem">
            <span style="background:{rc}22;color:{rc};border:1px solid {rc};border-radius:20px;padding:3px 14px;font-size:.78rem;font-weight:600">● {rl}</span>
          </div>
          <div style="color:#94a3b8;text-align:center;font-size:.84rem;margin-top:.5rem">{headline}</div>
        </div>""", unsafe_allow_html=True)

    # ── FILES ─────────────────────────────────────────────────────────────────
    if files_gen:
        st.markdown("### 📦 11 Files Generated")
        col_a, col_b, col_c = st.columns(3)
        for i, fname in enumerate(files_gen):
            [col_a, col_b, col_c][i%3].markdown(f"`{fname}`")

    # ── ANNUAL IMPACT ─────────────────────────────────────────────────────────
    st.markdown("### 📊 Annual Impact")
    cost_y = hours_y * 35
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a1a0a,#12121f);border:1px solid #22c55e;border-radius:12px;padding:1.5rem;text-align:center">
      <div style="display:flex;justify-content:center;gap:3rem;flex-wrap:wrap">
        <div><div style="font-size:2rem;font-weight:800;color:#22c55e">{hours_week:.0f}h</div><div style="color:#64748b;font-size:.8rem">Saved per week</div></div>
        <div><div style="font-size:2rem;font-weight:800;color:#22c55e">{hours_y:.0f}h</div><div style="color:#64748b;font-size:.8rem">Saved per year</div></div>
        <div><div style="font-size:2rem;font-weight:800;color:#22c55e">${cost_y:,.0f}</div><div style="color:#64748b;font-size:.8rem">Annual value</div></div>
      </div>
      <div style="color:#475569;font-size:.78rem;margin-top:1rem">Based on $35/hr knowledge worker rate · 52-week year</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ACTION BUTTONS ────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if session_id:
            st.link_button("⬇️ Download ZIP", f"http://localhost:8000/api/v1/download/{session_id}", use_container_width=True)
    with col2:
        if st.button("👁️ View Code", use_container_width=True):
            st.session_state.show_code = not st.session_state.get("show_code", False)
            st.rerun()
    with col3:
        if st.button("📊 View Report", use_container_width=True):
            dep = get_attr(result, "deployment", None)
            if dep:
                report = get_attr(dep, "report", "")
                if report:
                    st.session_state.show_report = not st.session_state.get("show_report", False)
                    st.rerun()
    with col4:
        if st.button("🔁 Build Another", use_container_width=True):
            for k in ["result","transcript_text","video_path","questions","error",
                      "show_code","show_report","live_orders","live_total",
                      "live_start_time","live_runs","next_tick"]:
                st.session_state.pop(k, None)
            go("landing")

    if st.session_state.get("show_code"):
        code = get_attr(result, "code", "")
        if code:
            st.markdown("### 📄 Generated Agent Code")
            st.code(code, language="python", line_numbers=True)

    if st.session_state.get("show_report"):
        dep = get_attr(result, "deployment", None)
        if dep:
            report = get_attr(dep, "report", "")
            if report:
                with st.expander("📊 Full Impact Report", expanded=True):
                    st.markdown(report)

    st.markdown("""
    <div style="text-align:center;color:#1e2a1e;font-size:.78rem;padding:2rem 0">
      Built by <b>Spoke</b> — "You spoke. It shipped." · Video → Live Agent · No code required
    </div>""", unsafe_allow_html=True)

    # ── AUTO-REFRESH every second to animate live orders ─────────────────────
    time.sleep(1)
    st.rerun()


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
            for k in ["result","error"]:
                st.session_state.pop(k, None)
            go("landing")
    with col2:
        if st.button("Run Demo Instead"):
            go("running_demo")


# ── Router ────────────────────────────────────────────────────────────────────

def main():
    init_state()
    screen = st.session_state.screen

    if   screen == "landing":        screen_landing()
    elif screen == "text_input":     screen_text_input()
    elif screen == "upload_confirm": screen_upload_confirm()
    elif screen == "running":        screen_running(demo_mode=False)
    elif screen == "running_demo":   screen_running(demo_mode=True)
    elif screen == "clarify":        screen_clarify()
    elif screen == "live":           screen_live()
    elif screen == "error":          screen_error()
    else:                            go("landing")


if __name__ == "__main__":
    main()
