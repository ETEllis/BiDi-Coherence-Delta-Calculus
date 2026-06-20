# Native Self-Hosting Mandate

This repository is not finished while the executable center is a host language.

The intended end state is:

```text
.cdc source
  -> .cdc parser/reducer expressed in .cdc
  -> .cdc witnesses expressed in .cdc
  -> minimal host loader only until the native reducer can run directly
```

Python remains only as the bootstrap loader because it is portable and easy to
inspect. It is not the language, not the calculus, and not the semantic
substrate.

## Current Host Boundary

As of v0.2.0, host code is restricted to one file:

- `cdc_boot.py`: minimal loader/checker for native `.cdc` declarations.

All reducer semantics, invariants, capability claims, and witness obligations
must be expressed as `.cdc` declarations. The bootloader may parse, collect, and
check expectations; it may not become the reducer or witness suite.

The minimal bootloader target for the Python phase is:

```text
read .cdc source -> parse lines -> collect native declarations/obligations
                 -> verify expectations -> report
```

Anything beyond that reintroduces host debt unless it has a named native removal
gate.

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
resting equilibrium and an open crossing state, not binary false or absence.
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

Acceptance: native `.cdc` can declare and verify the same term, rule, invariant,
capability, and witness objects without a Python semantic registry.

### Gate 2: Native Reducer Kernel

Encode the reducer as `.cdc` transition rules over explicit state records.

Acceptance: native `.cdc` owns `kernel.cdc`, `system.cdc`, `laws.cdc`,
`relations.cdc`, and trace/window witness scenarios through the native contract.

### Gate 3: Native Witness Harness

Move law, relation, acceptance, and trace/window witnesses into `.cdc`.

Status: complete for v0.2.0. Verification now invokes `.cdc` files and checks
their declared expectations.

### Gate 4: Host Loader Collapse

Collapse former reducer, semantic-registry, law, acceptance, relation, and
trace/window host modules into native `.cdc` sources.

Status: complete for v0.2.0. The only remaining host artifact is `cdc_boot.py`,
and its behavior is fully specified by `kernel.cdc` expectations.

### Gate 5: Host Removal Or Replacement

Replace the remaining host loader with a smaller neutral bootstrap target or
native executable path.

Candidate directions:

- a tiny C/Zig/Rust loader;
- a WASM runtime;
- a generated standalone reducer from `.cdc`;
- a theorem-prover-extracted kernel;
- a direct native binary once `.cdc` has a compiler path.

Acceptance: the repository can verify the language without expanding beyond the
minimal bootloader.

## Immediate Rule

From this point forward, new behavior must be added first as `.cdc` source or
as native-semantics documentation. Host code may only appear inside
`cdc_boot.py`, and only when paired with a named native deletion gate.

The project is allowed to use a bootloader. It is not allowed to confuse the
bootloader with the language.
