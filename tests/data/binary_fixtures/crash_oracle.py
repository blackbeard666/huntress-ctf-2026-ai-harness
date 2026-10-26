"""Independent oracle for crash_* fixtures: unzip -Z1/-p, javap -p -c, readelf -SW/-h, objcopy --only-section,
nm, objdump -d, iconv. Prints the expected crash_sidecar_facts JSON (no lib.binary import).
usage: python3 crash_oracle.py <fixture.bin>"""
import json, re, subprocess as sp, sys, tempfile, os

def run(*a, inp=None):
    return sp.run(a, input=inp, capture_output=True, check=False).stdout

def name(fr):
    s = fr.strip()
    s = re.sub(r"^at\s+", "", s)
    if "!" in s:
        s = s.split("!", 1)[1]
    s = re.split(r"[\s(+]", s, 1)[0]
    return s.rsplit(".", 1)[-1]

path = sys.argv[1]
data = open(path, "rb").read()
rec, raw, src, methods, calls = None, None, "none", set(), {}
if data[:2] == b"PK":
    ents = run("unzip", "-Z1", path).decode().split()
    for e in ents:
        if re.search(r"(trace\.json|crash[^/]*\.json|stack\.txt)$", e):
            t = run("unzip", "-p", path, e).decode()
            if e.endswith(".txt"):
                lines = [l.strip() for l in t.splitlines() if l.strip().startswith("at ")]
                rec, raw, src = {"kind": t.split(":")[0].split()[-1].rsplit(".", 1)[-1]}, lines, e
            else:
                o = json.loads(t)
                fl = o.get("frames") or o.get("stack") or o.get("backtrace")
                if fl:
                    rec, raw, src = o, fl, e
            if raw:
                break
    mc = re.search(r"Main-Class:\s*(\S+)", run("unzip", "-p", path, "META-INF/MANIFEST.MF").decode()).group(1)
    with tempfile.TemporaryDirectory() as d:
        run("unzip", "-q", "-o", path, mc + ".class", "-d", d)
        jp = run("javap", "-p", "-c", "-v", os.path.join(d, mc + ".class")).decode()
    cur = None
    bsm = dict(re.findall(r"(?m)^\s+(\d+): #\d+ REF_invokeStatic .*\n\s+Method arguments:\n\s+#\d+ (\S+)", jp))
    for l in jp.splitlines():
        m = re.match(r"^  (?:[\w.$<>\[\]]+ )*?([\w$<>]+)\((.*)\);$", l)
        if m:
            cur = m.group(1); methods.add(cur); calls.setdefault(cur, set())
        m2 = re.search(r"invoke\w+ .*// (?:Interface)?Method (?:[\w/$]+\.)?\"?([\w$<>]+)\"?:", l)
        if cur and m2:
            calls[cur].add(m2.group(1))
        m3 = re.search(r"invokedynamic .*// InvokeDynamic #(\d+):", l)
        if cur and m3 and m3.group(1) in bsm:
            calls[cur].add(bsm[m3.group(1)])
else:
    secs = run("readelf", "-SW", path).decode()
    sn = re.search(r"\]\s+(\.\S*(?:crash|trace)\S*)\s", secs)
    if sn:
        with tempfile.NamedTemporaryFile() as f:
            run("objcopy", "-O", "binary", "--only-section=" + sn.group(1), "--set-section-flags", sn.group(1) + "=alloc", path, f.name)
            t = open(f.name, "rb").read().decode()
            src = "raw"
    else:
        h = run("readelf", "-hW", path).decode()
        g = lambda k: int(re.search(k + r":\s+(\d+)", h).group(1))
        end = g("Start of section headers") + g("Number of section headers") * g("Size of section headers")
        t = run("iconv", "-f", "UTF-16LE", "-t", "UTF-8", inp=data[end:]).decode()
        src = "raw"
    try:
        o = json.loads(t)
        raw = o.get("frames") or o.get("stack") or o.get("backtrace")
        rec = o if raw else None
    except ValueError:
        pass
    syms = {}
    for l in run("nm", "-S", "--defined-only", path).decode().splitlines():
        p = l.split()
        if len(p) == 4 and p[2] in "Tt":
            syms[p[3]] = (int(p[0], 16), int(p[1], 16))
    methods = set(syms)
    if raw:
        out = []
        for fr in raw:
            if re.fullmatch(r"0x[0-9a-f]+", fr):
                a = int(fr, 16)
                fr = next(n for n, (v, s) in syms.items() if v <= a < v + s)
            out.append(fr)
        raw_names = out
    cur = None
    for l in run("objdump", "-d", "--no-show-raw-insn", path).decode().splitlines():
        m = re.match(r"^[0-9a-f]+ <([\w.@]+)>:", l)
        if m:
            cur = m.group(1); calls.setdefault(cur, set())
        m2 = re.search(r"\scall\s+[0-9a-f]+ <([\w.@]+)>", l)
        if cur and m2:
            calls[cur].add(m2.group(1))
if not raw:
    print(json.dumps({"crash_found": "false", "crash_schema": "none", "crash_kind": "none", "crash_fault_method": "none",
                      "crash_fault_frame": "none", "crash_outer_method": "none", "crash_frame_count": "0",
                      "crash_frames": "none", "crash_trace_entry": "none", "crash_frames_match_methods": "false",
                      "crash_fault_in_primary": "false", "crash_frames_call_chain": "false"}, indent=1))
    sys.exit()
fr = [name(x) for x in (raw_names if data[:2] != b"PK" else raw)]
tf = lambda x: "true" if x else "false"
print(json.dumps({"crash_found": "true", "crash_schema": rec.get("schema") or "none", "crash_kind": rec.get("kind") or "none",
                  "crash_fault_method": fr[0], "crash_fault_frame": raw[0], "crash_outer_method": fr[-1],
                  "crash_frame_count": str(len(fr)), "crash_frames": json.dumps(fr, separators=(",", ":")),
                  "crash_trace_entry": src, "crash_frames_match_methods": tf(all(x in methods for x in fr)),
                  "crash_fault_in_primary": tf(fr[0] in methods),
                  "crash_frames_call_chain": tf(all(x in methods for x in fr) and all(fr[k] in calls.get(fr[k + 1], ()) for k in range(len(fr) - 1)))}, indent=1))
