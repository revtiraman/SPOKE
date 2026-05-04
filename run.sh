#!/bin/bash
# SPOKE Genesis v2.0 — One-command startup
# Usage:
#   ./run.sh            → Classic Spoke UI (port 8501)
#   ./run.sh genesis    → SPOKE Genesis UI (port 8502)
#   ./run.sh full       → API + Classic UI
#   ./run.sh api        → API only (port 8000)

set -e

MODE=${1:-demo}

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

# Install deps
echo "  Installing dependencies..."
pip install -r requirements.txt -q 2>&1 | tail -5

# Create .env if missing
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ⚠️  Created .env from template — add HF_API_TOKEN for full pipeline"
fi

# Create dirs
mkdir -p logs storage/generated

if [ "$MODE" = "genesis" ]; then
    echo ""
    echo "  🚀 Launching SPOKE Genesis (10 AI systems)..."
    echo "  → Open http://localhost:8502"
    echo ""
    streamlit run frontend/genesis_app.py --server.port 8502 --server.headless false

elif [ "$MODE" = "full" ]; then
    echo ""
    echo "  Starting SPOKE Genesis API..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    echo "  → API:     http://localhost:8000"
    echo "  → Docs:    http://localhost:8000/docs"
    echo "  → Genesis: http://localhost:8000/api/v1/genesis/demo"
    echo ""
    echo "  Starting Genesis UI..."
    streamlit run frontend/genesis_app.py --server.port 8502

elif [ "$MODE" = "api" ]; then
    echo "  → API: http://localhost:8000"
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

else
    # Default: classic Spoke UI
    echo ""
    echo "  Starting Classic Spoke UI..."
    echo "  → Open http://localhost:8501"
    echo "  (Use ./run.sh genesis for SPOKE Genesis)"
    echo ""
    streamlit run frontend/app.py --server.port 8501 --server.headless false
fi
