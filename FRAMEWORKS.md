# Native Task Frameworks

The kernel gives the calculus its verbs: `flow`, `commit`, `nest`, `guard`,
`trace`, `measure`, `policy`, `bridge`, `counter`, `compile`, `interpret`,
`council`, `evolve`. This layer gives those verbs task-shaped names. Each
framework is a **binding plus an executed exemplar**, not new machinery:

- no new grammar directives;
- no new host code (`cdc_boot.py` and the C runtimes are untouched);
- every binding witness links to a job the C native runtime actually executes;
- every exemplar ships with deterministic expectations checked by
  `./scripts/verify.sh`.

A framework file therefore has three sections: a capability registry entry
(`H1`–`H4`), a runnable exemplar with `expect-*` values, and binding witnesses
whose `framework=`/`role=` attributes name the pattern while their job links
(`guard=`, `reducer=`, `trace=`, `measure=`, `policy=`, `bridge=`, `counter=`,
`compile=`, `interpret=`, `council=`, `evolution=`) keep every claim attached
to executed behavior.

## The Generic Task Loop

The four frameworks are named slices of one loop that the kernel already
executes end to end:

```text
sense        flow        continuous phase motion
gate         guard       open/closed precondition on a crossing cell
act          commit      guarded balanced-ternary event (accepted/held)
integrate    nest        child coherence up, parent context down
record       trace       window-local ternary content, no global tick
consolidate  bridge      occupancy -> dyadic/triadic coordinate (a key)
decide       council     member trits -> quorum -> one coordinate
enact        evolve      decision written into durable source memory
refine       policy      recursive window adaptation
```

The balanced-ternary carrier is the shared alphabet throughout:
`+1` advance/outward, `0` hold/open crossing, `-1` withdraw/inward.

## Transition Framework (`framework_transition.cdc`, capability `H1`)

The catch-all for action, state change, and transitional dynamics.

| role | primitive | exemplar job |
|---|---|---|
| precondition | `guard` open state | `transition-guard` |
| action | `flow` phase motion | `transition-action` |
| fired transition | accepted `commit` | `transition-fire` |
| blocked transition | held `commit` + reason | `transition-blocked` |
| hierarchy | `nest` | `transition-lift` |
| transition log | `trace` | `transition-trace` |
| observation | `measure` | `transition-measure` |
| transition policy | `policy` | `transition-policy` |
| state key | `bridge` coordinate | `transition-bridge` |
| tally | `counter` | `transition-counter` |

A machine configuration is a committed module; its six-trit field trace
projects to one `bridge64` coordinate, so every machine state has a canonical
64-state key. Illegal transitions are held with `balance-violation` rather
than mutating state — retry semantics are native, not bolted on.

```bash
build/cdc_native_runtime run framework_transition.cdc
build/cdc_native_runtime surface framework_transition.cdc
```

## Procedural Framework (`framework_procedural.cdc`, capability `H2`)

Procedural memory: skills as ordered, compilable, refinable step sequences.

| role | primitive | exemplar job |
|---|---|---|
| cue | `flow` | `procedural-cue` |
| executed step | accepted `commit` | `procedural-execute` |
| retry | held `commit` | `procedural-retry` |
| consolidation | `nest` belief integration | `procedural-consolidate` |
| proceduralization | `compile` source -> reducer IR | `procedural-ir` |
| skilled execution | `interpret` IR path | `procedural-ir-exec` |

The classic declarative-to-procedural conversion is literal here: the same
declarative `.cdc` source compiles into reducer IR and then executes through
the interpreter path, with identical checked outcomes on both paths.

```bash
build/cdc_native_runtime run framework_procedural.cdc
build/cdc_native_runtime compile framework_procedural.cdc
build/cdc_native_runtime interpret framework_procedural.cdc
```

## Episodic Framework (`framework_episodic.cdc`, capability `H3`)

Episodic memory: record, consolidate, recall, replay.

| role | primitive | exemplar job |
|---|---|---|
| lived episode | `flow` | `episodic-live` |
| record | accepted `commit` | `episodic-record` |
| consolidation | `nest` into the archive | `episodic-consolidate` |
| recording aperture | `guard` open state | `episodic-guard` |
| episode content | `trace` window | `episodic-trace` |
| recall | committing `measure` | `episodic-recall` |
| recording policy | `policy` | `episodic-policy` |
| memory key | `bridge` coordinate | `episodic-key` |
| episode order | local `counter` | `episodic-ordinal` |

An episode is a window-local ternary trace — episode order needs no global
clock because trace time is window-relative (`trace-order-locality`). The
committed trace consolidates through `bridge64` into a content-addressable
coordinate, and recall runs both directions through the codebook: content
(`110011`) to key (`303`) and key back to content. The `replay` runtime verb
is the re-experience path for recorded reducer output.

```bash
build/cdc_native_runtime run framework_episodic.cdc
build/cdc_native_runtime surface framework_episodic.cdc
build/cdc_bridge_runtime lookup-dyadic bridge64.cdc 110011   # recall by content
build/cdc_bridge_runtime lookup-triadic bridge64.cdc 303     # recall by key
```

## Deliberative Framework (`framework_deliberative.cdc`, capability `H4`)

Decision and agency: deliberate, decide, enact, remember.

| role | primitive | exemplar job |
|---|---|---|
| options | modules | `option-a`, `option-b`, `option-c` |
| deliberation | `council` + `deliberate` quorum | `deliberative-quorum` |
| decision | one bridge coordinate | `111101` -> `331` |
| enactment | `evolve` source write | `deliberative-enactment` |

Option trits project into one occupancy word; the decision is adopted only at
quorum. The adopted coordinate is then enacted by writing a decision-memory
witness into a source copy — deliberation ends in durable source memory, not
a transient outcome. The gate requires the appended witness line itself, so
enactment cannot be satisfied by the copy alone.

```bash
build/cdc_native_runtime council framework_deliberative.cdc
build/cdc_native_runtime evolve framework_deliberative.cdc
```

## Writing Your Own Instance

1. Declare state with existing forms: `field`, `module`, `cell`, `channel`.
2. Pick the loop slices you need and declare their jobs with `expect-*`
   values computed from the kernel semantics (trit of a cell is `cos(theta)`
   against the field deadband; commits walk cells in declaration order under
   the nonnegative-balance barrier; a traced field needs exactly six cells to
   project through `bridge64`).
3. Add one binding witness per role, linked to its job, and `expect` lines so
   `cdc_boot.py` enforces the linkage.
4. Execute the file through the matching runtime modes and wire the checked
   output into `scripts/verify.sh`.

## Honest Boundaries

Framework claims live in the `witnessed` and `runtime-checked` tiers of
`VERIFICATION_OBLIGATION_MATRIX.md`, never in `proved`. Explicitly queued, not
claimed:

- **No persistent episode store.** Episodes persist within a run and through
  `evolve`-written source copies; there is no cross-run store or retrieval
  index beyond the finite codebooks.
- **No learned parameters.** Consolidation updates belief/prior state through
  declared dynamics; nothing is fitted.
- **Recall is codebook lookup**, exact and finite — not similarity-based or
  reconstructive retrieval.
- **Procedure IR is bounded** to `flow`/`commit`/`nest` op kinds; richer
  procedure control flow is a reducer-semantics obligation, not a framework
  patch.
- **Council/evolve generalization** into the main reducer and trace/window
  policy layer remains queued in the matrix, unchanged by this layer.

## Registry

| capability | framework | file |
|---|---|---|
| `H1` | transition | `framework_transition.cdc` |
| `H2` | procedural | `framework_procedural.cdc` |
| `H3` | episodic | `framework_episodic.cdc` |
| `H4` | deliberative | `framework_deliberative.cdc` |

The kernel contract requires all four through `provides`/`expect provides`
(`transition-framework procedural-framework episodic-framework
deliberative-framework`) and the raised capability and witness floors in
`kernel.cdc`.
