"""Independent oracle for reloc_*.bin: GNU readelf -rW / -dW / -lW / -sW / -SW + objdump -d (no lib.binary).
usage: python3 reloc_oracle.py <elf> [--hcfg]   -> JSON of the expected elf_reloc_facts subset
  --hcfg: also the expected HCFG offset = file offset of the local symbol c0 (the first table chunk; readelf -sW value
          mapped through readelf -SW), the config itself comes from the generator's JSON argument."""
import json, re, subprocess, sys


def run(*a):
    return subprocess.run(list(a), capture_output=True, text=True).stdout


p = sys.argv[1]
if not open(p, "rb").read(4) == b"\x7fELF":
    print(json.dumps(None))
    sys.exit(0)
rel = run("readelf", "-rW", p)
out, counts, kinds = {}, {}, {k: 0 for k in ("JUMP_SLOT", "GLOB_DAT", "RELATIVE", "IRELATIVE", "COPY")}
plt, cps, total, secnames = [], [], 0, []
for blk in re.split(r"\n(?=Relocation section ')", rel):
    m = re.match(r"Relocation section '([^']+)' at offset \S+ contains (\d+) entr", blk.strip())
    if not m:
        continue
    sec, n = m.group(1), int(m.group(2))
    secnames.append(sec)
    out[sec.strip(".").replace(".", "_") + "_count"] = n
    total += n
    for ln in blk.splitlines():
        r = re.match(r"^([0-9a-f]{8,16})\s+[0-9a-f]+\s+(R_\S+)\s*(.*)$", ln)
        if not r:
            continue
        t, rest = r.group(2), r.group(3)
        counts[t] = counts.get(t, 0) + 1
        short = t.split("_", 3)[-1] if t.startswith("R_X86_64_") else t
        if short in kinds:
            kinds[short] += 1
        sym = re.match(r"[0-9a-f]+\s+(\S+?)(?:@\S+)?\s+[+-]", rest)
        name = sym.group(1) if sym else ""
        if sec.endswith(".plt"):
            plt.append(name if name else "*ABS*+0x" + rest.strip())
        if short == "COPY":
            cps.append(name)
dyn = run("readelf", "-dW", p)
now = bool(re.search(r"\(BIND_NOW\)|\(FLAGS\).*\bBIND_NOW\b|\(FLAGS_1\).*\bNOW\b", dyn))
relro = ("full" if now else "partial") if "GNU_RELRO" in run("readelf", "-lW", p) else "none"
stubs = {}
for m in re.finditer(r"^0*([0-9a-f]+) <(.+)@plt>:", run("objdump", "-d", "-j", ".plt", "-j", ".plt.sec", p), re.M):
    stubs["0x" + m.group(1)] = m.group(2)
out.update({"relocation_sections": json.dumps(secnames), "counts": counts, "relocation_count": total,
            "plt_imports": json.dumps(plt), "plt_import_count": len(plt), "plt_stubs": stubs,
            "copy_symbols": json.dumps(cps), "bind_now": "true" if now else "false",
            "lazy_binding": "true" if plt and not now else "false", "relro": relro,
            "has_relro": "false" if relro == "none" else "true"})
out.update({k.lower() + "_count": v for k, v in kinds.items()})
if "--hcfg" in sys.argv:
    sym = re.search(r"\s([0-9a-f]{16})\s+\d+\s+OBJECT\s+LOCAL\s+\w+\s+\S+\s+c0$", run("readelf", "-sW", p), re.M)
    va = int(sym.group(1), 16)
    for s in re.finditer(r"\]\s+(\S+)\s+\S+\s+([0-9a-f]{16})\s+([0-9a-f]+)\s+([0-9a-f]+)", run("readelf", "-SW", p)):
        a, o, n = int(s.group(2), 16), int(s.group(3), 16), int(s.group(4), 16)
        if a and a <= va < a + n:
            out["hcfg_offset"] = o + va - a
print(json.dumps(out, sort_keys=True))
