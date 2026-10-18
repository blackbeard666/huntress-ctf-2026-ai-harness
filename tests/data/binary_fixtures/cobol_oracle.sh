#!/bin/sh
# Independent oracle for cobol_* fixtures (no lib.binary): binutils readelf -dW / nm -D / objdump -d / strings -a parsed
# by a python3 one-off. program_id = the PROGRAM-ID line of the COBOL source handed to cobc; HCFG = the blob rebuilt
# from the source's X"..." VALUE literals (crc via zlib.crc32); offset = file offset of its first literal in .rodata
# (cobc -O0 split fields) or of the instruction that puts 'HCFG' (movabs $imm / rip-relative movdqa of the .rodata
# constant, from objdump -d), mapped through readelf -lW.
# usage: sh cobol_oracle.sh <bin> <cobol source or -> <source name given to cobc or ->
python3 - "$@" <<'PY'
import json, re, subprocess, sys, zlib, struct
f, srcp, srcname = sys.argv[1], sys.argv[2], sys.argv[3]
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout
d = open(f, "rb").read()
needed = re.findall(r"\(NEEDED\)\s+Shared library: \[([^\]]+)\]", run("readelf", "-dW", f))
und = sorted({l.split()[-1].split("@")[0] for l in run("nm", "-D", "--undefined-only", f).splitlines() if l.split()})
cob = [n for n in und if n.startswith("cob_")]
so = next((n for n in needed if n.startswith("libcob.so")), None)
rt = bool(so or "cob_init" in cob)
facts = {"format": "elf" if "ELF" in run("file", "-b", f) else "none",
         "architecture": "x86-64" if "x86-64" in run("file", "-b", f) else "none", "needed": needed,
         "has_libcob_needed": "true" if so else "false", "libcob_soname": so or "none", "cob_imports": cob,
         "has_cobol_runtime": "true" if rt else "false"}
cfg, off, enc = "none", "none", "none"
if srcp != "-":
    src = open(srcp).read()
    pid = re.search(r"PROGRAM-ID\.\s+([A-Za-z0-9-]+)", src).group(1)
    date = re.search(r"\n%s\n([A-Z][a-z]{2} [ 0-3]\d \d{4} \d\d:\d\d:\d\d)\n" % pid, run("strings", "-a", f))
    facts.update(program_id=pid, program_ids=[pid], source_file=srcname, compile_date=date.group(1) if date else "none")
    lits = [bytes.fromhex(h) for h in re.findall(r'X"([0-9A-F]+)"', src)]
    blob = b"".join(lits)
    ver, key, n, crc = struct.unpack_from("<BBHI", blob, 4)
    plain = bytes(c ^ key for c in blob[12:12 + n])
    if zlib.crc32(plain) == crc:
        cfg = json.loads(plain)
        loads = [l.split() for l in run("readelf", "-lW", f).splitlines() if l.split()[:1] == ["LOAD"]]
        loads = [(int(x[1], 16), int(x[2], 16), int(x[4], 16)) for x in loads]   # off, vaddr, filesz
        v2o = lambda v: next(o + v - va for o, va, sz in loads if va <= v < va + sz)
        o2v = lambda q: next(va + q - o for o, va, sz in loads if o <= q < o + sz)
        rod = d.find(lits[0] + b"\0")
        if len(lits) > 1 and rod >= 0 and d.find(lits[1] + b"\0", rod) > rod:   # literals in .rodata (memcpy src)
            off, enc = rod, "split-raw"
        else:
            hv = o2v(d.find(blob[:16])) if d.find(blob[:16]) >= 0 else None
            for l in run("objdump", "-d", "--no-show-raw-insn", f).splitlines():
                m = re.match(r"\s*([0-9a-f]+):\s+(\S+)\s+(.*)", l)
                if not m:
                    continue
                if m.group(2) == "movabs" and re.search(r"\$0x[0-9a-f]*47464348,", m.group(3)) or \
                        hv is not None and m.group(2) in ("movdqa", "movdqu", "movaps", "movups") and \
                        re.search(r"# %x\b" % hv, m.group(3)):
                    off, enc = v2o(int(m.group(1), 16)), "stack-built"
                    break
else:
    facts.update(program_id="none", program_ids=[], source_file="none", compile_date="none")
facts["has_gnucobol_runtime"] = facts["has_cobol_runtime"]
print(json.dumps({"expected_offset": off, "encoding": enc, "expected_config": cfg, "expected_facts": facts}))
PY
