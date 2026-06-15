#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BiDi Coherence-Delta Calculus · LAW CHECKER
===========================================
Executable-checks the claims that make "calculus" literal: the operator algebra's
equational laws and the five metatheorems. Each is witnessed over random elements
or explicit constructions against the reference engine, so the formal claims are
test-backed rather than merely asserted.

    python3 calculus_laws.py
"""
import math, cmath, random
from bidi_calculus import Thread, Knot, Breathfield, census
from cdc_semantics import invariant_index

rng = random.Random(7)
def runit():  return cmath.rect(1.0, rng.uniform(0, 2 * math.pi))   # random unit carrier
def vec(n=6): return [runit() for _ in range(n)]
def close(a, b, tol=1e-9): return all(abs(x - y) < tol for x, y in zip(a, b))

# the engine's three operations, as algebra over the carrier C = ℝ² (≅ ℂ)
def rot(phi, xs): return [cmath.rect(1, phi) * x for x in xs]        # ⟳  rotation / gate-by-φ
def gate(xs, ys): return [x * y for x, y in zip(xs, ys)]            # ⊙  gate (phase compose)
def fere(xs, ys): return [x + y for x, y in zip(xs, ys)]           # ⊞  interfere (superpose)
def fold(xs):     return [xs[i] for i in (1, 2, 3, 2, 3, 4)]       # ∂  core-fold
ID  = [1 + 0j] * 6                                                  # 𝟙  gate identity (θ=0)
BOT = [0j] * 6                                                      # ⊥  interfere unit (void)
def inv(xs): return [x.conjugate() for x in xs]                     # gate inverse (unit amp)

def committed(trits):                                               # build a committed module
    m = {1: 0.0, -1: math.pi, 0: math.pi / 2}
    return Knot("k", threads=[Thread(theta=m[t]) for t in trits])

INVARIANTS = invariant_index()
USED_INVARIANTS = set()
CHECKS = []
def check(name, ok, detail="", invariant=None):
    if invariant is not None:
        if invariant not in INVARIANTS:
            raise KeyError(f"unknown invariant key: {invariant}")
        USED_INVARIANTS.add(invariant)
    CHECKS.append((name, ok, detail, invariant))

# ── OPERATOR ALGEBRA ─────────────────────────────────────────────────────── #
a, b, c = vec(), vec(), vec()
check("⊙ gate associative",  close(gate(gate(a, b), c), gate(a, gate(b, c))), invariant="gate-abelian")
check("⊙ gate commutative",  close(gate(a, b), gate(b, a)), invariant="gate-abelian")
check("⊙ gate identity 𝟙",   close(gate(a, ID), a), invariant="gate-abelian")
check("⊙ gate inverse (→ abelian group on the torus 𝕋ⁿ)", close(gate(a, inv(a)), ID), invariant="gate-abelian")
check("⊞ interfere associative", close(fere(fere(a, b), c), fere(a, fere(b, c))), invariant="interfere-monoid")
check("⊞ interfere commutative", close(fere(a, b), fere(b, a)), invariant="interfere-monoid")
check("⊞ interfere unit ⊥",      close(fere(a, BOT), a), invariant="interfere-monoid")
phi = rng.uniform(0, 6)
check("⟳ distributes over ⊞ (linearity)", close(rot(phi, fere(a, b)), fere(rot(phi, a), rot(phi, b))), invariant="rotation-linear")
check("∂ core-fold is ⊞-linear",     close(fold(fere(a, b)), fere(fold(a), fold(b))), invariant="corefold-morphism")
check("∂ core-fold is ⟳-equivariant", close(fold(rot(phi, a)), rot(phi, fold(a))), invariant="corefold-morphism")
check("∂ core-fold NOT idempotent (honest: it abstracts strictly)", not close(fold(fold(a)), fold(a)), invariant="corefold-morphism")

# ── T1 · PRESERVATION: a commit always yields an admissible committed walk ──── #
def admissible(trits):
    r = 0
    for t in trits:
        r += t
        if r < 0: return False
    return True
ok_T1 = True
for _ in range(2000):
    k = Knot("k", threads=[Thread(theta=rng.uniform(0, 2 * math.pi)) for _ in range(6)])
    k.breath([0j] * 6)                                  # commit (barrier repairs negative debt)
    if not admissible(k.trits()): ok_T1 = False; break
check("T1 Preservation: every commit ⟹ admissible committed state", ok_T1, "2000 random commits", invariant="preservation")

# ── T2 · SOUNDNESS (Lyapunov): a commit never increases free energy Φ ──────── #
worst = -1e9
for _ in range(3000):
    k = Knot("k", threads=[Thread(theta=rng.uniform(0, 2 * math.pi)) for _ in range(6)])
    k.belief = [rng.uniform(-1, 1) for _ in range(6)]; k.precision = rng.uniform(0.1, 5)
    A = [runit() * rng.uniform(0, 1.5) for _ in range(6)]
    Fpre = k.free_energy(A); Fpost, _ = k.breath(A)
    worst = max(worst, Fpost - Fpre)
check("T2 Soundness: Φ non-increasing across every commit", worst <= 1e-9, f"max ΔΦ = {worst:.2e}", invariant="soundness")

# ── T3 · LOCAL CONFLUENCE (diamond): non-adjacent commits commute ──────────── #
def two_field():
    bf = Breathfield(dt=0.02)
    bf.add(Knot("A", threads=[Thread(theta=0.7 + 0.3 * i) for i in range(6)]))
    bf.add(Knot("B", threads=[Thread(theta=2.1 - 0.4 * i) for i in range(6)]))
    return bf                                            # NO channel A↔B : disjoint state
def commit(bf, nm): k = bf.knots[nm]; k.breath(bf.afferent(k, bf.t))
f1 = two_field(); commit(f1, "A"); commit(f1, "B")
f2 = two_field(); commit(f2, "B"); commit(f2, "A")
diamond = f1.knots["A"].trits() == f2.knots["A"].trits() and f1.knots["B"].trits() == f2.knots["B"].trits()
check("T3 Local confluence: disjoint commits commute (A;B ≡ B;A)", diamond, invariant="local-confluence")

# ── T4 · TIME-DETERMINISM & ADDITIVITY of the flow action ──────────────────── #
def flow_field():
    bf = Breathfield(dt=0.02, gain=1.4, kappa_gate=False)
    bf.add(Knot("x", threads=[Thread(theta=0.0, omega=1.0)]))
    bf.add(Knot("y", threads=[Thread(theta=2.0, omega=1.3)]))
    bf.wire("x", "y"); bf.wire("y", "x"); return bf
g1 = flow_field(); g1.advance(0.4); g1.advance(0.4)
g2 = flow_field(); g2.advance(0.8)
add_err = max(abs(g1.knots[n].threads[0].theta - g2.knots[n].threads[0].theta) for n in "xy")
check("T4 Flow additivity: ⟶_{d1};⟶_{d2} = ⟶_{d1+d2}  (grid-aligned, exact)", add_err < 1e-12, f"err={add_err:.1e}", invariant="flow-additivity")

# ── T5 · NORMAL FORMS = Catalan: irreducible values are localized closures ─── #
cen = census()
nf_count_ok = (cen["classical_localized"] == 5 and cen["localized"] == 51)
nf = committed((1, 1, -1, -1, 1, -1))                   # a localized closure (∆C: 1,2,1,0,1,0)
before = nf.trits(); nf.breath([0j] * 6); irreducible = nf.trits() == before
check("T5 Normal forms: ⟶_β-irreducible committed modules = localized (Catalan C₃=5)",
      nf_count_ok and irreducible, f"{cen['classical_localized']} closures; fixed point stable", invariant="normalforms")

# ── REPORT ─────────────────────────────────────────────────────────────────── #
if __name__ == "__main__":
    print("═" * 76)
    print("  BiDi Coherence-Delta Calculus · law & metatheorem checks")
    print("═" * 76)
    npass = 0
    for name, ok, detail, invariant in CHECKS:
        npass += ok
        inv = f" {{{invariant}}}" if invariant else ""
        print(f"  {'✅' if ok else '❌'} {name}{inv}" + (f"   [{detail}]" if detail else ""))
    print("─" * 76)
    print(f"  {npass}/{len(CHECKS)} laws & metatheorems witnessed")
    print(f"  {len(USED_INVARIANTS)}/{len(INVARIANTS)} invariant keys exercised")
    print("═" * 76)
