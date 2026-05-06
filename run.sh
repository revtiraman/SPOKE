#!/bin/bash
# SPOKE Genesis v2.0 — One-command startup
# Usage:
#   ./run.sh web      → Production Web UI at http://localhost:8000  ← RECOMMENDED
#   ./run.sh genesis  → SPOKE Genesis Streamlit UI (port 8502)
#   ./run.sh api      → API only (port 8000, no browser UI)
#   ./run.sh demo     → CLI demo in terminal
#   ./run.sh          → defaults to web

set -e

MODE=${1:-web}

echo ""
echo "  ⚡  SPOKE Genesis — Autonomous Business Automation Intelligence"
echo "  Mode: ${MODE^^}"
echo ""

# Create virtualenv if needed
if [ ! -d ".venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "  Installing dependencies..."
pip install -r requirements.txt -q 2>&1 | tail -3

# Create .env if missing
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ⚠️  Created .env from template — add HF_API_TOKEN for full pipeline"
fi

mkdir -p logs storage/generated

if [ "$MODE" = "web" ]; then
    echo ""
    echo "  🚀 SPOKE Genesis — Production Web UI"
    echo "  → Open http://localhost:8000"
    echo ""
    # Only watch source dirs — excluding storage/ prevents auto-restart when
    # generated agent files are written to disk during a pipeline run.
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload \
      --reload-dir agents --reload-dir api --reload-dir core \
      --reload-dir llm --reload-dir frontend

elif [ "$MODE" = "genesis" ]; then
    echo ""
    echo "  🚀 Launching SPOKE Genesis Streamlit UI..."
    echo "  → Open http://localhost:8502"
    echo ""
    streamlit run frontend/genesis_app.py --server.port 8502 --server.headless false

elif [ "$MODE" = "demo" ]; then
    echo ""
    echo "  Running CLI demo..."
    echo ""
    python demo_cli.py

else
    # api mode
    echo ""
    echo "  Starting SPOKE Genesis API..."
    echo "  → API:  http://localhost:8000"
    echo "  → Docs: http://localhost:8000/docs"
    echo "  → Web UI: http://localhost:8000/"
    echo ""
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload \
      --reload-dir agents --reload-dir api --reload-dir core \
      --reload-dir llm --reload-dir frontend
fi
