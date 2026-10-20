"""Independent oracle for the jvm_* fixtures: `javap -v -p` text + `unzip -Z1` / `unzip -p` (no lib code).
usage: python3 jvm_oracle.py <fixture.bin> [class entry]  -> prints the expected JSON dict"""
import json, re, subprocess, sys, tempfile, zipfile, os
path = sys.argv[1]
j = lambda v: json.dumps(v, separators=(",", ":"))
out = {}
data = open(path, "rb").read()
cls = None
if data[:2] == b"PK":
    names = subprocess.run(["unzip", "-Z1", path], capture_output=True, text=True).stdout.split()
    mf = subprocess.run(["unzip", "-p", path, "META-INF/MANIFEST.MF"], capture_output=True, text=True).stdout
    m = re.search(r"^Main-Class:\s*(\S+)", mf, re.M)
    out.update(main_class=m.group(1) if m else "none", class_count=str(sum(n.endswith(".class") for n in names)),
               entry_count=str(len(names)))
    ent = sys.argv[2] if len(sys.argv) > 2 else (m.group(1).replace(".", "/") + ".class" if m else None)
    if ent:
        cls = tempfile.mktemp(suffix=".class")
        open(cls, "wb").write(subprocess.run(["unzip", "-p", path, ent], capture_output=True).stdout)
    else:   # no Main-Class: the class-level fields are absent
        out.update({k: "none" for k in ("methods", "method_count", "access_flags", "major_version", "this_class")})
else:   # javap only takes a *.class path
    cls = tempfile.mktemp(suffix=".class")
    open(cls, "wb").write(data)
if cls:
    r = subprocess.run(["javap", "-v", "-p", cls], capture_output=True, text=True)
    t = r.stdout
    if r.returncode != 0 or "major version" not in t:
        if data[:2] != b"PK":
            out["_all"] = "none"   # javap rejects it: not a class file
    else:
        g = lambda rx: re.search(rx, t, re.M).group(1)
        acc = int(g(r"^\s*flags: \(0x([0-9a-f]+)\)"), 16)
        entries = re.findall(r"^\s+#(\d+) = (\w+)", t, re.M)
        last = int(entries[-1][0]) + (1 if entries[-1][1] in ("Long", "Double") else 0)
        # members: javap prints each field/method declaration then "descriptor:" / "flags:" lines
        body = t.split("\n{\n", 1)[1].rsplit("\n}\n", 1)[0]
        mem = re.findall(r"^  (\S.*?);\n    descriptor: (\S+)\n    flags: \(0x([0-9a-f]+)\)", body, re.M)
        def mname(decl):
            if decl == "static {}" or decl.endswith(" static {}"):   # Clojure AOT: "public static {}"
                return "<clinit>"
            nm = re.search(r"(\S+)\(", decl)
            if nm:
                n = nm.group(1).split(".")[-1]
                return "<init>" if n == g(r"^\s*this_class: #\d+\s+// (\S+)").split("/")[-1] else n
            return decl.split()[-1]
        flds = [(mname(d), ds) for d, ds, _ in mem if not ds.startswith("(")]
        meths = [(mname(d), ds) for d, ds, _ in mem if ds.startswith("(")]
        tail = t.rsplit("\n}\n", 1)[1]
        sup = re.search(r"^\s*super_class: #\d+\s+// (\S+)", t, re.M)
        out.update(minor_version=g(r"minor version: (\d+)"), major_version=g(r"major version: (\d+)"),
                   constant_pool_count=str(last + 1), access_flags=str(acc), access_flags_hex=f"0x{acc:04x}",
                   this_class=g(r"^\s*this_class: #\d+\s+// (\S+)"), super_class=sup.group(1) if sup else "none",
                   interface_count=g(r"interfaces: (\d+)"), field_count=g(r"fields: (\d+)"),
                   method_count=g(r"methods: (\d+)"), attribute_count=g(r"attributes: (\d+)"),
                   fields=j([n for n, _ in flds]), field_descriptors=j([d for _, d in flds]),
                   methods=j([n for n, _ in meths]), method_descriptors=j([d for _, d in meths]),
                   source_file=(re.search(r'^SourceFile: "(.*)"', tail, re.M) or [None, "none"])[1],
                   signature=(re.search(r"^Signature: #\d+\s+// (\S+)", tail, re.M) or [None, "none"])[1],
                   attributes=j([a or b for a, b in   # unknown attrs (ScalaSig, ScalaInlineInfo) print indented
                                re.findall(r"^(\w+):|^  (\w+): length = 0x", tail, re.M)]))
        km = re.search(r"kotlin\.Metadata\(\n(.*?)\n\s*\)", tail, re.S)
        out["has_kotlin_metadata"] = "true" if km else "false"
        if km:
            for k, v in re.findall(r"^\s*(\w+)=(.*)$", km.group(1), re.M):
                if v.startswith("["):
                    items = re.findall(r'"((?:[^"\\]|\\.)*)"|(-?\d+)', v)
                    vals = [int(n) if n else json.loads('"' + s + '"') for s, n in items]
                    out["kotlin_" + k] = json.dumps(vals, separators=(",", ":"), ensure_ascii=False)
                else:
                    out["kotlin_" + k] = v
print(json.dumps(out, indent=1, ensure_ascii=False))
