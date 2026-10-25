"""Independent oracle for cljns_* fixtures: `unzip -Z1` / `unzip -p` + OpenJDK `javap -c -p -v` TEXT (no lib.binary).
usage: python3 cljns_oracle.py <fixture.bin>  -> JSON of expected clojure_facts fields."""
import json, os, re, subprocess, sys, tempfile

jar = os.path.abspath(sys.argv[1])
names = subprocess.run(["unzip", "-Z1", jar], capture_output=True, text=True).stdout.split()
mf = subprocess.run(["unzip", "-p", jar, "META-INF/MANIFEST.MF"], capture_output=True, text=True).stdout
main = (re.findall(r"^Main-Class:\s*(\S+)", mf, re.M) or ["none"])[0]
inits = [n for n in names if n.endswith("__init.class") and not n.startswith("clojure/")]
out = {"main_class": main, "has_clojure_runtime": json.dumps(any(n.startswith("clojure/lang/") for n in names))}
keys = ("namespace", "vars", "var_count", "fn_classes", "var_fn_classes", "anon_fn_classes", "ns_loader_class",
        "init_class", "gen_class", "source_file", "primary_class", "references_clojure_runtime")
out.update({k: "none" for k in keys})


def javap(d, cls):
    return subprocess.run(["javap", "-c", "-p", "-v", "-cp", d, cls], capture_output=True, text=True).stdout


with tempfile.TemporaryDirectory() as d:
    subprocess.run(["unzip", "-q", "-o", jar, "-d", d], check=True)
    init = [n for n in inits]
    if init and "void __init0();" in javap(d, init[0][:-6]):
        base = init[0][:-12]
        txt = javap(d, base + "__init")
        body = txt.split("void __init0();", 1)[1]
        ins = re.findall(r"^\s+\d+: (\w+)\s*(?:#\d+(?:, \d+)?)?\s*(?://\s*(.*))?$", body, re.M)
        fld, triples = {}, []
        for i, (op, c) in enumerate(ins):
            if op == "invokestatic" and "clojure/lang/RT.var:" in c and i >= 2:
                a, b = (re.match(r"String (.*)", ins[i - k][1]).group(1) for k in (2, 1))
                triples.append((a, b))
                put = next(x for x in ins[i + 1:] if x[0] == "putstatic")
                fld[re.search(r"Field (\w+):", put[1]).group(1)] = (a, b)
        ns = next(a for a, b in triples if a != "clojure.core")
        vars_ = [b for a, b in triples if a == ns]
        load = txt.split("void load();", 1)[1].split("void __init0();", 1)[0]
        fn, cur, new = {}, None, None
        for op, c in re.findall(r"^\s+\d+: (\w+)\s*(?:#\d+(?:, \d+)?)?\s*(?://\s*(.*))?$", load, re.M):
            if op == "getstatic" and (m := re.search(r"Field (\w+):", c)) and fld.get(m.group(1), ("",))[0] == ns:
                cur, new = fld[m.group(1)][1], None
            elif op == "new" and c.startswith("class " + base + "$"):
                new = c[6:]
            elif op in ("ldc", "ldc_w"):
                new = None
            elif op == "invokevirtual" and "Var.bindRoot" in c and cur and new:
                fn.setdefault(cur, new)
                new = None
        subs = [n[:-6] for n in names if n.startswith(base + "$") and n.endswith(".class")]
        src, prim, refs = "none", None, False
        for c in [base + "__init"] + subs + [base]:
            if c + ".class" not in names:
                continue
            t = javap(d, c)
            refs = refs or "clojure/lang/" in t
            if src == "none" and (m := re.search(r'^SourceFile: "(.*)"', t, re.M)):
                src = m.group(1)
            if prim is None and re.search(r"= Utf8\s+(HCFG|SENGR|48434647)", t):
                prim = c
        fcls = [fn[v] for v in vars_ if v in fn]
        out.update(namespace=ns, vars=json.dumps(vars_, separators=(",", ":")), var_count=str(len(vars_)),
                   fn_classes=json.dumps(fcls, separators=(",", ":")),
                   var_fn_classes=json.dumps({v: fn[v] for v in vars_ if v in fn}, separators=(",", ":")),
                   anon_fn_classes=json.dumps([c for c in subs if re.fullmatch(re.escape(base) + r"\$fn__\d+", c)],
                                              separators=(",", ":")),
                   ns_loader_class=next((c for c in subs if "$loading__" in c), "none"), init_class=base + "__init",
                   gen_class=base if base + ".class" in names else "none", source_file=src,
                   primary_class=prim or base + "__init", references_clojure_runtime=json.dumps(refs))
print(json.dumps(out, indent=1))
