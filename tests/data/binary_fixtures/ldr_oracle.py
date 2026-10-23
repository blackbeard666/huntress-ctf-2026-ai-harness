"""Independent oracle: GNU readelf -lW / -dW text (never lib.binary). usage: python3 ldr_oracle.py <file>
prints the expected_facts json (or null when readelf rejects the file)."""
import json, re, subprocess, sys
f = sys.argv[1]
d = subprocess.run(["readelf", "-dW", f], capture_output=True, text=True)
l = subprocess.run(["readelf", "-lW", f], capture_output=True, text=True)
if "Not an ELF file" in d.stderr + l.stderr or d.returncode and not d.stdout.strip():
    print("null"); sys.exit()
m = re.search(r"\[Requesting program interpreter: (.*)\]", l.stdout)
br = lambda tag: [x for x in re.findall(r"\(%s\)\s+\S+ [^:]*: \[(.*)\]" % tag, d.stdout)]
flags = re.search(r"\(FLAGS\)\s+Flags: (.*)", d.stdout)
flags1 = re.search(r"\(FLAGS_1\)\s+Flags: (.*)", d.stdout)
rp, rn = br("RPATH"), br("RUNPATH")
interp = m.group(1) if m else "none"
fl = flags.group(1).split() if flags else []
f1 = flags1.group(1).split() if flags1 else []
paths = " ".join(rp + rn)
toks = sorted(set(re.findall(r"\$\{?(ORIGIN|LIB|PLATFORM)", paths)))
tf = lambda b: "true" if b else "false"
print(json.dumps({
    "interpreter": interp, "has_interp": tf(m), "needed": br("NEEDED"), "soname": (br("SONAME") or ["none"])[0],
    "rpath": ":".join(rp) or "none", "runpath": ":".join(rn) or "none",
    "search_path_tag": "DT_RUNPATH" if rn else ("DT_RPATH" if rp else "none"),
    "search_path": ":".join(rn or rp) or "none", "dst_tokens": toks, "has_origin": tf("ORIGIN" in toks),
    "flags": fl, "flags_1": f1, "bind_now": tf("(BIND_NOW)" in d.stdout or "BIND_NOW" in fl or "NOW" in f1),
    "pie": tf("PIE" in f1), "nodeflib": tf("NODEFLIB" in f1)}, indent=1))
