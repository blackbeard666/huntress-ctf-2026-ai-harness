"""Independent oracle for symver_*.bin: readelf -VW / readelf --dyn-syms -W / objdump -d -Mintel (binutils) +
nm -D --defined-only on the host libc.so.6 (the libc name set) + pyelftools (string at an address). Never lib.binary.
usage: python3 symver_oracle.py <file.bin>   -> JSON expected_facts on stdout ("none" for empty/absent)"""
import json, re, subprocess, sys
from elftools.elf.elffile import ELFFile

f = sys.argv[1]
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout
if open(f, "rb").read(4) != b"\x7fELF":
    print(json.dumps(None)); sys.exit()
V = run("readelf", "-VW", f)
nz = lambda v: v if v else "none"
verdefs, cur = [], None
for l in V.split("Version needs")[0].splitlines():
    m = re.search(r"Flags: (.+?)\s+Index: (\d+)\s+Cnt: \d+\s+Name: (\S+)", l)
    if m:
        cur = {"index": int(m.group(2)), "flags": m.group(1).strip(), "name": m.group(3), "parents": []}
        verdefs.append(cur)
    m = re.search(r"Parent \d+: (\S+)", l)
    if m and cur:
        cur["parents"].append(m.group(1))
verneeds = {}
if "Version needs" in V:
    for l in V.split("Version needs")[1].splitlines():
        m = re.search(r"File: (\S+)", l)
        if m:
            lst = verneeds.setdefault(m.group(1), [])
        m = re.search(r"Name: (\S+)\s+Flags", l)
        if m:
            lst.append(m.group(1))
syms = []
for l in run("readelf", "--dyn-syms", "-W", f).splitlines():
    m = re.match(r"\s*(\d+): ([0-9a-f]+)\s+(\d+) (\w+)\s+(\w+)\s+(\w+)\s+(\w+) (\S+)(?: \((\d+)\))?$", l)
    if m and m.group(1) != "0":
        syms.append(dict(zip(("i", "val", "size", "type", "bind", "vis", "ndx", "label"), m.groups()[:8])))
for s in syms:
    s["name"] = re.split(r"@@?", s["label"])[0]
uniq = lambda xs: nz(list(dict.fromkeys(xs)))
libc = set(run("nm", "-D", "--defined-only", "/lib/x86_64-linux-gnu/libc.so.6").split()[2::3])
libc = {x.split("@")[0] for x in libc}
defined = [s for s in syms if s["ndx"] != "UND"]
interposed = uniq(s["name"] for s in defined if s["type"] == "FUNC" and s["name"] in libc)
# RTLD_NEXT: objdump functions; a call to dlsym (PLT or GOT) preceded in the same function by mov rdi,-1, or a call to
# a local helper that does so
D = run("objdump", "-d", "-Mintel", "--no-show-raw-insn", f)
funcs, cur = {}, None
for l in D.splitlines():
    m = re.match(r"([0-9a-f]+) <([^>]+)>:", l)
    if m:
        cur = funcs.setdefault(m.group(2), [])
        continue
    if cur is not None and l.strip():
        cur.append(l)
def direct(fn):
    neg = False
    for l in funcs.get(fn, []):
        if re.search(r"\tmov\s+rdi,0xffffffffffffffff", l):
            neg = True
        elif re.search(r"\tcall", l):
            if "dlsym" in l and neg:
                return True
            neg = False
    return False
def calls_next(fn):
    if direct(fn):
        return True
    for l in funcs.get(fn, []):
        m = re.search(r"\tcall\s+[0-9a-f]+ <([^>@+]+)>", l)
        if m and m.group(1) != fn and direct(m.group(1)):
            return True
    return False
rtl = [s["name"] for s in defined if s["type"] == "FUNC" and calls_next(s["name"])]
# returned strings of multi-version functions: objdump lea rax,[rip+..] # <addr>, string read with pyelftools
e = ELFFile(open(f, "rb"))
def cstr(va):
    for seg in e.iter_segments():
        if seg["p_type"] == "PT_LOAD" and seg["p_vaddr"] <= va < seg["p_vaddr"] + seg["p_filesz"]:
            d = seg.data()[va - seg["p_vaddr"]:]
            return d[:d.index(b"\0")].decode()
cnt = {}
for s in defined:
    if "@" in s["label"]:
        cnt[s["name"]] = cnt.get(s["name"], 0) + 1
rets = {}
addr2body = {}
cur = None
for l in D.splitlines():
    m = re.match(r"([0-9a-f]+) <", l)
    if m:
        cur = addr2body.setdefault(int(m.group(1), 16), [])
    elif cur is not None:
        cur.append(l)
for s in defined:
    if cnt.get(s["name"], 0) > 1:
        for l in addr2body.get(int(s["val"], 16), []):
            m = re.search(r"\tlea\s+rax,\[rip\+0x[0-9a-f]+\]\s+# ([0-9a-f]+)", l)
            if m:
                rets[s["label"]] = cstr(int(m.group(1), 16))
                break
dflt = next((rets[s["label"]] for s in defined if "@@" in s["label"] and s["label"] in rets), "none")
out = {
    "verdefs": nz(verdefs), "verdef_names": nz([v["name"] for v in verdefs]),
    "base_version": next((v["name"] for v in verdefs if v["flags"] == "BASE"), "none"),
    "verneeds": nz(verneeds), "needed_versions": nz([x for v in verneeds.values() for x in v]),
    "versioned_symbols": nz([s["label"] for s in syms if "@" in s["label"]]),
    "default_versions": nz({s["name"]: s["label"].split("@@")[1] for s in syms if "@@" in s["label"]}),
    "hidden_versions": nz([s["label"] for s in defined if "@" in s["label"] and "@@" not in s["label"]]),
    "weak_symbols": uniq(s["name"] for s in syms if s["bind"] == "WEAK"),
    "unique_symbols": uniq(s["name"] for s in syms if s["bind"] == "UNIQUE"),
    "protected_symbols": uniq(s["name"] for s in syms if s["vis"] == "PROTECTED"),
    "exported_symbols": uniq(s["name"] for s in defined if s["bind"] != "LOCAL"),
    "imports": uniq(s["name"] for s in syms if s["ndx"] == "UND"),
    "interposed": interposed, "rtld_next_callers": nz(rtl), "calls_rtld_next": "true" if rtl else "false",
    "returns": nz(rets), "default_return": dflt,
}
print(json.dumps(out, indent=1))
