"""Independent oracle for the jcg_* fixtures: unzip + `javap -p -c -l -v` TEXT (not lib.binary) -> expected facts.
usage: python3 jcg_oracle.py <fixture.bin>   (prints the expected_facts JSON)"""
import io, json, re, subprocess, sys, tempfile, zipfile, os

b = open(sys.argv[1], "rb").read()
tmp = tempfile.mkdtemp()
NONE = {k: "none" for k in ("jcg_fault_method", "jcg_fault_exception", "jcg_throw_line", "jcg_call_chain",
                            "jcg_call_depth", "jcg_catch_method", "jcg_catch_type", "jcg_caught", "jcg_callees_of:main")}
if b[:4] == b"\xca\xfe\xba\xbe":
    files = [os.path.join(tmp, "X.class")]
    open(files[0], "wb").write(b)
else:
    try:
        z = zipfile.ZipFile(io.BytesIO(b))
    except zipfile.BadZipFile:
        print(json.dumps({"jcg_found": "false", **NONE}, indent=1)); sys.exit()
    mc = re.search(r"Main-Class:\s*(\S+)", z.read("META-INF/MANIFEST.MF").decode()).group(1).replace(".", "/")
    files = []
    for n in z.namelist():
        if n.endswith(".class") and (n == mc + ".class" or n.startswith(mc + "$")):
            p = os.path.join(tmp, n.replace("/", "_").replace("$", "_D_"))
            open(p, "wb").write(z.read(n)); files.append(p)
calls, throws, xt, order, sites = {}, {}, {}, [], {}
units = {re.search(r"this_class: #\d+ +// (\S+)", subprocess.run(["javap", "-v", fp], capture_output=True, text=True).stdout).group(1)
         for fp in files}
for fp in files:
    t = subprocess.run(["javap", "-p", "-c", "-l", "-v", fp], capture_output=True, text=True).stdout
    bsm = {}
    for m in re.finditer(r"^  (\d+): #\d+ REF_\w+ ([^\n]+)\n    Method arguments:\n((?:      #\d+ [^\n]*\n)+)", t, re.M):
        args = re.findall(r"#\d+ ([^\n]*)", m.group(3))
        nm = [re.match(r"REF_\w+ [\w$/.]+\.([\w$<>]+):", a).group(1) for a in args if a.startswith("REF_")]
        bsm[int(m.group(1))] = nm or [a for a in args if re.fullmatch(r"[\w$<>]+", a) and not a.isdigit()]
    for m in re.finditer(r"^  (?:[\w<>\[\]$.,]+ )*?([\w$<>]+)\([^\n]*;\n((?:(?!^  \S)[^\n]*\n)*)", t, re.M):
        name, body = m.group(1), m.group(2)
        name = "<init>" if any(name == u.rsplit("/", 1)[-1].replace("/", ".") for u in units) else name   # javap ctor
        if name not in calls:
            order.append(name)
        out = calls.setdefault(name, set())
        lines = [(int(a), int(c)) for c, a in re.findall(r"line (\d+): (\d+)", body)]
        pend = None
        for pc, ins, cm in re.findall(r"^ +(\d+): (\w+)[^\n]*?(?://([^\n]*))?$", body, re.M):
            pc, cm = int(pc), (cm or "").strip()
            if ins == "new" or ins.startswith("ldc") and cm.startswith("class "):
                pend = (cm.split()[-1], None)   # construction pc set by the <init> call
            elif ins.startswith("invoke") and ins != "invokedynamic":
                mm = re.match(r"(?:Interface)?Method (?:([\w$/]+)\.)?\"?([\w$<>]+)\"?:", cm)
                if mm and mm.group(2) == "<init>" and pend:
                    pend = (pend[0], pc)
                if mm and (mm.group(1) is None or mm.group(1) in units):   # javap omits the owner for this class
                    out.add(mm.group(2)); sites.setdefault((name, mm.group(2)), []).append(pc)
            elif ins == "invokedynamic":
                k = int(re.match(r"InvokeDynamic #(\d+):", cm).group(1))
                for a in bsm.get(k, []):
                    if a == "<init>":
                        pend = (pend[0], pc) if pend else None
                    else:
                        out.add(a); sites.setdefault((name, a), []).append(pc)
            elif ins == "athrow":
                if pend and pend[1] is not None:
                    ln = max((l for s, l in lines if s <= pend[1]), default=None)
                    throws.setdefault(name, []).append((pend[0], ln, pc))
                pend = None
        for s, e, h, ty in re.findall(r"^ +(\d+) +(\d+) +(\d+) +(Class \S+|any)$", body, re.M):
            xt.setdefault(name, []).append((int(s), int(e), ty.split()[-1]))
names = set(order)
calls = {k: {x for x in v if x in names} for k, v in calls.items()}
f = {"jcg_found": "true", **NONE}
f["jcg_callees_of:main"] = json.dumps(sorted(calls.get("main", ())), separators=(",", ":"))
tm = [m for m in order if m in throws]
if len(tm) == 1:
    fault = tm[0]
    exc, ln, apc = throws[fault][0]
    f.update(jcg_fault_method=fault, jcg_fault_exception=exc.rsplit("/", 1)[-1].replace("/", "."), jcg_throw_line=str(ln))
    prev, q = {"main": None}, ["main"]
    while q:
        x = q.pop(0)
        for y in sorted(calls.get(x, ())):
            if y not in prev:
                prev[y] = x; q.append(y)
    ch, x = [], fault
    while x:
        ch.append(x); x = prev.get(x)
    ch.reverse()
    f["jcg_call_chain"] = json.dumps(ch, separators=(",", ":")); f["jcg_call_depth"] = str(len(ch) - 1)
    f["jcg_caught"] = "false"
    SUP = {"IllegalStateException": ["RuntimeException", "Exception", "Throwable"]}
    for i in range(len(ch) - 1, -1, -1):
        pcs = [apc] if i == len(ch) - 1 else sites.get((ch[i], ch[i + 1]), [])
        hit = [ty for s, e, ty in xt.get(ch[i], []) for pc in pcs if s <= pc < e and (
            ty == "any" or ty == exc or ty.rsplit("/", 1)[-1] in SUP.get(exc.rsplit("/", 1)[-1], []))]
        if hit:
            f.update(jcg_catch_method=ch[i], jcg_catch_type=hit[0].rsplit("/", 1)[-1], jcg_caught="true"); break
print(json.dumps(f, indent=1))
