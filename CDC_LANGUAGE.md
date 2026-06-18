# The `.cdc` Language
### Native source format for the Coherence-Delta Calculus

`.cdc` is the native language surface for the calculus kernel. A `.cdc` file is
a calculus term plus a schedule of reductions and proof obligations — nothing in
it is borrowed from any other programming language. Its meaning is fixed by the
kernel semantics
(`BIDI_CALCULUS_CORE.md`): **`flow` is continuous reduction `⟶_d`, `commit` is
guarded reduction `⟶_β`, `expect` is an assertion discharged against the term.**

The supplied implementation has exactly one non-`.cdc` execution artifact:
`cdc_boot.py`, the **transitional bootstrap bridge** that maps `.cdc` reduction
onto host hardware. It delegates semantics to the calculus and transitional
reducer, and is replaceable by any conforming bridge.

```
python3 cdc_boot.py kernel.cdc system.cdc laws.cdc
```

---

## Grammar

```ebnf
program     = { directive } ;
directive   = deadband | kernel | field | counter | top-expect ;

deadband    = "deadband" real ;

kernel      = "kernel" name [ "stage" "=" int ] [ "target" "=" name ] newline
                { kernel-stmt }
              "end" ;
kernel-stmt = "term" name
            | "rule" name
            | "provides" name { name }
            | "bootloader" name { name }
            | expect ;

field       = "field" name { kwarg } newline
                { field-stmt }
              "end" ;
field-stmt  = module | channel | nest | guard | flow | commit | expect ;

module      = "module" name "theta" real { real } [ "omega" real { real } ]
                                              [ "precision" real ]
                                              [ "prior" real{6} ] [ "act" real ]
            | "module" name "trits" pole pole pole pole pole pole ;
pole        = "+" | "-" | "o" ;                 (* +1 expansion, -1 localization, o equilibrium crossing *)

channel     = "channel" path "->" path { kwarg } [ "plastic" ] ;
nest        = "nest" name { kwarg } newline { module | channel } "end" ;
guard       = "guard" name "crossing" int ;
flow        = "flow" real ;                     (* ⟶_d : evolve continuously *)
commit      = "commit" ( name | "all" ) ;       (* ⟶_β : guarded discrete commit *)

counter     = "counter" name newline { reg | instr | run | expect } "end" ;
reg         = "reg" name int ;
instr       = "instr" name "inc"   name "->" name
            | "instr" name "jzdec" name "->" name "|" name
            | "instr" name "halt" ;
run         = "run" "from" name ;

expect      = "expect" predicate ;
top-expect  = "expect" "law" lawname ;

kwarg       = key "=" value ;                   (* e.g. gain=2.5 delay=0.7 open=yes *)
real        = number | "pi" | "pi/2" | "pi/4" | "3pi/2" | "tau" ;
path        = name { "/" name } ;
```

`#` begins a comment. Reals accept the circle literals `pi`, `pi/2`, … directly.
`lines=` is a comma-separated list of nonnegative target cell indexes.

---

## Constructs

| construct | calculus meaning |
|---|---|
| `field … end` | a coupled field term; `open=yes` lifts boundary gating (plain coupling), `open=no` keeps it (gated coupling) |
| `module m theta …` | a boundary module: the cell-vector by phase; `omega` sets intrinsic frequency, `precision`/`prior`/`act` arm predictive coding and active inference |
| `module m trits + - o …` | a module by committed/crossing poles |
| `channel a -> b` | a delayed weighted channel; `delay=τ`, `weight=w`, `angle=α`, `lines=0,2`, and `plastic` are supported |
| `channel P/c -> P` | a path-aware relation crossing nesting boundaries; endpoint depth determines up/down/lateral/diagonal orientation |
| `nest m … end` | attach a child field to module `m`; closing the block installs the `α=0` bidiγΔ up/down relation cone |
| `guard m crossing i` | arm an event: a `commit` fires when cell `i` reaches its crossing |
| `flow d` | continuous reduction `⟶_d` for real duration `d` |
| `commit m` / `commit all` | guarded reduction `⟶_β` (snap, barrier, belief, free-energy guard, latch) |
| `counter … end` | a universality term: registers + instruction modules executed by generic commits |
| `kernel … end` | native self-hosting contract: names calculus terms, reducer rules, capabilities, and the shrinking host-loader boundary |

---

## Assertions (`expect`)

Discharged by the bridge against the running term:

```
expect coherence-global >= 0.85       expect admissible M
expect coherence X >= 0.9             expect localized M
expect address M == 27                expect delay W D 0.7
expect belief G near 1.0 0.1          expect weight a b > 0.6
expect events-offgrid                 expect multirate >= 4
expect interference A B cos <= -0.9   expect interference P/c P gamma >= 0.5
expect reg c1 == 7                     (inside a counter)
expect law balanced-ternary-carrier | dyadic-triadic-closure
expect law gate-abelian | interfere-monoid | rotation-linear | corefold-morphism
expect law preservation | soundness | local-confluence | flow-additivity | normalforms
```

---

## Self-hosting

`.cdc` is computationally universal in the standard two-counter sense: the
`counter` form executes register-machine programs by generic commits
(`system.cdc` runs addition and multiplication this way). This gives a precise path
to self-hosting: a `.cdc` reducer can be encoded as `.cdc` data and execution rules.
Until that reducer is written, `cdc_boot.py` remains the executable bridge rather
than a semantic dependency.

The project target is stronger than "a host bridge can run `.cdc`." The target
is native `.cdc` self-hosting: parser state, reducer state, witness state, and
trace/window measurement state must become representable as `.cdc` terms. The
host bridge is transitional debt with an explicit removal plan in
`NATIVE_SELF_HOSTING_MANDATE.md`.

The committed discrete carrier is balanced ternary, not Boolean:

```text
-1  inward localization / contraction
 0  resting equilibrium / open crossing
+1  outward expansion / dissipation
```

`kernel.cdc` also pins the 64-state dyadic/triadic bridge constraint
(`2^6 = 4^3 = 64`) as native source for future bootloader design.

---

## The complete system, in `.cdc`

| file | content |
|---|---|
| `system.cdc` | continuous dynamics, delay lines, hybrid events, multirate nesting, predictive coding, plasticity, normal-form commits, two-counter universality |
| `laws.cdc` | the operator algebra (`⊙ ⊞ ⟳ ∂`) and metatheorems (T1 preservation, T2 soundness, T5 normal forms) as proof obligations |
| `relations.cdc` | angular phase, dimension projection, and cross-scale path relation witnesses |
| `kernel.cdc` | native self-hosting contract for terms, rules, capabilities, balanced ternary, and bootloader shrinkage |
| `examples/*.cdc` | showcase programs |
| `cdc_boot.py` | transitional bootstrap bridge (not the language; targeted for removal) |

`BIDI_CALCULUS_CORE.md` is the canonical semantics; this document is the source format that denotes it.
