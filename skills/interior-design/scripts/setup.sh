#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .cache/pip .cache/npm
export PIP_CACHE_DIR="$PWD/.cache/pip"
export npm_config_cache="$PWD/.cache/npm"
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.lock.txt
npm --prefix assets/viewer ci --ignore-scripts
if command -v blender >/dev/null 2>&1; then
  blender --version
else
  printf '%s\n' 'Blender not found: drawings work; install Blender 4.3+ for 3D and HD rendering.'
fi
printf '%s\n' 'From this skill directory: .venv/bin/python scripts/project.py build assets/example-project.json --out assets/viewer/public/generated --blender'
printf '%s\n' 'Then: npm --prefix assets/viewer run dev'
