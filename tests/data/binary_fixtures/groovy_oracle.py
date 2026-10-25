"""Independent oracle for groovy_* fixtures: unzip -Z1 / unzip -p + `javap -v -p` TEXT (OpenJDK 21), no lib import.
usage: python3 groovy_oracle.py <jar> [--unit X.groovy]  -> expected JSON (groovy_facts keys + javap method facts)."""
import json, re, subprocess, sys, tempfile, pathlib

jar = sys.argv[1]
unit = sys.argv[sys.argv.index("--unit") + 1] if "--unit" in sys.argv else None
names = subprocess.run(["unzip", "-Z1", jar], capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.split()
tmp = pathlib.Path(tempfile.mkdtemp())
jp = {}
for n in names:
    if n.endswith(".class"):
        (tmp / "c.class").write_bytes(subprocess.run(["unzip", "-p", jar, n], capture_output=True).stdout)
        jp[n] = subprocess.run(["javap", "-v", "-p", str(tmp / "c.class")], capture_output=True, text=True).stdout
J = lambda v: json.dumps(v, separators=(",", ":"))
keys = ("unit groovy_kind is_groovy_script primary_class primary_class_dotted primary_classfile primary_super_class "
        "source_file closures closure_count closure_names closure_do_call all_closures all_closure_count "
        "call_site_names call_site_count script_body_method hcfg_class hcfg_in_primary hcfg_cp_index hcfg_constant "
        "references_groovy_runtime has_groovy_runtime groovy_class_major groovy_indy").split()
out = {k: "none" for k in keys}
out["has_groovy_runtime"] = J(any(n.startswith("groovy/lang/") for n in names))
out["references_groovy_runtime"] = J(any(re.search(r"= Class\s+#\d+\s+// (groovy/lang/|org/codehaus/groovy/)", t)
                                         for t in jp.values()))
grv = {n: t for n, t in jp.items() if re.search(r"^(public )?.*class \S+ (extends groovy\.lang\.Script|.*implements "
                                                r".*groovy\.lang\.GroovyObject)", t, re.M)}
stem = unit.rsplit(".", 1)[0] if unit else None
prim = next((n for n in grv if n[:-6].rsplit("/", 1)[-1] == stem), None)
if prim:
    t = jp[prim]
    this = re.search(r"this_class: #\d+\s+// (\S+)", t).group(1)
    sup = re.search(r"super_class: #\d+\s+// (\S+)", t).group(1)
    ic = t.split("\nInnerClasses:\n", 1)[1].split("\n", 1)[0] if "\nInnerClasses:\n" in t else ""
    inner = re.findall(r"// (\w+)=class (\S+?) of", t.split("\nInnerClasses:\n", 1)[1].split("\nSourceFile")[0]) \
        if "\nInnerClasses:\n" in t else []
    inner = inner or re.findall(r"// (\w+)=class (\S+)", t.split("\nInnerClasses:\n", 1)[1].split("\nSourceFile")[0])
    clos = [n[:-6] for n, x in jp.items() if " extends groovy.lang.Closure " in x and n.startswith(this + "$")]
    clos.sort(key=lambda c: int(re.search(r"(\d*)$", c).group(1) or 0))
    dc = {}
    for c in clos:
        dc[c] = re.findall(r"\bdoCall\(.*\);\n\s+descriptor: (\S+)", jp[c + ".class"])
    bsm = t.split("\nBootstrapMethods:\n", 1)[1] if "\nBootstrapMethods:\n" in t else ""
    calls = [m.group(1) for m in re.finditer(r"IndyInterface\.bootstrap.*\n\s+Method arguments:\n\s+#\d+ (.*)", bsm)]
    script = sup == "groovy/lang/Script"
    out.update(unit=unit, groovy_kind="script" if script else "class", is_groovy_script=J(script), primary_class=this,
               primary_class_dotted=this.replace("/", "."), primary_classfile=prim, primary_super_class=sup,
               source_file=re.search(r'^SourceFile: "(.*)"', t, re.M).group(1),
               closures=J([c for _, c in inner]), closure_count=str(len(inner)), closure_names=J([s for s, _ in inner]),
               closure_do_call=J(dc), all_closures=J(clos), all_closure_count=str(len(clos)), call_site_names=J(calls),
               call_site_count=str(len(calls)), script_body_method="run" if script else "none",
               groovy_class_major=re.search(r"major version: (\d+)", t).group(1),
               groovy_indy=J(bool(calls)), hcfg_in_primary="false")
    for n in [prim] + [x for x in grv if x != prim] + [x for x in jp if x not in grv]:
        m = re.search(r"#(\d+) = String\s+#\d+\s+// ((?:HCFG|SENGR|48434647|JBBUOR)\S*)", jp[n])
        if m:
            h = re.search(r"this_class: #\d+\s+// (\S+)", jp[n]).group(1)
            out.update(hcfg_class=h, hcfg_in_primary=J(h == this), hcfg_cp_index=m.group(1), hcfg_constant=m.group(2))
            break
    hd = re.search(r"interfaces: \d+, fields: \d+, methods: (\d+)", t)
    simple = this.rsplit("/", 1)[-1]
    ms = [m.group(2) or "<clinit>" for m in re.finditer(r"^  (\S.*? ([\w$.]+)\(.*\)[^;]*;|static \{\};)$", t, re.M)]
    ms = ["<init>" if m.rsplit(".", 1)[-1] == simple else m for m in ms]
    out.update(method_count=hd.group(1), methods=J(ms),
               access_flags=str(int(re.search(r"^  flags: \((0x[0-9a-f]+)\)", t, re.M).group(1), 16)))
cfg = None
if out["hcfg_constant"] != "none":   # HCFG v1: magic, ver, key, u16 len, u32 crc32(plain) LE, body ^ key
    import base64, struct, zlib
    blob = base64.b64decode(out["hcfg_constant"])
    _, key, n, crc = struct.unpack_from("<BBHI", blob, 4)
    plain = bytes(c ^ key for c in blob[12:12 + n])
    cfg = json.loads(plain) if zlib.crc32(plain) == crc else None
print(json.dumps({"expected": out, "expected_config": cfg}, indent=1))
