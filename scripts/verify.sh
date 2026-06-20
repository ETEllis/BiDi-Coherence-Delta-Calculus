#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p build

echo "== Minimal Python bootloader syntax =="
python3 - <<'PY'
import py_compile

py_compile.compile("cdc_boot.py", cfile="build/cdc_boot.pyc", doraise=True)
PY

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
echo "== Operational bridge runtime =="
command -v cc >/dev/null 2>&1 || {
  echo "cc is required for operational bridge verification" >&2
  exit 1
}
cc -std=c99 -Wall -Wextra -pedantic -O2 \
  runtime/cdc_bridge_runtime.c \
  -o build/cdc_bridge_runtime
build/cdc_bridge_runtime verify bridge64.cdc

dyadic_lookup="$(build/cdc_bridge_runtime lookup-dyadic bridge64.cdc 101011)"
case "$dyadic_lookup" in
  *"index=43"*"triadic=223"*) echo "$dyadic_lookup" ;;
  *) echo "unexpected dyadic lookup: $dyadic_lookup" >&2; exit 1 ;;
esac

triadic_lookup="$(build/cdc_bridge_runtime lookup-triadic bridge64.cdc 223)"
case "$triadic_lookup" in
  *"index=43"*"dyadic=101011"*) echo "$triadic_lookup" ;;
  *) echo "unexpected triadic lookup: $triadic_lookup" >&2; exit 1 ;;
esac

trace_projection="$(build/cdc_bridge_runtime project-trits bridge64.cdc '+0-+0-' council)"
case "$trace_projection" in
  *"occupancy=101101"*"index=45"*"triadic=231"*) echo "$trace_projection" ;;
  *) echo "unexpected trace projection: $trace_projection" >&2; exit 1 ;;
esac

build/cdc_bridge_runtime run-jobs bridge64.cdc bridge_jobs.cdc
build/cdc_bridge_runtime codebook 9
build/cdc_bridge_runtime codebook 12
build/cdc_bridge_runtime verify-codebook bridge512.cdc 9
build/cdc_bridge_runtime verify-codebook bridge4096.cdc 12
build/cdc_bridge_runtime emit-codebook 9 > build/bridge512.cdc
build/cdc_bridge_runtime emit-codebook 12 > build/bridge4096.cdc
cmp -s build/bridge512.cdc bridge512.cdc || {
  echo "bridge512.cdc is stale; regenerate with: build/cdc_bridge_runtime emit-codebook 9 > bridge512.cdc" >&2
  exit 1
}
cmp -s build/bridge4096.cdc bridge4096.cdc || {
  echo "bridge4096.cdc is stale; regenerate with: build/cdc_bridge_runtime emit-codebook 12 > bridge4096.cdc" >&2
  exit 1
}
build/cdc_bridge_runtime grid bridge64.cdc > build/bridge64-grid.txt
build/cdc_bridge_runtime grid-svg bridge64.cdc > build/bridge64-grid.svg
test -s build/bridge64-grid.txt
test -s build/bridge64-grid.svg
grep -q "class=\"bridge-cell\"" build/bridge64-grid.svg
grep -q "function selectCell" build/bridge64-grid.svg
cmp -s build/bridge64-grid.svg assets/bridge64-grid.svg || {
  echo "assets/bridge64-grid.svg is stale; regenerate with: build/cdc_bridge_runtime grid-svg bridge64.cdc > assets/bridge64-grid.svg" >&2
  exit 1
}

echo
echo "== Native reducer runtime =="
cc -std=c99 -Wall -Wextra -pedantic -O2 \
  runtime/cdc_native_runtime.c \
  -o build/cdc_native_runtime \
  -lm
native_reducer="$(build/cdc_native_runtime run native_reducer.cdc)"
echo "$native_reducer"
grep -q "flow=reducer-flow .*theta council.b=0.250000" <<<"$native_reducer" || {
  echo "native reducer flow check failed" >&2
  exit 1
}
grep -q "commit=reducer-commit .*trits=0+- .*balance=admissible" <<<"$native_reducer" || {
  echo "native reducer commit check failed" >&2
  exit 1
}
grep -q "nest=reducer-nest .*parent-belief=0.666667 .*child-prior=0.666667" <<<"$native_reducer" || {
  echo "native reducer nest check failed" >&2
  exit 1
}
grep -q "native reducer ok steps=3 flow=1 commit=1 nest=1" <<<"$native_reducer" || {
  echo "native reducer summary check failed" >&2
  exit 1
}
native_compile="$(build/cdc_native_runtime compile native_reducer.cdc)"
echo "$native_compile"
grep -q "native compile ok jobs=1 ops=3" <<<"$native_compile" || {
  echo "native compile check failed" >&2
  exit 1
}
native_interpret="$(build/cdc_native_runtime interpret native_reducer.cdc)"
echo "$native_interpret"
grep -q "ir-interpreter source=native_reducer.cdc ops=3" <<<"$native_interpret" || {
  echo "native IR interpreter did not compile IR" >&2
  exit 1
}
grep -q "native interpret ok ops=3 flow=1 commit=1 nest=1" <<<"$native_interpret" || {
  echo "native IR interpreter check failed" >&2
  exit 1
}
native_proof="$(build/cdc_native_runtime prove native_reducer.cdc)"
echo "$native_proof"
grep -q "proof=trit-walk-n6 .*total=729 .*admissible=267 .*localized=51 .*saturated=20 .*catalan=5" <<<"$native_proof" || {
  echo "native proof finite trit-walk check failed" >&2
  exit 1
}
grep -q "native proof ok jobs=1" <<<"$native_proof" || {
  echo "native proof summary check failed" >&2
  exit 1
}
native_surface="$(build/cdc_native_runtime surface native_surface.cdc)"
echo "$native_surface"
grep -q "guard=surface-guard .*state=open" <<<"$native_surface" || {
  echo "native surface guard check failed" >&2
  exit 1
}
grep -q "trace=surface-trace .*trits=+0-+0- .*events=4" <<<"$native_surface" || {
  echo "native surface trace check failed" >&2
  exit 1
}
grep -q "measure=surface-measure .*outcome=+0- .*potential=nonincrease" <<<"$native_surface" || {
  echo "native surface measurement check failed" >&2
  exit 1
}
grep -q "policy=surface-policy .*sampling=local .*commit=guarded .*adapt=recursive" <<<"$native_surface" || {
  echo "native surface policy check failed" >&2
  exit 1
}
grep -q "bridge=surface-bridge .*dyadic=101101 .*triadic=231" <<<"$native_surface" || {
  echo "native surface bridge check failed" >&2
  exit 1
}
grep -q "counter=surface-counter .*final=4" <<<"$native_surface" || {
  echo "native surface counter check failed" >&2
  exit 1
}
grep -q "native surface ok guards=1 traces=1 measures=1 policies=1 bridges=1 counters=1" <<<"$native_surface" || {
  echo "native surface summary check failed" >&2
  exit 1
}
council_output="$(build/cdc_native_runtime council council_bridge.cdc)"
echo "$council_output"
grep -q "council=bridge-council .*dyadic=101101 .*triadic=231 .*decision=adopt" <<<"$council_output" || {
  echo "native council deliberation check failed" >&2
  exit 1
}
grep -q "native council ok deliberations=1" <<<"$council_output" || {
  echo "native council summary check failed" >&2
  exit 1
}
self_evolution="$(build/cdc_native_runtime evolve council_bridge.cdc)"
echo "$self_evolution"
grep -q "evolution=bridge-coordinate-evolution coordinate=101101" <<<"$self_evolution" || {
  echo "native self-evolution check failed" >&2
  exit 1
}
grep -q "native evolution ok jobs=1" <<<"$self_evolution" || {
  echo "native self-evolution summary check failed" >&2
  exit 1
}
grep -q "self-evolution-bridge" build/evolved_native_reducer.cdc || {
  echo "evolved .cdc output is missing the bridge-written witness" >&2
  exit 1
}

echo
echo "== Lean/Coq finite carrier and algebraic proofs =="
if command -v lean >/dev/null 2>&1; then
  lean formal/lean/CDCFinite.lean
  echo "lean finite carrier/algebra proof: ok"
else
  echo "lean not found; skipping Lean finite carrier/algebra proof check"
fi

if command -v coqc >/dev/null 2>&1; then
  coqc -q formal/coq/CDCFinite.v
  rm -f formal/coq/CDCFinite.vo formal/coq/CDCFinite.vos formal/coq/CDCFinite.vok formal/coq/CDCFinite.glob formal/coq/.CDCFinite.aux
  echo "coq finite carrier/algebra proof: ok"
else
  echo "coqc not found; skipping Coq finite carrier/algebra proof check"
fi

echo
echo "== Paper compile =="
if command -v tectonic >/dev/null 2>&1; then
  (cd paper/arxiv && tectonic main.tex)
else
  echo "tectonic not found; skipping PDF compile"
fi

echo
echo "All checks passed."
