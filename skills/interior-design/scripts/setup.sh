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
  printf '%s\n' 'Blender is optional: use your agent image tool for presentation; native geometry extraction requires Blender.'
fi
printf '%s\n' 'Try the complete sample: .venv/bin/python scripts/interior_design.py demo --out /path/to/project/review'
printf '%s\n' 'Replace /path/to/project/review with a project directory outside this installed skill.'
printf '%s\n' 'The review opens in your browser. Add --no-serve to only package files.'
