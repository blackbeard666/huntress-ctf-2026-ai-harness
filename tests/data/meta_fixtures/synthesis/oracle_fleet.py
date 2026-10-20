"""Independent oracle for synthesis_fleet fixtures: per-member cpu types via macholib (thin + fat), pyelftools
(e_machine), pefile (FILE_HEADER.Machine), `ar t` + `ar p` (GNU binutils) and zipfile for archive members.
usage: oracle_fleet.py <kit.zip> -> JSON of every field (Files = zip order)."""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

from elftools.elf.elffile import ELFFile
import macholib.MachO
import pefile

ELF = {"EM_AARCH64": 0x0100000C, "EM_X86_64": 0x01000007, "EM_386": 7, "EM_ARM": 12}
PE = {0xAA64: 0x0100000C, 0x8664: 0x01000007, 0x14C: 7}


def cpus(b, depth=0):
    with tempfile.NamedTemporaryFile(delete=False) as t:
        t.write(b)
    p = t.name
    try:
        try:
            m = macholib.MachO.MachO(p)
            return ("fat" if m.fat else "thin"), [h.header.cputype & 0xFFFFFFFF for h in m.headers]
        except Exception:
            pass
        try:
            e = ELFFile(io.BytesIO(b))
            return "elf", [ELF[e["e_machine"]]] if e["e_machine"] in ELF else []
        except Exception:
            pass
        try:
            pe = pefile.PE(data=b, fast_load=True)
            return "pe", [PE[pe.FILE_HEADER.Machine]] if pe.FILE_HEADER.Machine in PE else []
        except Exception:
            pass
        out = []
        if b[:8] == b"!<arch>\n":
            names = subprocess.run(["ar", "t", p], capture_output=True, text=True).stdout.split()
            mem = [subprocess.run(["ar", "p", p, n], capture_output=True).stdout for n in names]
        elif zipfile.is_zipfile(io.BytesIO(b)):
            z = zipfile.ZipFile(io.BytesIO(b))
            mem = [z.read(n) for n in z.namelist()]
        else:
            return "data", []
        for x in mem:
            for c in cpus(x, depth + 1)[1]:
                if c not in out:
                    out.append(c)
        return "archive", out
    finally:
        os.unlink(p)


z = zipfile.ZipFile(sys.argv[1])
rows = [(n,) + cpus(z.read(n)) for n in z.namelist()]
WORDS = {0x0100000C: ("arm64", "aarch64"), 0x01000007: ("x86_64", "amd64", "x64"), 7: ("i386", "x86", "ia32", "i686")}


def liar(n, k, cs):
    toks = re.split(r"[^a-z0-9_]+", n.lower().replace("x86-64", "x86_64"))
    toks = [t for tok in toks for t in ([tok] if tok in ("x86_64",) else tok.split("_"))] + toks
    if ({"universal", "fat"} & set(toks)) and not (k == "fat" and len(set(cs)) >= 2):
        return True
    return any(c not in cs for c, ws in WORDS.items() if set(ws) & set(toks))


groups = {}
for n, _, cs in rows:
    for c in cs:
        groups.setdefault("0x%08x" % c, set()).add(n)
union = []
for _, _, cs in rows:
    union += [c for c in cs if c not in union]
res = {"files_supporting_" + a: [n for n, _, cs in rows if c in cs] for c, (a, *_) in WORDS.items()}
res.update({"count_" + k[17:]: len(v) for k, v in list(res.items())})
res.update(universal_files=[n for n, k, cs in rows if k == "fat" and len(set(cs)) >= 2],
           thin_files=[n for n, k, _ in rows if k == "thin"],
           cpu_type_groups={k: sorted(groups[k]) for k in sorted(groups)},
           extension_or_name_liars=[n for n, k, cs in rows if liar(n, k, cs)],
           union_cpu_type_set=["0x%08x" % c for c in union])
print(json.dumps({k: (json.dumps(v, separators=(",", ":")) if isinstance(v, (list, dict)) and v else
                      ("none" if isinstance(v, (list, dict)) else str(v))) for k, v in res.items()}, indent=1))
