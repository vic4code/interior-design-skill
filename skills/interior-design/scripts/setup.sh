#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .cache/pip .cache/npm
export PIP_CACHE_DIR="$PWD/.cache/pip"
export npm_config_cache="$PWD/.cache/npm"
if [ ! -x .venv/bin/python ]; then
  python_bin="${INTERIOR_PYTHON:-python3}"
  if ! "$python_bin" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
    python_bin=''
    for candidate in python3.13 python3.12 python3.11; do
      if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
        python_bin="$candidate"
        break
      fi
    done
    if [ -z "$python_bin" ]; then
      printf '%s\n' 'Python 3.11+ is required; set INTERIOR_PYTHON to its executable.' >&2
      exit 1
    fi
  fi
  "$python_bin" -m venv .venv
fi
if .venv/bin/python - <<'PY'
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
import sys
try:
    ready = all(version(name) == wanted for name, wanted in
                (line.split('==') for line in Path('scripts/requirements.lock.txt').read_text().splitlines()
                 if line and not line.startswith('#')))
except PackageNotFoundError:
    ready = False
sys.exit(0 if ready else 1)
PY
then
  printf '%s\n' 'Drawing dependencies already match the lock file; skipping downloads.'
elif command -v uv >/dev/null 2>&1; then
  UV_HTTP_TIMEOUT=20 UV_HTTP_RETRIES=1 uv pip install --python .venv/bin/python -r scripts/requirements.lock.txt
else
  .venv/bin/python -m pip install --disable-pip-version-check --timeout 20 --retries 1 -r scripts/requirements.lock.txt
fi
# The shipped viewer opens without npm; source changes are built on first use.
if command -v blender >/dev/null 2>&1; then
  blender --version
else
  printf '%s\n' 'Blender is optional: use your agent image tool for presentation; native geometry extraction requires Blender.'
fi
printf '%s\n' 'Try the complete sample: .venv/bin/python scripts/interior_design.py demo --out /path/to/project/review'
printf '%s\n' 'Replace /path/to/project/review with a project directory outside this installed skill.'
printf '%s\n' 'The review opens in your browser. Add --no-serve to only package files.'
