# Operational Bridge Runtime

`bridge64.cdc` is now consumed as data by a non-Python runtime:

```text
runtime/cdc_bridge_runtime.c
```

The runtime does not embed the 64-row table. It reads `bridge64.cdc`, parses each
`witness bridge64-*` row, builds the table in memory, and rejects the source if:

- the table does not contain exactly 64 rows;
- a dyadic six-bit code is duplicated or malformed;
- a triadic three-digit base-4 code is duplicated or malformed;
- an index is duplicated or out of range;
- any row fails the canonical mapping between six binary bits and three base-4
  slots.

## Commands

```bash
cc -std=c99 -Wall -Wextra -pedantic -O2 \
  runtime/cdc_bridge_runtime.c \
  -o build/cdc_bridge_runtime

build/cdc_bridge_runtime verify bridge64.cdc
build/cdc_bridge_runtime lookup-dyadic bridge64.cdc 101011
build/cdc_bridge_runtime lookup-triadic bridge64.cdc 223
build/cdc_bridge_runtime project-trits bridge64.cdc '+0-+0-' council
build/cdc_bridge_runtime run-jobs bridge64.cdc bridge_jobs.cdc
build/cdc_bridge_runtime grid bridge64.cdc
build/cdc_bridge_runtime grid-svg bridge64.cdc > build/bridge64-grid.svg
build/cdc_bridge_runtime codebook 9
build/cdc_bridge_runtime codebook 12
build/cdc_bridge_runtime emit-codebook 9 > build/bridge512.cdc
build/cdc_bridge_runtime emit-codebook 12 > build/bridge4096.cdc
build/cdc_bridge_runtime verify-codebook bridge512.cdc 9
build/cdc_bridge_runtime verify-codebook bridge4096.cdc 12
```

`project-trits` gives the bridge a real trace-coordinate job. It projects a
six-trit trace or field slice into committed occupancy:

```text
+ or - -> 1
0 or o -> 0
```

That occupancy vector is then looked up in `bridge64.cdc`. This is not a lossless
encoding of the full `3^6` balanced-ternary state. It is the bridge coordinate
for committed/non-open occupancy, which is exactly the finite `2^6 = 4^3`
surface the codebook names.

`bridge_jobs.cdc` declares source-level jobs for the runtime to execute. The
current jobs cover a council channel and a trace window. Verification fails if
the projected coordinate does not match the expected dyadic and triadic values.

## Higher-Arity Growth

`bridge_codebooks.cdc` declares the extension rule:

```text
n = 3k
2^n = (2^k)^3
```

The first declared growth targets are:

```text
n=9:  2^9  = 8^3  = 512
n=12: 2^12 = 16^3 = 4096
```

The C runtime exposes the same rule with `codebook 9` and `codebook 12`, emits
the complete generated rows with `emit-codebook`, and verifies the tracked
`bridge512.cdc` and `bridge4096.cdc` files with `verify-codebook`. The full
generated higher-arity rows are therefore part of the checked source tree, not
only a declared growth rule.

## Interactive Bridge Grid

`grid-svg` emits the visible bridge coordinate grid as an interactive SVG. Each
cell carries bridge metadata (`data-index`, `data-dyadic`, `data-triadic`, and
`data-witness`), focus/hover affordances, a title, and a small script that
updates the selected bridge coordinate. `./scripts/verify.sh` regenerates the
SVG and rejects the tracked asset if the interactive output drifts.

## Gate 5 Status

This is a concrete Gate 5 pilot, not full host removal. The repo still uses
`cdc_boot.py` as the minimal declaration checker, but bridge execution no longer
depends on Python. The bridge has an operational consumer, verified lookup jobs,
trace-coordinate projection, generated higher-arity codebooks, and an
interactive grid asset. The companion native runtime now handles source-declared
reducer execution, compile-IR output, IR interpretation, finite proof checking,
council deliberation, and bridge-coordinate source evolution from `.cdc`.
