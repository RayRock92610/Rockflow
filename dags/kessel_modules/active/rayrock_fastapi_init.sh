#!/bin/bash
set -euo pipefail
HOME_VENV="$HOME/rayrock_fastapi_venv"
echo "🛠️ Creating $HOME_VENV + FastAPI stack..."
mkdir -p "$HOME"
rm -rf "$HOME_VENV"
python3 -m venv "$HOME_VENV"
source "$HOME_VENV/bin/activate"
pip install --upgrade pip setuptools wheel --no-cache-dir
pip install --no-binary=:all: "fastapi[standard]==0.104.1"
python -c "from fastapi._compat import get_compat_model_name_map; print('✅ ARM64 FastAPI ready')" | tee -a "$HOME/kessel_modules/kessel_flow.log"
pip freeze | grep -v '^#' > "$HOME/kessel_modules/fastapi_deps.txt"
echo "🌌 $HOME_VENV created + locked. Activate: source $HOME_VENV/bin/activate"
echo "$(date '+%Y-%m-%d %H:%M:%S') | Rayrock FastAPI venv deployed at $HOME_VENV" >> "$HOME/kessel_modules/kessel_flow.log"
