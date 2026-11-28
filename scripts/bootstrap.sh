#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

python_bin=$(command -v "${PYTHON_BIN:-python3}")
"$python_bin" - <<'PY'
import platform
import sys

if (sys.implementation.name, sys.version_info[:2], sys.platform, platform.machine()) != (
    "cpython", (3, 12), "linux", "x86_64"
):
    raise SystemExit("Use CPython 3.12 on Linux x86-64. Set PYTHON_BIN if python3 selects a different version.")
PY

uv_version=0.9.15
uv_bin="$PWD/.cache/uv-bin/uv"
if [[ ! -x "$uv_bin" || $("$uv_bin" --version) != "uv $uv_version"* ]]; then
  mkdir -p "$(dirname "$uv_bin")"
  uv_tmp=$(mktemp -d "$PWD/.cache/uv-bin/install.XXXXXXXX")
  trap 'rm -rf -- "$uv_tmp"' EXIT
  uv_archive=uv-x86_64-unknown-linux-gnu.tar.gz
  uv_sha256=2053df0089327569cddd6afea920c2285b482d9b123f5db9f658273e96ab792c
  curl -fLSs --retry 3 "https://github.com/astral-sh/uv/releases/download/$uv_version/$uv_archive" -o "$uv_tmp/$uv_archive"
  printf '%s  %s\n' "$uv_sha256" "$uv_tmp/$uv_archive" | sha256sum --check
  tar -xzf "$uv_tmp/$uv_archive" -C "$uv_tmp" --strip-components=1 uv-x86_64-unknown-linux-gnu/uv
  mv "$uv_tmp/uv" "$uv_bin"
fi

export UV_CACHE_DIR="$PWD/.cache/uv"
"$uv_bin" venv --python "$python_bin" --allow-existing .venv
mkdir -p .cache/wheels
"$uv_bin" pip sync --python .venv/bin/python --require-hashes --only-binary :all: \
  --index-strategy unsafe-best-match --find-links "$PWD/.cache/wheels" requirements.txt
"$uv_bin" pip check --python .venv/bin/python
mkdir -p results/environment
"$uv_bin" pip freeze --python .venv/bin/python > results/environment/requirements.resolved.txt
.venv/bin/python scripts/doctor.py --strict
