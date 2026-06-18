#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical semantic spine for BiDi Coherence-Delta Calculus.

This module is intentionally declarative. It does not replace the verified
reference reducer in `bidi_calculus.py`; it names the AST, runtime state, small
step kinds, and invariant registry that future reducer/proof projections should
share.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Tuple

Real = float
Name = str
Phase = float
Trit = int


class SourceKind(str, Enum):
    DEADBAND = "deadband"
    FIELD = "field"
    NEST = "nest"
    COUNTER = "counter"
    MODULE = "module"
    CHANNEL = "channel"
    GUARD = "guard"
    FLOW = "flow"
    COMMIT = "commit"
    EXPECT = "expect"
    REG = "reg"
    INSTR = "instr"
    RUN = "run"


BLOCK_KINDS = {SourceKind.FIELD, SourceKind.NEST, SourceKind.COUNTER}


@dataclass(frozen=True)
class SourceNode:
    kind: SourceKind
    flags: Tuple[str, ...]
    kwargs: Mapping[str, str]
    children: Tuple["SourceNode", ...] = field(default_factory=tuple)
    line: int = 0
    source: str = ""


@dataclass(frozen=True)
class SourceProgram:
    children: Tuple[SourceNode, ...]
    filename: str = ""


def _parts(line: str, line_no: int) -> SourceNode:
    tokens = line.split()
    if not tokens:
        raise SyntaxError(f"line {line_no}: empty statement")
    try:
        kind = SourceKind(tokens[0])
    except ValueError as exc:
        raise SyntaxError(f"line {line_no}: unknown directive {tokens[0]!r}") from exc
    is_kv = lambda t: "=" in t and t.split("=", 1)[0].isidentifier()
    kwargs = dict(t.split("=", 1) for t in tokens if is_kv(t))
    flags = tuple(t for t in tokens if not is_kv(t))
    return SourceNode(kind=kind, flags=flags, kwargs=kwargs, line=line_no, source=line)


def parse_cdc(source: str, filename: str = "") -> SourceProgram:
    """Parse `.cdc` source into a block-structured AST.

    The parser intentionally stays small: `.cdc` is line-oriented, comments begin
    with `#`, and `field`/`nest`/`counter` blocks close with `end`.
    """
    lines = []
    for line_no, raw in enumerate(source.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append((line_no, line))

    def parse_block(index: int, opener: SourceKind | None = None):
        children = []
        while index < len(lines):
            line_no, line = lines[index]
            if line == "end":
                if opener is None:
                    raise SyntaxError(f"line {line_no}: unmatched end")
                return tuple(children), index + 1

            node = _parts(line, line_no)
            if node.kind in BLOCK_KINDS:
                nested, index = parse_block(index + 1, node.kind)
                node = SourceNode(
                    kind=node.kind,
                    flags=node.flags,
                    kwargs=node.kwargs,
                    children=nested,
                    line=node.line,
                    source=node.source,
                )
            else:
                index += 1
            children.append(node)

        if opener is not None:
            raise SyntaxError(f"unterminated {opener.value} block")
        return tuple(children), index

    children, _ = parse_block(0)
    return SourceProgram(children=children, filename=filename)


class StepKind(str, Enum):
    FLOW = "flow"
    COMMIT = "commit"
    NEST = "nest"


@dataclass(frozen=True)
class CellTerm:
    theta: Phase
    amplitude: Real = 1.0
    omega: Real = 0.0
    plasticity: Real = 0.0
    latched: Trit | None = None


@dataclass(frozen=True)
class ModuleTerm:
    name: Name
    cells: Tuple[CellTerm, ...]
    belief: Tuple[Real, ...] = field(default_factory=tuple)
    prior: Tuple[Real, ...] = field(default_factory=tuple)
    precision: Real = 1.0
    action_gain: Real = 0.0


@dataclass(frozen=True)
class ChannelTerm:
    src: Name                      # may be a nesting path: "m", "m/n", "m/n/p"
    dst: Name
    weight: Real = 1.0
    delay: Real = 0.0
    line: int | None = None
    plastic: bool = False
    angle: Real = 0.0              # angular phase bias on entry to the target frame
    lines: Tuple[int, ...] | None = None


@dataclass(frozen=True)
class FieldTerm:
    name: Name
    modules: Tuple[ModuleTerm, ...] = field(default_factory=tuple)
    channels: Tuple[ChannelTerm, ...] = field(default_factory=tuple)
    children: Mapping[Name, "FieldTerm"] = field(default_factory=dict)
    dt: Real = 0.02
    gain: Real = 1.2
    deadband: Real = 0.5
    gated: bool = True


@dataclass(frozen=True)
class CounterInstr:
    name: Name
    op: str
    reg: Name | None = None
    nxt: Name | None = None
    alt: Name | None = None


@dataclass(frozen=True)
class CounterTerm:
    name: Name
    registers: Mapping[Name, int]
    instructions: Mapping[Name, CounterInstr]
    start: Name


ProgramTerm = FieldTerm | CounterTerm


@dataclass(frozen=True)
class CellState:
    theta: Phase
    amplitude: Real
    plasticity: Real
    omega: Real
    sigma: Trit
    memory: Real = 0.0


@dataclass(frozen=True)
class ModuleState:
    name: Name
    cells: Tuple[CellState, ...]
    belief: Tuple[Real, ...]
    prior: Tuple[Real, ...]
    precision: Real
    action_gain: Real
    child: Name | None = None


@dataclass(frozen=True)
class RuntimeState:
    t: Real
    modules: Mapping[Name, ModuleState]
    channels: Tuple[ChannelTerm, ...]
    fields: Mapping[Name, "RuntimeState"] = field(default_factory=dict)
    deadband: Real = 0.5
    dt: Real = 0.02
    gain: Real = 1.2
    gated: bool = True


@dataclass(frozen=True)
class ReductionStep:
    kind: StepKind
    duration: Real = 0.0
    module: Name | None = None
    witness: str = ""


@dataclass(frozen=True)
class InvariantSpec:
    key: str
    statement: str
    witness_file: str
    witness_name: str
    future_formal_target: str


INVARIANTS: Tuple[InvariantSpec, ...] = (
    InvariantSpec(
        key="gate-abelian",
        statement="Gate composition is an abelian group action on saturated phase modules.",
        witness_file="calculus_laws.py",
        witness_name="⊙ gate associative/commutative/identity/inverse",
        future_formal_target="algebraic group proof over the torus",
    ),
    InvariantSpec(
        key="interfere-monoid",
        statement="Interference is a commutative monoid with void unit.",
        witness_file="calculus_laws.py",
        witness_name="⊞ interfere associative/commutative/unit",
        future_formal_target="commutative monoid proof over carrier addition",
    ),
    InvariantSpec(
        key="rotation-linear",
        statement="Global rotation distributes over interference.",
        witness_file="calculus_laws.py",
        witness_name="⟳ distributes over ⊞",
        future_formal_target="linearity proof for the carrier action",
    ),
    InvariantSpec(
        key="corefold-morphism",
        statement="Core-fold is linear over interference and equivariant under rotation.",
        witness_file="calculus_laws.py",
        witness_name="∂ core-fold linear/equivariant",
        future_formal_target="module morphism proof for the projection operator",
    ),
    InvariantSpec(
        key="preservation",
        statement="Every accepted commit yields an admissible nonnegative trit walk.",
        witness_file="calculus_laws.py",
        witness_name="T1 Preservation",
        future_formal_target="induction over cell order in the commit barrier",
    ),
    InvariantSpec(
        key="soundness",
        statement="Accepted commits do not increase local free energy.",
        witness_file="calculus_laws.py",
        witness_name="T2 Soundness",
        future_formal_target="case split on guard accept/hold semantics",
    ),
    InvariantSpec(
        key="local-confluence",
        statement="Disjoint commits commute up to structural congruence.",
        witness_file="calculus_laws.py",
        witness_name="T3 Local confluence",
        future_formal_target="footprint-disjoint diamond lemma",
    ),
    InvariantSpec(
        key="flow-additivity",
        statement="Flow composes additively under the stated deterministic flow assumptions.",
        witness_file="calculus_laws.py",
        witness_name="T4 Flow additivity",
        future_formal_target="monoid action proof for the flow relation",
    ),
    InvariantSpec(
        key="normalforms",
        statement="Localized committed modules are stable normal-form values.",
        witness_file="calculus_laws.py",
        witness_name="T5 Normal forms",
        future_formal_target="normalization proof over finite trit walks",
    ),
)


def invariant_index() -> Mapping[str, InvariantSpec]:
    return {inv.key: inv for inv in INVARIANTS}
