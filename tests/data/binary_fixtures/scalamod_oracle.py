"""Independent oracle for the scalamod_* fixtures: `javap -v -p` text + `unzip -Z1/-p` (no lib code), via jvm_oracle.py
for the ClassFile basics. Rule under test (D24/D26 "primary classfile named by that unit"): scalac `object X` ->
X$.class (javap: `public static final X$ MODULE$;`) is primary, X.class (Main-Class, static forwarders) the forwarder;
a source unit `X.scala` names the classes whose javap `SourceFile: "X.scala"`; otherwise the class itself, no forwarder.
usage: python3 scalamod_oracle.py <jar> [--unit X.scala] [--primary]   -> prints the expected JSON dict"""
import json, os, re, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__))
path, args = sys.argv[1], sys.argv[2:]
unit = args[args.index("--unit") + 1] if "--unit" in args else None
j = lambda v: json.dumps(v, separators=(",", ":"))
names = subprocess.run(["unzip", "-Z1", path], capture_output=True, text=True).stdout.split()
mf = subprocess.run(["unzip", "-p", path, "META-INF/MANIFEST.MF"], capture_output=True, text=True).stdout
m = re.search(r"^Main-Class:\s*(\S+)", mf, re.M)
out = {"main_class": m.group(1) if m else "none"}


def javap(ent):
    if ent not in names:
        return ""
    f = tempfile.mktemp(suffix=".class")
    open(f, "wb").write(subprocess.run(["unzip", "-p", path, ent], capture_output=True).stdout)
    r = subprocess.run(["javap", "-v", "-p", f], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 and "major version" in r.stdout else ""


def facts(ent):
    t = javap(ent)
    if not t:
        return None
    b = json.loads(subprocess.run([sys.executable, os.path.join(here, "jvm_oracle.py"), path, ent],
                                  capture_output=True, text=True).stdout)
    this = b["this_class"]
    meths = json.loads(b["methods"])
    body = t.split("\n{\n", 1)[1].rsplit("\n}\n", 1)[0]
    mflags = [int(x, 16) for d, x in re.findall(r"^  \S.*?;\n    descriptor: (\(\S+)\n    flags: \(0x([0-9a-f]+)\)",
                                                body, re.M)]
    bsm = re.search(r"^BootstrapMethods:\n((?:  .*\n)+)", t, re.M)
    sig = "scala.reflect.ScalaSignature(" in t or re.search(r"^  ScalaSig: length", t, re.M) is not None
    tasty = re.search(r"^  TASTY: length = 0x", t, re.M) is not None
    b.update(bootstrap_method_count=str(len(re.findall(r"^  \d+: #\d+ REF_", bsm.group(1), re.M)) if bsm else 0),
             invokedynamic_count=str(len(re.findall(r"^\s+\d+: invokedynamic", t, re.M))),
             anonfun_methods=j([n for n in meths if "$anonfun$" in n]),
             lambda_methods=j([n for n in meths if n.startswith("lambda$") or "$anonfun$" in n]),
             synthetic_methods=j([n for n, fl in zip(meths, mflags) if fl & 0x1000]),
             has_tasty_attribute=j(tasty), has_scala_signature=j(sig),
             scala_major="3" if tasty else "2" if sig or re.search(r"^  ScalaInlineInfo: length", t, re.M) else "none",
             has_module_field=j(this.endswith("$") and re.search(r"^  public static final \S+\$ MODULE\$;", t, re.M)
                                is not None))
    b.pop("main_class", None), b.pop("class_count", None), b.pop("entry_count", None)
    return b


def start_of_unit(u):
    fn = u.rsplit("/", 1)[-1]
    stem = fn.rsplit(".", 1)[0]
    cand = [n for n in names if n.endswith(".class") and re.search(r'^SourceFile: "%s"' % re.escape(fn), javap(n), re.M)]
    for suf in (".class", "$.class", "__init.class"):
        hit = [n for n in cand if n.rsplit("/", 1)[-1] == stem + suf]
        if hit:
            return hit[0]
    hit = [n for n in cand if re.search(r"^  public static void main\(java\.lang\.String\[\]\)", javap(n), re.M)]
    hit = hit or [n for n in cand if n.endswith("$_main.class")]   # Clojure -main fn class
    return (hit or cand or [None])[0]


ent = start_of_unit(unit) if unit else (m.group(1).replace(".", "/") + ".class" if m else None)
prim = fwd = None
if ent and facts(ent) is not None or (ent and ent.endswith("$.class")):
    base = ent[:-6]
    mod = facts(base + "$.class") if not base.endswith("$") else facts(ent)
    if base.endswith("$"):
        prim, fwd = ent, (base[:-1] + ".class" if mod and mod["has_module_field"] == "true" and base[:-1] + ".class" in names else None)
    elif mod and mod["has_module_field"] == "true":
        prim, fwd = base + "$.class", ent
    elif base + "__init.class" in names:
        prim, fwd = base + "__init.class", ent
    else:
        prim = ent
tasty = [n for n in names if n.endswith(".tasty")]
majors = set()
for role, e in (("primary", prim), ("forwarder", fwd)):
    f = facts(e) if e else None
    out[role + "_classfile"] = e if f else "none"
    out[role + "_class"] = f["this_class"] if f else "none"
    for k in ("methods", "method_count", "access_flags", "major_version", "minor_version", "source_file",
              "bootstrap_method_count", "invokedynamic_count", "anonfun_methods", "has_scala_signature", "scala_major"):
        out[f"{role}_{k}"] = f[k] if f else "none"
    majors.add(out[role + "_scala_major"])
out["module_class"] = out["primary_class"] if prim and facts(prim)["has_module_field"] == "true" else "none"
out.update(tasty_count=str(len(tasty)), has_tasty_entries=j(bool(tasty)),
           scala_major="3" if tasty or "3" in majors else "2" if "2" in majors else "none")
member = prim if (unit or "--primary" in args) and prim else ent
f = facts(member) if member else None
if f:
    out["jvm_member"] = member
    for k in ("methods", "method_count", "access_flags", "major_version", "minor_version", "source_file", "this_class",
              "bootstrap_method_count", "invokedynamic_count", "anonfun_methods", "lambda_methods", "synthetic_methods",
              "has_tasty_attribute", "has_scala_signature"):
        out[k] = f[k]
else:
    out.update({k: "none" for k in ("methods", "method_count", "access_flags", "source_file", "this_class")})
print(json.dumps(out, indent=1, ensure_ascii=False))
