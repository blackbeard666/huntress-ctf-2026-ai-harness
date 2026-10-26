"""Independent oracle for jvmniche_* fixtures: unzip -Z1 / unzip -p + `javap -v -p` TEXT (OpenJDK 21) and stdlib
base64/zlib for the HCFG check -- no lib import. Cue rules (class refs `= Class #n // pkg/X`, descriptors `Lpkg/X;`,
super/interfaces, RUBY$ method names; String literals ignored) mirror each compiler's output shape.
usage: python3 jvmniche_oracle.py <jar|class> [--unit hello.py]  -> expected JSON"""
import base64, json, re, struct, subprocess, sys, tempfile, pathlib, zlib

f = sys.argv[1]
unit = sys.argv[sys.argv.index("--unit") + 1] if "--unit" in sys.argv else None
tmp = pathlib.Path(tempfile.mkdtemp())
J = lambda v: json.dumps(v, separators=(",", ":"))
keys = ("niche_language niche_classes niche_class_count niche_primary_classfile niche_primary_class niche_source_file "
        "niche_hcfg_classfile niche_hcfg_in_primary references_niche_runtime jython_module jython_code_objects "
        "jruby_methods ceylon_module_class ceylon_module kotlin_script_class kotlin_script_base").split()
out = {k: "none" for k in keys}
raw = pathlib.Path(f).read_bytes()
if raw[:4] == b"\xca\xfe\xba\xbe":
    (tmp / "c.class").write_bytes(raw)
    jp = {"?": subprocess.run(["javap", "-v", "-p", str(tmp / "c.class")], capture_output=True, text=True).stdout}
    jp = {re.search(r"this_class: #\d+\s+// (\S+)", jp["?"]).group(1) + ".class": jp["?"]}
else:
    r = subprocess.run(["unzip", "-Z1", f], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode:
        print(J(None)); sys.exit(0)
    jp = {}
    for n in r.stdout.split():
        if n.endswith(".class"):
            (tmp / "c.class").write_bytes(subprocess.run(["unzip", "-p", f, n], capture_output=True).stdout)
            jp[n] = subprocess.run(["javap", "-v", "-p", str(tmp / "c.class")], capture_output=True, text=True).stdout
CUES = [("kotlin_script", r"kotlin/script/|org/jetbrains/kotlin/mainKts/"), ("jython", r"org/python/core/"),
        ("jruby", r"org/jruby/"), ("ceylon", r"com/redhat/ceylon/|org/eclipse/ceylon/|ceylon/language/"),
        ("eta", r"eta/runtime/"), ("frege", r"frege/run"), ("beanshell", r"bsh/"),
        ("xtend", r"org/eclipse/xtext/xbase/lib/|org/eclipse/xtend2?/lib/")]


def lang(t):
    lit = set(re.findall(r"= String\s+(#\d+)", t))
    utf = [m.group(2) for m in re.finditer(r"^\s+(#\d+) = Utf8\s+(.*)$", t, re.M) if m.group(1) not in lit]
    if re.search(r"^\s+super_class: #\d+\s+// kotlin/script/", t, re.M):
        return "kotlin_script"
    if re.search(r"^  \S.* RUBY\$\S*\(", t, re.M):
        return "jruby"
    for lg, rx in CUES[1:]:
        if any(re.match(rx, u) or re.search("L(?:" + rx + ")", u) for u in utf):
            return lg
    return None


langs = {n: lang(t) for n, t in jp.items()}
mine = [n for n, l in langs.items() if l]
out["references_niche_runtime"] = J(bool(mine))
if mine:
    lg = langs[mine[0]]
    sf = lambda n: (re.search(r'^SourceFile: "(.*)"', jp[n], re.M) or [None, "none"])[1]
    stem = unit.rsplit(".", 1)[0] if unit else ""
    named = {stem, stem + "$py", stem + "_", (stem[:1].upper() + stem[1:]).replace(".", "_")}   # compiler naming
    src = [n for n in mine if sf(n) == unit]
    prim = (next((n for n in src if n[:-6].rsplit("/", 1)[-1] in named), None) or src[0]) if unit else mine[0]
    this = re.search(r"this_class: #\d+\s+// (\S+)", jp[prim]).group(1)
    out.update(niche_language=lg, niche_classes=J(mine), niche_class_count=str(len(mine)), niche_primary_classfile=prim,
               niche_primary_class=this, niche_source_file=sf(prim))
    for n in [prim] + [x for x in jp if x != prim]:
        hit = False
        for s in re.findall(r"= Utf8\s+([A-Za-z0-9+/]{80,}={0,2})$", jp[n], re.M):
            d = base64.b64decode(s)
            if d[:4] == b"HCFG":
                ln, crc = struct.unpack_from("<HI", d, 6)
                body = bytes(c ^ d[5] for c in d[12:12 + ln])
                hit = zlib.crc32(body) == crc
                if hit:
                    out["expected_config"] = json.loads(body)
                    break
        if hit:
            out.update(niche_hcfg_classfile=n, niche_hcfg_in_primary=J(n == prim))
            break
    meths = re.findall(r"^  \S.*? ([\w$]+)\(.*\);$", jp[prim], re.M)
    if lg == "jython":
        co = sorted((int(m.group(2)), m.group(0)) for m in (re.match(r"^(.+)\$(\d+)$", x) for x in meths) if m)
        out.update(jython_module=this[:-3], jython_code_objects=J([c for _, c in co]))
    if lg == "jruby":
        out["jruby_methods"] = J([m.group(1) for m in (re.match(r"^RUBY\$method\$(.+?)\$\d+$", x) for x in meths) if m])
    if lg == "kotlin_script":
        out.update(kotlin_script_class=this,
                   kotlin_script_base=re.search(r"super_class: #\d+\s+// (\S+)", jp[prim]).group(1))
    mod = next((n for n in mine if n.endswith("/$module_.class")), None)
    if mod:
        out.update(ceylon_module_class=mod, ceylon_module=re.search(r'name="([^"]+)"', jp[mod]).group(1)
                   if re.search(r'name="([^"]+)"', jp[mod]) else "none")
print(J(out))
