# RESUME_HERE — BiDi/CDC lane

Exact continuation state for any successor (including the integration lane
inheriting per amendment §14). Read in this order:

1. `CDC_TOOLCHAIN_PLAN.md` — the base plan (with its Amendment Record section).
2. The CDC Toolchain + Memory Manifold Full-Build Amendment (2026-07-22) —
   held by the operator as
   `CODEX_CDC_MEMORY_MANIFOLD_FULL_BUILD_AMENDMENT_20260722.md`; binding per
   `docs/build/DECISIONS.md` D1. Not committed here (contains operator-local
   context); request it from the operator if you do not have it.
3. `CDC_MEMORY_MANIFOLD_INTERFACE.md` — the digest-pinned cross-repo contract.
4. `docs/build/BUILD_STATE.md` — current identity, gates, deviations, blockers.
5. `docs/build/DECISIONS.md` — D1–D6.

## Where the build stands

- Phase A complete in this repository (provenance freeze, contract, registry
  partition, continuity docs). Gate CT0 partial: provenance recorded; binary
  reproducibility + verdict digest embedding land with Phases B/C.
- Phases B–D are next, in order, entirely in this repository:
  - B: canonical frontend (lexer/parser/AST/diagnostics/spans/canonical
    serialization), differential oracle vs. legacy path over every root
    `.cdc`, fuzz + malformed-input policy, `CDC_BRIDGE_NO_MAIN`, stable
    `cdc_abi` v1, then legacy-parser deletion through a recorded gate (CT1,
    CT2).
  - C: `cdc run` / `cdc test` with lifecycle, budgets, deterministic mode,
    typed commit/hold/nest/fail gate policy, ordered per-check parity vectors
    (CT3).
  - D: generic durable state substrate — `cdc_store` protocol, WAL journal,
    BLAKE3 identities, atomic activation, fsync boundaries, crash-injection
    recovery matrix, effects behind BiDi commit (feeds CT4, MM1).
- Phases E–H (Memory Manifold greenfield) are BLOCKED in this environment:
  the Memory Manifold repository is not in session scope. Do not implement
  the product inside this repository; a small conformance fixture is the
  only Memory artifact allowed here.

## Hard rules in force

- Execute; do not re-architect. Where plan text and amendment conflict, the
  amendment governs (D1).
- Every commit lands green through `./scripts/verify.sh` (CI runs
  `--require-formal`). Byte-identical output strings for existing runtime
  paths until their recorded removal gates.
- Do not resume or simulate physical PC6. Do not convert local/simulated
  evidence into device claims.
- Balanced ternary is typed everywhere; unexpected HOLD fails gates but is
  never merged into pass/fail totals.
- All durable mutation goes behind the BiDi commit path (A10) — including
  toolchain state like package installs.
- Single writer per worktree; interface changes only by publishing a new
  digest-pinned version.

## Next executable action (verbatim)

Implement Phase B step 1 exactly as specified in
`docs/build/BUILD_STATE.md` § "Next executable action". Start by reading
`runtime/cdc_source.h` and `runtime/cdc_source.c` end-to-end (the second
oracle alongside `cdc_boot.py`), then create the four frontend module pairs,
then the differential harness, then the `verify.sh` section with its negative
fixtures. Commit at the CT1-evidence boundary.
