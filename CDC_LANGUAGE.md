# The `.cdc` Language
### Native source format for the Coherence-Delta Calculus

`.cdc` is the native language surface for the calculus kernel. In v0.2.0 the
checked surface is a native declaration and witness format: terms, reducer
rules, invariants, capabilities, witnesses, and expectations are expressed in
`.cdc`; Python is limited to the small `cdc_boot.py` loader/checker.

The semantic target remains the full calculus:

```text
flow(d)       continuous reduction
commit(m)     guarded balanced-ternary event reduction
nest(m,F)     nested bidirectional coherence-delta coupling
trace/window  derived observer projection
```

The bootloader does not implement those reductions. It verifies that the native
source tree declares them and that every claim has a native witness handle.

## Current Checked Grammar

```ebnf
program      = { directive } ;
directive    = kernel | term | rule | provides | bootloader
             | invariant | law | capability | witness | expect | "end" ;

kernel       = "kernel" name { kwarg } ;
term         = "term" name { name } ;
rule         = "rule" name { name } ;
provides     = "provides" name { name } ;
bootloader   = "bootloader" name { name } ;

invariant    = "invariant" key { kwarg } ;
law          = "law" key { kwarg } ;
capability   = "capability" key { kwarg } ;
witness      = "witness" key { kwarg } ;

expect       = "expect" predicate ;
kwarg        = key "=" value ;
```

`#` begins a comment. Values may be quoted with shell-style quoting.

## Native Expectation Predicates

The minimal bootloader currently verifies:

```text
expect native substrate == cdc
expect host-debt <= 1
expect python-files == 1
expect bootloader minimal == true
expect terms >= N
expect rules >= N
expect invariants >= N
expect witnesses >= N
expect capabilities >= N
expect provides <capability...>
expect law <invariant-key>
expect capability <capability-key>
expect witness <witness-id>
```

`expect law K` requires both an `invariant K` declaration and at least one native
`witness ... invariant=K`. `expect capability C` requires both a
`capability C` declaration and at least one native `witness ... capability=C`.

## Native Files

| file | content |
|---|---|
| `kernel.cdc` | language terms, reducer rules, provided capabilities, bootloader boundary, and global expectations |
| `laws.cdc` | invariant registry and 22 law/metatheorem witness declarations |
| `system.cdc` | 24 capability declarations and native witness handles |
| `relations.cdc` | angular, projected, cross-scale, detuning, and overlap relation witness handles |
| `trace_windows.cdc` | balanced-ternary trace/window, local-counter, coupled-observer, and recursive-policy witness handles |
| `cdc_boot.py` | minimal loader/checker; not the reducer or language semantics |

## Balanced Ternary Carrier

The committed discrete carrier is balanced ternary, not binary:

```text
-1  inward localization / contraction
 0  resting equilibrium / open crossing
+1  outward expansion / dissipation
```

The middle value is a real equilibrium/crossing state. It is not false, null, or
absence.

## Full Semantic Syntax Target

The following forms remain the semantic target for the native reducer:

```text
field <name> dt=<real> gain=<real>
module <name> theta <theta...>
module <name> trits <pole...>
channel <path-a> -> <path-b> delay=<real> weight=<real> angle=<real> lines=<i,j>
guard <name> crossing <i>
flow <real>
commit <name>
counter <name>
trace <window>
measure <observer> <target>
policy <window> sampling=<mode> commit=<mode> adapt=<mode>
```

Those forms are part of the calculus language design. They should be reintroduced
as native reducer clauses in `.cdc`, not by growing Python back into a runtime.
