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
from cdc_semantics import AgencySummary, IncidenceSpec, MeasurementRecord, TraceSpan, WindowSpec

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
    __slots__ = ("src", "dst", "weight", "tau", "line", "hebbian", "eta", "angle", "lines", "broadcast")
    def __init__(self, src, dst, weight=1.0, tau=0.0, line=None, hebbian=False, eta=0.2,
                 angle=0.0, lines=None, broadcast=False):
        self.src, self.dst, self.weight, self.tau = src, dst, weight, tau
        self.line, self.hebbian, self.eta = line, hebbian, eta   # line=None couples all aligned threads
        self.angle = angle                                       # alpha: angular phase bias on entry
        self.lines = lines                                       # dimension projection; None means all target cells
        self.broadcast = broadcast                               # one aggregate source -> all target cells


class Aggregate:
    """Read-only phasor source for the mean state of a field or module list."""
    __slots__ = ("scope",)

    def __init__(self, scope):
        self.scope = scope

    def _modules(self):
        return list(self.scope.knots.values()) if hasattr(self.scope, "knots") else self.scope

    def delayed(self, t, tau):
        zs = [cmath.rect(1, th.theta) for k in self._modules() for th in k.threads]
        return [sum(zs) / len(zs)] if zs else [0j]


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
        self.inbound   = []                       # path-aware and cross-scale relations targeting this module
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
        self.trace_log = []      # TraceSpan records from passive observation
        self.measurements = []   # MeasurementRecord records from committing observation

    def add(self, knot):     self.knots[knot.name] = knot; knot.deadband = self.deadband; return knot
    @staticmethod
    def _lines(lines, n):
        if lines is None:
            return None
        vals = (lines,) if isinstance(lines, int) else tuple(lines)
        if not vals:
            raise ValueError("lines must name at least one target cell")
        bad = [i for i in vals if not isinstance(i, int) or i < 0 or i >= n]
        if bad:
            raise ValueError(f"line index out of range for target arity {n}: {bad}")
        return vals

    def wire(self, s, d, weight=1.0, tau=0.0, line=None, hebbian=False, eta=0.2, angle=0.0, lines=None):
        dst = self.knots[d]
        if lines is None and line is not None:
            lines = (line,)
        lines = self._lines(lines, dst.n)
        self.strands.append(Strand(self.knots[s], dst, weight, tau, line, hebbian, eta, angle, lines))

    def resolve(self, path):
        """Resolve a nesting path like 'm', 'm/n', or 'm/n/p' to a module."""
        if not isinstance(path, str):
            return path
        field, knot = self, None
        for part in path.split("/"):
            field = field if knot is None else knot.child
            if field is None:
                raise KeyError(f"cannot descend through module without child field: {knot.name}")
            knot = field.knots[part]
        return knot

    def relate(self, src_path, dst_path, weight=1.0, tau=0.0, angle=0.0, lines=None):
        """Path-aware, angle-biased bidi-gamma-delta relation.

        Source and destination may live at different nesting depths. Direction
        (up, down, lateral, or diagonal) is determined by the endpoints.
        """
        src, dst = self.resolve(src_path), self.resolve(dst_path)
        lines = self._lines(lines, dst.n)
        s = Strand(src, dst, weight, tau, None, False, 0.2, angle, lines)
        dst.inbound.append(s)
        return s

    def relation_readout(self, strand, t=None):
        """Return averaged phase-interference observables for a relation."""
        if t is None:
            t = self.t
        dst, srcz = strand.dst, strand.src.delayed(t, strand.tau)
        lines = strand.lines if strand.lines is not None else range(dst.n)
        cs = ss = en = 0.0
        acc = 0j
        n = 0
        for i in lines:
            if i >= dst.n:
                continue
            val = srcz[0] if strand.broadcast else (srcz[i] if i < len(srcz) else None)
            if val is None:
                continue
            dth = (cmath.phase(val) + strand.angle) - dst.threads[i].theta
            kap_src = (max(0.0, 1.0 - abs(math.cos(cmath.phase(val))) / self.deadband)
                       if abs(val) > EPS else 0.0)
            kap_dst = dst.threads[i].kappa(self.deadband)
            cs += math.cos(dth)
            ss += math.sin(dth)
            en += kap_src * kap_dst * (1 - math.cos(dth))
            acc += strand.weight * cmath.rect(1, dth)
            n += 1
        n = max(1, n)
        return dict(cos=cs / n, sin=ss / n, gamma=abs(acc) / n, energy=en / n)

    def window(self, name, scope_path, horizon_time=None, horizon_events=None,
               lines=None, angle_frame=0.0, projection="phase",
               sampling_policy="history", commit_policy="passive"):
        """Describe a derived observer window over a path in this field."""
        scope = self.resolve(scope_path)
        lines = self._lines(lines, scope.n)
        return WindowSpec(name=name, scope_path=scope_path, horizon_time=horizon_time,
                          horizon_events=horizon_events, lines=lines,
                          angle_frame=angle_frame, projection=projection,
                          sampling_policy=sampling_policy, commit_policy=commit_policy)

    @staticmethod
    def _history_at(knot, t):
        h = knot.history
        if t <= h[0][0]:
            return h[0][1]
        if t >= h[-1][0]:
            return h[-1][1]
        lo, hi = 0, len(h) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if h[mid][0] <= t:
                lo = mid
            else:
                hi = mid
        (t0, v0), (t1, v1) = h[lo], h[hi]
        f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
        return [a + (b - a) * f for a, b in zip(v0, v1)]

    def trace_window(self, scope_path, t0=None, t1=None, horizon_time=None,
                     horizon_events=None, lines=None, angle_frame=0.0,
                     name="window", record=True):
        """Passively observe a ternary phase window without changing dynamics."""
        knot = self.resolve(scope_path)
        lines = self._lines(lines, knot.n)
        t1 = self.t if t1 is None else t1
        if t1 > self.t + EPS:
            raise ValueError("trace windows cannot read future field state")
        if t0 is None:
            if horizon_time is not None:
                t0 = max(0.0, t1 - horizon_time)
            elif horizon_events:
                event_times = [t for t, nm in self.events if nm == knot.name and t <= t1]
                t0 = event_times[-horizon_events] if len(event_times) >= horizon_events else 0.0
            else:
                t0 = t1
        if t0 > t1 + EPS:
            raise ValueError("trace window start cannot be after its end")
        idxs = tuple(lines) if lines is not None else tuple(range(knot.n))
        times = {t0, t1}
        times.update(t for t, _ in knot.history if t0 <= t <= t1)
        samples = []
        gammas, cos_steps, sin_steps, energies = [], [], [], []
        total_motion = 0.0
        prev = None
        for ts in sorted(times):
            zs = self._history_at(knot, ts)
            phases = tuple(wrap(cmath.phase(zs[i]) + angle_frame) for i in idxs if i < len(zs))
            if not phases:
                continue
            selected = [cmath.rect(1, p) for p in phases]
            gammas.append(abs(sum(selected)) / len(selected))
            samples.append((ts, phases))
            if prev is not None:
                deltas = [sdiff(a, b) for a, b in zip(phases, prev)]
                if deltas:
                    mean_delta = sum(deltas) / len(deltas)
                    cos_steps.append(math.cos(mean_delta))
                    sin_steps.append(math.sin(mean_delta))
                    energies.append(1 - math.cos(mean_delta))
                    total_motion += sum(abs(d) for d in deltas) / len(deltas)
            prev = phases
        event0 = sum(1 for t, _ in self.events if t < t0)
        event1 = sum(1 for t, _ in self.events if t <= t1)
        commit_count = sum(1 for t, nm in self.events if t0 < t <= t1 and nm == knot.name)
        trace = TraceSpan(
            scope_path=scope_path,
            t0=t0,
            t1=t1,
            event0=event0,
            event1=event1,
            lines=lines,
            angle_frame=angle_frame,
            samples=tuple(samples),
            commit_count=commit_count,
            holds=0,
            mean_cos_delta=sum(cos_steps) / len(cos_steps) if cos_steps else 1.0,
            mean_sin_delta=sum(sin_steps) / len(sin_steps) if sin_steps else 0.0,
            mean_gamma=sum(gammas) / len(gammas) if gammas else 0.0,
            mean_energy=sum(energies) / len(energies) if energies else 0.0,
            total_phase_motion=total_motion,
        )
        if record:
            self.trace_log.append(trace)
        return trace

    def _relation_energy_between(self, observer, target):
        candidates = [s for s in self.strands if s.dst is target] + target.inbound
        strand = next((s for s in candidates if s.src is observer), None)
        return self.relation_readout(strand)["energy"] if strand is not None else 0.0

    def measure(self, observer_path, target_path=None, lines=None, angle_frame=0.0,
                snap=0.25, commit=True):
        """Measure through a window; committing measurements are guarded ternary commits."""
        target_path = target_path or observer_path
        observer = self.resolve(observer_path)
        target = self.resolve(target_path)
        win = self.window("measurement", target_path, horizon_time=self.dt,
                          lines=lines, angle_frame=angle_frame,
                          commit_policy="committing" if commit else "passive")
        pre = self.trace_window(target_path, horizon_time=self.dt, lines=win.lines,
                                angle_frame=angle_frame, name=win.name, record=False)
        A = self.afferent(target, self.t)
        F0 = target.free_energy(A)
        if commit:
            F1, ok = target.commit(A, snap=snap)
            if ok:
                target.push(self.t)
                self.events.append((self.t, target.name))
                self.F_log.append((self.t, target.name, F1))
        else:
            F1, ok = F0, False
        post = self.trace_window(target_path, horizon_time=self.dt, lines=win.lines,
                                 angle_frame=angle_frame, name=win.name, record=False)
        record = MeasurementRecord(
            observer_path=observer_path,
            target_path=target_path,
            window=win,
            pre_trace=pre,
            post_trace=post,
            outcome_trit=target.trits(),
            phi_delta=F1 - F0,
            relation_energy=self._relation_energy_between(observer, target),
            committed=bool(ok),
            barrier_applied=commit and target.admissible(),
        )
        self.measurements.append(record)
        return record

    def project_boundary(self, name, source_paths, lines=None, angle_frame=0.0):
        """Project subordinate paths into a higher-order boundary module."""
        sources = [self.resolve(p) for p in source_paths]
        n = max((s.n for s in sources), default=0)
        lines = self._lines(lines, n) if lines is not None else None
        idxs = tuple(lines) if lines is not None else tuple(range(n))
        threads = []
        for i in range(n):
            if i not in idxs:
                threads.append(Thread(theta=math.pi / 2))
                continue
            vals = [s.threads[i].z for s in sources if i < s.n]
            z = sum(vals) / len(vals) if vals else 0j
            threads.append(Thread(theta=wrap(cmath.phase(z) + angle_frame), amp=abs(z) if abs(z) > EPS else 1.0))
        knot = Knot(name, threads=threads)
        self.add(knot)
        return knot

    def agency_summary(self, scope_path, horizon_time=None, lines=None):
        """Summarize scale-relative agency as windowed stability and error reduction."""
        knot = self.resolve(scope_path)
        trace = self.trace_window(scope_path, horizon_time=horizon_time or self.dt,
                                  lines=lines, record=False)
        A = self.afferent(knot, self.t)
        current_f = knot.free_energy(A)
        prior_error = sum((knot.belief[i] - knot.prior[i]) ** 2 for i in range(knot.n)) / max(1, knot.n)
        return AgencySummary(scope_path=scope_path,
                             window=self.window("agency", scope_path, horizon_time=horizon_time or self.dt, lines=lines),
                             free_energy_drop=max(0.0, trace.mean_energy - current_f),
                             prediction_error_drop=max(0.0, trace.mean_energy - prior_error),
                             action_effect=sum(abs(th.omega) for th in knot.threads) / max(1, knot.n),
                             cross_scale_gain=sum(s.weight for s in knot.inbound),
                             stability=trace.mean_gamma)

    def nest(self, parent_name, child_field):
        parent = self.knots[parent_name]
        parent.child = child_field
        parent.inbound.append(Strand(Aggregate(child_field), parent,
                                     weight=self.gain * 0.6, angle=0.0, broadcast=True))
        for child in child_field.knots.values():
            child.inbound.append(Strand(Aggregate([parent]), child,
                                        weight=child_field.gain * 0.3, angle=0.0, broadcast=True))
        return parent

    # afferent vector A for a knot (delayed, permeability-gated superposition) ---
    def afferent(self, knot, t):
        A = [0j] * knot.n
        for s in [s for s in self.strands if s.dst is knot] + knot.inbound:
            srcz = s.src.delayed(t, s.tau)
            rot = cmath.rect(1.0, s.angle)
            lines = s.lines if s.lines is not None else range(knot.n)
            has_threads = hasattr(s.src, "threads")
            for i in lines:
                val = srcz[0] if s.broadcast else (srcz[i] if i < len(srcz) else None)
                if val is None or i >= knot.n:
                    continue
                if self.kappa_gate:
                    kap_src = (max(0.0, 1.0 - abs(math.cos(cmath.phase(val))) / self.deadband)
                               if abs(val) > EPS else 0.0)
                    kap_dst = knot.threads[i].kappa(self.deadband)
                else:
                    kap_src = kap_dst = 1.0
                plast = s.src.threads[i].plast if (has_threads and i < len(s.src.threads)) else 0.0
                A[i] += s.weight * (1.0 + plast) * kap_src * kap_dst * (rot * val)
        return A

    # continuous flow ------------------------------------------------------- #
    def _dtheta(self, knot, thetas, A):
        d = []
        for i, th in enumerate(knot.threads):
            drive = abs(A[i]) * math.sin(cmath.phase(A[i]) - thetas[i]) if abs(A[i]) > EPS else 0.0
            d.append(th.omega + self.gain * drive)
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
    def step(self, dt=None):
        saved_dt = self.dt
        if dt is not None:
            self.dt = dt
        # Step each child field fast; cross-scale context flows through relations.
        for knot in self.knots.values():
            if knot.child is not None:
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
        self.dt = saved_dt

    def advance(self, T):
        target = self.t + T
        while self.t + EPS < target:
            self.step(min(self.dt, target - self.t))

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
