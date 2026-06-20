# Formal Semantic Spine

This document pins the next formalization pass to one canonical object. CDC is
the language; this spine is the semantic kernel that keeps `.cdc`, the paper,
the transitional host reducer, the bridge, and the witnesses from drifting into
parallel descriptions.

## Principle

Every artifact should become a projection of the same semantic spine:

```text
.cdc source
  -> typed AST
  -> runtime state tuple
  -> small-step relation
  -> invariant table
  -> executable witnesses
  -> theorem-prover obligations
```

The current repository already has working reducer behavior and passing witness
suites. The refinement is to make the formal spine explicit enough that future
code and proofs can be generated from, or audited against, the same source.

Trace/window semantics are derived from this spine. They do not add a fourth
foundational step kind. They name causal observer windows, trace spans, and
measurement records over `flow`, `commit`, and `nest`.

## AST

The AST should represent only the canonical calculus primitives:

- `CellTerm`: phase, amplitude, intrinsic frequency, plasticity, optional latch.
- `ModuleTerm`: named cell vector plus belief, prior, precision, and action gain.
- `ChannelTerm`: source path, destination path, weight, delay, angular phase bias,
  optional line projection, and plasticity flag.
- `FieldTerm`: modules, channels, child fields, timestep, gain, deadband, gating.
- `CounterTerm`: register-machine witness term for universality.
- `WindowSpec`, `TraceSpan`, `ObserverSpec`, `MeasurementRecord`,
  `AgencySummary`, and `IncidenceSpec`: derived observer/measurement records over
  the same field state.

`cdc_semantics.py` now defines these as dataclasses.

Those dataclasses are transitional host descriptions. The native target is for
the same spine to be expressed as `.cdc` terms and transition rules, starting
with `kernel.cdc` and continuing until the host loader is only mechanical
bootstrap code. See `NATIVE_SELF_HOSTING_MANDATE.md`.

## Runtime State Tuple

A runtime state is:

```text
S = (t, modules, channels, child_fields, inbound_relations, deadband, dt, gain, gated)
```

Each module state carries:

```text
M = (name, cells, belief, prior, precision, action_gain, child)
```

Each cell state carries:

```text
x = (theta, amplitude, plasticity, omega, sigma, memory)
```

This tuple is the intended bridge between mathematical notation and executable
code. `bidi_calculus.py` currently realizes the same structure through mutable
Python objects; the semantic spine names the immutable shape those objects
instantiate.

## Small-Step Relation

The canonical reduction relation has three step kinds:

| step | source form | meaning |
|---|---|---|
| `flow(d)` | `F ->_d F'` | evolve phase, amplitude, belief, and plasticity for duration `d` |
| `commit(m)` | `F ->_beta F'` | guarded quantize/barrier/belief/latch update for module `m` |
| `nest(m)` | `m[[F]]` | exchange parent context downward and child coherence upward |

Operationally, nesting is represented as two automatically installed
path-aware relations at angular bias `alpha=0`: one aggregate child-to-parent
up-cone and one aggregate parent-to-child down-cone for each child module.
General channels may use nonzero `alpha` and projected `lines`, so the original
parent/child cone is the neutral case of the same relation operator.

The reference reducer may integrate flow numerically, but the semantic relation
is the source of truth. Numerical choices should be recorded as realization
parameters, not confused with the calculus definition.

## Derived Trace/Window Layer

The trace/window layer records how a bounded observer window sees a field:

```text
phase-time      continuous flow and rotation
event-time      ordered guarded commits
trace-time      phase/event history through a window
```

Trace-time is local. Smooth phase motion can accumulate with zero commit events,
and event density can differ by window. A global tick is a realization detail,
not part of the semantic spine.

The discrete outcome space is balanced ternary: `-1`, `0`, `+1`. The middle
value is resting equilibrium and a real crossing/aperture state, not binary
false. A committing measurement is a guarded balanced-ternary commit plus a
`MeasurementRecord`; passive observation produces a `TraceSpan` and leaves field
dynamics unchanged.

## Typed Invariant Table

Each invariant should have:

- a stable key;
- a mathematical statement;
- the witness file and witness name;
- a future theorem-prover target.

`cdc_semantics.py` now defines `InvariantSpec` and `INVARIANTS` for:

- `gate-abelian`;
- `interfere-monoid`;
- `rotation-linear`;
- `corefold-morphism`;
- `balanced-ternary-carrier`;
- `dyadic-triadic-closure`;
- `existence-viability`;
- `trace-order-locality`;
- `preservation`;
- `soundness`;
- `local-confluence`;
- `flow-additivity`;
- `normalforms`.

## Projection Targets

### `.cdc`

The parser should eventually produce the AST directly rather than executing line
by line. The current `cdc_boot.py` can then become:

```text
parse .cdc -> ProgramTerm -> initialize RuntimeState -> reduce -> check expects
```

The stronger self-hosting target is:

```text
parse .cdc -> native kernel terms -> native reducer transitions -> native expects
```

At that point a host language is no longer the semantic center; it is only one
replaceable loader for a language that can describe itself.

### `bidi_calculus.py`

The reducer should be audited as an implementation of the small-step relation.
The current class names can remain stable API names while internal transitions
move toward explicit `ReductionStep` records.

### `calculus_laws.py`

Law checks should iterate over `INVARIANTS`, not manually duplicate the invariant
registry. Each executable witness should declare which invariant it discharges.

### Paper

The paper should present the same AST/state/reduction/invariant table, then state
which parts are currently executable witnesses and which parts are future formal
proof obligations.

### Lean/Coq/Kani

The first formal target should be the finite discrete layer:

1. trit quantization;
2. prefix-walk admissibility;
3. commit barrier preservation;
4. localized normal forms.

After that, formalize the algebraic carrier laws, then the flow relation under
explicit Lipschitz/determinism assumptions.

## Acceptance Criteria For The Next Pass

- `.cdc` parses into `ProgramTerm`.
- `cdc_boot.py` executes from a parsed source AST rather than raw line commands.
- `kernel.cdc` grows from contract declarations into executable native reducer
  clauses.
- relation witnesses cover angular phase, dimension projection, path endpoints,
  and `.cdc` nesting auto-cone installation.
- trace/window witnesses cover passive observation, committing measurement,
  trace additivity, causal windows, observer roles, incidence projections,
  agency summaries, trace-order locality, and projected higher-order boundaries.
- every witness in `calculus_laws.py` references an `InvariantSpec`.
- the paper's invariant table matches `cdc_semantics.py`.
- native `.cdc` replacements are introduced before host files are removed.
- `scripts/verify.sh` proves code, `.cdc`, witnesses, and semantic registry stay
  synchronized.

This is the path from executable calculus to theorem-prover-ready calculus
without losing the working system.
