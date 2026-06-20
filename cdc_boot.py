#!/usr/bin/env python3
"""
cdc_boot: minimal Python bootloader for native .cdc contracts.

This file is intentionally small. It does not implement the calculus reducer,
the semantic registry, or the witness suite in Python. Those live in .cdc files.
The bootloader only reads .cdc source, records native declarations, and verifies
declared expectations.
"""
from __future__ import annotations

import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BootState:
    root: Path
    kernel: dict[str, str] = field(default_factory=dict)
    terms: set[str] = field(default_factory=set)
    rules: set[str] = field(default_factory=set)
    provides: set[str] = field(default_factory=set)
    bootloader_steps: set[str] = field(default_factory=set)
    invariants: dict[str, dict[str, str]] = field(default_factory=dict)
    capabilities: dict[str, dict[str, str]] = field(default_factory=dict)
    witnesses: dict[str, dict[str, str]] = field(default_factory=dict)
    expectations: list[tuple[str, list[str], str]] = field(default_factory=list)


def strip_comment(line: str) -> str:
    return line.split("#", 1)[0].strip()


def split_line(line: str, filename: str, line_no: int) -> list[str]:
    try:
        return shlex.split(line)
    except ValueError as exc:
        raise SyntaxError(f"{filename}:{line_no}: {exc}") from exc


def kv(tokens: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for token in tokens:
        if "=" in token:
            key, value = token.split("=", 1)
            out[key] = value
    return out


def flags(tokens: list[str]) -> list[str]:
    return [token for token in tokens if "=" not in token]


def parse_file(state: BootState, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = strip_comment(raw)
        if not line or line == "end":
            continue
        tokens = split_line(line, str(path), line_no)
        if not tokens:
            continue
        cmd, rest = tokens[0], tokens[1:]
        args, attrs = flags(rest), kv(rest)
        source = f"{path.name}:{line_no}"

        if cmd == "kernel":
            if not args:
                raise SyntaxError(f"{source}: kernel requires a name")
            state.kernel = {"name": args[0], **attrs}
        elif cmd == "term":
            state.terms.update(args)
        elif cmd == "rule":
            state.rules.update(args)
        elif cmd == "provides":
            state.provides.update(args)
        elif cmd == "bootloader":
            state.bootloader_steps.update(args)
        elif cmd in {"invariant", "law"}:
            if not args:
                raise SyntaxError(f"{source}: {cmd} requires a key")
            key = args[0]
            state.invariants.setdefault(key, {})
            state.invariants[key].update({"kind": cmd, **attrs})
        elif cmd == "capability":
            if not args:
                raise SyntaxError(f"{source}: capability requires a key")
            key = args[0]
            state.capabilities.setdefault(key, {})
            state.capabilities[key].update(attrs)
        elif cmd == "witness":
            if not args:
                raise SyntaxError(f"{source}: witness requires an id")
            wid = args[0]
            state.witnesses[wid] = {"source": source, **attrs}
        elif cmd == "expect":
            state.expectations.append((source, rest, line))
        else:
            raise SyntaxError(f"{source}: unknown directive {cmd!r}")


def python_files(state: BootState) -> list[Path]:
    return sorted(p for p in state.root.glob("*.py") if p.is_file())


def witnesses_for(state: BootState, key: str, field: str) -> list[str]:
    return [wid for wid, attrs in state.witnesses.items() if attrs.get(field) == key]


def compare(got: int | str, op: str, want: int | str) -> bool:
    if isinstance(got, int) and isinstance(want, int):
        if op == "==":
            return got == want
        if op == ">=":
            return got >= want
        if op == "<=":
            return got <= want
    if op == "==":
        return got == want
    raise ValueError(f"unsupported comparison: {got!r} {op} {want!r}")


def eval_expect(state: BootState, args: list[str]) -> tuple[bool, str]:
    if not args:
        return False, "empty expectation"

    head = args[0]
    if head == "native" and args[1:3] == ["substrate", "=="]:
        want = args[3]
        got = state.kernel.get("target", "")
        return got == want, f"native substrate == {want} (got {got or 'unset'})"

    if head == "host-debt":
        op, want = args[1], int(args[2])
        got = 1 if state.bootloader_steps else 0
        return compare(got, op, want), f"host-debt {op} {want} (got {got})"

    if head in {"terms", "rules", "invariants", "witnesses", "capabilities"}:
        op, want = args[1], int(args[2])
        collections = {
            "terms": state.terms,
            "rules": state.rules,
            "invariants": state.invariants,
            "witnesses": state.witnesses,
            "capabilities": state.capabilities,
        }
        got = len(collections[head])
        return compare(got, op, want), f"{head} {op} {want} (got {got})"

    if head == "provides":
        missing = [item for item in args[1:] if item not in state.provides]
        return not missing, f"provides {' '.join(args[1:])}" + (f" (missing {missing})" if missing else "")

    if head == "law":
        key = args[1]
        linked = witnesses_for(state, key, "invariant")
        return key in state.invariants and bool(linked), f"law {key} (witnesses {len(linked)})"

    if head == "capability":
        key = args[1]
        linked = witnesses_for(state, key, "capability")
        return key in state.capabilities and bool(linked), f"capability {key} (witnesses {len(linked)})"

    if head == "witness":
        wid = args[1]
        return wid in state.witnesses, f"witness {wid}"

    if head == "python-files":
        op, want = args[1], int(args[2])
        files = python_files(state)
        return compare(len(files), op, want), f"python-files {op} {want} (got {len(files)}: {[p.name for p in files]})"

    if head == "bootloader":
        if args[1:] == ["minimal", "==", "true"]:
            files = python_files(state)
            ok = len(files) == 1 and files[0].name == "cdc_boot.py"
            return ok, f"bootloader minimal == true (python files {[p.name for p in files]})"

    return False, f"unknown expectation: {' '.join(args)}"


def report(state: BootState) -> bool:
    print("=" * 74)
    print("  .cdc native contract report")
    print("=" * 74)
    passed = 0
    for source, args, _line in state.expectations:
        ok, label = eval_expect(state, args)
        passed += int(ok)
        print(f"  {'OK' if ok else 'FAIL'} {label}   [{source}]")
    print("-" * 74)
    print(f"  {passed}/{len(state.expectations)} expectations met")
    print(f"  {len(state.terms)} terms, {len(state.rules)} rules, {len(state.invariants)} invariants")
    print(f"  {len(state.capabilities)} capabilities, {len(state.witnesses)} native witnesses")
    print("=" * 74)
    return passed == len(state.expectations)


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent
    paths = [root / arg for arg in argv] if argv else sorted(root.glob("*.cdc"))
    state = BootState(root=root)
    for path in paths:
        parse_file(state, path)
    return 0 if report(state) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
