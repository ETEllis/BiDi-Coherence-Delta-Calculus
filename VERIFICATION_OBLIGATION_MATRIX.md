# Verification Obligation Matrix

This matrix separates three layers:

```text
claim -> native .cdc witness -> formal obligation
```

The project does not resolve critique by weakening claims. It resolves critique
by making every claim native in `.cdc` now or explicitly queued for mechanical
verification.

| Claim | Current native witness | Formal obligation |
|---|---|---|
| balanced-ternary carrier | `laws.cdc` declares carrier witnesses | finite codomain proof for `commit` |
| dyadic/triadic bridge closure | `laws.cdc` declares the invariant; `bridge64.cdc` declares all 64 rows; `runtime/cdc_bridge_runtime.c` consumes and validates them | finite uniqueness/bijection proof for bootstrap codebook |
| existence viability | `laws.cdc`, `relations.cdc`, and `trace_windows.cdc` declare viability witnesses | viability invariant over bounded continuity, permeability, and transition capacity |
| trace-order locality | `laws.cdc`, `relations.cdc`, and `trace_windows.cdc` declare local trace, local-counter, detuning, overlap, and recursive-policy witnesses | partial-order theorem for causal trace windows, local event counters, and projection policy |
| gate is abelian | `laws.cdc` declares associativity, commutativity, identity, inverse witnesses | algebraic group proof over torus carrier |
| interference is monoidal | `laws.cdc` declares associativity, commutativity, void-unit witnesses | commutative monoid proof |
| rotation is linear | `laws.cdc` declares rotation-linearity witness | carrier action proof |
| core-fold is a morphism | `laws.cdc` declares linearity/equivariance and non-idempotence witnesses | projection morphism proof |
| commit preservation | `laws.cdc` declares preservation witness | induction over cell order and barrier repair |
| commit soundness | `laws.cdc` declares commit and flow-subset soundness witnesses | guard accept/hold case split |
| local confluence | `laws.cdc` declares disjoint-commit witness | footprint-disjoint diamond lemma |
| flow additivity | `laws.cdc` declares split-duration witness | monoid-action proof for the flow relation |
| normal forms | `laws.cdc` declares localized normal-form witnesses; `native_reducer.cdc` declares `proof trit-walk-n6`; `runtime/cdc_native_runtime.c` checks `729 / 267 / 51 / 20 / 5`; Lean and Coq mirrors live in `formal/` | extend finite normalization from checked counts into commit-barrier preservation theorem |
| angular/path relation | `relations.cdc` declares angle, lines, path endpoints, and nesting-cone witnesses | path-indexed relation algebra |
| trace/window layer | `trace_windows.cdc` declares passive/committing separation, role-relative observer, incidence boundary, coupled-observer, shared-state commit, and causal-window witnesses | derived-observer theorem over flow/commit/nest |
| bridge coordinate runtime | `system.cdc` declares `G1`; `bridge_jobs.cdc` declares coordinate jobs; `scripts/verify.sh` compiles the C runtime and checks lookup, source-declared jobs, higher arity, and grid generation | native `.cdc` reducer or extracted kernel replacing the C bridge pilot |
| native reducer runtime | `native_reducer.cdc` declares field/module/cell/channel state and flow/commit/nest jobs; `runtime/cdc_native_runtime.c` executes them | broaden source-declared reducer to the full trace/window/measure surface |
| native compile/proof path | `native_reducer.cdc` declares compile/proof jobs; `runtime/cdc_native_runtime.c` emits reducer IR and exhaustively checks finite carrier counts | self-host the compiler/reducer in `.cdc`; extract or port proof obligations to Lean/Coq/Kani |
| native language center | `kernel.cdc` declares terms, rules, capabilities, witness counts, and one-file Python boundary | native reducer and proof checker expressed in `.cdc` |

## First Mechanized Target

The first theorem-prover port is now seeded by `formal/lean/CDCFinite.lean` and
`formal/coq/CDCFinite.v`, and mirrored by the native C proof checker. It remains
finite:

1. balanced-ternary carrier;
2. `3^6` committed-walk codomain;
3. prefix-walk admissibility;
4. commit-barrier preservation;
5. localized normal forms;
6. `2^6 = 4^3 = 64` bridge codebook uniqueness and totality.

This is the shortest route from native witness declaration to mechanically
checked calculus without prematurely formalizing the continuous numeric
realization. The next proof increment is commit-barrier preservation over the
same finite carrier.
