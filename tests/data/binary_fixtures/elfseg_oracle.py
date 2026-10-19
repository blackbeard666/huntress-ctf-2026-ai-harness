"""Independent oracle for elfseg_* fixtures: GNU readelf -hlWd text (+ file -b for pie/static) and pyelftools for the
ELFOSABI_* / PT_* enum spellings. Never imports lib.  usage: python3 elfseg_oracle.py X.bin -> JSON expected dict."""
import json, re, subprocess, sys
p = sys.argv[1]
r = subprocess.run(["readelf", "-hlWd", p], capture_output=True, text=True)
fb = subprocess.run(["file", "-b", p], capture_output=True, text=True).stdout.strip()
t = r.stdout
if "ELF Header:" not in t or "Magic:" not in t or "Error" in r.stderr:
    print(json.dumps({"_all": "none", "file": fb, "readelf_err": r.stderr.strip()[:200]})); sys.exit()
g = lambda k: re.search(r"^\s*" + re.escape(k) + r":\s*(.*?)\s*$", t, re.M).group(1)
from elftools.elf.elffile import ELFFile
with open(p, "rb") as f:
    e = ELFFile(f)
    osabi = e.header.e_ident.EI_OSABI
    ptypes = [s.header.p_type for s in e.iter_segments()]
segs = re.findall(r"^  ([A-Z][A-Z_0-9]+)\s+0x", t.split("Program Headers:")[1].split("Section to Segment")[0], re.M) \
    if "Program Headers:" in t else []
stack = re.search(r"^  GNU_STACK .*? (R?W?E?)\s+0x[0-9a-f]+$", t, re.M)
dyn = t.split("Dynamic section")[1] if "Dynamic section" in t else ""
now = bool(re.search(r"\(BIND_NOW\)|\(FLAGS\)\s+.*BIND_NOW|\(FLAGS_1\)\s+Flags:.*\bNOW\b", dyn))
interp = re.search(r"\[Requesting program interpreter: (.*?)\]", t)
etype = g("Type").split()[0]
exe = etype in ("EXEC", "DYN")
out = {"e_flags": g("Flags").split(",")[0], "os_abi": osabi, "os_abi_label": g("OS/ABI"),
       "abi_version": g("ABI Version"), "e_phnum": int(g("Number of program headers")),
       "e_shnum": int(g("Number of section headers")), "e_shstrndx": int(g("Section header string table index")),
       "segments": ptypes, "segments_short": segs, "segment_count": len(segs),
       "interpreter": interp.group(1) if interp else "none",
       "needed": re.findall(r"\(NEEDED\)\s+Shared library: \[(.*?)\]", dyn),
       "bind_now": "true" if now else "false", "has_gnu_stack": "true" if stack else "false",
       "has_nx": ("true" if stack and "E" not in stack.group(1) else "false") if exe else "none",
       "execstack": ("false" if stack and "E" not in stack.group(1) else "true") if exe else "none",
       "relro": ("full" if now else "partial") if "GNU_RELRO" in segs else "none",
       "is_pie": ("true" if "pie executable" in fb else "false") if exe else "none",
       "is_static": ("true" if ("statically linked" in fb or "static-pie linked" in fb) else "false") if exe else "none"}
out["has_relro"] = "false" if out["relro"] == "none" else "true"
print(json.dumps(out))
