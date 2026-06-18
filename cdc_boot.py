#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cdc_boot — the bootstrap bridge for the .cdc language
=====================================================
This is the supplied non-.cdc execution bridge, not the language itself. It reads
`.cdc` source and drives the calculus reduction (continuous flow ⟶_d and guarded
commit ⟶_β) on the host. Programs, witnesses, and law obligations live in `.cdc`;
this file gives them an executable substrate.

Semantics are delegated to the reference reducer (`bidi_calculus`) and checked by
the law/acceptance suites. A different conforming bridge should produce the same
observable reductions for the same source.

    python3 cdc_boot.py program.cdc [more.cdc ...]
"""
import sys, math, cmath, random
from bidi_calculus import Thread, Knot, Breathfield, CounterField, census
from cdc_semantics import SourceKind, SourceNode, parse_cdc, invariant_index

# ── carrier literals ───────────────────────────────────────────────────────── #
def num(tok):
    t = tok.strip()
    table = {"pi": math.pi, "pi/2": math.pi / 2, "pi/4": math.pi / 4, "-pi": -math.pi,
             "2pi": 2 * math.pi, "tau": 2 * math.pi, "3pi/2": 3 * math.pi / 2}
    if t in table: return table[t]
    return float(t)
TRIT = {"+": 0.0, "-": math.pi, "o": math.pi / 2, "0": math.pi / 2}


def parse_lines(value):
    lines = tuple(int(x) for x in value.split(",") if x != "")
    if not lines:
        raise SyntaxError("lines= must name at least one target cell")
    if any(i < 0 for i in lines):
        raise SyntaxError(f"lines= cannot contain negative indexes: {value}")
    return lines

# ── operator algebra over the carrier (for `expect law ...`) ───────────────── #
def _rand(n=6):  return [cmath.rect(1.0, random.uniform(0, 2 * math.pi)) for _ in range(n)]
def _close(a, b, tol=1e-9): return all(abs(x - y) < tol for x, y in zip(a, b))
def _law(name):
    if name not in invariant_index():
        raise KeyError(name)
    rng = random.Random(1); random.seed(1)
    a, b, c = _rand(), _rand(), _rand()
    rot = lambda p, xs: [cmath.rect(1, p) * x for x in xs]
    mul = lambda xs, ys: [x * y for x, y in zip(xs, ys)]
    add = lambda xs, ys: [x + y for x, y in zip(xs, ys)]
    fold = lambda xs: [xs[i] for i in (1, 2, 3, 2, 3, 4)]
    one = [1 + 0j] * 6; bot = [0j] * 6; phi = 1.234
    if name == "gate-abelian":
        return (_close(mul(mul(a, b), c), mul(a, mul(b, c))) and _close(mul(a, b), mul(b, a))
                and _close(mul(a, one), a) and _close(mul(a, [x.conjugate() for x in a]), one))
    if name == "interfere-monoid":
        return (_close(add(add(a, b), c), add(a, add(b, c))) and _close(add(a, b), add(b, a))
                and _close(add(a, bot), a))
    if name == "rotation-linear":
        return _close(rot(phi, add(a, b)), add(rot(phi, a), rot(phi, b)))
    if name == "corefold-morphism":
        return (_close(fold(add(a, b)), add(fold(a), fold(b))) and _close(fold(rot(phi, a)), rot(phi, fold(a)))
                and not _close(fold(fold(a)), fold(a)))
    if name == "preservation":
        for _ in range(500):
            k = Knot("k", threads=[Thread(theta=random.uniform(0, 6.28)) for _ in range(6)])
            k.commit([0j] * 6)
            r = 0
            for t in k.trits():
                r += t
                if r < 0: return False
        return True
    if name == "soundness":
        worst = -1e9
        for _ in range(800):
            k = Knot("k", threads=[Thread(theta=random.uniform(0, 6.28)) for _ in range(6)])
            k.belief = [random.uniform(-1, 1) for _ in range(6)]; k.precision = random.uniform(.1, 5)
            A = [cmath.rect(random.uniform(0, 1.5), random.uniform(0, 6.28)) for _ in range(6)]
            f0 = k.free_energy(A); f1, _ = k.commit(A); worst = max(worst, f1 - f0)
        return worst <= 1e-9
    if name == "normalforms":
        c = census(); return c["classical_localized"] == 5 and c["localized"] == 51
    raise KeyError(name)

# ── the bootstrap interpreter ──────────────────────────────────────────────── #
class Field:
    def __init__(self, name, dt, gain, open_, deadband):
        self.name = name
        self.deadband = deadband
        self.bf = Breathfield(dt=dt, gain=gain, deadband=deadband, kappa_gate=not open_)

class Counter:
    def __init__(self, name): self.name = name; self.cf = CounterField(); self.start = None; self.result = None

class CDC:
    def __init__(self):
        self.stack = []          # nested Field/Counter contexts
        self.fields = {}         # name -> Field (for reference)
        self.results = []        # (ok, label)
        self.deadband = 0.5      # global default; can be overridden before fields

    def top(self):  return self.stack[-1]
    def field_top(self):
        for c in reversed(self.stack):
            if isinstance(c, Field): return c
        raise SyntaxError("no enclosing field")

    def run_files(self, paths):
        for p in paths:
            self.run(open(p, encoding="utf-8").read(), p)
        return self

    def run(self, src, fname=""):
        program = parse_cdc(src, fname)
        for node in program.children:
            self.exec_node(node)

    def exec_node(self, node: SourceNode):
        if node.kind in (SourceKind.FIELD, SourceKind.NEST, SourceKind.COUNTER):
            self.exec_statement(node)
            for child in node.children:
                self.exec_node(child)
            self.exec_end()
            return
        self.exec_statement(node)

    def exec_line(self, line):
        program = parse_cdc(line)
        if len(program.children) != 1:
            raise SyntaxError(f"expected one statement: {line}")
        self.exec_node(program.children[0])

    def exec_end(self):
        ctx = self.stack.pop()
        if isinstance(ctx, Field) and hasattr(ctx, "_attach"):
            parent, module = ctx._attach
            parent.bf.nest(module, ctx.bf)
        if isinstance(ctx, Counter) and ctx.start is not None:
            ctx.result = ctx.cf.run(ctx.start)

    def exec_statement(self, node: SourceNode):
        kw = node.kind.value
        kv = dict(node.kwargs)
        flags = list(node.flags)      # keeps operators like >=, ==, <=
        line = node.source

        if kw == "deadband":
            if self.stack:
                raise SyntaxError("deadband must be declared outside any field or counter")
            value = num(flags[1])
            if not (0.0 < value < 1.0):
                raise SyntaxError("deadband must satisfy 0 < deadband < 1")
            self.deadband = value
            return

        if kw == "field":
            deadband = float(kv.get("deadband", self.deadband))
            f = Field(flags[1], float(kv.get("dt", 0.02)), float(kv.get("gain", 1.2)),
                      kv.get("open", "no").lower() in ("yes", "true", "1"), deadband)
            self.stack.append(f); self.fields[f.name] = f; return

        if kw == "nest":
            module = flags[1]
            deadband = float(kv.get("deadband", self.field_top().deadband))
            child = Field("_child", float(kv.get("dt", 0.005)), float(kv.get("gain", 1.2)),
                          kv.get("open", "no").lower() in ("yes", "true", "1"), deadband)
            child._attach = (self.field_top(), module)
            self.stack.append(child); return

        if kw == "counter":
            self.stack.append(Counter(flags[1])); return

        if kw == "expect" and not self.stack:                     # top-level law assertions
            a = flags[1:]
            if a and a[0] == "law":
                self.results.append((_law(a[1]), f"law {a[1]}")); return
            raise SyntaxError(f"top-level expect: {line}")

        ctx = self.top()

        # ----- counter sub-language -----
        if isinstance(ctx, Counter):
            if kw == "reg":   ctx.cf.reg(flags[1], int(flags[2]) if len(flags) > 2 else 0); return
            if kw == "instr":
                name = flags[1]; op = flags[2]
                if op == "inc":
                    ctx.cf.instr(name, "inc", reg=flags[3], nxt=flags[5]); return
                if op == "jzdec":
                    # instr L0 jzdec c2 -> L1 | H
                    reg = flags[3]; nz = flags[5]; z = flags[7]
                    ctx.cf.instr(name, "jzdec", reg=reg, nxt=nz, alt=z); return
                if op == "halt":
                    ctx.cf.instr(name, "halt"); return
            if kw == "run":    ctx.start = flags[2]; return  # run from <start>
            if kw == "expect":
                # expect reg c1 == 7
                if flags[1] == "reg":
                    if ctx.result is None: ctx.result = ctx.cf.run(ctx.start)
                    got = ctx.result.get(flags[2]); want = int(flags[4])
                    self.results.append((got == want, f"{ctx.name}: reg {flags[2]} == {want} (got {got})"))
                    return
            raise SyntaxError(f"counter: {line}")

        # ----- field language -----
        bf = ctx.bf
        if kw == "module":
            name = flags[1]
            sub = flags[2]
            if sub == "theta":
                vals = []; i = 3
                while i < len(flags) and flags[i] not in ("omega", "precision", "prior", "act"):
                    vals.append(num(flags[i])); i += 1
                ths = [Thread(theta=v) for v in vals]
                if "omega" in flags:
                    j = flags.index("omega") + 1; oms = []
                    while j < len(flags) and flags[j] not in ("precision", "prior", "act"):
                        oms.append(num(flags[j])); j += 1
                    for t, o in zip(ths, oms * len(ths)): t.omega = o
                k = Knot(name, threads=ths)
            elif sub == "trits":
                k = Knot(name, threads=[Thread(theta=TRIT[x]) for x in flags[3:3 + 6]])
            else:
                raise SyntaxError(line)
            if "precision" in flags: k.precision = num(flags[flags.index("precision") + 1])
            if "act" in flags:       k.act_gain = num(flags[flags.index("act") + 1])
            if "prior" in flags:
                j = flags.index("prior") + 1; k.prior = [num(flags[j + i]) for i in range(k.n)]
            bf.add(k); return

        if kw == "channel":
            src, dst = flags[1], flags[3]
            angle = num(kv["angle"]) if "angle" in kv else 0.0
            lines = parse_lines(kv["lines"]) if "lines" in kv else None
            weight = num(kv.get("weight", "1.0"))
            tau = num(kv.get("delay", "0.0"))
            if "/" in src or "/" in dst:
                bf.relate(src, dst, weight=weight, tau=tau, angle=angle, lines=lines)
            else:
                bf.wire(src, dst, weight=weight, tau=tau, angle=angle, lines=lines,
                        hebbian=("plastic" in flags))
            return
        if kw == "guard":
            i = int(flags[3]) if len(flags) > 3 else 0
            bf.guards[flags[1]] = (lambda idx: (lambda k, t: math.sin(k.threads[idx].theta) - 0.7))(i); return
        if kw == "flow":   bf.advance(num(flags[1])); return
        if kw == "commit":
            if flags[1] == "all": bf.breathe_all()
            else:
                k = bf.knots[flags[1]]; k.commit(bf.afferent(k, bf.t))
            return
        if kw == "expect":
            self.results.append(self.eval_expect(bf, flags[1:], line)); return

        raise SyntaxError(f"unknown: {line}")

    # ----- expectation predicates -----
    def eval_expect(self, bf, a, line):
        p = a[0]
        if p == "law":
            return (_law(a[1]), f"law {a[1]}")
        if p == "coherence-global":
            v = float(a[2]); g = bf.global_coherence()
            ok = g >= v if a[1] == ">=" else g <= v
            return (ok, f"coherence-global {a[1]} {v} (got {g:.2f})")
        if p == "coherence":
            m = bf.knots[a[1]]; v = float(a[3]); g = m.coherence()
            ok = g >= v if a[2] == ">=" else g <= v
            return (ok, f"coherence {a[1]} {a[2]} {v} (got {g:.2f})")
        if p == "admissible":
            return (bf.knots[a[1]].admissible(), f"admissible {a[1]}")
        if p == "localized":
            return (bf.knots[a[1]].localized(), f"localized {a[1]}")
        if p == "address":
            got = bf.knots[a[1]].address(); want = int(a[3])
            return (got == want, f"address {a[1]} == {want} (got {got})")
        if p == "belief":
            m = bf.knots[a[1]]; v = float(a[3]); tol = float(a[4]) if len(a) > 4 else 0.1
            sens = bf.afferent(m, bf.t)[0].real
            return (abs(m.belief[0] - v) < tol and abs(sens - v) < 0.2, f"belief {a[1]} near {v} (got {m.belief[0]:.3f})")
        if p == "weight":
            src, dst = a[1], a[2]; v = float(a[4])
            w = next(s.weight for s in bf.strands if s.src.name == src and s.dst.name == dst)
            ok = w > v if a[3] == ">" else w < v
            return (ok, f"weight {src}->{dst} {a[3]} {v} (got {w:.2f})")
        if p == "delay":
            src, dst, tau = a[1], a[2], float(a[3])
            W = bf.knots[src]; now = W.threads[0].theta % (2 * math.pi)
            d = cmath.phase(W.delayed(bf.t, tau)[0]) % (2 * math.pi)
            lag = (now - d) % (2 * math.pi); want = (W.threads[0].omega * tau) % (2 * math.pi)
            return (abs(lag - want) < 0.06, f"delay {src}->{dst} ≈ ω·τ={want:.2f} (got {lag:.2f})")
        if p == "events-offgrid":
            if not bf.events: return (False, "events-offgrid (none fired)")
            te = bf.events[0][0]; off = abs((te / bf.dt) - round(te / bf.dt))
            return (off > 1e-6, f"events-offgrid (t={te:.4f}, off {off:.3f})")
        if p == "multirate":
            v = int(a[2])
            ipo = max((getattr(k.child, "inner_per_outer", 0) for k in bf.knots.values() if k.child), default=0)
            return (ipo >= v, f"multirate >= {v} (got {ipo})")
        if p == "interference":
            # expect interference <src-path> <dst-path> <cos|sin|gamma|energy> <op> <v>
            src, dst, fld, op, v = a[1], a[2], a[3], a[4], float(a[5])
            src_obj, dst_obj = bf.resolve(src), bf.resolve(dst)
            candidates = [s for s in bf.strands if s.dst is dst_obj] + dst_obj.inbound
            strand = next((s for s in candidates if s.src is src_obj), None)
            if strand is None:
                raise SyntaxError(f"no relation found for interference assertion: {src} -> {dst}")
            ro = bf.relation_readout(strand)[fld]
            ok = ro >= v if op == ">=" else ro <= v if op == "<=" else abs(ro - v) < 1e-6
            return (ok, f"interference {src}->{dst} {fld} {op} {v} (got {ro:.2f})")
        raise SyntaxError(f"expect: {line}")

    def report(self):
        print("═" * 74)
        print("  .cdc execution report   (bootstrap bridge → calculus reduction)")
        print("═" * 74)
        npass = 0
        for ok, label in self.results:
            npass += ok
            print(f"  {'✅' if ok else '❌'} {label}")
        print("─" * 74)
        print(f"  {npass}/{len(self.results)} expectations met")
        print("═" * 74)
        return npass == len(self.results)


if __name__ == "__main__":
    paths = sys.argv[1:] or []
    ok = CDC().run_files(paths).report()
    sys.exit(0 if ok else 1)
