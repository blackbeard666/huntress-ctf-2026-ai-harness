#!/usr/bin/env python3
"""Independent oracle for the idcol_* fixtures: reads dex2jar's baksmali output (d2j-baksmali.sh -o <dir> <apk>), finds
the instruction feeding the append right after the `proof=` literal and resolves its target by FULL descriptor:
invoke `Lcls;->m(desc)ret` -> that exact `.method` body's const-string, sget `Lcls;->f:type` -> the const-string
sput into exactly `Lcls;->f:type`. usage: oracle.py <smali dir>"""
import re, sys
from pathlib import Path
allm = "\n".join(p.read_text() for p in Path(sys.argv[1]).rglob("*.smali"))
m = re.search(r'const-string [vp]\d+, "[^"]*proof="(.*)', allm, re.S)
parts = m.group(1).split("StringBuilder;->append") if m else []
seg = parts[1] if len(parts) > 1 else ""  # between the append of the literal and the next append
val = None
inv = re.search(r"invoke-static \{[^}]*\}, (L[^;]+;)->(\w+)(\([^)]*\)\S+)", seg)
sg = re.search(r"sget-object [vp]\d+, (L[^;]+;->\w+:\S+)", seg)
if inv:
    cls, name, desc = inv.groups()
    body = next((p.read_text() for p in Path(sys.argv[1]).rglob("*.smali") if re.search(r"^\.class.* %s$" % re.escape(cls), p.read_text(), re.M)), "")
    mm = re.search(r"^\.method [^\n]*\b%s%s\n(.*?)^\.end method" % (re.escape(name), re.escape(desc)), body, re.S | re.M)
    cs = mm and re.findall(r'const-string [vp]\d+, "([^"]*)"', mm.group(1))
    val = cs[-1] if cs else None
elif sg:
    hits = re.findall(r'const-string ([vp]\d+), "([^"]*)"\s+sput-object \1, %s\s' % re.escape(sg.group(1)), allm)
    val = hits[-1][1] if hits else None
print(val if val and re.fullmatch(r"ANS-[0-9a-fA-F]{16}", val) else None)
