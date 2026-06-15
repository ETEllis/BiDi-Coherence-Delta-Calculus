# BiDi Coherence-Delta Calculus

BiDi Coherence-Delta Calculus is a compact formal substrate for hybrid systems
that need continuous dynamics, evented discrete commits, delayed coupling, local
invariants, nested reference frames, and executable coherence witnesses.

The repository contains:

- `BIDI_CALCULUS_CORE.md`: the formal core: carrier algebra, term syntax,
  structural congruence, hybrid reduction relation, operator algebra, and
  metatheorem witnesses.
- `FORMAL_SEMANTIC_SPINE.md`: the AST/state/small-step/invariant spine for the
  next formalization pass.
- `CDC_LANGUAGE.md`: the `.cdc` source language.
- `bidi_calculus.py`: the Python reference reducer.
- `cdc_semantics.py`: declarative semantic dataclasses and invariant registry.
- `cdc_boot.py`: the `.cdc` bootstrap bridge.
- `calculus_laws.py`: executable law and metatheorem witnesses.
- `acceptance.py`: capability witness suite.
- `system.cdc` and `laws.cdc`: native `.cdc` programs for system behavior and
  law obligations.
- `paper/arxiv/main.tex`: arXiv-ready paper source.

## One-Sentence Definition

BiDi Coherence-Delta Calculus models computation as nested boundary modules made
of phase-state cells, connected by delayed weighted channels, evolved through
continuous flow, and periodically committed through event-triggered invariant
gates that preserve coherence and reject free-energy-increasing transitions.

## Why It Exists

Many modern systems mix regimes that are usually implemented separately:

- continuous simulation or control;
- evented state transitions;
- delayed signals and feedback;
- policy gates and invariants;
- local learning and adaptive weights;
- predictive belief updates;
- nested scale and reference-frame coupling;
- symbolic/discrete computation.

This calculus gives those regimes one shared vocabulary: cells, channels,
modules, fields, commits, and bidirectional coherence-delta coupling.

## Quick Start

Run the full verification gate:

```bash
./scripts/verify.sh
```

Run the law witnesses only:

```bash
python3 calculus_laws.py
```

Run native `.cdc` source:

```bash
python3 cdc_boot.py system.cdc laws.cdc
```

Run the capability witnesses:

```bash
python3 acceptance.py
```

## Current Verification Snapshot

The current package is expected to pass:

- Python syntax checks for the reference reducer and bridge.
- `16/16` law and metatheorem witnesses.
- `17/17` native `.cdc` expectations across `system.cdc` and `laws.cdc`.
- `24/24` capability acceptance witnesses.
- a targeted smoke check proving `.cdc` `deadband` propagation reaches fields.

## The Calculus Core

The formal spine is:

```text
carrier algebra
  -> term syntax
  -> structural congruence
  -> hybrid reduction: flow + commit
  -> operator algebra
  -> executable metatheorem witnesses
```

Canonical vocabulary:

- `cell`: continuous phase-state carrier with a latched committed pole.
- `channel`: directed weighted influence with continuous delay.
- `module`: bounded group of cells with read/write cones, belief, prior, and
  optional child field.
- `field`: graph of modules and channels.
- `commit`: guarded discrete update that quantizes state, enforces the
  nonnegative balance invariant, updates belief, and rejects free-energy
  increases.
- `bidi-gamma-delta` / `bidiγΔ`: bidirectional coherence-delta coupling across
  nested reference frames.

The reference API preserves implementation names for compatibility:
`Thread`, `Strand`, `Knot`, `Breathfield`, and `breath`.

## Native `.cdc`

Example:

```text
deadband 0.5
field demo dt=0.02 gain=1.4
  module A theta 0 0.3 0.6 0.9 1.2 1.5 omega 1.0
  module B trits + o - + o -
  channel A -> B delay=0.2 weight=1.0
  guard B crossing 0
  flow 3.0
  commit B
  expect admissible B
end
```

`.cdc` is a source format for declaring fields, modules, channels, reductions,
counter programs, and executable proof obligations.

## Paper

The arXiv-oriented paper source lives at:

```text
paper/arxiv/main.tex
```

It is intentionally flattened and dependency-light. If a TeX toolchain is
available, compile with:

```bash
cd paper/arxiv
pdflatex main.tex
pdflatex main.tex
```

The repository does not require LaTeX to run the executable witnesses.

The paper style intentionally nods to Knuth: restrained TeX/Computer Modern
presentation, literate-programming structure, and code/source fragments woven
into the mathematical exposition.

## Boundaries

The law checks are executable witnesses, not a completed theorem-prover
formalization. The current bridge now parses `.cdc` into an explicit source AST
before execution, and the law checker routes witnesses through the typed
invariant registry in `cdc_semantics.py`. The next theorem-prover pass is pinned
in `FORMAL_SEMANTIC_SPINE.md`: initialize execution from the immutable runtime
state tuple, define flow/commit/nest as small-step relations, and port those
invariants to Lean/Coq/Kani-style obligations.

The current implementation establishes a compact formal substrate and verified
reference behavior. It does not claim production scaling, biological completeness,
or superiority over every existing runtime.

## License

MIT License. See `LICENSE`.
