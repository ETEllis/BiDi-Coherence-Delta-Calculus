# BUILD_STATE — BiDi/CDC lane

Updated at every accepted gate boundary. Companion files: `RESUME_HERE.md`
(exact continuation), `DECISIONS.md` (append-only decision record),
`../../evidence/gates/<gate-id>/` (evidence bundles).

## Current source identity

- repository: `ETEllis/BiDi-Coherence-Delta-Calculus` (GitHub remote)
- branch: `claude/bun-equivalent-build-plan-lxe772` (draft PR #3)
- baseline at Phase A freeze: `origin/main` = `8cfe48fdb71e53af78411471869c064e6c650c63`;
  work-branch HEAD entering Phase A = `99747e0a63ad14ad243934c122da73ec94a57940`
  (adds `CDC_TOOLCHAIN_PLAN.md`)
- environment: Claude Code remote container — Linux 6.18.5, cc (Ubuntu 13.3.0),
  Python 3.11.15, Lean pin `leanprover/lean4:4.31.0` (CI); full identity in
  `evidence/gates/CT0/toolchain.txt`
- tracked-file digests: `evidence/gates/CT0/source-identity.txt` (git blob ids)
  and `evidence/gates/CT0/sha256-manifest.txt` (interim SHA-256, see D2)

## Last completed phase and gate

- **Phase B steps 1–2 — canonical frontend + differential oracle: COMPLETE
  (this commit).** New modules `runtime/cdc_diagnostic.{c,h}`,
  `runtime/cdc_lexer.{c,h}`, `runtime/cdc_ast.{c,h}`,
  `runtime/cdc_parser.{c,h}` (grammar-version 1: collecting typed
  diagnostics, source spans, canonical serialization; acceptance
  byte-compatible with grammar 0 including the D5 comment quirk), harness
  `runtime/cdc_frontend_check.c`, gated `cdc_boot.py --dump` (D7), invalid
  corpus `tests/fixtures/frontend/`, and the `verify.sh` CT1 section.
- **Gate CT1 — partial.** Green: differential dump byte-identical over all
  18 root files (5286 records), roundtrip, attr-parity
  (47665 checked, 0 collisions/duplicates/failures; 4863 known
  quoting-class divergences), 12-case adversarial bounds, allocator-failure
  injection (765 runs), ASan/UBSan pass, 6/6 rejection-parity fixtures.
  Open for CT1 PASS: arbitrary-input fuzzing beyond the deterministic
  corpus, and "no production command uses the legacy substring parser" —
  the native/bridge runtimes still parse with `cdc_source.c`; conversion
  happens with the ABI (Phase B steps 3–7). Evidence:
  `evidence/gates/CT1/differential-summary.txt`.

### Earlier

- **Phase A — Freeze, provenance, and cross-repo contract: COMPLETE (this commit)**
  for the items executable in this repository/environment:
  - A.1/A.2 baseline tagged by digest record (no git tag pushed; the freeze is
    the evidence bundle + this file, per D6 single-branch discipline);
    toolchain identity recorded.
  - A.3 `CDC_MEMORY_MANIFOLD_INTERFACE.md` v1.0.0 published (digest in
    `evidence/gates/CT0/interface-digest.txt`); the Memory Manifold repository
    must carry the same content at the same digest before its Phase E starts.
  - A.4 machine-readable version registry: interface §1 (grammar 0→1,
    abi 0→1, evidence-format 1, mm-schema 0→1).
  - A.5 existing verification fixtures preserved untouched (all root `.cdc`
    files, `scripts/verify.sh` negative fixtures, Lean/Coq mirrors); inventory
    is the CT0 manifest.
  - A.6–A.9 (legacy Python archaeology, dual-schema inventory, ledger-first
    declaration, greenfield tree creation) are **Memory Manifold repository
    items — deferred**: that repository is not in this session's scope (see
    Deviations). The amendment §13 clean-room findings stand as the interim
    inventory of record, including the `payload_json`/`content` defect to be
    captured as an archaeological fixture at first access.
- **Gate CT0 — partial.** Provenance and toolchain identity recorded and
  reproducible from a clean checkout of this branch. Full CT0 (reproducible
  native binaries; manifest digest embedded in every verdict) completes when
  Phase B/C verdict emission exists. No PASS is claimed yet.

## Exact commands and results (Phase A)

```text
git rev-parse HEAD                      -> 99747e0a63ad14ad243934c122da73ec94a57940 (pre-Phase-A)
git rev-parse origin/main               -> 8cfe48fdb71e53af78411471869c064e6c650c63
./scripts/verify.sh                     -> "All checks passed." (local; Lean/Coq/Tectonic skipped, not installed here)
CI run 29960029272 (ci.yml, --require-formal) on 99747e0 -> in progress at freeze time
```

## Material deviations and rationale

1. **Remote container, not operator-local checkout.** The amendment's local
   paths (`/Users/edwardellis/...`, `/Volumes/ET External/...`) do not exist
   here; `ls /Volumes` → no such directory. Baseline recorded from the GitHub
   remote instead (D4). Reconciliation against the unpushed local branch
   `codex/mobius-u-identity-system` @ `313f0a1` is queued for whenever it is
   pushed or its digests are supplied.
2. **Superposition live tree unreachable.** §3.4's read-before-adapter list
   cannot be read from this container. Not blocking Phases A–D; required
   before Phase K/adapter work. The PC6 hard pause is preserved (nothing here
   can start it, and nothing will claim device evidence).
3. **Memory Manifold repository not in session scope.** GitHub access is
   scoped to this repository; repo-listing approval was requested and not yet
   granted. Phases E–H cannot land in their owning repository from this
   session until it is added. This lane proceeds A→D here; E–H follow when
   access exists (or transfer to the integration lane per amendment §14).
4. **Single work branch** `claude/bun-equivalent-build-plan-lxe772` for all
   phases in this lane (D6), instead of per-phase branches.
5. **Interim digests** (D2): git SHA-1 + SHA-256 until BLAKE3 is vendored.

## Next executable action

Phase B step 3 (Amendment A2): define the stable embeddable ABI —
`runtime/cdc_abi.h` with opaque `cdc_program` / `cdc_runtime` / `cdc_result`
handles, documented ownership/lifetime/determinism/error behavior, and an ABI
version — implemented over the grammar-1 frontend, then begin converting the
CLI/verification consumers to it. Then step 6 (`CDC_BRIDGE_NO_MAIN` +
old/new driver parity) and step 7 (legacy-path deletion through the recorded
gates, including D7's `frontend-differential-dump`). Fuzzing beyond the
deterministic corpus remains queued for CT1 PASS.

## External blockers

- Memory Manifold repository access (blocks Phases E–H in this lane).
- Superposition tree access or supplied document digests (blocks Phase K
  conformance work; does not block A–D).
- Operator push of `codex/mobius-u-identity-system` (blocks reconciliation
  against the amendment's recorded local HEAD; does not block A–D).
