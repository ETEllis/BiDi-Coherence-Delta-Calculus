# Verification Obligation Matrix

This matrix separates three layers:

```text
claim -> executable witness -> formal obligation
```

The project does not resolve critique by weakening claims. It resolves critique
by making every claim either executable now or explicitly queued for mechanical
verification.

| Claim | Current executable witness | Formal obligation |
|---|---|---|
| balanced-ternary carrier | `calculus_laws.py` enumerates `{-1,0,+1}` symmetry and all `3^6` committed walks | finite codomain proof for `commit` |
| dyadic/triadic bridge closure | `calculus_laws.py` checks the `2^6 = 4^3 = 64` bijective codebook | finite bijection proof for bootstrap codebook |
| existence viability | `calculus_laws.py` checks passive, reactive, intent, agentic, and self-referential frame summaries | viability invariant over bounded continuity, permeability, and transition capacity |
| trace-order locality | `calculus_laws.py` checks smooth phase motion through local windows with zero global commit events | partial-order theorem for causal trace windows and event counters |
| gate is abelian | `calculus_laws.py` checks associativity, commutativity, identity, inverse | algebraic group proof over torus carrier |
| interference is monoidal | `calculus_laws.py` checks associativity, commutativity, void unit | commutative monoid proof |
| rotation is linear | `calculus_laws.py` checks distribution over interference | carrier action proof |
| core-fold is a morphism | `calculus_laws.py` checks linearity/equivariance and non-idempotence | projection morphism proof |
| commit preservation | random commits plus exact finite committed-walk enumeration | induction over cell order and barrier repair |
| commit soundness | 3000 randomized commits with `max ΔΦ <= 0` | guard accept/hold case split |
| flow soundness subset | symmetric delay-free ungated coupling reduces phase disagreement | Lyapunov proof under stated coupling assumptions |
| local confluence | disjoint `A;B` and `B;A` commits commute | footprint-disjoint diamond lemma |
| flow additivity | off-grid split duration agrees with one combined duration within numeric realization tolerance | monoid-action proof for the flow relation |
| normal forms | census of Catalan/Motzkin closures and fixed-point stability | finite normalization proof over balanced trit walks |
| angular/path relation | `relation_witness.py` and `relations.cdc` cover angle, lines, path endpoints, nesting cones | path-indexed relation algebra |
| trace/window layer | `trace_window_witness.py` covers passive/committing separation, role-relative observer, incidence boundary, causal windows | derived-observer theorem over flow/commit/nest |
| native language center | `kernel.cdc` declares terms, rules, capabilities, and host-debt boundary | native reducer expressed in `.cdc` |

## First Mechanized Target

The first theorem-prover port should remain finite:

1. balanced-ternary carrier;
2. `3^6` committed-walk codomain;
3. prefix-walk admissibility;
4. commit-barrier preservation;
5. localized normal forms;
6. `2^6 = 4^3 = 64` bridge codebook.

This is the shortest route from executable witness to mechanically checked
calculus without prematurely formalizing the continuous numeric realization.
