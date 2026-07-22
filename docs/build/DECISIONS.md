# Build Decisions — BiDi/CDC lane

Format: decision id, date, decision, rationale, consequences. Append-only.

## D1 — 2026-07-22 — Amendment adopted as binding over the toolchain plan

The CDC Toolchain + Memory Manifold Full-Build Amendment (2026-07-22) is
adopted as an amendment to `CDC_TOOLCHAIN_PLAN.md`, not a competing rewrite.
Where the original plan text conflicts, the amendment governs; the specific
supersessions are recorded in the plan's Amendment Record section. Execution
follows the amendment's Phase A–L sequence with this repository owning the
generic language/runtime/toolchain concerns only (no Memory Manifold product
code here beyond a small conformance fixture).

## D2 — 2026-07-22 — Interim digest algorithm

Amendment A3 mandates BLAKE3 (content) + Ed25519 (signatures) as canonical.
Neither is vendored yet. Until the vendored BLAKE3 lands (Phase B/D), Phase A
provenance records use git object ids plus SHA-256, labeled interim. All
interim records are re-digested with BLAKE3 when it lands; the re-digest is
recorded as evidence, and no public claim may rest on an interim digest.

## D3 — 2026-07-22 — Capability identifier partition

G9 (toolchain driver), H6–H11 (toolchain frameworks), H12–H17 (Memory
Manifold frameworks) reserved as listed in `CDC_MEMORY_MANIFOLD_INTERFACE.md`
§2. Live registry (A–F, G1–G8, H1–H5, U1) is untouched. No identifier reuse.

## D4 — 2026-07-22 — Remote-environment baseline

This lane executes in the Claude Code remote container against the GitHub
remote (`ETEllis/BiDi-Coherence-Delta-Calculus`). The operator-local branch
`codex/mobius-u-identity-system` @ `313f0a167a755b94f102969291a4f9ba415ed4f7`
named by the amendment was never pushed to this remote and is unreachable
here. The Phase A freeze therefore records the observed remote identity
(`origin/main` = 8cfe48f, work branch HEAD at freeze = 99747e0). If the
operator later pushes the local branch, a reconciliation pass compares it
against this baseline before any of its content is treated as canonical.

## D5 — 2026-07-22 — Grammar quirk preservation for parity

The legacy loader strips `#` comments before shell-style splitting
(`cdc_boot.py` `strip_comment` → `split_line`), so `#` truncates a line even
inside a quoted attribute value. The grammar-1 frontend must replicate this
behavior exactly while the legacy path is the differential oracle, and must
record it as a typed diagnostic candidate. Changing the behavior is a
grammar-version bump, never a silent fix.

## D6 — 2026-07-22 — Single work branch and PR

All BiDi/CDC lane work lands on the session-designated branch
`claude/bun-equivalent-build-plan-lxe772` (draft PR #3), committing at gate
boundaries, rather than per-phase branches. Rationale: the branch is the
authorized push target for this execution environment; PR #3 carries CI
(`verify.sh --require-formal`) on every push, which enforces the
every-commit-green discipline the amendment requires.
