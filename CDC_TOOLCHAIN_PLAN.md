# CDC Toolchain Plan

This document is the executable build plan for the native `cdc` toolchain: one
binary, five commands, functionally equivalent to Bun's surface for the CDC
ecosystem — Runtime (`cdc run`), Package manager (`cdc install`), Test runner
(`cdc test`), Bundler (`cdc build`), and Package runner (`cdc x`) — plus two
commands Bun has no analog for (`cdc verify`, `cdc prove`).

It is the direct continuation of the language success criterion in
`README.md` ("developers can install `cdc`, write `.cdc`, run `.cdc`, test
`.cdc`, and eventually build/package `.cdc` programs without touching the
construction host") and of obligations already queued in
`VERIFICATION_OBLIGATION_MATRIX.md` (single-process executor fusing all modes,
unbounded cycle iteration, self-hosted compiler path, persistent store).

Equivalence claim, stated honestly up front: parity with Bun is per-component
functional parity *for `.cdc` programs* — `cdc` runs, installs, tests,
bundles, and executes CDC packages the way Bun does JavaScript packages. It
does not run JavaScript, and the components where Bun leans on host powers the
calculus does not grant (network registries, process spawning) declare those
as named queued host gates rather than pretending to them.

## Why CDC can do this better, not just equivalently

Each command inherits a guarantee from the calculus that its Bun counterpart
cannot offer:

| Bun | CDC | Language-derived advantage |
|---|---|---|
| `bun run` | `cdc run` | fused verified execution; typed hold reasons; deterministic replay |
| `bun install` | `cdc install` | provably atomic latch-or-hold installs via the commit balance barrier |
| `bun test` | `cdc test` | every program is already its own test (`expect-*`); balanced-ternary results (+1 pass / 0 held / -1 fail); exhaustive finite-proof tier |
| `bun build` | `cdc build` | proof-carrying bundles: compile/interpret parity plus byte-identical replay required before the artifact is accepted |
| `bunx` | `cdc x` | ephemeral-registry isolation; barrier-gated staging that never touches project state |
| — | `cdc verify` | whole-project contract closure (frameworks, witnesses, packages) in one gate |
| — | `cdc prove` | exhaustive 3^n balanced-ternary enumeration as a first-class command |

## Two load-bearing repo facts the design rests on

1. `cdc_boot.py` globs only root `*.cdc`, non-recursively (`cdc_boot.py:444`),
   and rejects unknown directives (`cdc_boot.py:194`). Therefore a package
   store under `cdc_modules/` and package sources under `packages/` are
   invisible to the existing bootloader (zero blast radius), while any new
   root-level directive (manifest, lockfile) requires a small collect-only
   addition to `cdc_boot.py` — permitted by the mandate only when paired with
   a named native deletion gate. The gate for all boot additions in this plan
   is named `toolchain-verify-parity` (Phase 0).
2. `runtime/cdc_native_runtime.c` already wraps `main` in
   `#ifndef CDC_NATIVE_NO_MAIN` (`runtime/cdc_native_runtime.c:2132`). The
   unified `cdc` binary is therefore a link-level composition of the existing
   runtimes, not a rewrite; and the queued "single-process executor" already
   exists in embryo, because `run_universal` holds one live runtime through
   reducer, surface, council, closure, and enactment.

## Binding constraints (every phase)

- `NATIVE_SELF_HOSTING_MANDATE.md` Immediate Rule: new behavior lands first as
  `.cdc` source or native-semantics documentation; host code only inside the
  C runtimes (Gate-5 pilot consumers) or `cdc_boot.py` with a named deletion
  gate. No new Python files (`scripts/verify.sh` enforces the boundary).
- Every component is a framework per the `FRAMEWORKS.md` recipe: capability
  declaration, `framework H<n> requires=<roles> permits=<primitives>` role
  contract, state via field/module/cell/channel, exemplar jobs with
  deterministic `expect-*` values, one binding witness per role,
  `expect framework H<n> complete`, and `scripts/verify.sh` wiring including
  negative fixtures. Template: `framework_procedural.cdc`.
- Registration surfaces per component: `kernel.cdc` (provides + count floors:
  currently `witnesses >= 4811`, `capabilities >= 38`, `frameworks >= 5`),
  `system.cdc` capability table, the `.cdc` file registry in
  `CDC_LANGUAGE.md`, `FRAMEWORKS.md`, and new rows in
  `VERIFICATION_OBLIGATION_MATRIX.md` (claims land in witnessed /
  runtime-checked tiers only; nothing enters proved without mechanization).
- The balanced-ternary carrier is preserved everywhere: `+1 / 0 / -1`, with
  `0` as resting equilibrium / open crossing, never binary false. Test
  results, install staging states, and hold reasons all use it.

Capability allocation: **G9** `unified-toolchain-driver` (joins operational
runtimes G1–G8); task frameworks **H6** manifest, **H7** runner, **H8** test,
**H9** install, **H10** build, **H11** package-runner. `U1` is untouched.

---

## Phase 0 — Manifest layer and unified driver skeleton (`cdc verify`)

**Goal.** Give `.cdc` a package identity without breaking glob-everything
loading, and stand up the single `cdc` binary with `verify` as its first
subcommand at parity with `python3 cdc_boot.py`.

**Manifest.** New root file `package.cdc` (this repo becomes its own first
package — dogfooding):

```text
# package.cdc -- native manifest for the bidi-cdc package.
package bidi-cdc version=0.3.0 edition=2026 entry=framework_loop.cdc entry-job=loop-u720
member kernel.cdc kind=contract
member laws.cdc kind=contract
member system.cdc kind=contract
member bridge64.cdc kind=codebook
member native_reducer.cdc kind=program
member framework_loop.cdc kind=program
# ... one member line per root .cdc file ...
provides task-loop-composition universal-operator
require none
expect package closed          # every member exists; no root .cdc orphaned outside the manifest
expect package entry-runnable  # entry-job is a declared job in the entry member
```

Resolution is file-set closure over the merged registry (reusing the
`expect frameworks closed` machinery), not versioned dependency solving —
stated as a boundary below.

**Framework exemplar** `framework_manifest.cdc` (H6):

```text
capability H6 label="package-manifest-closure"
framework H6 label=manifest requires=declare,enumerate,close,key permits=guard,counter,trace,bridge
```

with roles bound as: `declare` (guard on an open registry cell), `enumerate`
(counter whose value is the member count), `close` (window-local trace over
the member set), `key` (bridge projection of the closed manifest to one
`bridge64` coordinate) — one witness per role, `expect framework H6 complete`.

**Driver.** New `runtime/cdc_toolchain.c`: subcommands
`verify | run | test | install | build | x` plus passthrough of the nine
legacy verbs to the linked native runtime, so `build/cdc run native_reducer.cdc`
works in legacy form during transition. Build line:

```sh
cc ... runtime/cdc_toolchain.c runtime/cdc_native_runtime.c \
    runtime/cdc_bridge_runtime.c runtime/cdc_source.c \
    -DCDC_NATIVE_NO_MAIN -DCDC_BRIDGE_NO_MAIN -o build/cdc -lm
```

New header `runtime/cdc_native.h` un-statics roughly ten entry points
(`parse_source`, `run_steps`, `compile_source`, `interpret_source`,
`prove_source`, `run_surface`, `run_council`, `run_evolution`,
`run_universal`, `cdc_native_replay_json`) with **byte-identical output
strings** — the existing `verify.sh` greps are the regression suite for the
refactor. `cdc_bridge_runtime.c` gains the symmetric `CDC_BRIDGE_NO_MAIN`
guard.

`cdc verify` reimplements bootloader collection plus expectation evaluation in
C over the root glob united with manifest members, printing the same
`N/N expectations met` summary shape.

**Host additions and their gate.** `cdc_boot.py` gains collect-only handling
for `package` / `member` / `require` / `entry` plus the two `expect package`
heads (~40 lines). Deletion gate `toolchain-verify-parity`: `verify.sh` runs
both checkers and asserts identical pass/total counts every CI run; when the
parity assertion has held for a full release cycle, the bash comparison —
and eventually `cdc_boot.py` itself (Mandate Gate 5) — can be retired, with
`kernel.cdc`'s `python-files == 1` renegotiated to `== 0` as the final,
explicitly-approved kernel-contract change.

**Verification wiring.** `verify.sh` compiles `build/cdc`, runs
`build/cdc verify`, asserts bootloader parity. Negative fixtures in the
existing sed-fixture style: a manifest with a deleted `member` line must fail
`expect package closed` in both checkers; `entry-job=nonexistent` must fail
`entry-runnable`.

**Docs.** Registry rows in `CDC_LANGUAGE.md` for `package.cdc`,
`framework_manifest.cdc`, `runtime/cdc_toolchain.c`, `runtime/cdc_native.h`;
new directives documented in the syntax section; `kernel.cdc` gains
`provides manifest-registry package-closure unified-toolchain` and bumped
floors; `system.cdc` gains G9 and H6; mandate records `cdc verify` as the
Gate-5 candidate; matrix row "package manifest closure" (runtime-checked;
obligation: registry-closure theorem over member sets).

**Size.** ~500 C, ~40 gated Python, ~120 `.cdc`, ~60 shell.

**Honest boundaries.** Manifest resolution is file-set closure, not
dependency solving; boot and C checkers are dual until the parity gate
retires one.

---

## Phase 1 — Runtime: `cdc run` (H7)

**Goal.** One invocation, one live runtime state: reducer chain → surface
(guard/trace/measure/policy/bridge/counter) → council → evolve → universal,
over state the earlier stages mutated. This discharges the queued
"single-process executor fusing all modes" and the honest boundary in
`FRAMEWORKS.md` that the loop composition "spans four runtime invocations."

**Behavior.** `cdc run` bare resolves the manifest `entry=`/`entry-job=`;
`cdc run file.cdc [job]` is explicit. Core refactor: generalize
`run_universal`'s fused ordering into
`cdc_fused_execute(Runtime*, const char *source, const char *entry_job)` and
have both call sites use it. Optional `cycles=N` on the entry iterates the
fused loop, discharging the queued "unbounded cycle iteration" obligation —
cheap here because state carrying across cycles is already proven by the
existing two-cycle expectations (0.492228 / 1.333333 in
`framework_loop.cdc`).

**Framework.** `framework_runner.cdc` (H7,
`requires=select,fuse,carry,close,report`,
`permits=flow,commit,nest,guard,trace,measure,policy,bridge,counter,council,evolve,universal`).

**Verification.** Existing per-stage output lines unchanged; new summary line
`cdc run ok source=framework_loop.cdc stages=5 flow=4 commit=2 nest=2 status=accepted`.
Negative fixture: the existing coordinate-mismatch fixture run through
`cdc run` must yield `status=held reason=coordinate-mismatch` **and** produce
no enacted output file — proving the fused path inherits evolve's
no-write-on-mismatch guarantee.

**Size.** ~450 C, ~90 `.cdc`.

**Honest boundaries.** Fusion is sequential in one process; parallel `∥`
remains semantic; no wall clock.

---

## Phase 2 — Test runner: `cdc test` (H8)

**Goal.** Universal discovery for free: every `expect-*` attribute on every
declared job plus every `expect` line, across manifest members. Each file is
executed through every mode its directives require (contains `universal` →
universal mode; `council` → council; and so on), collecting per-check results
with typed reasons reusing the hold vocabulary (`expect-mismatch`,
`balance-violation`, `coordinate-mismatch`, `snapshot-mismatch`, ...).

**Result carrier.** Balanced ternary, not boolean: `+1` pass, `0` held or
skipped (equilibrium is first-class, not failure), `-1` fail.

**Tiers.**
- unit: inline `expect-*` job assertions;
- contract: framework completeness and registry closure;
- snapshot (`--replay`): byte-compare replay JSON against tracked goldens
  (extending the `demo/replay.json` pattern); `--update-snapshots`
  regenerates;
- property (`--prove`): the `proof` jobs' exhaustive 3^n enumeration
  (729/267/51/20/5 at n=6);
- formal: delegate to `lean` / `coqc` when present.

**Key C change.** `cdc_source.c` gains a collect-don't-die expectation mode
(`cdc_expect_set_collect(int)` plus a failure counter) so a single run reports
all failures; default abort behavior is unchanged for legacy verbs.

**Absorbing verify.sh (bash deletion gate).** The per-file grep blocks of
`verify.sh` are belt-and-braces duplicates of in-runtime `expect-*` checks,
so absorption is mostly deletion: add `build/cdc test --gate` (grep
`cdc test ok files=N jobs=M checks=K failures=0`), then delete grep blocks
framework-by-framework across commits. Kept in bash permanently: compiler
invocations, `assert_fresh_file` freshness checks, Lean/Coq/Tectonic, and the
Python-boundary check until Gate 5.

**Framework.** `framework_test.cdc` (H8,
`requires=discover,execute,check,report,snapshot,enumerate`), plus a tracked
`tests/fixtures/` directory of intentionally-failing `.cdc` files replacing
inline sed fixtures over time. The runner's own exemplar asserts the exact
fixture failure count (`expect-failures=3`) — the test runner tests itself.

**Size.** ~700 C, ~120 `.cdc`, net −300 shell.

**Honest boundaries.** No isolation/sandboxing beyond per-file runtime reset;
no timing; the proof tier is finite enumeration, not general model checking.

### Milestone v0.3.0 = Phases 0–2 (`cdc verify` + `cdc run` + `cdc test`)

---

## Phase 3 — Package manager: `cdc install` (H9)

**Goal.** Filesystem-path package sources first (example dependency
`packages/ternary-stats/` with its own `package.cdc`); git and network
registries are named queued host gates — the runtimes have no sockets and no
subprocess, and the mandate requires host powers to be declared, not assumed.

**Store and lockfile.** Store at `cdc_modules/<name>-<version>/` (invisible
to the boot glob — zero blast radius). Root `lock.cdc` is generated, tracked,
and freshness-checked like the codebooks:

```text
# lock.cdc -- generated by `cdc install`; do not edit by hand.
lock ternary-stats version=0.1.0 source=path:packages/ternary-stats files=4 checks=17 dyadic=101101100110 triadic=2646 status=latched reason=none
witness lock-ternary-stats invariant=dyadic-triadic-closure capability=H9 coordinate=101101100110 claim="ternary-stats 0.1.0 latched atomically; staged checks 17/17; coordinate verified against bridge4096"
expect witness lock-ternary-stats
```

Lock witnesses deliberately carry **no** `framework=`/`role=` attributes —
one lock entry per package would otherwise violate the one-witness-per-role
rule in the framework-contract checker; framework-less witnesses are ignored
by the closure check. Subtle, and required.

**Transactional install — the commit barrier, literally.** Each resolved
package contributes one trit: `+1` staged-and-validated, `-1` failed, `0`
pending. The install commit runs the nonnegative-prefix balance barrier over
the sequence: any failure holds the **entire** install with a typed reason
(`integrity-violation`, `closure-violation`, `missing-member`) and mutates
nothing; success latches via atomic `rename()` from `build/staging/` into
`cdc_modules/` plus the `lock.cdc` rewrite, using evolve's
declared-`output=`-only writer.

**Integrity model.** (a) The staged copy's own `expect-*`/`expect` surface is
re-executed via the Phase-2 checker; (b) `expect frameworks closed` over the
installed set united with the project — dependency closure as a first-class
check (no orphan witnesses); (c) the package's canonical serialized registry
folds to a 12-bit accumulator projected through `bridge4096` as a short
verifiable tag with an exact coordinate↔triadic inverse.

**Framework.** `framework_install.cdc` (H9,
`requires=resolve,stage,gate,latch,integrity,record,key,rollback`,
`permits=measure,trace,guard,commit,counter,bridge,flow,nest`).

**Verification.** `build/cdc install --check` dry-run parity: the regenerated
lock must match tracked `lock.cdc` (`assert_fresh_file`); grep
`cdc install ok packages=1 status=latched reason=none`. Negative fixtures:
(1) corrupted staged member → `status=held reason=integrity-violation`, store
and lock untouched; (2) atomicity fixture — two requires, second broken →
**neither** latched; (3) orphan-witness package → `closure-violation`.

**Size.** ~900 C, ~150 `.cdc`.

**Honest boundaries (verbatim commitments).** Bridge coordinates are **not
cryptographic hashes** — the 12-bit fold is lossy; the exact-inverse property
is coordinate↔triadic, not content↔coordinate. Integrity rests on semantic
re-execution of the package's own checks, with the coordinate as a short
verifiable tag. No registry protocol, no network, no semver ranges (exact
versions only), no dedup/hoisting.

---

## Phase 4 — Bundler: `cdc build` (H10)

**Goal.** Merge the manifest closure into one canonical `.cdc` artifact
(`build/<name>-bundle.cdc`): declaration-order-stable, comment-stripped,
one directive per line, emitted through evolve's writer with an appended
provenance witness carrying the bundle's bridge coordinate and the source
lock coordinates.

**Tree-shaking roots at witnesses, not jobs.** Reachability starts from the
entry framework's label: its witnesses → their linked jobs (via the witness
link-form relation already formalized in the bootloader) → the jobs'
referenced fields/modules/cells/channels/traces/councils, transitively. A
closure that would drop a witnessed job **refuses to build**
(`closure-violation`) rather than emit a bundle that fails
`expect framework complete`.

**Parity proof.** The bundle must survive `compile` + `interpret` + fused run
against the source with identical op counts, identical final-state snapshot,
and byte-identical replay JSON (`bundle-parity ops=N ok`) — a bundler that
demonstrates bundle ≡ source on every build, exploiting the
compile→IR→interpret parity the runtime already enforces.

**Framework.** `framework_build.cdc` (H10,
`requires=close,shake,serialize,key,enact,parity`,
`permits=trace,counter,bridge,evolve,compile,interpret`).

**Verification.** `build/cdc build` → grep
`cdc build ok members=N kept=K shaken=S coordinate=...`; the artifact must
contain the `bundle-provenance` witness; parity block asserted; freshness
check if the bundle is tracked. Negative fixtures: (1) hand-tampered bundle →
`cdc build --check` fails `reason=parity-mismatch`; (2) shaken-witness
fixture → refusal, not emission.

**Size.** ~800 C, ~120 `.cdc`.

**Honest boundaries.** Parity is runtime-checked equivalence per build, not a
semantic-preservation theorem (the theorem is queued in the matrix); no
minification or optimization; single package plus installed deps only.

---

## Phase 5 — Package runner: `cdc x <pkg>` (H11)

**Goal.** Resolve `<pkg>` from `cdc_modules/` (or `path:`), parse **only**
that package's manifest closure into a fresh ephemeral registry, run its
`entry-job` through the fused executor, and exit — never touching the current
project's registry, `lock.cdc`, or `package.cdc`. If absent from the store,
stage and validate to `build/x-cache/` with Phase-3 machinery, barrier-gated,
never latched into the store.

**Framework.** `framework_xrun.cdc` (H11,
`requires=resolve,isolate,execute,discard`,
`permits=guard,measure,flow,commit,counter`).

**Verification.** `build/cdc x ternary-stats` → grep
`cdc x ok package=ternary-stats entry=<job> status=accepted`. Isolation
negatives: `lock.cdc` and `package.cdc` byte-compared before/after (must be
untouched); `cdc x` of the broken fixture package → held with typed reason
and no store write.

**Size.** ~250 C, ~80 `.cdc`.

---

## Phase 6 — Consolidation and deletion gates

`verify.sh` shrinks to: compile runtimes → `build/cdc verify` (with the
Python parity assertion until Gate 5) → `build/cdc test --gate` →
`build/cdc install --check` → `build/cdc build --check` → freshness / formal
/ paper checks. `NATIVE_SELF_HOSTING_MANDATE.md` Gate-5 status records
`cdc verify` as the concrete `cdc_boot.py` replacement; the Python file is
deleted only after the parity gate has been green in CI for a full release
cycle, renegotiating `python-files == 1` to `== 0` in `kernel.cdc` as the
last, explicitly-approved kernel-contract change.

**Tag v0.4.0 = the full five-command toolchain.** A `scripts/build.sh`
producing the single `build/cdc` binary, a WASM build of the toolchain core
(extending `runtime/cdc_wasm_exports.c`), and a README quickstart switch to
`build/cdc run` / `build/cdc test` complete the "install `cdc`" story.

---

## Sequencing, sizes, risks

**Dependencies.** 0 → 1 → 2 serial (the v0.3.0 cut). Phase 3 depends on 0+2
(integrity reuses the test checker). Phase 4 depends on 0+1+3 (lock
coordinates in provenance). Phase 5 depends on 1+3. Parallelizable: Phase 3
and Phase 4's serializer can proceed alongside Phase 2; doc/matrix rows per
phase are independent.

**Totals.** ~3.6k new C (the driver stays a composition layer; core semantics
untouched), ~700 new `.cdc`, net-negative bash, ~60 gated Python lines (all
scheduled for deletion).

**Risk register.**

1. Un-static refactor of `cdc_native_runtime.c` perturbing output strings →
   rule: header extraction only, zero string changes; existing verify.sh
   greps are the regression suite.
2. Boot/C checker drift → the parity assertion compares pass/total counts on
   every CI run until deletion.
3. Overclaiming integrity (bridge key ≠ hash) → honest-boundary language
   fixed in Phase 3; cryptographic integrity stays out of every tier, queued
   as a host gate.
4. Kernel count-floor churn (`witnesses >= 4811`, `capabilities >= 38`)
   breaking CI mid-phase → bump floors in the same commit as each framework
   file; each phase lands atomically green.
5. Stealth host logic violating the mandate → every `cmd_*` must be
   directive-driven, consuming source-declared jobs and manifests like every
   existing mode; per-phase review question: "what `.cdc` line makes this
   behavior happen?"

## Honest Boundaries (whole plan)

- Bun parity is functional parity for the CDC ecosystem; `cdc` does not
  execute JavaScript, and no such claim is made.
- Network package registries, git-protocol fetching, and subprocess-based
  runners require host powers the runtimes do not have; each is a named
  queued host gate, not an assumed capability.
- Execution remains sequential in one process; parallel composition stays
  semantic.
- The self-hosted reducer (Mandate Gate 2) is not discharged by this plan;
  the plan narrows Gate 5 by making `cdc verify` the concrete bootloader
  replacement candidate.
- Nothing in this plan enters the proved tier of
  `VERIFICATION_OBLIGATION_MATRIX.md` without mechanization; all new claims
  land as witnessed or runtime-checked.
