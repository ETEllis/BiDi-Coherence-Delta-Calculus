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

The C runtime exposes the same rule with `codebook 9` and `codebook 12`. Larger
generated `.cdc` rows can follow, but the finite bridge rule is already checked
by the runtime.

## Gate 5 Status

This is a concrete Gate 5 pilot, not full host removal. The repo still uses
`cdc_boot.py` as the minimal declaration checker, but bridge execution no longer
depends on Python. The bridge has an operational consumer, a verified lookup
job, a trace-coordinate projection, and generated grid output. The companion
native runtime now handles source-declared reducer execution, compile-IR output,
and finite proof checking from `native_reducer.cdc`.
