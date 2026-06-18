#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BiDi Coherence-Delta Calculus · reference reducer (v1)
=====================================================
The canonical definition is `BIDI_CALCULUS_CORE.md`: a carrier algebra, term
syntax, structural congruence, hybrid reduction relation, operator algebra, and
executable metatheorem witnesses. This Python file realizes that calculus so the
claims can be exercised; it is one substrate among many, not the language itself.

Implementation names retained for API stability:
  Thread      — cell: continuous state (angle θ, amplitude a, plasticity p);
                latched pole σ and memory μ commit only at guarded commits.
  Strand      — channel: directed coupling with a continuous delay constant τ.
  Knot        — module: a bundle of cells with read/write cones, a generative
                belief state, and an optional nested field.
  Breathfield — field: a network of modules/channels evolving by continuous flow,
                punctuated by event-driven guarded commits.
  bidiγΔ      — bidirectional coherence-delta: down-cone parent context and
                up-cone child coherence across nested reference frames.

Time model: continuous flow (RK4 on phase, forward-Euler on slow variables)
between events; commits fire when guard predicates cross zero, located off-grid
by linear interpolation. No global tick.
"""
import math, cmath, itertools

TAU2 = 2 * math.pi
EPS  = 1e-12
def wrap(t):  return t % TAU2
def sdiff(a, b): return ((a - b + math.pi) % TAU2) - math.pi


# --------------------------------------------------------------------------- #
#  THREAD — continuous-time atom
# --------------------------------------------------------------------------- #
class Thread:
    __slots__ = ("theta", "amp", "plast", "omega", "sigma", "mu")
    def __init__(self, theta=0.0, amp=1.0, plast=0.0, omega=0.0, sigma=None, mu=0.0):
        self.theta, self.amp, self.plast, self.omega = theta, amp, plast, omega
        self.sigma = sigma if sigma in (-1, 1) else (1 if math.cos(theta) >= 0 else -1)
        self.mu = mu
    @property
    def z(self):     return cmath.rect(self.amp, self.theta)
    def trit(self, deadband=0.5):
        if self.amp < 1e-9: return 0
        c = math.cos(self.theta)
        return 1 if c > deadband else -1 if c < -deadband else 0
    def kappa(self, deadband=0.5):
        return max(0.0, 1.0 - abs(math.cos(self.theta)) / deadband)


# --------------------------------------------------------------------------- #
#  STRAND — directed coupling with a continuous delay τ
# --------------------------------------------------------------------------- #
class Strand:
    __slots__ = ("src", "dst", "weight", "tau", "line", "hebbian", "eta")
    def __init__(self, src, dst, weight=1.0, tau=0.0, line=None, hebbian=False, eta=0.2):
        self.src, self.dst, self.weight, self.tau = src, dst, weight, tau
        self.line, self.hebbian, self.eta = line, hebbian, eta   # line=None couples all aligned threads


# --------------------------------------------------------------------------- #
#  KNOT — module (read cone, write cone, belief, optional child field)
# --------------------------------------------------------------------------- #
class Knot:
    def __init__(self, name, threads=None, n=6, deadband=0.5):
        self.name = name
        self.threads = threads if threads is not None else [Thread(theta=math.pi / 2) for _ in range(n)]
        self.n = len(self.threads)
        self.deadband = deadband
        self.belief    = [0.0] * self.n          # generative model (predictive coding)
        self.prior     = [0.0] * self.n          # prior / setpoint
        self.precision = 1.0                      # sensory precision
        self.act_gain  = 0.0                      # >0 enables active inference (acts on the world)
        self.child     = None                     # nested Breathfield (child field)
        self.history   = [(0.0, [th.z for th in self.threads])]  # for delayed strand reads
        # universality (instruction-knot) fields — dormant unless set:
        self.kind = None; self.reg = None; self.nxt = None; self.alt = None; self.count = 0

    # --- readings --------------------------------------------------------- #
    def trits(self):       return tuple(th.trit(self.deadband) for th in self.threads)
    def sigma(self):       return tuple(th.sigma for th in self.threads)
    def address(self):     return sum((1 if s > 0 else 0) << i for i, s in enumerate(self.sigma()))
    def permeability(self):return sum(th.kappa(self.deadband) for th in self.threads) / self.n
    def coherence(self):                                   # γ — local order parameter
        zs = [cmath.rect(1, th.theta) for th in self.threads]
        return abs(sum(zs)) / self.n
    def rank_walk(self):                                   # the coherence-debt walk
        r, out = 0, []
        for th in self.threads: r += th.trit(self.deadband); out.append(r)
        return out
    def admissible(self): return all(r >= 0 for r in self.rank_walk())
    def localized(self):
        w = self.rank_walk(); return all(r >= 0 for r in w) and w[-1] == 0
    def output(self):      return [th.z for th in self.threads]
    def delayed(self, t, tau):                              # this knot's output at t-τ (interp)
        tt = t - tau; h = self.history
        if tt <= h[0][0]:  return h[0][1]
        if tt >= h[-1][0]: return h[-1][1]
        lo, hi = 0, len(h) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if h[mid][0] <= tt: lo = mid
            else: hi = mid
        (t0, v0), (t1, v1) = h[lo], h[hi]
        f = 0.0 if t1 == t0 else (tt - t0) / (t1 - t0)
        return [a + (b - a) * f for a, b in zip(v0, v1)]
    def push(self, t):
        self.history.append((t, [th.z for th in self.threads]))
        if len(self.history) > 4096: self.history.pop(0)

    # --- free energy F (variational): prediction error + complexity + coupling --- #
    def free_energy(self, A):
        f = 0.0
        for i in range(self.n):
            sens = A[i].real
            f += 0.5 * self.precision * (sens - self.belief[i]) ** 2
            f += 0.5 * (self.belief[i] - self.prior[i]) ** 2
            f += -abs(A[i]) * math.cos(cmath.phase(A[i]) - self.threads[i].theta) if abs(A[i]) > EPS else 0.0
        return f

    # --- operators (Gate / interfere / Core-fold), scale-relative ---------- #
    def gate(self, other):                                  # data-as-operator: phasor multiply
        return [a.z * b.z for a, b in zip(self.threads, other.threads)]
    def interfere(self, other, gain=1.0):                   # superposition / correlation
        return [a.z + gain * b.z for a, b in zip(self.threads, other.threads)]
    def corefold(self):                                     # 互 nuclear — abstraction
        l = self.threads
        idx = (1, 2, 3, 2, 3, 4) if self.n == 6 else tuple(range(self.n))
        return [l[i].z for i in idx]

    # --- guarded discrete commit (barrier + free-energy guard) ---------------- #
    def commit(self, A, snap=0.25):
        """Commit toward attractors, latch σ, enforce the coherence barrier (rank≥0),
        but only if free energy does not increase."""
        F0 = self.free_energy(A)
        # candidate: snap phases toward nearest committed peak, drain rank to admissible
        peaks = (0.0, math.pi)
        cand = []
        for th in self.threads:
            best = min(peaks, key=lambda c: abs(sdiff(c, th.theta)))
            cand.append(th.theta + snap * sdiff(best, th.theta))
        # coherence barrier: walk runtime trits; a rank-violating line rotates to crossing
        r = 0
        for i, ct in enumerate(cand):
            c = math.cos(ct); t = 1 if c > self.deadband else -1 if c < -self.deadband else 0
            if r + t < 0:
                cand[i] = math.pi / 2 if abs(sdiff(math.pi / 2, ct)) < abs(sdiff(3 * math.pi / 2, ct)) else 3 * math.pi / 2
                t = 0
            r += t
        # belief commit toward sensory (perception)
        newbelief = [self.belief[i] + snap * (A[i].real - self.belief[i]) for i in range(self.n)]
        # tentatively apply, measure F
        saved = [(th.theta, th.amp) for th in self.threads]; savedb = list(self.belief)
        for th, ct in zip(self.threads, cand): th.theta = ct
        self.belief = newbelief
        F1 = self.free_energy(A)
        if F1 > F0 + 1e-9:                                   # guard: reject F-increasing commit
            for th, (th0, a0) in zip(self.threads, saved): th.theta, th.amp = th0, a0
            self.belief = savedb
            return F0, False
        for th in self.threads:                              # latch σ on committed lines
            t = th.trit(self.deadband)
            if t != 0: th.sigma = t
        return F1, True

    def breath(self, A, snap=0.25):
        """Compatibility alias for the older reference API name."""
        return self.commit(A, snap=snap)


# --------------------------------------------------------------------------- #
#  STATIC COMBINATORIAL LAYER — the calculus's normal-form value census
# --------------------------------------------------------------------------- #
def census(n=6):
    """Count committed runtime walks over {−,0,+}ⁿ by the coherence-debt invariant.
    The localized (closed) classical walks are the calculus's normal-form values —
    directed-animal / Motzkin / central-binomial / Catalan constants."""
    def adm(ts):
        r = 0
        for t in ts:
            r += t
            if r < 0: return False
        return True
    def loc(ts):
        r = 0
        for t in ts:
            r += t
            if r < 0: return False
        return r == 0
    allh = list(itertools.product((1, 0, -1), repeat=n))
    cls = [h for h in allh if all(v != 0 for v in h)]
    return dict(total=len(allh), admissible=sum(adm(h) for h in allh),
                localized=sum(loc(h) for h in allh), classical=len(cls),
                classical_admissible=sum(adm(h) for h in cls),
                classical_localized=sum(loc(h) for h in cls))


# --------------------------------------------------------------------------- #
#  BREATHFIELD — the runtime: continuous flow + event-driven guarded commits
# --------------------------------------------------------------------------- #
class Breathfield:
    def __init__(self, dt=0.02, gain=1.2, deadband=0.5, dt_inner=None, kappa_gate=True):
        self.knots = {}          # name -> Knot
        self.strands = []        # list[Strand]
        self.dt = dt
        self.dt_inner = dt_inner or dt / 4.0
        self.gain = gain
        self.deadband = deadband
        self.kappa_gate = kappa_gate   # True: I Ching boundary-gated coupling; False: plain oscillator
        self.t = 0.0
        self.events = []         # (time, knot_name) log of commits fired off-grid
        self.guards = {}         # knot_name -> callable(knot, t) -> float ; commit fires on up-crossing
        self.F_log = []          # (t, knot, F) at commits — free-energy witness

    def add(self, knot):     self.knots[knot.name] = knot; knot.deadband = self.deadband; return knot
    def wire(self, s, d, weight=1.0, tau=0.0, line=None, hebbian=False, eta=0.2):
        self.strands.append(Strand(self.knots[s], self.knots[d], weight, tau, line, hebbian, eta))
    def nest(self, parent_name, child_field):
        self.knots[parent_name].child = child_field

    # afferent vector A for a knot (delayed, permeability-gated superposition) ---
    def afferent(self, knot, t):
        A = [0j] * knot.n
        for s in self.strands:
            if s.dst is not knot: continue
            srcz = s.src.delayed(t, s.tau)
            for i in range(knot.n):
                if self.kappa_gate and abs(srcz[i]) > EPS:
                    kap_src = max(0.0, 1.0 - abs(math.cos(cmath.phase(srcz[i]))) / self.deadband)
                else:
                    kap_src = 1.0
                A[i] += s.weight * (1.0 + s.src.threads[i].plast) * kap_src * srcz[i]
        # bidiγΔ up-cone: a nested child's coherence organizes the parent (mean-field pull)
        if knot.child is not None:
            gchild = sum(k.coherence() for k in knot.child.knots.values()) / max(1, len(knot.child.knots))
            zmean = sum(cmath.rect(1, th.theta) for th in knot.threads)
            phi = cmath.phase(zmean) if abs(zmean) > EPS else 0.0
            for i in range(knot.n):
                A[i] += self.gain * 0.6 * gchild * cmath.rect(1, phi)
        return A

    # continuous flow ------------------------------------------------------- #
    def _dtheta(self, knot, thetas, A):
        d = []
        for i, th in enumerate(knot.threads):
            kap = (max(0.0, 1.0 - abs(math.cos(thetas[i])) / self.deadband)) if self.kappa_gate else 1.0
            drive = abs(A[i]) * math.sin(cmath.phase(A[i]) - thetas[i]) if abs(A[i]) > EPS else 0.0
            d.append(th.omega + self.gain * kap * drive)
        return d

    def _flow_step(self, dt):
        # RK4 on phase, forward-Euler on amplitude / belief / plasticity weights
        for knot in self.knots.values():
            A = self.afferent(knot, self.t)
            th0 = [th.theta for th in knot.threads]
            k1 = self._dtheta(knot, th0, A)
            k2 = self._dtheta(knot, [t + 0.5 * dt * d for t, d in zip(th0, k1)], A)
            k3 = self._dtheta(knot, [t + 0.5 * dt * d for t, d in zip(th0, k2)], A)
            k4 = self._dtheta(knot, [t + dt * d for t, d in zip(th0, k3)], A)
            for i, th in enumerate(knot.threads):
                th.theta = th0[i] + (dt / 6.0) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
                th.amp  += dt * 0.8 * (1.0 - th.amp)                       # amplitude relaxation
            # predictive-coding belief flow (gradient descent on F): perception
            for i in range(knot.n):
                sens = A[i].real
                knot.belief[i] += dt * (knot.precision * (sens - knot.belief[i]) - (knot.belief[i] - knot.prior[i]))
            # active inference: act_gain>0 lets the knot ACT (move its phase) to make its
            # own sensed value match its prior — gradient descent on (prior - sensed)²
            if knot.act_gain > 0:
                for i, th in enumerate(knot.threads):
                    sensed = A[i].real
                    err = knot.prior[i] - sensed
                    th.theta += -dt * knot.act_gain * err * math.sin(th.theta)
        # plasticity (continuous Hebbian on strand weights)
        for s in self.strands:
            if not s.hebbian: continue
            corr = sum(math.cos(s.src.threads[i].theta - s.dst.threads[i].theta) for i in range(s.dst.n)) / s.dst.n
            s.weight = max(0.0, min(4.0, s.weight + dt * s.eta * (corr - 0.15 * s.weight)))

    # one outer advance with nesting (multirate) + event detection ---------- #
    def step(self):
        # down-cone (bidiγΔ): parent state biases each child's prior; step child fast (multirate)
        for knot in self.knots.values():
            if knot.child is not None:
                ctx = knot.threads[0].theta
                for ck in knot.child.knots.values():
                    ck.prior = [0.3 * math.cos(ctx)] * ck.n
                inner = max(1, int(round(self.dt / knot.child.dt)))
                for _ in range(inner):
                    knot.child.step()
                knot.child.inner_per_outer = inner
        # guard values before
        g_before = {nm: self.guards[nm](self.knots[nm], self.t) for nm in self.guards}
        self._flow_step(self.dt)
        self.t += self.dt
        for knot in self.knots.values():
            knot.push(self.t)
        # event-driven commits: guard up-crossing located off-grid by linear interp
        for nm, g in self.guards.items():
            g1 = g(self.knots[nm], self.t)
            g0 = g_before[nm]
            if g0 < 0.0 <= g1:
                frac = g0 / (g0 - g1) if g1 != g0 else 1.0
                t_event = (self.t - self.dt) + frac * self.dt
                A = self.afferent(self.knots[nm], self.t)
                F, ok = self.knots[nm].commit(A)
                self.events.append((t_event, nm))
                self.F_log.append((t_event, nm, F))

    def advance(self, T):
        steps = int(round(T / self.dt))
        for _ in range(steps):
            self.step()

    # convenience: a discrete guarded commit on every module (used without a clock) #
    def breathe_all(self):
        for knot in self.knots.values():
            A = self.afferent(knot, self.t)
            F, ok = knot.commit(A)
            self.F_log.append((self.t, knot.name, F))

    def global_coherence(self):
        zs = [cmath.rect(1, th.theta) for k in self.knots.values() for th in k.threads]
        return abs(sum(zs)) / len(zs) if zs else 0.0


# --------------------------------------------------------------------------- #
#  UNIVERSALITY — a 2-counter construction executed by generic commits.
#  The program is data (instruction modules + channels); the commit mechanic
#  executes it without a counting-specific evaluator.
# --------------------------------------------------------------------------- #
class CounterField:
    """A Breathfield specialization whose commits execute guarded instructions."""
    def __init__(self):
        self.knots = {}; self.active = None; self.trace = []
    def reg(self, name, count=0):
        k = Knot(name, n=1); k.kind = "reg"; k.count = count; self.knots[name] = k; return k
    def instr(self, name, kind, reg=None, nxt=None, alt=None):
        k = Knot(name, n=1); k.kind = kind; k.reg = reg; k.nxt = nxt; k.alt = alt
        self.knots[name] = k; return k
    def commit(self, knot):
        """Generic guarded instruction commit. Returns the next active instruction."""
        if knot.kind == "inc":
            self.knots[knot.reg].count += 1
            return knot.nxt
        if knot.kind == "jzdec":
            if self.knots[knot.reg].count > 0:
                self.knots[knot.reg].count -= 1
                return knot.nxt
            return knot.alt
        if knot.kind == "halt":
            return None
        raise ValueError(knot.kind)
    def run(self, start, max_steps=100000):
        self.active = start
        steps = 0
        while self.active is not None and steps < max_steps:
            k = self.knots[self.active]
            if k.kind == "halt": break
            self.trace.append((self.active, {n: self.knots[n].count for n in self.knots if self.knots[n].kind == "reg"}))
            self.active = self.commit(k)
            steps += 1
        return {n: self.knots[n].count for n in self.knots if self.knots[n].kind == "reg"}

    def breath(self, knot):
        """Compatibility alias for the older reference API name."""
        return self.commit(knot)


def minsky_add(a, b):
    """c1 += c2 via the standard 2-counter program. Returns final counters."""
    F = CounterField()
    F.reg("c1", a); F.reg("c2", b)
    F.instr("L0", "jzdec", reg="c2", nxt="L1", alt="H")   # if c2>0: c2--, ->L1 ; else ->H
    F.instr("L1", "inc",   reg="c1", nxt="L0")            # c1++ ; ->L0
    F.instr("H",  "halt")
    return F.run("L0")


# --------------------------------------------------------------------------- #
#  LEGACY MINI-SYNTAX — compact field programs used by the acceptance witness
# --------------------------------------------------------------------------- #
def parse_legacy_program(source):
    """Minimal field-program syntax. Statements (one per line, # comments):
        breathfield dt=0.02 gain=1.2 deadband=0.5
        knot A theta 0 1.57 3.14 1.57 0 1.57
        knot B trits + 0 - + 0 -
        strand A -> B tau=0.3 weight=1.0 [hebbian]
        guard A crossing 0            # fire a commit when thread 0 reaches its crossing
        flow 5.0                      # advance continuous time
        breath A                      # one guarded commit on A
    """
    bf = None
    for raw in source.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line: continue
        tok = line.split()
        h = tok[0].lower()
        if h == "breathfield":
            kv = dict(p.split("=", 1) for p in tok[1:] if "=" in p)
            bf = Breathfield(dt=float(kv.get("dt", 0.02)), gain=float(kv.get("gain", 1.2)),
                             deadband=float(kv.get("deadband", 0.5)))
        elif h == "knot":
            name = tok[1]
            if tok[2].lower() == "theta":
                ths = [Thread(theta=float(x)) for x in tok[3:9]]
            elif tok[2].lower() == "trits":
                m = {"+": 0.0, "-": math.pi, "0": math.pi / 2}
                ths = [Thread(theta=m[x]) for x in tok[3:9]]
            else:
                ths = [Thread(theta=math.pi / 2) for _ in range(6)]
            bf.add(Knot(name, threads=ths))
        elif h == "strand":
            s, _, d = tok[1], tok[2], tok[3]
            kv = dict(p.split("=", 1) for p in tok[4:] if "=" in p)
            bf.wire(s, d, weight=float(kv.get("weight", 1.0)), tau=float(kv.get("tau", 0.0)),
                    hebbian=("hebbian" in [x.lower() for x in tok]))
        elif h == "guard":
            name = tok[1]
            if tok[2].lower() == "crossing":
                idx = int(tok[3])
                bf.guards[name] = (lambda i: (lambda k, t: math.cos(k.threads[i].theta) ** 2 - 0.001))(idx)
        elif h == "flow":
            bf.advance(float(tok[1]))
        elif h == "breath":
            k = bf.knots[tok[1]]; A = bf.afferent(k, bf.t); k.commit(A)
    return bf


if __name__ == "__main__":
    bf = Breathfield(dt=0.02, gain=1.4)
    bf.add(Knot("A", threads=[Thread(theta=0.3 * i, omega=1.0) for i in range(6)]))
    bf.add(Knot("B", threads=[Thread(theta=0.5 * i + 1, omega=1.0) for i in range(6)]))
    bf.wire("A", "B"); bf.wire("B", "A")
    R0 = bf.global_coherence(); bf.advance(8.0); R1 = bf.global_coherence()
    print(f"continuous sync: R {R0:.2f} -> {R1:.2f}   (t={bf.t:.2f})")
    print("minsky 3+4 =", minsky_add(3, 4)["c1"], " | 6+9 =", minsky_add(6, 9)["c1"])
