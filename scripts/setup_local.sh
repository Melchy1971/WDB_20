#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m venv "$ROOT_DIR/backend/.venv"
source "$ROOT_DIR/backend/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/backend/requirements.txt"

deactivate

cd "$ROOT_DIR/frontend"
npm install

echo "Local setup complete."
