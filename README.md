# BiDi Coherence-Delta Calculus

<p align="center">
  <img src="assets/bidi-cdc-icon.svg" alt="BiDi Coherence-Delta Calculus logo" width="140">
</p>

<p align="center">
  <strong>A native language with a formal coherence-calculus kernel</strong><br>
  Continuous flow • Balanced-ternary commits • Delayed angular channels • Operational bridge coordinates • Trace/window measurement
</p>

BiDi Coherence-Delta Calculus is a native `.cdc` language whose semantic kernel
is a compact coherence calculus. It models computation as nested boundary
modules of phase-state cells, connected by delayed weighted channels that may
also carry angular phase bias, dimension projection, and path-aware cross-scale
endpoints. Fields evolve through continuous flow and periodically commit through
event-triggered balanced-ternary invariant gates. A derived trace/window layer
lets any module, relation, or projected boundary act as observer, participant,
or measurement interface without adding a binary observer primitive.

## Center Of Gravity

CDC is the language. The calculus is the kernel semantics.

That gives the project two separate success stories:

- **Language success:** developers can install `cdc`, write `.cdc`, run `.cdc`,
  test `.cdc`, and eventually build/package `.cdc` programs without touching the
  construction host.
- **Calculus success:** the language kernel has explicit terms, reductions,
  invariants, witnesses, and theorem-prover obligations.

The only Python file left is `cdc_boot.py`, a minimal bootloader that reads
native `.cdc` declarations and verifies expectations. It is not the calculus.
The 64-state bridge has a separate non-Python runtime in
`runtime/cdc_bridge_runtime.c` that consumes `bridge64.cdc` as a lookup table,
generates and verifies the `n=9` and `n=12` higher-arity codebooks, and emits
the interactive bridge SVG. The first native reducer runtime lives in
`runtime/cdc_native_runtime.c` and executes source-declared `.cdc` `flow`,
`commit`, `nest`, `interpret`, `council`, and `evolve` jobs from
`native_reducer.cdc` and `council_bridge.cdc`.

## Native Status

This repository is on a native `.cdc` self-hosting track. The removal plan is
explicit in `NATIVE_SELF_HOSTING_MANDATE.md`: all current host behavior must be
replaced by native `.cdc` semantics and witnesses before host files are deleted
without breaking verification.

The practical bootloader decision for this release is now enforced by the repo:
Python is allowed only as `cdc_boot.py`. `.cdc` owns the source terms, declared
reducer rules, proof obligations, capability witnesses, and self-hosting
contract.

## Installation & Exploration

Requires Python >= 3.10 and a C compiler (`cc`) for the full verification gate.
There are no package dependencies.

```bash
git clone https://github.com/ETEllis/bidi-coherence-delta-calculus.git
cd bidi-coherence-delta-calculus
./scripts/verify.sh          # Full verification gate (start here)
python3 cdc_boot.py          # Native .cdc contract/witness verification
```

Editable install:

```bash
pip install -e .
```

## Core Architecture

```mermaid
flowchart TD
    subgraph M["Module (nested boundary)"]
        Cells["Phase-state cells<br/>+ latched committed poles"]
        Channels["Delayed angular channels<br/>(weight × delay × angle × lines)"]
        Cells --> Channels
    end

    Flow["⟶_d  Continuous Flow<br/>(Lipschitz vector field<br/>+ belief / weight update)"]
    Commit["⟶_β  Commit<br/>(Guard fires → trit-walk barrier<br/>+ free-energy non-increase check)"]
    Bidi["γΔ  bidiγΔ coupling<br/>Path-aware relations across nested frames<br/>α=0 cone: parent ↔ child"]

    Channels --> Flow
    Flow --> Commit
    Commit --> Bidi
    Bidi --> Cells

    style Commit fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    style Bidi fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    style Flow fill:#fff8e1,stroke:#f9a825
```

**Canonical vocabulary**
- `cell` — continuous phase-state carrier with latched pole
- `channel` — directed influence with delay, weight, angular phase, and optional line projection
- `module` — bounded group with read/write cones, belief, prior
- `field` — graph of modules + channels under monoidal composition
- `commit` — discrete update enforcing a balanced-ternary nonnegative balance invariant
- `bidiγΔ` — bidirectional coherence-delta across nested reference frames and path endpoints
- `window` — derived observer projection over a field, producing ternary traces and measurement records

## Why This Substrate Exists

Modern hybrid systems routinely combine continuous simulation or control, evented transitions, delayed feedback, policy invariants, local learning, predictive belief updates, and nested scale coupling — usually implemented in fragmented toolkits.

This calculus supplies one shared, executable vocabulary and verified reference semantics for all of them under a single coherence-preserving spine.

## Novelty at a Glance

- **`bidiγΔ` operator** — first-class bidirectional coherence exchange across distinct reference frames; nesting is the `α=0` special case of the same relation operator.
- **Angular/path channels** — channels can rotate incoming phase by `angle=`, project onto selected `lines=`, and connect paths such as `P/c -> P`.
- **Trace/window observer layer** — any module, relation, or projected boundary can hold a causal window; committing measurements are guarded balanced-ternary commits.
- **Trace-order locality** — phase-time can flow smoothly while event-time remains local to the observing window; there is no required global tick.
- **Recursive window policy** — observer windows can carry local counters and projection/update policy without adding a binary observer or global clock.
- **Balanced-ternary carrier** — committed values are `-1 / 0 / +1` around real equilibrium, not binary false/true labels.
- **Existence viability** — frames persist by preserving bounded coherent continuity while retaining mode-appropriate transition capacity.
- **64-state dyadic/triadic bridge** — `bridge64.cdc` declares every `2^6 = 4^3 = 64` codebook row for bootstrap/runtime bridge design.
- **Generated higher-arity codebooks** — `bridge512.cdc` and `bridge4096.cdc` contain the full generated rows for `n=9` and `n=12`, with runtime regeneration checks.
- **Operational bridge runtime** — `runtime/cdc_bridge_runtime.c` parses `bridge64.cdc`, verifies bijection, performs dyadic/triadic lookup, projects trace trits into bridge coordinates, verifies generated codebooks, and emits an interactive 64-cell SVG.
- **Operational native reducer** — `runtime/cdc_native_runtime.c` parses `native_reducer.cdc` and executes source-declared flow, commit, and nest transitions.
- **Native compile/interpreter/proof path** — the same runtime emits reducer IR, executes that IR through an interpreter path, and exhaustively checks the finite n=6 balanced-ternary walk spectrum.
- **Council + self-evolution scenario** — `council_bridge.cdc` deliberates across modules into a bridge coordinate and writes a bridge-coordinate witness into an evolved `.cdc` source copy.
- **Trit-walk barrier + nonnegative balance** — clean discrete guard preventing rank violation on continuous-to-discrete quantization.
- **Native free-energy witnesses** — commits are guarded against Φ increase; continuous flow has explicit subset obligations.
- **`.cdc` literate DSL** — single source format declaring fields, modules, channels, guards, flows, and proof obligations.
- **Native kernel contract** — `kernel.cdc` starts the self-hosting path by declaring calculus terms, reducer rules, capabilities, and the shrinking bootloader boundary.
- **Minimal bootloader** — `cdc_boot.py` only loads `.cdc`, checks declarations, and reports expectations.

Core metatheorems and bridge invariants are witnessed by native `.cdc`. The
finite discrete layer now has an executable C proof check plus Lean and Coq
source mirrors for the same n=6 carrier spectrum.

## Verification Status (v0.2.4)

The package passes 100%:

- 1/1 Python bootloader file: `cdc_boot.py`
- 169/169 native `.cdc` expectations
- 13/13 native invariant declarations
- 31/31 native capability declarations
- 4759/4759 native witness declarations
- C bridge runtime compile, lookup, trace-coordinate, generated higher-arity codebook, and interactive grid/SVG checks
- C native reducer runtime run/compile/interpret/proof/council/evolve checks
- Lean and Coq finite carrier and algebraic law proof checks when `lean` or `coqc` are installed
- Paper compile through `tectonic` when available

Run the full gate anytime:

```bash
./scripts/verify.sh
```

## Native `.cdc` Example

```cdc
kernel bidi stage=2 target=cdc
  term cell channel module field counter trace window measurement bridge policy
  rule flow commit nest relation trace trace-order window measure adapt synchronize
  provides native-witness-suite native-capability-suite
  bootloader read-source parse-lines collect-native-declarations verify-expectations report
  expect native substrate == cdc
  expect python-files == 1
  expect witnesses >= 4759
end
```

## Operational Bridge

<p align="center">
  <img src="assets/bridge64-grid.svg" alt="bridge64 dyadic and triadic codebook grid" width="760">
</p>

The bridge is operational, not only declared:

```bash
build/cdc_bridge_runtime verify bridge64.cdc
build/cdc_bridge_runtime lookup-dyadic bridge64.cdc 101011
build/cdc_bridge_runtime lookup-triadic bridge64.cdc 223
build/cdc_bridge_runtime project-trits bridge64.cdc '+0-+0-' council
build/cdc_bridge_runtime run-jobs bridge64.cdc bridge_jobs.cdc
build/cdc_bridge_runtime verify-codebook bridge512.cdc 9
build/cdc_bridge_runtime verify-codebook bridge4096.cdc 12
build/cdc_bridge_runtime emit-codebook 9
build/cdc_bridge_runtime emit-codebook 12
build/cdc_bridge_runtime grid-svg bridge64.cdc
```

`./scripts/verify.sh` compiles the runtime, runs those checks, and confirms that
the tracked 64-cell interactive SVG and the generated `bridge512.cdc` and
`bridge4096.cdc` files match runtime output. Details are in `BRIDGE_RUNTIME.md`.

## Native Reducer Runtime

The reducer is no longer only a target described in prose. `native_reducer.cdc`
declares a small field with modules, cells, an angular channel, and three
source-level reducer jobs:

```bash
build/cdc_native_runtime run native_reducer.cdc
build/cdc_native_runtime compile native_reducer.cdc
build/cdc_native_runtime interpret native_reducer.cdc
build/cdc_native_runtime prove native_reducer.cdc
build/cdc_native_runtime council council_bridge.cdc
build/cdc_native_runtime evolve council_bridge.cdc
```

The C runtime consumes that source and executes:

- `flow`: continuous phase evolution plus angular channel coupling;
- `commit`: balanced-ternary quantization with nonnegative prefix-balance repair;
- `nest`: child coherence upward and parent context downward.
- `compile`: reducer source to a small IR listing;
- `interpret`: execute the compiled reducer IR as an IR path rather than only printing it;
- `prove`: exhaustive n=6 trit-walk counts: `729 / 267 / 51 / 20 / 5`.
- `council`: deliberate across source-declared council members into a bridge coordinate;
- `evolve`: write a bridge-coordinate witness into a copied `.cdc` source.

`cdc_boot.py` only indexes those declarations and verifies their witness links;
it does not execute the reducer.

Lean and Coq mirrors of the finite carrier and algebraic law proof live in
`formal/lean/CDCFinite.lean` and `formal/coq/CDCFinite.v`. `./scripts/verify.sh`
runs them automatically when the corresponding toolchain is installed.

## Paper

Knuth-inspired, dependency-light literate paper:

- Source: `paper/arxiv/main.tex`
- The checked source tree is the current paper source; `./scripts/verify.sh` compiles it when `tectonic` is available.

Compile locally (TeX toolchain):

```bash
cd paper/arxiv && pdflatex main.tex && pdflatex main.tex
```

## Boundaries & Next

The finite carrier layer and finite algebraic laws now have executable proof
checks. The broader formalization spine (immutable runtime state tuple,
small-step relations for flow/commit/nest, and expanded Lean/Coq/Kani proofs) is in
`FORMAL_SEMANTIC_SPINE.md`.

Claim-to-witness-to-proof tracking is in `VERIFICATION_OBLIGATION_MATRIX.md`.
The observer/measurement extension is documented in `TERNARY_TRACE_WINDOW_SEMANTICS.md`.
The native self-hosting mandate is documented in `NATIVE_SELF_HOSTING_MANDATE.md`.

Current work delivers a compact, verified substrate — not production scaling, biological completeness, or a finished physics theory.

## License

MIT License. See `LICENSE`.

---

If this substrate proves useful, cite via `CITATION.cff` or the paper.
