#!/usr/bin/env bash
set -euo pipefail

echo "Start backend: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "Start frontend: cd frontend && npm run dev"
