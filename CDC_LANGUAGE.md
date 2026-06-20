# The `.cdc` Language
### Native source format for the Coherence-Delta Calculus

`.cdc` is the native language surface for the calculus kernel. In v0.2.4 the
checked surface includes native declarations, witnesses, and the first
source-declared reducer jobs: terms, reducer rules, field/module/cell/channel
state, flow/commit/nest jobs, guard/trace/measure/policy/bridge/counter jobs,
IR interpretation, council deliberation, bridge-coordinate source evolution,
native replay JSON, invariants, capabilities, witnesses, and expectations are expressed in `.cdc`;
Python is limited to the small `cdc_boot.py` loader/checker.

The semantic target remains the full calculus:

```text
flow(d)       continuous reduction
commit(m)     guarded balanced-ternary event reduction
nest(m,F)     nested bidirectional coherence-delta coupling
trace/window  derived observer projection
```

The bootloader does not implement those reductions. It verifies that the native
source tree declares them and that every claim has a native witness handle. The
non-Python runtime `runtime/cdc_native_runtime.c` consumes `native_reducer.cdc`,
`native_surface.cdc`, and `council_bridge.cdc`; executes the checked `flow`,
`commit`, `nest`, `guard`, `trace`, `measure`, `policy`, `bridge`, `counter`,
`interpret`, `council`, `evolve`, and `replay` jobs; and verifies their expectations.
Both C runtimes share `runtime/cdc_source.c` / `runtime/cdc_source.h` for
native `.cdc` line parsing, attribute extraction, typed attributes, and
primitive expectation assertions.
`runtime/cdc_wasm_exports.c` exposes the replay path through a compile-checked
C ABI for an eventual Emscripten build.

## Current Checked Grammar

```ebnf
program      = { directive } ;
directive    = kernel | term | rule | provides | bootloader
             | invariant | law | capability | witness
             | field | module | cell | channel | guard | counter
             | flow | commit | nest | trace | measure | policy | bridge
             | compile | interpret | proof | council | deliberate | evolve
             | expect | "end" ;

kernel       = "kernel" name { kwarg } ;
term         = "term" name { name } ;
rule         = "rule" name { name } ;
provides     = "provides" name { name } ;
bootloader   = "bootloader" name { name } ;

invariant    = "invariant" key { kwarg } ;
law          = "law" key { kwarg } ;
capability   = "capability" key { kwarg } ;
witness      = "witness" key { kwarg } ;

field        = "field" key { kwarg } ;
module       = "module" key { kwarg } ;
cell         = "cell" key { kwarg } ;
channel      = "channel" path "->" path { kwarg } ;
guard        = "guard" key { kwarg } ;
counter      = "counter" key { kwarg } ;
flow         = "flow" key { kwarg } ;
commit       = "commit" key { kwarg } ;
nest         = "nest" key { kwarg } ;
trace        = "trace" key { kwarg } ;
measure      = "measure" key { kwarg } ;
policy       = "policy" key { kwarg } ;
bridge       = "bridge" key { kwarg } ;
compile      = "compile" key { kwarg } ;
interpret    = "interpret" key { kwarg } ;
proof        = "proof" key { kwarg } ;
council      = "council" key { kwarg } ;
deliberate   = "deliberate" key { kwarg } ;
evolve       = "evolve" key { kwarg } ;

expect       = "expect" predicate ;
kwarg        = key "=" value ;
```

`#` begins a comment. Values may be quoted with shell-style quoting.

## Native Expectation Predicates

The minimal bootloader currently verifies:

```text
expect native substrate == cdc
expect host-debt <= 1
expect python-files == 1
expect bootloader minimal == true
expect terms >= N
expect rules >= N
expect invariants >= N
expect witnesses >= N
expect capabilities >= N
expect provides <capability...>
expect law <invariant-key>
expect capability <capability-key>
expect witness <witness-id>
expect reducer <witness-id>
expect guard <witness-id>
expect trace <witness-id>
expect measure <witness-id>
expect policy <witness-id>
expect bridge <witness-id>
expect counter <witness-id>
expect compile <witness-id>
expect interpret <witness-id>
expect proof <witness-id>
expect council <witness-id>
expect evolution <witness-id>
```

`expect law K` requires both an `invariant K` declaration and at least one native
`witness ... invariant=K`. `expect capability C` requires both a
`capability C` declaration and at least one native `witness ... capability=C`.
`expect reducer W` requires witness `W` to link to a declared native reducer
step through `witness ... reducer=<flow-or-commit-or-nest-id>`.
`expect guard W`, `expect trace W`, `expect measure W`, `expect policy W`,
`expect bridge W`, `expect counter W`, `expect compile W`, `expect interpret W`,
`expect proof W`, `expect council W`, and `expect evolution W` use the same
linkage pattern for source-declared full-surface, compile, IR interpretation,
finite-proof, council, and source-evolution jobs.

## Native Files

| file | content |
|---|---|
| `kernel.cdc` | language terms, reducer rules, provided capabilities, bootloader boundary, and global expectations |
| `laws.cdc` | invariant registry and 22 law/metatheorem witness declarations |
| `bridge64.cdc` | explicit 64-row `2^6 = 4^3` dyadic/triadic bootstrap codebook |
| `bridge_codebooks.cdc` | higher-arity bridge declarations for `n=9` and `n=12` |
| `bridge512.cdc` | full generated `n=9`, `2^9 = 8^3 = 512` bridge codebook rows |
| `bridge4096.cdc` | full generated `n=12`, `2^12 = 16^3 = 4096` bridge codebook rows |
| `bridge_jobs.cdc` | source-declared bridge-coordinate jobs consumed by the C runtime |
| `native_reducer.cdc` | source-declared field/module/cell/channel state plus reducer, compile, interpret, and finite-proof jobs consumed by the C native runtime |
| `native_surface.cdc` | source-declared guard, trace, measure, policy, bridge, and counter jobs consumed by the C native runtime |
| `council_bridge.cdc` | source-declared council deliberation and bridge-coordinate source-evolution jobs |
| `system.cdc` | 32 capability declarations and native witness handles |
| `relations.cdc` | angular, projected, cross-scale, detuning, and overlap relation witness handles |
| `trace_windows.cdc` | balanced-ternary trace/window, local-counter, coupled-observer, and recursive-policy witness handles |
| `cdc_boot.py` | minimal loader/checker; not the reducer or language semantics |
| `runtime/cdc_source.c` / `runtime/cdc_source.h` | shared native `.cdc` line parser, attribute reader, typed attribute accessors, and primitive expectation checks for C consumers |
| `runtime/cdc_bridge_runtime.c` | non-Python bridge consumer for lookup, trace projection, generated codebook verification, interactive grid/SVG output, and finite validation |
| `runtime/cdc_native_runtime.c` | non-Python reducer, full-surface, compile-IR, IR interpreter, finite-proof, council, source-evolution, and replay consumer for source-declared jobs |
| `runtime/cdc_wasm_exports.c` | compile-checked C ABI wrapper for the native replay JSON path |
| `formal/lean/CDCFinite.lean` | Lean mirror of the finite n=6 balanced-ternary carrier and algebraic law proofs |
| `formal/coq/CDCFinite.v` | Coq mirror of the finite n=6 balanced-ternary carrier and algebraic law proofs |

## Balanced Ternary Carrier

The committed discrete carrier is balanced ternary, not binary:

```text
-1  inward localization / contraction
 0  resting equilibrium / open crossing
+1  outward expansion / dissipation
```

The middle value is a real equilibrium/crossing state. It is not false, null, or
absence.

## Full Semantic Syntax Target

The following forms are now part of the checked reducer surface:

```text
field <name> dt=<real> gain=<real> deadband=<real>
module <name> field=<field> belief=<real> prior=<real>
cell <path> module=<module> theta=<real> amplitude=<real> omega=<real>
channel <path-a> -> <path-b> delay=<real> weight=<real> angle=<real> lines=<i,j>
guard <name> cell=<path> expect-state=<open|closed>
flow <name> field=<field> duration=<real>
commit <name> module=<module>
nest <name> parent=<module> child=<module>
counter <name> value=<int> increment=<int> decrement=<int>
trace <window> field=<field> expect-trits=<trits> expect-events=<int>
measure <name> observer=<module> target=<module> mode=<mode>
policy <name> window=<trace> sampling=<mode> commit=<mode> adapt=<mode>
bridge <name> trace=<trace> via=<codebook>
compile <name> source=<path> expect-ops=<int>
interpret <name> source=<path> expect-ops=<int>
proof <name> carrier=balanced-ternary arity=<int>
council <name> field=<field> members=<module-list> quorum=<int>
deliberate <name> council=<council>
evolve <name> source=<path> output=<path> coordinate=<dyadic> append-witness=<id>
```

Those forms must continue to grow as native reducer clauses in `.cdc`, not by
growing Python back into a runtime.
