#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== Minimal Python bootloader syntax =="
python3 -m py_compile cdc_boot.py

echo
echo "== Python host boundary =="
python3 - <<'PY'
from pathlib import Path

py = sorted(p.name for p in Path(".").glob("*.py"))
assert py == ["cdc_boot.py"], py
print("python host boundary: ok (cdc_boot.py only)")
PY

echo
echo "== Native .cdc contract and witness suite =="
python3 cdc_boot.py

echo
echo "== Paper compile =="
if command -v tectonic >/dev/null 2>&1; then
  (cd paper/arxiv && tectonic main.tex)
else
  echo "tectonic not found; skipping PDF compile"
fi

echo
echo "All checks passed."
