# Native Self-Hosting Mandate

This repository is not finished while the executable center is a host language.

The intended end state is:

```text
.cdc source
  -> .cdc parser/reducer expressed in .cdc
  -> .cdc witnesses expressed in .cdc
  -> minimal host loader only until the native reducer can run directly
```

Python currently remains a transitional bootstrap and verification host. It is
not the language, not the calculus, and not an acceptable final substrate.

## Current Host Debt

As of v0.1.2, host code still provides:

- `bidi_calculus.py`: transitional reducer and runtime objects;
- `cdc_boot.py`: bootstrap bridge from `.cdc` source to the reducer;
- `cdc_semantics.py`: declarative AST, state, invariant, and trace/window records;
- `calculus_laws.py`: law and metatheorem witnesses;
- `acceptance.py`: capability witnesses;
- `relation_witness.py`: angular/path relation witnesses;
- `trace_window_witness.py`: ternary trace/window witnesses.

That is useful construction scaffolding, not the target architecture.

## Non-Negotiable Direction

The language must become native in its own source language:

- `.cdc` must express the core term syntax;
- `.cdc` must express flow, commit, nest, relation, trace, window, and measure
  semantics;
- `.cdc` must express its own witness programs;
- `.cdc` must express the reducer transition rules well enough that the host
  loader becomes mechanical and replaceable;
- no foundational behavior may depend on host-object semantics.

The discrete layer is balanced ternary: `-1 / 0 / +1`. The middle value is
resting equilibrium and an open crossing state, not Boolean false or absence.
Self-hosting must preserve this equilibrium-centered carrier.

## Required Burn-Down Gates

Do not remove host files by breaking the executable artifact. Remove them only
when the native replacement is green.

### Gate 1: Native Core Terms

Add `.cdc` forms for declaring the semantic spine itself:

```text
cell
module
channel
field
commit-rule
flow-rule
nest-rule
relation-rule
window-rule
measure-rule
bridge-rule
```

Acceptance: native `.cdc` can parse and represent the same objects named in
`cdc_semantics.py`.

### Gate 2: Native Reducer Kernel

Encode the reducer as `.cdc` transition rules over explicit state records.

Acceptance: native `.cdc` runs at least `kernel.cdc`, `system.cdc`, `laws.cdc`,
`relations.cdc`, and trace/window witness scenarios through the native kernel.

### Gate 3: Native Witness Harness

Move law, relation, acceptance, and trace/window witnesses into `.cdc`.

Acceptance: host test code is only a loader that invokes `.cdc` witness files and
checks their declared expectations.

### Gate 4: Host Loader Collapse

Collapse `bidi_calculus.py`, `cdc_semantics.py`, `calculus_laws.py`,
`acceptance.py`, `relation_witness.py`, and `trace_window_witness.py` into native
`.cdc` sources.

Acceptance: the only remaining host artifact is a minimal loader whose behavior
is fully specified by `.cdc`.

### Gate 5: Host Removal Or Replacement

Replace the remaining host loader with a smaller neutral bootstrap target or
native executable path.

Candidate directions:

- a tiny C/Zig/Rust loader;
- a WASM runtime;
- a generated standalone reducer from `.cdc`;
- a theorem-prover-extracted kernel;
- a direct native binary once `.cdc` has a compiler path.

Acceptance: the repository can verify the language without the transitional
Python host.

## Immediate Rule

From this point forward, new behavior should be added first as `.cdc` source or
as native-semantics documentation. Host code may only appear as a temporary
bridge when paired with a named native deletion gate.

The project is allowed to use a bootloader. It is not allowed to confuse the
bootloader with the language.
