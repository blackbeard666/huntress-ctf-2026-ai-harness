"""Independent oracle for jnib_* fixtures (offline; NOT lib.binary): javap -p -s / -c (native methods, ldc before
loadLibrary), readelf -W --dyn-syms / -s / -r / -x / -d (exports, func addresses, RELATIVE relocs -> JNINativeMethod
triples, SONAME), grep -obUa (HCFG base64 offset), javac -h header (export <-> Method/Signature).
usage: python3 jnib_oracle.py <jar> <so> [javac -h header]  -> JSON of the expected facts"""
import json, re, subprocess, sys, tempfile, zipfile

jar, so = sys.argv[1], sys.argv[2]
hdr = sys.argv[3] if len(sys.argv) > 3 else None
run = lambda *a: subprocess.run(a, capture_output=True, text=True).stdout
out, natives, libs = {}, [], []
with tempfile.TemporaryDirectory() as td:
    try:
        z = zipfile.ZipFile(jar)
        names = [n for n in z.namelist() if n.endswith(".class")]
        z.extractall(td)
    except zipfile.BadZipFile:
        names = []
    hc = None
    for n in names:
        p = f"{td}/{n}"
        cur = None
        for ln in run("javap", "-p", "-s", p).splitlines():
            m = re.match(r"\s*(.*?)\bnative\b.*?(\w+)\(.*\);$", ln)
            if m:
                cur = {"name": m.group(2), "static": "true" if " static " in f" {m.group(1)} " else "false"}
            elif cur and "descriptor:" in ln:
                cur["descriptor"] = ln.split("descriptor:")[1].strip()
                cls = run("javap", p).split("class ", 1)[1].split()[0].split("<")[0]
                natives.append(dict(cls=cls, **cur)); cur = None
        prev = None
        for ln in run("javap", "-c", "-p", p).splitlines():
            m = re.search(r"Method java/lang/(System|Runtime)\.(loadLibrary|load):", ln)
            if m and prev:
                libs.append((m.group(2), prev))
            s = re.search(r"ldc.*// String (.*)$", ln)
            prev = s.group(1) if s else (prev if "invokestatic" not in ln and "invokevirtual" not in ln else None)
        g = run("grep", "-obUa", "SENGRwE", p).split(":")[0]
        if g and hc is None:
            hc = ("jar", n, g)
elf = run("readelf", "-h", so).find("ELF Header") >= 0
exports, funcs = [], {}
if elf:
    for ln in run("readelf", "-W", "--dyn-syms", so).splitlines():
        f = ln.split()
        if len(f) >= 8 and f[0].endswith(":") and f[6] != "UND" and f[4] in ("GLOBAL", "WEAK") and f[3] in ("FUNC", "OBJECT", "NOTYPE"):
            exports.append(f[7].split("@")[0])
    for ln in run("readelf", "-W", "-s", so).splitlines():
        f = ln.split()
        if len(f) >= 8 and f[3] == "FUNC" and f[6] != "UND":
            funcs.setdefault(int(f[1], 16), f[7].split("@")[0])
    rel = {}
    for ln in run("readelf", "-W", "-r", so).splitlines():
        f = ln.split()
        if len(f) >= 4 and "RELATIVE" in f[2]:
            rel[int(f[0], 16)] = int(f[3], 16)
    raw = open(so, "rb").read()
    secs = []
    for ln in run("readelf", "-W", "-S", so).splitlines():
        m = re.match(r"\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+\S+\s+(\S*)", ln)
        if m:
            secs.append((m.group(1), int(m.group(3), 16), int(m.group(4), 16), int(m.group(5), 16), m.group(6)))
    v2o = lambda va: next((o + va - a for _, a, o, sz, fl in secs if a and a <= va < a + sz and "A" in fl), None)
    cs = lambda va: raw[v2o(va):raw.index(b"\0", v2o(va))].decode("utf-8", "replace") if v2o(va) is not None else ""
    regs = []
    for slot in sorted(rel):
        if slot + 8 in rel and slot + 16 in rel:
            n, sg, fn = cs(rel[slot]), cs(rel[slot + 8]), rel[slot + 16]
            if re.fullmatch(r"[A-Za-z_]\w*", n) and sg.startswith("(") and ")" in sg:
                regs.append({"name": n, "signature": sg, "fn_address": hex(fn), "fn_symbol": funcs.get(fn, "none"),
                             "table": "0", "slot": hex(slot)})
    soname = re.search(r"\(SONAME\).*\[(.*)\]", run("readelf", "-d", so))
    g = run("grep", "-obUa", "SENGRwE", so).split(":")[0]
    if g:
        hc = ("so", "<lib>", g)
    out["soname"] = soname.group(1) if soname else "none"
    out["jni_onload"] = "true" if "JNI_OnLoad" in exports else "false"
    out["registered_natives"] = regs or "none"
    out["registered_count"] = str(len(regs))
    jexp = [e for e in exports if e.startswith("Java_")]
    out["jni_export_count"] = str(len(jexp))
    hmap = {}
    if hdr:   # javac -h: /* Class: .. Method: m Signature: (..)R */ JNIEXPORT .. JNICALL Java_..
        for m in re.finditer(r"Method:\s+(\S+)\s+\* Signature:\s+(\S+)\s+\*/\s+JNIEXPORT \w+ JNICALL (Java_\w+)", open(hdr).read()):
            hmap[(m.group(1), m.group(2))] = m.group(3)
    nm = []
    for n in natives:
        sym = hmap.get((n["name"], n["descriptor"]))
        r = next((x for x in regs if x["name"] == n["name"] and x["signature"] == n["descriptor"]), None)
        if sym and sym in exports:
            b = ("export", sym, hex(next(a for a, s in funcs.items() if s == sym)))
        elif r:
            b = ("register", r["fn_symbol"], r["fn_address"])
        else:
            b = ("none", "none", "none")
        nm.append({"class": n["cls"], "name": n["name"], "descriptor": n["descriptor"], "static": n["static"],
                   "binding": b[0], "symbol": b[1], "fn_address": b[2]})
    out["native_methods"] = nm or "none"
ll = [a for k, a in libs if k == "loadLibrary"]
out.update(native_method_count=str(len(natives)), load_library=ll[0] if ll else "none", load_libraries=ll or "none",
           native_method_names=[n["name"] for n in natives] or "none",
           hcfg_member=hc[0] if hc else "none", hcfg_entry=hc[1] if hc else "none", hcfg_offset=hc[2] if hc else "none")
print(json.dumps(out if elf or names else None, indent=1))
