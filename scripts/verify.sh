#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

REQUIRE_FORMAL=0

usage() {
  cat <<'EOF'
Usage: ./scripts/verify.sh [--require-formal]

  --require-formal  Fail if Lean, Coq/Rocq, or Tectonic are unavailable.
EOF
}

while (($#)); do
  case "$1" in
    --require-formal)
      REQUIRE_FORMAL=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown verify option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

on_error() {
  local status=$?
  local line=${BASH_LINENO[0]:-${LINENO}}
  echo "verify failed at line ${line}: ${BASH_COMMAND} (exit ${status})" >&2
}
trap on_error ERR

run_step() {
  echo "+ $*"
  "$@"
}

require_or_skip() {
  local tool=$1
  local label=$2

  if command -v "$tool" >/dev/null 2>&1; then
    return 0
  fi

  if (( REQUIRE_FORMAL )); then
    echo "$tool is required for --require-formal ($label)" >&2
    exit 1
  fi

  echo "$tool not found; skipping $label"
  return 1
}

assert_fresh_file() {
  local generated=$1
  local tracked=$2
  local refresh_hint=$3

  test -s "$generated"
  if ! cmp -s "$generated" "$tracked"; then
    echo "$tracked is stale; regenerate with: $refresh_hint" >&2
    exit 1
  fi
}

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
rm -f build/cdc_bridge_runtime
run_step cc -std=c99 -Wall -Wextra -pedantic -O2 \
  runtime/cdc_bridge_runtime.c \
  runtime/cdc_source.c \
  -o build/cdc_bridge_runtime
run_step build/cdc_bridge_runtime verify bridge64.cdc

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

run_step build/cdc_bridge_runtime run-jobs bridge64.cdc bridge_jobs.cdc
run_step build/cdc_bridge_runtime codebook 9
run_step build/cdc_bridge_runtime codebook 12
run_step build/cdc_bridge_runtime verify-codebook bridge512.cdc 9
run_step build/cdc_bridge_runtime verify-codebook bridge4096.cdc 12
echo "+ build/cdc_bridge_runtime emit-codebook 9 > build/bridge512.cdc"
build/cdc_bridge_runtime emit-codebook 9 > build/bridge512.cdc
echo "+ build/cdc_bridge_runtime emit-codebook 12 > build/bridge4096.cdc"
build/cdc_bridge_runtime emit-codebook 12 > build/bridge4096.cdc
assert_fresh_file \
  build/bridge512.cdc \
  bridge512.cdc \
  "build/cdc_bridge_runtime emit-codebook 9 > bridge512.cdc"
assert_fresh_file \
  build/bridge4096.cdc \
  bridge4096.cdc \
  "build/cdc_bridge_runtime emit-codebook 12 > bridge4096.cdc"
echo "+ build/cdc_bridge_runtime grid bridge64.cdc > build/bridge64-grid.txt"
build/cdc_bridge_runtime grid bridge64.cdc > build/bridge64-grid.txt
echo "+ build/cdc_bridge_runtime grid-svg bridge64.cdc > build/bridge64-grid.svg"
build/cdc_bridge_runtime grid-svg bridge64.cdc > build/bridge64-grid.svg
test -s build/bridge64-grid.txt
grep -q "class=\"bridge-cell\"" build/bridge64-grid.svg
grep -q "function selectCell" build/bridge64-grid.svg
assert_fresh_file \
  build/bridge64-grid.svg \
  assets/bridge64-grid.svg \
  "build/cdc_bridge_runtime grid-svg bridge64.cdc > assets/bridge64-grid.svg"

echo
echo "== Native reducer runtime =="
rm -f build/cdc_native_runtime
run_step cc -std=c99 -Wall -Wextra -pedantic -O2 \
  runtime/cdc_native_runtime.c \
  runtime/cdc_source.c \
  -o build/cdc_native_runtime \
  -lm
echo
echo "== Native WASM replay export surface =="
run_step cc -std=c99 -Wall -Wextra -pedantic -O2 -Wno-unused-function \
  -c runtime/cdc_wasm_exports.c \
  -o build/cdc_wasm_exports.o
run_step cc -std=c99 -Wall -Wextra -pedantic -O2 \
  -c runtime/cdc_source.c \
  -o build/cdc_source.o
if command -v emcc >/dev/null 2>&1; then
  run_step emcc -O2 runtime/cdc_wasm_exports.c runtime/cdc_source.c \
    -sEXPORTED_FUNCTIONS='["_cdc_wasm_replay_json"]' \
    -sEXPORTED_RUNTIME_METHODS='["ccall","cwrap"]' \
    -o build/cdc_wasm_replay.js
  test -s build/cdc_wasm_replay.js
  test -s build/cdc_wasm_replay.wasm
else
  echo "emcc not found; skipping live WASM link"
fi
native_reducer="$(build/cdc_native_runtime run native_reducer.cdc)"
echo "$native_reducer"
grep -q "flow=reducer-flow .*theta council.b=0.250000" <<<"$native_reducer" || {
  echo "native reducer flow check failed" >&2
  exit 1
}
grep -q "commit=reducer-commit .*trits=0+- .*balance=admissible .*status=accepted .*reason=none" <<<"$native_reducer" || {
  echo "native reducer commit check failed" >&2
  exit 1
}
grep -q "commit=reducer-hold .*trits=-+0 .*balance=violated .*status=held .*reason=balance-violation" <<<"$native_reducer" || {
  echo "native reducer held-commit check failed" >&2
  exit 1
}
grep -q "nest=reducer-nest .*parent-belief=0.666667 .*child-prior=0.666667" <<<"$native_reducer" || {
  echo "native reducer nest check failed" >&2
  exit 1
}
grep -q "native reducer ok steps=4 flow=1 commit=2 nest=1" <<<"$native_reducer" || {
  echo "native reducer summary check failed" >&2
  exit 1
}
native_compile="$(build/cdc_native_runtime compile native_reducer.cdc)"
echo "$native_compile"
grep -q "native compile ok jobs=1 ops=4" <<<"$native_compile" || {
  echo "native compile check failed" >&2
  exit 1
}
native_interpret="$(build/cdc_native_runtime interpret native_reducer.cdc)"
echo "$native_interpret"
grep -q "ir-interpreter source=native_reducer.cdc ops=4" <<<"$native_interpret" || {
  echo "native IR interpreter did not compile IR" >&2
  exit 1
}
grep -q "native interpret ok ops=4 flow=1 commit=2 nest=1" <<<"$native_interpret" || {
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
native_replay="$(build/cdc_native_runtime replay native_reducer.cdc native_surface.cdc framework_loop.cdc)"
echo "$native_replay"
echo "$native_replay" > build/demo-replay.json
assert_fresh_file \
  build/demo-replay.json \
  demo/replay.json \
  "build/cdc_native_runtime replay native_reducer.cdc native_surface.cdc framework_loop.cdc > demo/replay.json"

echo
echo "== Runtime replay demo contract =="
export NATIVE_REDUCER_OUTPUT="$native_reducer"
export NATIVE_SURFACE_OUTPUT="$native_surface"
export TRACE_PROJECTION_OUTPUT="$trace_projection"
export NATIVE_REPLAY_OUTPUT="$native_replay"
python3 - <<'PY'
import json
import os
import re
from pathlib import Path


def match(pattern: str, text: str, label: str) -> tuple[str, ...]:
    found = re.search(pattern, text)
    if not found:
        raise SystemExit(f"demo replay could not read {label}")
    return found.groups()


html = Path("demo/index.html").read_text(encoding="utf-8")
payload = re.search(
    r'<script type="application/json" id="replay-data">\s*(.*?)\s*</script>',
    html,
    re.S,
)
if not payload:
    raise SystemExit("demo replay data block missing")
replay = json.loads(payload.group(1))
native_replay = json.loads(os.environ["NATIVE_REPLAY_OUTPUT"])
if replay != native_replay:
    raise SystemExit("demo replay data does not match native replay JSON")

native = os.environ["NATIVE_REDUCER_OUTPUT"]
surface = os.environ["NATIVE_SURFACE_OUTPUT"]
projection = os.environ["TRACE_PROJECTION_OUTPUT"]

(theta_raw,) = match(r"theta council\.b=([0-9.]+)", native, "flow theta")
accepted = match(
    r"commit=reducer-commit .*trits=([^ ]+) .*balance=([^ ]+) .*status=([^ ]+) .*reason=([^\n]+)",
    native,
    "accepted commit",
)
held = match(
    r"commit=reducer-hold .*trits=([^ ]+) .*balance=([^ ]+) .*status=([^ ]+) .*reason=([^\n]+)",
    native,
    "held commit",
)
nest = match(
    r"nest=reducer-nest .*up=([0-9.]+) .*parent-belief=([0-9.]+) .*child-prior=([0-9.]+)",
    native,
    "nest transfer",
)
trace = match(r"trace=surface-trace .*trits=([^ ]+) .*events=([0-9]+)", surface, "surface trace")
surface_bridge = match(
    r"bridge=surface-bridge .*dyadic=([^ ]+) .*triadic=([^\n]+)",
    surface,
    "surface bridge",
)
projected_bridge = match(
    r"occupancy=([^ ]+) index=([^ ]+) triadic=([^ ]+)",
    projection,
    "projected bridge",
)

universal = replay.get("universal")
if not universal:
    raise SystemExit("demo replay is missing the universal operator block")
if universal["operator"] != "U720" or universal["status"] != "accepted":
    raise SystemExit("demo replay universal block is not an accepted U720 result")
if not (universal["recordCoordinate"] == universal["decisionCoordinate"] == universal["enactedCoordinate"]):
    raise SystemExit("demo replay universal coordinates do not agree")

checks = [
    (replay["flow"]["thetaCouncilBRaw"], theta_raw, "flow raw theta"),
    (replay["flow"]["thetaCouncilB"], str(float(theta_raw)), "flow display theta"),
    (tuple(replay["commit"][k] for k in ("trits", "balance", "status", "reason")), accepted, "accepted commit"),
    (tuple(replay["hold"][k] for k in ("trits", "balance", "status", "reason")), held, "held commit"),
    (tuple(replay["nest"][k] for k in ("up", "parentBelief", "childPrior")), nest, "nest values"),
    ((replay["trace"]["trits"], replay["trace"]["events"]), trace, "trace values"),
    ((replay["bridge"]["dyadic"], replay["bridge"]["triadic"]), surface_bridge, "surface bridge values"),
    ((replay["bridge"]["dyadic"], replay["bridge"]["index"], replay["bridge"]["triadic"]), projected_bridge, "projected bridge values"),
]
for got, want, label in checks:
    if got != want:
        raise SystemExit(f"demo replay mismatch for {label}: {got!r} != {want!r}")

print("runtime replay demo: ok")
PY
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
echo "== Native task frameworks =="
transition_run="$(build/cdc_native_runtime run framework_transition.cdc)"
echo "$transition_run"
grep -q "flow=transition-action .*theta fsm.s1=0.250000" <<<"$transition_run" || {
  echo "transition framework action check failed" >&2
  exit 1
}
grep -q "commit=transition-fire .*trits=+0- .*balance=admissible .*status=accepted .*reason=none" <<<"$transition_run" || {
  echo "transition framework fired-transition check failed" >&2
  exit 1
}
grep -q "commit=transition-blocked .*trits=-+0 .*balance=violated .*status=held .*reason=balance-violation" <<<"$transition_run" || {
  echo "transition framework blocked-transition check failed" >&2
  exit 1
}
grep -q "nest=transition-lift .*parent-belief=0.666667 .*child-prior=0.666667" <<<"$transition_run" || {
  echo "transition framework hierarchy check failed" >&2
  exit 1
}
transition_surface="$(build/cdc_native_runtime surface framework_transition.cdc)"
echo "$transition_surface"
grep -q "guard=transition-guard .*state=open" <<<"$transition_surface" || {
  echo "transition framework precondition check failed" >&2
  exit 1
}
grep -q "bridge=transition-bridge .*dyadic=101110 .*triadic=232" <<<"$transition_surface" || {
  echo "transition framework state-key check failed" >&2
  exit 1
}
grep -q "counter=transition-counter .*final=1" <<<"$transition_surface" || {
  echo "transition framework tally check failed" >&2
  exit 1
}
procedural_run="$(build/cdc_native_runtime run framework_procedural.cdc)"
echo "$procedural_run"
grep -q "commit=procedural-execute .*trits=0+- .*balance=admissible .*status=accepted .*reason=none" <<<"$procedural_run" || {
  echo "procedural framework step check failed" >&2
  exit 1
}
grep -q "commit=procedural-retry .*trits=-+0 .*balance=violated .*status=held .*reason=balance-violation" <<<"$procedural_run" || {
  echo "procedural framework retry check failed" >&2
  exit 1
}
grep -q "nest=procedural-consolidate .*parent-belief=0.666667 .*child-prior=0.666667" <<<"$procedural_run" || {
  echo "procedural framework consolidation check failed" >&2
  exit 1
}
procedural_compile="$(build/cdc_native_runtime compile framework_procedural.cdc)"
echo "$procedural_compile"
grep -q "native compile ok jobs=1 ops=4 source=framework_procedural.cdc" <<<"$procedural_compile" || {
  echo "procedural framework proceduralization check failed" >&2
  exit 1
}
procedural_interpret="$(build/cdc_native_runtime interpret framework_procedural.cdc)"
echo "$procedural_interpret"
grep -q "native interpret ok ops=4 flow=1 commit=2 nest=1 source=framework_procedural.cdc" <<<"$procedural_interpret" || {
  echo "procedural framework skilled-execution check failed" >&2
  exit 1
}
episodic_run="$(build/cdc_native_runtime run framework_episodic.cdc)"
echo "$episodic_run"
grep -q "commit=episodic-record .*trits=++0 .*balance=admissible .*status=accepted .*reason=none" <<<"$episodic_run" || {
  echo "episodic framework record check failed" >&2
  exit 1
}
grep -q "nest=episodic-consolidate .*parent-belief=0.666667 .*child-prior=0.666667" <<<"$episodic_run" || {
  echo "episodic framework consolidation check failed" >&2
  exit 1
}
episodic_surface="$(build/cdc_native_runtime surface framework_episodic.cdc)"
echo "$episodic_surface"
grep -q "trace=episodic-trace .*trits=++00-+ .*events=4" <<<"$episodic_surface" || {
  echo "episodic framework content check failed" >&2
  exit 1
}
grep -q "bridge=episodic-key .*dyadic=110011 .*triadic=303" <<<"$episodic_surface" || {
  echo "episodic framework key check failed" >&2
  exit 1
}
grep -q "counter=episodic-ordinal .*final=1" <<<"$episodic_surface" || {
  echo "episodic framework ordinal check failed" >&2
  exit 1
}

episodic_recall_by_content="$(build/cdc_bridge_runtime lookup-dyadic bridge64.cdc 110011)"
case "$episodic_recall_by_content" in
  *"index=51"*"triadic=303"*) echo "$episodic_recall_by_content" ;;
  *) echo "episodic recall by content failed: $episodic_recall_by_content" >&2; exit 1 ;;
esac
episodic_recall_by_key="$(build/cdc_bridge_runtime lookup-triadic bridge64.cdc 303)"
case "$episodic_recall_by_key" in
  *"index=51"*"dyadic=110011"*) echo "$episodic_recall_by_key" ;;
  *) echo "episodic recall by key failed: $episodic_recall_by_key" >&2; exit 1 ;;
esac
deliberative_council="$(build/cdc_native_runtime council framework_deliberative.cdc)"
echo "$deliberative_council"
grep -q "council=deliberative-council .*dyadic=111101 .*triadic=331 .*occupancy=5 .*quorum=4 .*decision=adopt" <<<"$deliberative_council" || {
  echo "deliberative framework quorum check failed" >&2
  exit 1
}
deliberative_enactment="$(build/cdc_native_runtime evolve framework_deliberative.cdc)"
echo "$deliberative_enactment"
grep -q "evolution=deliberative-enactment coordinate=111101" <<<"$deliberative_enactment" || {
  echo "deliberative framework enactment check failed" >&2
  exit 1
}
grep -q "^witness deliberative-decision-memory invariant=dyadic-triadic-closure coordinate=111101" build/enacted_decision.cdc || {
  echo "enacted decision output is missing the appended decision-memory witness" >&2
  exit 1
}

echo
echo "== Native task-loop composition =="
loop_run="$(build/cdc_native_runtime run framework_loop.cdc)"
echo "$loop_run"
grep -q "flow=loop-sense-1 .*theta agent.b=0.250000" <<<"$loop_run" || {
  echo "loop cycle-1 sense check failed" >&2
  exit 1
}
grep -q "nest=loop-integrate-1 .*parent-belief=0.666667" <<<"$loop_run" || {
  echo "loop cycle-1 integration check failed" >&2
  exit 1
}
grep -q "flow=loop-sense-2 .*theta agent.b=0.492228" <<<"$loop_run" || {
  echo "loop cycle-2 carried-state sense check failed" >&2
  exit 1
}
grep -q "nest=loop-integrate-2 .*parent-belief=1.333333 .*child-prior=1.333333" <<<"$loop_run" || {
  echo "loop cycle-2 cumulative integration check failed" >&2
  exit 1
}
grep -q "flow=loop-turn-half .*theta loop-cover.phase=6.283185" <<<"$loop_run" || {
  echo "loop half-turn cover check failed" >&2
  exit 1
}
grep -q "flow=loop-turn-full .*theta loop-cover.phase=12.566371" <<<"$loop_run" || {
  echo "loop full-turn cover check failed" >&2
  exit 1
}
grep -q "native reducer ok steps=8 flow=4 commit=2 nest=2 source=framework_loop.cdc" <<<"$loop_run" || {
  echo "loop two-cycle summary check failed" >&2
  exit 1
}
loop_interpret="$(build/cdc_native_runtime interpret framework_loop.cdc)"
grep -q "native interpret ok ops=8 flow=4 commit=2 nest=2 source=framework_loop.cdc" <<<"$loop_interpret" || {
  echo "loop skilled-execution check failed" >&2
  exit 1
}
loop_compile="$(build/cdc_native_runtime compile framework_loop.cdc)"
grep -q "native compile ok jobs=1 ops=8 source=framework_loop.cdc" <<<"$loop_compile" || {
  echo "loop proceduralization check failed" >&2
  exit 1
}
loop_surface="$(build/cdc_native_runtime surface framework_loop.cdc)"
echo "$loop_surface"
grep -q "bridge=loop-key .*dyadic=110101 .*triadic=311" <<<"$loop_surface" || {
  echo "loop key check failed" >&2
  exit 1
}
grep -q "counter=loop-cycle .*final=2" <<<"$loop_surface" || {
  echo "loop cycle-count check failed" >&2
  exit 1
}
loop_council="$(build/cdc_native_runtime council framework_loop.cdc)"
echo "$loop_council"
grep -q "council=loop-council .*dyadic=110101 .*triadic=311 .*occupancy=4 .*quorum=4 .*decision=adopt" <<<"$loop_council" || {
  echo "loop decision check failed" >&2
  exit 1
}
loop_enactment="$(build/cdc_native_runtime evolve framework_loop.cdc)"
echo "$loop_enactment"
grep -q "^witness loop-decision-memory invariant=dyadic-triadic-closure coordinate=110101" build/enacted_loop.cdc || {
  echo "enacted loop output is missing the appended decision-memory witness" >&2
  exit 1
}
loop_recall="$(build/cdc_bridge_runtime lookup-dyadic bridge64.cdc 110101)"
case "$loop_recall" in
  *"index=53"*"triadic=311"*) echo "$loop_recall" ;;
  *) echo "loop recorded-coordinate recall failed: $loop_recall" >&2; exit 1 ;;
esac

echo
echo "== Universal operator closure =="
universal_run="$(build/cdc_native_runtime universal framework_loop.cdc)"
echo "$universal_run"
grep -q "universal=loop-u720 .*holonomy=0.125000 .*half-projection=returned .*half-sheet=inverted .*full-projection=returned .*full-sheet=restored .*winding=2 .*record=110101 .*decision=110101 .*enacted=110101 .*status=accepted .*reason=none" <<<"$universal_run" || {
  echo "universal closure acceptance check failed" >&2
  exit 1
}
grep -q "universal-parity ops=8 ok" <<<"$universal_run" || {
  echo "universal interpreter parity check failed" >&2
  exit 1
}
grep -q "^witness loop-decision-memory invariant=universal-closure coordinate=110101 winding=2 sheet=restored holonomy=0.125000 status=accepted" build/enacted_loop.cdc || {
  echo "universal enactment is missing the appended universal-closure witness" >&2
  exit 1
}

sed -e '/^universal /s/full-step=loop-turn-full/full-step=loop-turn-half/' \
    -e '/^universal /s/expect-status=accepted expect-reason=none/expect-status=held expect-reason=full-sheet-mismatch/' \
    framework_loop.cdc > build/fixture_360_only.cdc
universal_360="$(build/cdc_native_runtime universal build/fixture_360_only.cdc)"
echo "$universal_360"
grep -q "universal=loop-u720 .*winding=1 .*status=held .*reason=full-sheet-mismatch" <<<"$universal_360" || {
  echo "universal 360-only fixture did not hold with full-sheet-mismatch" >&2
  exit 1
}

sed -e 's/^channel agent.a -> context.b id=loop-radiant/channel agent.a -> context.c id=loop-radiant/' \
    -e '/^universal /s/expect-status=accepted expect-reason=none/expect-status=held expect-reason=cone-not-reciprocal/' \
    framework_loop.cdc > build/fixture_nonreciprocal.cdc
universal_cone="$(build/cdc_native_runtime universal build/fixture_nonreciprocal.cdc)"
echo "$universal_cone"
grep -q "universal=loop-u720 .*status=held .*reason=cone-not-reciprocal" <<<"$universal_cone" || {
  echo "universal nonreciprocal fixture did not hold with cone-not-reciprocal" >&2
  exit 1
}

rm -f build/universal_mismatch_output.cdc
sed -e '/^council loop-council/s/members=agent,context/members=context,agent/' \
    -e '/^council loop-council/s/expect-dyadic=110101/expect-dyadic=101110/' \
    -e '/^council loop-council/s/expect-triadic=311/expect-triadic=232/' \
    -e '/^evolve loop-enact/s|output=build/enacted_loop.cdc|output=build/universal_mismatch_output.cdc|' \
    -e '/^universal /s/expect-status=accepted expect-reason=none/expect-status=held expect-reason=coordinate-mismatch/' \
    framework_loop.cdc > build/fixture_mismatch.cdc
universal_mismatch="$(build/cdc_native_runtime universal build/fixture_mismatch.cdc)"
echo "$universal_mismatch"
grep -q "universal=loop-u720 .*record=110101 .*decision=101110 .*status=held .*reason=coordinate-mismatch" <<<"$universal_mismatch" || {
  echo "universal mismatch fixture did not hold with coordinate-mismatch" >&2
  exit 1
}
if [ -e build/universal_mismatch_output.cdc ]; then
  echo "universal mismatch fixture must not create evolved output" >&2
  exit 1
fi

echo
echo "== Lean/Coq finite carrier and algebraic proofs =="
if require_or_skip lean "Lean finite carrier/algebra proof check"; then
  run_step lean formal/lean/CDCFinite.lean
  echo "lean finite carrier/algebra proof: ok"
fi

if require_or_skip coqc "Coq/Rocq finite carrier/algebra proof check"; then
  run_step coqc -q formal/coq/CDCFinite.v
  rm -f formal/coq/CDCFinite.vo formal/coq/CDCFinite.vos formal/coq/CDCFinite.vok formal/coq/CDCFinite.glob formal/coq/.CDCFinite.aux
  echo "coq finite carrier/algebra proof: ok"
fi

echo
echo "== Paper compile =="
if require_or_skip tectonic "paper compile"; then
  (cd paper/arxiv && run_step tectonic main.tex)
fi

echo
echo "All checks passed."
