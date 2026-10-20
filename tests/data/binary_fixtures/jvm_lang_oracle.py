"""Independent oracle for the jvm_lang_* fixtures: jvm_oracle.py (javap -v -p + unzip) for the ClassFile fields, plus
JVM-language markers read from the same `javap -v -p` text and `unzip -Z1` names (no lib code).
usage: python3 jvm_lang_oracle.py <fixture.bin> [class entry]  -> prints the expected JSON dict"""
import json, os, re, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__))
path, ent = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
r = subprocess.run([sys.executable, os.path.join(here, "jvm_oracle.py"), path] + ([ent] if ent else []),
                   capture_output=True, text=True)
if r.returncode == 0:
    out = json.loads(r.stdout)
else:   # javap printed "Error: invalid index #0" + an empty pool (not a classfile): jar facts only, class fields none
    names = subprocess.run(["unzip", "-Z1", path], capture_output=True, text=True).stdout.split()
    mf = subprocess.run(["unzip", "-p", path, "META-INF/MANIFEST.MF"], capture_output=True, text=True).stdout
    m = re.search(r"^Main-Class:\s*(\S+)", mf, re.M)
    out = {"main_class": m.group(1) if m else "none", "class_count": str(sum(n.endswith(".class") for n in names)),
           "entry_count": str(len(names))}
    out.update({k: "none" for k in ("methods", "method_count", "access_flags", "major_version", "this_class",
                                    "jvm_language", "clojure_namespace", "is_scala_module")})
j = lambda v: json.dumps(v, separators=(",", ":"))
data = open(path, "rb").read()
if data[:2] == b"PK":
    names = subprocess.run(["unzip", "-Z1", path], capture_output=True, text=True).stdout.split()
    inits = [n[:-12] for n in names if n.endswith("__init.class")]
    out.update(container_format="jar", clojure_namespaces=j([n.replace("/", ".").replace("_", "-") for n in inits]))
    cls = tempfile.mktemp(suffix=".class") if ent else None
    if cls:
        open(cls, "wb").write(subprocess.run(["unzip", "-p", path, ent], capture_output=True).stdout)
else:
    out["container_format"] = "class"
    cls = tempfile.mktemp(suffix=".class")
    open(cls, "wb").write(data)
t = subprocess.run(["javap", "-v", "-p", cls], capture_output=True, text=True).stdout if cls else ""
if "major version" in t and "Error:" not in t:
    this = re.search(r"^\s*this_class: #\d+\s+// (\S+)", t, re.M).group(1)
    decl = re.search(r"^(?!Classfile )\S.*\b(?:class|interface)\b.*$", t, re.M).group(0)
    sig = "scala.reflect.ScalaSignature(" in t or re.search(r"^  ScalaSig: length", t, re.M) is not None
    module = this.endswith("$") and re.search(r"^  public static final \S+\$ MODULE\$;", t, re.M) is not None
    scala = sig or re.search(r"^  ScalaInlineInfo: length", t, re.M) is not None
    groovy = "groovy.lang.GroovyObject" in decl or "$getStaticMetaClass(" in t
    clj_init = this.endswith("__init") and "clojure/lang/RT" in t
    lang = "scala" if scala else "groovy" if groovy else "clojure" if "clojure/lang/" in t else "java"
    out.update(jvm_language=lang, has_scala_signature=j(sig), is_scala_module=j(scala and module),
               scala_companion_of=this[:-1] if scala and module else "none",
               is_groovy_object=j("groovy.lang.GroovyObject" in decl),
               has_groovy_metaclass=j("$getStaticMetaClass(" in t),
               clojure_namespace=this[:-6].replace("/", ".").replace("_", "-") if clj_init else "none",
               jvm_member=ent or ("none" if data[:2] == b"PK" else out.get("jvm_member", "none")))
    if data[:2] != b"PK":
        out.pop("jvm_member")
print(json.dumps(out, indent=1, ensure_ascii=False))
