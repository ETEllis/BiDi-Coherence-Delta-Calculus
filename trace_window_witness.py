#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ternary trace/window witnesses.

These checks exercise observer-relative traces as a derived layer over the
existing BIDI spine. They do not add a Boolean observer, a new collapse operator,
or a fourth reduction kind. Measurement remains a guarded ternary commit.
"""
import math
import sys

from bidi_calculus import Breathfield, Knot, Thread


CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((ok, f"{name}" + (f"   [{detail}]" if detail else "")))


def snapshot(bf):
    return (
        round(bf.t, 12),
        tuple(sorted(
            (name,
             tuple(round(th.theta, 12) for th in knot.threads),
             tuple(round(x, 12) for x in knot.belief),
             tuple(th.sigma for th in knot.threads))
            for name, knot in bf.knots.items()
        )),
        tuple(bf.events),
        tuple(bf.F_log),
        len(bf.measurements),
    )


# T6: trace additivity over phase-time windows.
bf = Breathfield(dt=0.05, gain=0.0, kappa_gate=False)
bf.add(Knot("M", threads=[Thread(theta=0.0, omega=1.0) for _ in range(3)]))
bf.advance(1.0)
a = bf.trace_window("M", t0=0.0, t1=0.5, record=False)
b = bf.trace_window("M", t0=0.5, t1=1.0, record=False)
whole = bf.trace_window("M", t0=0.0, t1=1.0, record=False)
add_ok = abs((a.total_phase_motion + b.total_phase_motion) - whole.total_phase_motion) < 1e-9
check("T6 trace motion composes across adjacent windows", add_ok,
      f"{a.total_phase_motion:.3f}+{b.total_phase_motion:.3f}={whole.total_phase_motion:.3f}")


# W5: passive observer changes no dynamics, only records a trace.
bf = Breathfield(dt=0.02, gain=0.0, kappa_gate=False)
bf.add(Knot("O", threads=[Thread(theta=0.2, omega=0.0) for _ in range(3)]))
bf.advance(0.1)
before = snapshot(bf)
log_before = len(bf.trace_log)
tr = bf.trace_window("O", horizon_time=0.06)
after = snapshot(bf)
check("W5 passive observation leaves field state unchanged",
      before == after and len(bf.trace_log) == log_before + 1 and tr.scope_path == "O",
      f"samples={len(tr.samples)}")


# W6: committing measurement is a ternary, admissible, Phi-nonincreasing commit.
bf = Breathfield(dt=0.02, gain=1.2, kappa_gate=False)
bf.add(Knot("S", threads=[Thread(theta=0.0) for _ in range(6)]))
bf.add(Knot("T", threads=[Thread(theta=math.pi / 2) for _ in range(6)]))
bf.wire("S", "T", weight=2.0)
bf.advance(0.2)
rec = bf.measure("S", "T", commit=True)
ternary = all(x in (-1, 0, 1) for x in rec.outcome_trit)
check("W6 committing measurement yields only ternary outcomes",
      ternary and rec.committed and rec.barrier_applied and bf.knots["T"].admissible(),
      f"outcome={rec.outcome_trit}")
check("W6 committing measurement does not increase Phi",
      rec.phi_delta <= 1e-9,
      f"delta={rec.phi_delta:.3f}")


# W7: passive and committing observers diverge only at the commit boundary.
def pair(commit):
    f = Breathfield(dt=0.02, gain=1.2, kappa_gate=False)
    f.add(Knot("S", threads=[Thread(theta=0.0) for _ in range(6)]))
    f.add(Knot("T", threads=[Thread(theta=math.pi / 2) for _ in range(6)]))
    f.wire("S", "T", weight=2.0)
    f.advance(0.2)
    before = tuple(round(th.theta, 8) for th in f.knots["T"].threads)
    f.measure("S", "T", commit=commit)
    after = tuple(round(th.theta, 8) for th in f.knots["T"].threads)
    return before, after


pb, pa = pair(False)
cb, ca = pair(True)
check("W7 observer effect appears only after committing measurement",
      pb == cb and pa != ca,
      f"passive={pa[0]:.3f}, committing={ca[0]:.3f}")


# W8: nested child coherence acts as a multiscale agency signal into the parent.
parent = Breathfield(dt=0.02, gain=1.5, kappa_gate=False)
parent.add(Knot("P", threads=[Thread(theta=1.0, omega=0.0)]))
child = Breathfield(dt=0.005, kappa_gate=False)
child.add(Knot("c", threads=[Thread(theta=0.0, omega=0.0)]))
parent.nest("P", child)
before = parent.knots["P"].threads[0].theta
parent.advance(5.0)
after = parent.knots["P"].threads[0].theta
agency = parent.agency_summary("P", horizon_time=0.1)
check("W8 multiscale agency pulls parent toward child coherence",
      after < before and agency.cross_scale_gain > 0 and agency.stability > 0.9,
      f"{before:.2f}->{after:.2f}, gain={agency.cross_scale_gain:.2f}")


# W9: subordinate modules can project into multiple higher-order boundaries.
bf = Breathfield(dt=0.02, gain=1.0, kappa_gate=False)
bf.add(Knot("A", threads=[Thread(theta=0.0) for _ in range(3)]))
bf.add(Knot("B", threads=[Thread(theta=0.2) for _ in range(3)]))
bf.add(Knot("C", threads=[Thread(theta=1.4) for _ in range(3)]))
bf.add(Knot("D", threads=[Thread(theta=math.pi / 2) for _ in range(3)]))
ab = bf.project_boundary("AB", ("A", "B"))
ac = bf.project_boundary("AC", ("A", "C"))
bf.wire("AB", "D", weight=1.0)
bf.wire("AC", "D", weight=1.0, angle=math.pi / 4)
check("W9 one subordinate module can participate in multiple projected boundaries",
      "AB" in bf.knots and "AC" in bf.knots and ab.coherence() > 0.9 and ac.coherence() > 0.7
      and sum(1 for s in bf.strands if s.dst is bf.knots["D"]) == 2,
      f"gamma AB={ab.coherence():.2f}, AC={ac.coherence():.2f}")


# W10: windows are causal; they cannot read future field state.
try:
    bf.trace_window("A", t0=0.0, t1=bf.t + 1.0, record=False)
except ValueError:
    causal = True
else:
    causal = False
check("W10 trace windows cannot read future state", causal)


if __name__ == "__main__":
    print("=" * 76)
    print("  Ternary trace/window witnesses")
    print("=" * 76)
    npass = 0
    for ok, label in CHECKS:
        npass += ok
        print(f"  {'OK' if ok else 'FAIL'} {label}")
    print("-" * 76)
    print(f"  {npass}/{len(CHECKS)} trace/window witnesses met")
    print("=" * 76)
    sys.exit(0 if npass == len(CHECKS) else 1)
