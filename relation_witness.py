#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relational phase-channel witnesses.

These checks exercise the angle-biased, dimension-projected, path-aware
generalization of bidi-gamma-delta:

  W1  angled channels change interference predictably;
  W2  lines= projects a relation onto chosen cells;
  W3  explicit cross-scale path relations transport coherence across nesting;
  W4  native .cdc nesting installs the same alpha=0 cone as the Python API.
"""
import math
import sys

from bidi_calculus import Breathfield, Knot, Thread
from cdc_boot import CDC


CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((ok, f"{name}" + (f"   [{detail}]" if detail else "")))


def open_pair(alpha):
    bf = Breathfield(dt=0.02, gain=0.0, kappa_gate=True)
    bf.add(Knot("A", threads=[Thread(theta=math.pi / 2)]))
    bf.add(Knot("B", threads=[Thread(theta=math.pi / 2)]))
    bf.wire("A", "B", weight=1.0, angle=alpha)
    return bf, bf.strands[-1]


# W1: angle controls interference and residual boundary energy.
rows = {alpha: Breathfield.relation_readout(*open_pair(alpha))
        for alpha in (0.0, math.pi / 2, math.pi)}
cos_ok = (rows[0.0]["cos"] > 0.99
          and abs(rows[math.pi / 2]["cos"]) < 1e-9
          and rows[math.pi]["cos"] < -0.99)
en_ok = (rows[0.0]["energy"] < 1e-9
         and 0.9 < rows[math.pi / 2]["energy"] < 1.1
         and rows[math.pi]["energy"] > 1.9)
check("W1 angle sets interference: cos delta = +1, 0, -1", cos_ok,
      f"cos={rows[0.0]['cos']:.2f},{rows[math.pi / 2]['cos']:.2f},{rows[math.pi]['cos']:.2f}")
check("W1 residual energy rises with angular misalignment", en_ok,
      f"energy={rows[0.0]['energy']:.2f},{rows[math.pi / 2]['energy']:.2f},{rows[math.pi]['energy']:.2f}")


# W2: lines= projects a relation onto named target dimensions only.
bf = Breathfield(dt=0.02, gain=1.5, kappa_gate=False)
bf.add(Knot("S", threads=[Thread(theta=0.0) for _ in range(6)]))
bf.add(Knot("T", threads=[Thread(theta=1.2, omega=0.0) for _ in range(6)]))
bf.wire("S", "T", weight=2.0, lines=[0, 2])
bf.advance(4.0)
theta = [round(th.theta, 3) for th in bf.knots["T"].threads]
moved = [abs(theta[i] - 1.2) > 0.2 for i in range(6)]
check("W2 lines= projects the relation onto chosen dimensions only",
      moved[0] and moved[2] and not any(moved[i] for i in (1, 3, 4, 5)),
      f"cells moved: {[i for i in range(6) if moved[i]]}")


# W3: explicit path relations can cut across nesting at an angular phase.
def tower(alpha=None):
    parent = Breathfield(dt=0.02, gain=1.5, kappa_gate=False)
    parent.add(Knot("P", threads=[Thread(theta=1.0, omega=0.0)]))
    child = Breathfield(dt=0.005, kappa_gate=False)
    child.add(Knot("c", threads=[Thread(theta=0.0, omega=0.0)]))
    parent.nest("P", child)
    if alpha is not None:
        parent.relate("P/c", "P", weight=2.0, angle=alpha)
    parent.advance(5.0)
    return parent.knots["P"].threads[0].theta


cone_only = tower()
reversed_ = tower(math.pi)
check("W3 alpha=0 nesting cone transports child coherence upward; alpha=pi opposes it",
      cone_only < 0.6 and reversed_ > 2.5,
      f"cone->{cone_only:.2f} alpha=pi->{reversed_:.2f}")


# W4: the native .cdc bridge must install the same auto cone when closing nest.
src = """
field tower open=yes gain=1.5 dt=0.02
  module P theta 1.0 omega 0.0
  nest P dt=0.005 open=yes
    module c theta 0.0 omega 0.0
  end
  flow 5.0
end
"""
c = CDC()
c.run(src)
parent = c.fields["tower"].bf.knots["P"]
child_inbounds = [len(k.inbound) for k in parent.child.knots.values()]
check("W4 .cdc nest installs auto up/down relation cones",
      len(parent.inbound) >= 1 and all(n >= 1 for n in child_inbounds)
      and parent.threads[0].theta < 0.6,
      f"parent theta={parent.threads[0].theta:.2f}, inbound={len(parent.inbound)}/{child_inbounds}")


if __name__ == "__main__":
    print("=" * 76)
    print("  Relational phase-channel witnesses (angular / projected / cross-scale)")
    print("=" * 76)
    npass = 0
    for ok, label in CHECKS:
        npass += ok
        print(f"  {'OK' if ok else 'FAIL'} {label}")
    print("-" * 76)
    print(f"  {npass}/{len(CHECKS)} relational witnesses met")
    print("=" * 76)
    sys.exit(0 if npass == len(CHECKS) else 1)
