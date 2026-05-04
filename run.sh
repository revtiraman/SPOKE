#!/bin/bash
# SPOKE Genesis v2.0 — One-command startup
# Usage:
#   ./run.sh          → API server (port 8000)
#   ./run.sh demo     → CLI demo in terminal

set -e

MODE=${1:-api}

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

if [ "$MODE" = "demo" ]; then
    echo ""
    echo "  Running CLI demo..."
    echo ""
    python demo_cli.py
else
    echo ""
    echo "  Starting SPOKE Genesis API..."
    echo "  → API:     http://localhost:8000"
    echo "  → Docs:    http://localhost:8000/docs"
    echo "  → Genesis: POST /api/v1/genesis/demo"
    echo ""
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
