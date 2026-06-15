# Formal Semantic Spine

This document pins the next formalization pass to one canonical object. The goal
is to prevent the paper, `.cdc`, `bidi_calculus.py`, `cdc_boot.py`, and
`calculus_laws.py` from drifting into parallel descriptions.

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

## AST

The AST should represent only the canonical calculus primitives:

- `CellTerm`: phase, amplitude, intrinsic frequency, plasticity, optional latch.
- `ModuleTerm`: named cell vector plus belief, prior, precision, and action gain.
- `ChannelTerm`: source, destination, weight, delay, optional line, plasticity flag.
- `FieldTerm`: modules, channels, child fields, timestep, gain, deadband, gating.
- `CounterTerm`: register-machine witness term for universality.

`cdc_semantics.py` now defines these as dataclasses.

## Runtime State Tuple

A runtime state is:

```text
S = (t, modules, channels, child_fields, deadband, dt, gain, gated)
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

The reference reducer may integrate flow numerically, but the semantic relation
is the source of truth. Numerical choices should be recorded as realization
parameters, not confused with the calculus definition.

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
- every witness in `calculus_laws.py` references an `InvariantSpec`.
- the paper's invariant table matches `cdc_semantics.py`.
- `scripts/verify.sh` proves code, `.cdc`, witnesses, and semantic registry stay
  synchronized.

This is the path from executable calculus to theorem-prover-ready calculus
without losing the working system.
