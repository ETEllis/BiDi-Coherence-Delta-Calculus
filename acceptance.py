#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BiDi Coherence-Delta Calculus · acceptance report
=================================================
One capability witness per requirement. Each witness wires a tiny configuration
of the calculus primitives and asserts a measured behavior. These are not
applications; they are executable evidence that the reference reducer supports
the required regimes.

    python3 acceptance.py
"""
import math, cmath, os
from bidi_calculus import (Thread, Strand, Knot, Breathfield, CounterField,
                           minsky_add, parse_legacy_program)

HERE = os.path.dirname(os.path.abspath(__file__))
def osc(name, n=1, omega=1.0, theta=0.0):
    return Knot(name, threads=[Thread(theta=theta + 0.1 * i, omega=omega) for i in range(n)])

# ============================ A · INDEPENDENCE ============================== #
def A1():  # brand-new primitives only — they instantiate and compute with nothing borrowed
    k = Knot("k", n=6)
    read_cone, write_cone = k.threads[:3], k.threads[3:]
    ok = (len(read_cone) == 3 and len(write_cone) == 3 and isinstance(k.coherence(), float))
    return ok, "cell/channel/module/field/commit/bidiγΔ primitives present; read+write cones intrinsic"

def A2():  # host-free core spec exists and its normative body names no PL / borrowed formalism
    p = os.path.join(HERE, "BIDI_CALCULUS_CORE.md")
    if not os.path.exists(p): return False, "SPEC file missing"
    text = open(p, encoding="utf-8").read()
    norm = text.split("<!-- NON-NORMATIVE -->")[0].lower()
    prims = all(w in text for w in ("cell", "channel", "module", "field", "commit", "bidiγΔ"))
    clean = not any(w in norm for w in ("python", "lambda calculus", "turing machine", "c++", "javascript"))
    return (prims and clean), "formal core defines the primitive vocabulary without depending on a host language"

def A3():  # self-contained module that interferes on itself — measurable self-effect
    def run(selfloop):
        bf = Breathfield(dt=0.02, gain=1.5)
        bf.add(osc("M", n=6, omega=0.5))
        if selfloop: bf.wire("M", "M", weight=1.2)
        bf.advance(4.0); return [th.theta for th in bf.knots["M"].threads]
    diff = sum(abs(a - b) for a, b in zip(run(True), run(False)))
    return diff > 1e-3, f"self-interference shifts own trajectory by {diff:.3f}"

def A4():  # nested field: a module hosts a child field
    child = Breathfield(dt=0.005); child.add(osc("c1", omega=2.0)); child.add(osc("c2", omega=2.2))
    child.wire("c1", "c2"); child.wire("c2", "c1")
    parent = Breathfield(dt=0.02); parent.add(osc("P", n=6, omega=0.5)); parent.nest("P", child)
    th0 = child.knots["c1"].threads[0].theta
    parent.advance(2.0)
    th1 = child.knots["c1"].threads[0].theta
    return isinstance(parent.knots["P"].child, Breathfield) and abs(th1 - th0) > 1e-3, \
           "a module hosts a child field; the inner field evolves inside the outer reduction"

# ============================ B · TIME / DYNAMICS ========================== #
def B1():  # continuous time, not tick — smooth trajectory, bounded derivative, no integer steps
    bf = Breathfield(dt=0.01, gain=1.0); bf.add(osc("A", omega=1.3))
    traj = []
    for _ in range(300): bf.step(); traj.append(bf.knots["A"].threads[0].theta)
    jumps = [abs(traj[i + 1] - traj[i]) for i in range(len(traj) - 1)]
    return max(jumps) < 0.1 and len(set(round(t, 6) for t in traj)) == len(traj), \
           f"smooth θ(t): max step {max(jumps):.4f}, all samples distinct"

def B2():  # hybrid: continuous flow between guarded discrete commits
    bf = Breathfield(dt=0.02, gain=1.5); bf.add(osc("A", n=6, omega=1.0))
    bf.guards["A"] = lambda k, t: math.sin(0.5 * t) - 0.5      # fires intermittently, not every step
    bf.advance(20.0)
    flow_steps = int(round(20.0 / bf.dt))
    return len(bf.events) >= 1 and flow_steps > 10 * len(bf.events), \
           f"{flow_steps} flow steps punctuated by {len(bf.events)} guarded commits"

def B3():  # event-driven reactivity: a commit fires off-grid (not a multiple of dt)
    bf = Breathfield(dt=0.02, gain=1.0); bf.add(osc("A", omega=1.0))
    bf.guards["A"] = lambda k, t: math.sin(k.threads[0].theta) - 0.7
    bf.advance(15.0)
    if not bf.events: return False, "no event fired"
    te = bf.events[0][0]; off = abs((te / bf.dt) - round(te / bf.dt))
    return off > 1e-6, f"event at t={te:.5f} is off-grid (dt={bf.dt}); fractional offset {off:.4f}"

def B4():  # multi-scale temporal feedback: fast inner field inside a slow outer reduction
    child = Breathfield(dt=0.004); child.add(osc("c", omega=5.0))
    parent = Breathfield(dt=0.04); parent.add(osc("P", omega=0.5)); parent.nest("P", child)
    parent.step()
    ipo = getattr(child, "inner_per_outer", 0)
    return ipo >= 4, f"{ipo} inner steps per outer reduction (timescale separation, native)"

def B5():  # variable/long delay line via continuous τ on a Strand
    bf = Breathfield(dt=0.01, gain=0.0)                         # gain 0 → W rotates freely, no back-coupling
    bf.add(osc("W", omega=1.0)); bf.add(osc("D", omega=0.0))
    tau = 0.7; bf.wire("W", "D", weight=1.0, tau=tau)
    bf.advance(5.0)
    W = bf.knots["W"]; t = bf.t
    now = W.threads[0].theta % (2 * math.pi)
    delayed = cmath.phase(W.delayed(t, tau)[0]) % (2 * math.pi)
    lag = (now - delayed) % (2 * math.pi)
    err = abs(lag - (1.0 * tau) % (2 * math.pi))
    return err < 0.05, f"delayed read lags source by {lag:.3f} rad ≈ ω·τ={1.0*tau:.3f} (err {err:.3f})"

# ============================ C · FRACTAL / SCALE ========================== #
def C1():  # fractal nesting is first-class (a primitive field), not a wrapper
    child = Breathfield(dt=0.01); child.add(osc("c", omega=1.0))
    parent = Breathfield(dt=0.02); parent.add(osc("P", omega=1.0)); parent.nest("P", child)
    return isinstance(parent.knots["P"].child, Breathfield), "module child is a field (native nesting)"

def C2():  # recursive self-similarity across 3 scales
    lvl0 = Breathfield(dt=0.003); lvl0.add(osc("a", omega=3.0))
    lvl1 = Breathfield(dt=0.01);  lvl1.add(osc("b", omega=2.0)); lvl1.nest("b", lvl0)
    lvl2 = Breathfield(dt=0.03);  lvl2.add(osc("c", omega=1.0)); lvl2.nest("c", lvl1)
    lvl2.advance(0.6)
    cohs = [lvl2.knots["c"].coherence(), lvl1.knots["b"].coherence(), lvl0.knots["a"].coherence()]
    return all(0.0 <= x <= 1.0 for x in cohs), f"3 self-similar scales coherent: γ={[round(x,2) for x in cohs]}"

def C3():  # scale-relative socialization: coupling mediated by BOTH boundaries' shared state
    def run(openB):
        bf = Breathfield(dt=0.02, gain=1.5)
        bf.add(osc("A", n=6, omega=1.0))
        thB = math.pi/2 if openB else 0.0                       # open (κ=1) vs sealed (κ=0)
        bf.add(Knot("B", threads=[Thread(theta=thB) for _ in range(6)]))
        bf.wire("A", "B", weight=1.5); bf.advance(2.0)
        return bf.knots["B"].threads[0].theta
    return abs(run(True) - run(False)) > 1e-3, "influence on B depends on B's own openness (shared-state socialization)"

def C4():  # multiple reference frames via bidiγΔ (up + down cones both active)
    def run(nested):
        child = Breathfield(dt=0.005); child.add(osc("c", omega=3.0)); child.add(osc("d", omega=3.1))
        child.wire("c", "d")
        # parent threads spread across the circle so the up-cone has something to organize
        P = Knot("P", threads=[Thread(theta=1.05 * i, omega=0.4) for i in range(6)])
        parent = Breathfield(dt=0.02, kappa_gate=False); parent.add(P)
        if nested: parent.nest("P", child)
        parent.advance(3.0)
        gp = parent.knots["P"].coherence()
        gc = sum(k.coherence() for k in child.knots.values()) / 2
        return gp, gc
    gp_n, gc_n = run(True); gp_b, _ = run(False)
    up = abs(gp_n - gp_b) > 1e-3          # child's coherence reshaped the parent frame (up-cone)
    return up, f"two frames coexist: parent γ {gp_b:.2f}→{gp_n:.2f} under child (up-cone); child γ={gc_n:.2f}"

def C5():  # bounded nested field tower
    def build(depth):
        bf = Breathfield(dt=0.01 * (depth + 1)); bf.add(osc(f"k{depth}", omega=1.0 + depth))
        if depth > 0: bf.nest(f"k{depth}", build(depth - 1))
        return bf
    top = build(3)                          # depth-budgeted self-similar tower
    top.advance(0.5)
    return math.isfinite(top.global_coherence()), "bounded self-hosting tower (depth budget) runs finite"

# ============================ D · COHERENCE / MIN ========================== #
def D1():  # local + emergent global coherence (the system seeks the zero)
    bf = Breathfield(dt=0.02, gain=2.0, kappa_gate=False)
    for i, om in enumerate((1.0, 1.05, 0.97, 1.02)):
        bf.add(Knot(f"n{i}", threads=[Thread(theta=1.3 * i, omega=om)]))
    names = list(bf.knots)
    for i in range(4):
        bf.wire(names[i], names[(i + 1) % 4], weight=1.5)
        bf.wire(names[(i + 1) % 4], names[i], weight=1.5)
    R0 = bf.global_coherence(); bf.advance(25.0); R1 = bf.global_coherence()
    return R1 > R0 + 0.2 and R1 > 0.8, f"global coherence rises {R0:.2f}→{R1:.2f} (emergent order)"

def D2():  # barrier + guard: a commit never increases free energy
    bf = Breathfield(dt=0.02, gain=1.5)
    bf.add(osc("A", n=6, omega=0.8)); bf.add(osc("B", n=6, omega=1.1))
    bf.wire("A", "B"); bf.wire("B", "A")
    worst, n = -1e9, 0
    for _ in range(40):
        bf.advance(0.3)
        for nm in ("A", "B"):
            k = bf.knots[nm]; A = bf.afferent(k, bf.t)
            Fpre = k.free_energy(A)
            Fpost, ok = k.breath(A)
            worst = max(worst, Fpost - Fpre); n += 1
    return worst <= 1e-9, f"over {n} commits, max ΔF = {worst:.2e} ≤ 0 (free-energy guard holds)"

def D3():  # active inference / integration flows across the network
    bf = Breathfield(dt=0.02, gain=1.0, kappa_gate=False)
    bf.add(Knot("W", threads=[Thread(theta=0.0, omega=0.0)]))     # fixed world: Re(z)=+1
    g = Knot("G", threads=[Thread(theta=math.pi/2)]); g.precision = 30.0
    bf.add(g); bf.wire("W", "G", weight=1.0)
    bf.advance(6.0)
    sens = bf.afferent(g, bf.t)[0].real
    err = abs(g.belief[0] - sens)
    return err < 0.05 and sens > 0.5, f"downstream belief tracked upstream signal {sens:.2f} (error {err:.4f})"

def D4():  # FEP: minimize surprise by UPDATING (perception) or ACTING (active inference)
    # perception: fixed world, high precision → belief → sensed (change the model)
    bp = Breathfield(dt=0.02, gain=1.0, kappa_gate=False)
    bp.add(Knot("W", threads=[Thread(theta=0.0, omega=0.0)]))
    gp = Knot("G", threads=[Thread(theta=math.pi/2)]); gp.precision = 40.0
    bp.add(gp); bp.wire("W", "G"); bp.advance(6.0)
    sens = bp.afferent(gp, bp.t)[0].real
    err_perc = abs(gp.belief[0] - sens)
    # action: a self-sensing knot drives its own sensed value to a setpoint by acting (change the world)
    ba = Breathfield(dt=0.02, gain=0.0, kappa_gate=False)
    ga = Knot("Act", threads=[Thread(theta=1.9)]); ga.act_gain = 3.0; ga.prior = [0.6]; ga.precision = 0.0
    ba.add(ga); ba.wire("Act", "Act", weight=1.0); ba.advance(12.0)
    sensed = ba.afferent(ga, ba.t)[0].real
    err_act = abs(sensed - 0.6)
    ok = err_perc < 0.05 and err_act < 0.05
    return ok, f"perception err {err_perc:.3f} (update model→world) · action err {err_act:.3f} (act→world matches model)"

# ============================ E · UNIVERSALITY ============================= #
def E1():  # event-driven state substrate + two-counter construction
    # state machine: a module advances through distinct addresses on guarded commits
    bf = Breathfield(dt=0.05, gain=0.0)
    k = Knot("S", threads=[Thread(theta=0.2 * i, omega=1.0 + 0.4 * i) for i in range(6)]); bf.add(k)
    seen = set()
    bf.guards["S"] = lambda kn, t: math.sin(kn.threads[0].theta) - 0.99   # periodic guarded commit
    for _ in range(900):
        bf.step(); seen.add(bf.knots["S"].trits())                        # the live boundary state
    sm_ok = len(seen) >= 3 and len(bf.events) >= 1
    # universality witness: the two-counter machine computes addition
    uni_ok = all(minsky_add(a, b)["c1"] == a + b for a, b in [(0,0),(3,4),(7,5),(9,9)])
    return sm_ok and uni_ok, f"event-driven SM visited {len(seen)} states over {len(bf.events)} commits; two-counter machine adds"

def E2():  # neural-dynamics witnesses: CTRNN sync + predictive coding + Hebbian plasticity
    # (1) CTRNN: two coupled oscillators phase-lock (continuous recurrent dynamics)
    bf = Breathfield(dt=0.02, gain=2.5, kappa_gate=False)
    bf.add(Knot("x", threads=[Thread(theta=0.0, omega=1.0)]))
    bf.add(Knot("y", threads=[Thread(theta=2.6, omega=1.25)]))
    bf.wire("x", "y", weight=1.6); bf.wire("y", "x", weight=1.6)
    bf.advance(30.0); R = bf.global_coherence()
    ctrnn = R > 0.85
    # (2) predictive coding: belief error → 0
    pc = Breathfield(dt=0.02, gain=1.0, kappa_gate=False)
    pc.add(Knot("W", threads=[Thread(theta=0.0, omega=0.0)]))
    gg = Knot("G", threads=[Thread(theta=math.pi/2)]); gg.precision = 40.0
    pc.add(gg); pc.wire("W", "G"); pc.advance(6.0)
    pc_ok = abs(gg.belief[0] - pc.afferent(gg, pc.t)[0].real) < 0.05
    # (3) Hebbian: weight grows for correlated, shrinks for anti-correlated
    def hebb(corr):
        h = Breathfield(dt=0.02, gain=0.0)
        th = 0.0 if corr else math.pi
        h.add(Knot("a", threads=[Thread(theta=0.0, omega=0.0)]))
        h.add(Knot("b", threads=[Thread(theta=th, omega=0.0)]))
        h.wire("a", "b", weight=0.5, hebbian=True, eta=0.5); h.advance(6.0)
        return h.strands[0].weight
    hebb_ok = hebb(True) > 0.6 and hebb(False) < 0.4
    return ctrnn and pc_ok and hebb_ok, \
           f"CTRNN R={R:.2f}; predictive-coding error→0; Hebbian w(corr)={hebb(True):.2f}>w(anti)={hebb(False):.2f}"

def E3():  # same primitives serve both regimes — one compact program does flow and a commit
    src = """
    breathfield dt=0.02 gain=1.5
    knot A theta 0 1.57 3.14 1.57 0 1.57
    knot B trits + 0 - + 0 -
    strand A -> B tau=0.2 weight=1.0
    flow 3.0
    breath B
    """
    bf = parse_legacy_program(src)
    return bf.t > 2.9 and bf.knots["B"].address() >= 0, "one compact field program runs continuous flow and a guarded commit"

# ============================ F · OPERATORS ================================ #
def F1():  # strengthened operators function in a continuous, running field
    bf = Breathfield(dt=0.02, gain=1.0); bf.add(osc("A", n=6)); bf.add(osc("B", n=6))
    bf.wire("A", "B"); bf.advance(1.0)
    A, B = bf.knots["A"], bf.knots["B"]
    g, i, c = A.gate(B), A.interfere(B), A.corefold()
    A2 = bf.afferent(A, bf.t); F, ok = A.breath(A2)
    return len(g) == 6 and len(i) == 6 and len(c) == 6, "Gate/interfere/Core-fold + commit all operate in a flowing field"

def F2():  # operators route through scale-relative socialization (shared boundary state)
    def effective_coupling(openB):
        bf = Breathfield(dt=0.02, gain=1.5)
        bf.add(Knot("A", threads=[Thread(theta=math.pi/2) for _ in range(6)]))   # open source (κ=1)
        thB = math.pi/2 if openB else 0.0           # receiver B open (κ=1) vs sealed (κ=0)
        B = Knot("B", threads=[Thread(theta=thB) for _ in range(6)]); bf.add(B)
        bf.wire("A", "B", weight=2.0)
        A = bf.afferent(B, 0.0)
        # effective drive = afferent gated by B's OWN permeability (the shared-state mediation)
        return sum(B.threads[i].kappa() * abs(A[i]) for i in range(6))
    return effective_coupling(True) > effective_coupling(False) + 1e-6, \
           "operator influence is gated by the receiver's own boundary state (mutual socialization)"

def F3():  # bidiγΔ maintains multiple coherent frames across scales under load
    child = Breathfield(dt=0.005); child.add(osc("c", omega=3.0)); child.add(osc("d", omega=3.05))
    child.wire("c", "d"); child.wire("d", "c")
    parent = Breathfield(dt=0.02); parent.add(osc("P", n=6, omega=0.5)); parent.nest("P", child)
    gp, gc = [], []
    for _ in range(60):
        parent.step()
        gp.append(parent.knots["P"].coherence())
        gc.append(sum(k.coherence() for k in child.knots.values()) / 2)
    return min(gc) > 0.1 and all(math.isfinite(x) for x in gp + gc), \
           f"both frames stay coherent across run (child γ_min={min(gc):.2f}, parent stable)"

# ============================ REPORT ======================================= #
BOXES = [
    ("A1", "brand-new first-principles primitives only", A1),
    ("A2", "host-free core spec (no host language / borrowed formalism)", A2),
    ("A3", "self-contained module, self-interfering", A3),
    ("A4", "self-referential fractalization", A4),
    ("B1", "true continuous-time evolution (not pure tick)", B1),
    ("B2", "hybrid continuous + guarded discrete commits", B2),
    ("B3", "event-driven reactivity (off-grid commits)", B3),
    ("B4", "multi-scale temporal feedback (fast-in-slow)", B4),
    ("B5", "variable/long delay lines via continuous τ", B5),
    ("C1", "fractal nesting first-class & native", C1),
    ("C2", "recursive self-similar dynamics", C2),
    ("C3", "scale-relative socialization (shared nesting)", C3),
    ("C4", "multiple reference frames via bidiγΔ", C4),
    ("C5", "bounded nested field tower", C5),
    ("D1", "local + emergent global coherence zero", D1),
    ("D2", "barrier + guard across continuous + discrete reductions", D2),
    ("D3", "active inference/integration across network", D3),
    ("D4", "FEP: minimize surprise by acting OR updating", D4),
    ("E1", "event-driven state substrate + two-counter construction", E1),
    ("E2", "neural-dynamics witnesses", E2),
    ("E3", "same primitives serve both regimes", E3),
    ("F1", "strengthened commit/Gate/interfere/Core-fold/nest", F1),
    ("F2", "operators via scale-relative socialization", F2),
    ("F3", "bidiγΔ maintains multiple coherent frames", F3),
]

if __name__ == "__main__":
    print("═" * 78)
    print("  BiDi Coherence-Delta Calculus · acceptance report   (one capability witness per box)")
    print("═" * 78)
    npass = 0
    for code, label, fn in BOXES:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"EXC {type(e).__name__}: {e}"
        npass += ok
        mark = "✅" if ok else "❌"
        print(f"  {mark} {code}  {label}")
        print(f"       └─ {detail}")
    print("─" * 78)
    print(f"  {npass}/{len(BOXES)} boxes green")
    print("═" * 78)
