#!/usr/bin/env python3
"""Independent oracle for the proofflow_* fixtures: reads jadx's decompiled Java (jadx -d <dir> <apk>), finds the
expression appended after `proof=` (`.append("..proof=").append(X)` or `"..proof=" + X`) and follows it through the
sources by regex: a field -> its last `X = "..."` assignment, `Cls.m()` -> `m() { return Y; }` -> Y. usage: oracle.py <jadx dir>"""
import re, sys
from pathlib import Path
src = {p.stem: p.read_text() for p in Path(sys.argv[1]).rglob("*.java")}
allj = "\n".join(src.values())
m = re.search(r'proof="\)\.append\(([\w.()]+)\)|proof=" \+ ([\w.()]+)', allj)
expr = (m.group(1) or m.group(2)) if m else None
for _ in range(5):
    if expr is None:
        break
    g = re.fullmatch(r"(?:(\w+)\.)?(\w+)\(\)", expr)
    if g:
        body = src.get(g.group(1), allj)
        r = re.search(r"\b%s\(\) \{\s*return ([^;]+);" % g.group(2), body)
        expr = r.group(1).strip() if r else None
        continue
    if expr.startswith('"'):
        break
    f = expr.split(".")[-1]
    body = src.get(expr.split(".")[0], allj) if "." in expr else allj
    hits = re.findall(r'\b%s = ("[^"]*")' % f, body)
    expr = hits[-1] if hits else None
val = expr.strip('"') if expr else None
print(val if val and re.fullmatch(r"ANS-[0-9a-fA-F]{16}", val) else None)
