#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== Python syntax =="
python3 -m py_compile bidi_calculus.py cdc_boot.py cdc_semantics.py calculus_laws.py acceptance.py relation_witness.py trace_window_witness.py

echo
echo "== Law and metatheorem witnesses =="
python3 calculus_laws.py

echo
echo "== Native .cdc execution =="
python3 cdc_boot.py system.cdc laws.cdc

echo
echo "== Relational phase-channel witnesses =="
python3 relation_witness.py
python3 cdc_boot.py relations.cdc

echo
echo "== Ternary trace/window witnesses =="
python3 trace_window_witness.py

echo
echo "== Capability acceptance witnesses =="
python3 acceptance.py

echo
echo "== Deadband propagation smoke check =="
python3 - <<'PY'
from cdc_boot import CDC

c = CDC()
c.run("deadband 0.25\nfield F dt=0.02 gain=1.2\nend\n")
assert abs(c.fields["F"].bf.deadband - 0.25) < 1e-12

c = CDC()
c.run("deadband 0.25\nfield F dt=0.02 gain=1.2 deadband=0.4\nend\n")
assert abs(c.fields["F"].bf.deadband - 0.4) < 1e-12

print("deadband propagation: ok")
PY

echo
echo "== Line projection validation =="
python3 - <<'PY'
from cdc_boot import CDC

try:
    CDC().run("""
field bad open=yes
  module A theta 0 0 0 0 0 0
  module B theta 0 0 0 0 0 0
  channel A -> B lines=-1
end
""")
except SyntaxError:
    print("line projection validation: ok")
else:
    raise AssertionError("negative line index was accepted")
PY

echo
echo "== Semantic invariant registry =="
python3 - <<'PY'
from cdc_semantics import INVARIANTS, invariant_index

idx = invariant_index()
required = {
    "gate-abelian",
    "interfere-monoid",
    "rotation-linear",
    "corefold-morphism",
    "preservation",
    "soundness",
    "local-confluence",
    "flow-additivity",
    "normalforms",
}
assert required == set(idx), sorted(set(idx) ^ required)
assert len(INVARIANTS) == len(idx)
print(f"semantic invariant registry: {len(INVARIANTS)} invariants")
PY

echo
echo "== Paper compile =="
if command -v tectonic >/dev/null 2>&1; then
  (cd paper/arxiv && tectonic main.tex)
else
  echo "tectonic not found; skipping PDF compile"
fi

echo
echo "All checks passed."
