# RESUME_HERE — BiDi/CDC lane

Exact continuation state for any successor (including the integration lane
inheriting per amendment §14). Rewritten 2026-07-23 after the adversarial
gate review (C1). Read in this order:

1. `CDC_TOOLCHAIN_PLAN.md` — the base plan with its binding Amendment Record.
2. The CDC Toolchain + Memory Manifold Full-Build Amendment (2026-07-22) and
   the PR #3 Adversarial Gate Review (2026-07-23) — both held by the
   operator; binding per `docs/build/DECISIONS.md` D1/D8. Request them from
   the operator if you do not have them.
3. `CDC_MEMORY_MANIFOLD_INTERFACE.md` — the digest-pinned cross-repo
   contract (v1.0.1: grammar 1, ABI 1.0).
4. `docs/build/BUILD_STATE.md` — current identity, exact gate states,
   deviations, blockers.
5. `docs/build/DECISIONS.md` — D1–D8.

## Where the build stands (exact gate language)

- **PR CI: PASS** on every pushed head of
  `claude/bun-equivalent-build-plan-lxe772` (draft PR #3 — do NOT merge
  without the combined-tree integration gate below).
- **CT0: PARTIAL** — provenance recorded; binary reproducibility and
  embedded verdict identity remain open.
- **CT1: PASS** — differential/roundtrip/attr-parity/bounds/oom evidence
  plus the two 2026-07-23 public-boundary counterexamples (diagnostic
  long-path serialization; unreadable/special-path rejection), all hard-
  gated in `verify.sh` including under ASan/UBSan. Reopens only if a new
  boundary counterexample lands.
- **CT2: SEED/PARTIAL** — ABI 1.0 parse/result surface and the A9 driver
  skeleton exist; execute/verify, `CDC_BRIDGE_NO_MAIN`, runtime-to-ABI
  conversion, and full ordered per-check parity remain open.
- **CT3–CT5, MM0–MM9, RG0: NOT STARTED.**
- The plan commit is documentation, not a gate.

## Next executable sequence (in order)

1. **Integration gate (review C2)**: `origin/codex/mobius-u-identity-system`
   (head `313f0a1`) merges into the PR branch as the combined tip;
   overlapping `scripts/verify.sh`, `.gitignore`, `README.md` resolved
   intentionally; the COMBINED tree must pass `./scripts/verify.sh`
   (toolchain + identity sections). If BUILD_STATE already records this
   merge, skip to 2.
2. Finish Phase B: `CDC_BRIDGE_NO_MAIN` (A11), link native+bridge runtimes
   into `build/cdc` as passthrough verbs with byte-identical output
   (existing greps are the parity net), grammar-1 registry + expect
   evaluation inside `cdc verify` compared field-for-field against the
   bootloader per interface §7 ordered vectors (gate
   `toolchain-verify-parity`), then CT2.
3. Phase C: real `cdc run` and `cdc test` on ABI 1.1 — lifecycle,
   cancellation, budgets, deterministic mode; typed commit/hold/nest/fail
   gate policy (unexpected HOLD fails `--gate`; merged totals forbidden);
   CT3.
4. Phase D: durable `cdc_store` — append/replay/snapshot/rebuild/
   transaction/CAS-fence/commit/rollback/recover/compact/attest/verify;
   WAL, BLAKE3 identities (vendor reference implementation), fsync
   boundaries, crash injection at every mutation boundary; all effects
   behind BiDi commit (A10).
5. Update `BUILD_STATE.md` + this file at every accepted gate; leave PC6
   hard-paused; Phases E–H stay in the Memory Manifold repository.

## Hard rules in force

- Repair-and-continue, not redesign. Amendment governs over plan text (D1);
  review corrections are binding (D8).
- Every commit lands green through `./scripts/verify.sh`; byte-identical
  output for existing runtime paths until their recorded removal gates.
- Unreadable/non-regular sources are CDC_ERR_IO, never empty programs;
  diagnostics are never truncated (permanent counterexamples enforce both).
- Balanced ternary stays typed; durable mutation stays behind BiDi commit;
  single writer per worktree; interface versions change only by new digest.
- Do not resume or simulate physical PC6; never convert local evidence into
  device claims.
