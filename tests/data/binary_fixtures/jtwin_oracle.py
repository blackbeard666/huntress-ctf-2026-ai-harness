"""Independent oracle for the jtwin_* fixtures: zipfile extract + JDK `javap -c -p -s` per class. Class names are
normalised here on their own terms (role word dropped; every run of digits after `__`/`$`/`_closure` replaced by its
rank among same-stem classes), method bodies compared as javap text with CP #indexes and branch offsets dropped.
usage: python3 jtwin_oracle.py A.jar B.jar ROLE_A ROLE_B  -> JSON facts"""
import json, os, re, subprocess, sys, tempfile, zipfile

def gens(names):
    stems = {}
    for n in names:
        stems.setdefault(re.sub(r"(?:(?<=__)|(?<=\$)|(?<=_closure))\d+", "N", n), []).append(n)
    out = {}
    for st, xs in stems.items():
        xs.sort(key=lambda n: [int(x) for x in re.findall(r"(?:(?<=__)|(?<=\$)|(?<=_closure))\d+", n)])
        for k, n in enumerate(xs):
            out[n] = f"{st}#{k}"
    return out

def side(jar, role):
    try:
        z = zipfile.ZipFile(jar)
    except zipfile.BadZipFile:
        return None
    d = tempfile.mkdtemp(); z.extractall(d)
    cls = [n[:-6] for n in z.namelist() if n.endswith(".class")]
    g = gens([c.replace(role, "") for c in cls])
    def canon(s):
        s = s.replace(role, "")
        for raw in sorted(g, key=len, reverse=True):
            s = re.sub(re.escape(raw) + r"(?!\d)", g[raw], s)
        return s
    out = {}
    for c in cls:
        txt = subprocess.run(["javap", "-c", "-p", "-s", os.path.join(d, c + ".class")], capture_output=True, text=True).stdout
        meths, cur, consts, invs = {}, None, [], {}
        for line in txt.splitlines():
            if re.match(r"^  \S.*(\);|static \{\};)$", line):
                cur = [line.strip(), None]; continue
            m = re.match(r"^    descriptor: (\S+)", line)
            if m and cur and cur[1] is None:
                cur[1] = m.group(1); key = (cur[0].split("(")[0].split()[-1] if "(" in cur[0] else "<clinit>") + cur[1]
                if key.startswith(c.replace("/", ".") + "("):
                    key = "<init>" + cur[1]
                meths[key] = []; invs[key] = []; continue
            m = re.match(r"^\s+\d+: (\w+)\s*(.*)$", line)
            if m and cur and cur[1]:
                op, rest = m.groups()
                com = rest.split("//", 1)[1].strip() if "//" in rest else re.sub(r"#\d+", "", rest).strip()
                if op.startswith(("if", "goto")): com = ""
                meths[key].append((op, canon(com)))
                if op.startswith("invoke"): invs[key].append(re.sub(r"^(Interface)?Method ", "", com).split(":")[0])
                if op in ("ldc", "ldc_w", "ldc2_w") and re.match(r"(int|long|float|double) ", com):
                    consts.append(com.split()[1].rstrip("lLfFdD"))
                elif op in ("bipush", "sipush"): consts.append(rest.strip())
                elif re.match(r"[il]const_", op): consts.append(op.split("_")[1].replace("m1", "-1"))
        out[canon(c)] = (c, meths, consts, invs)
    return out

A, B, ra, rb = sys.argv[1:5]
sa, sb = side(A, ra), side(B, rb)
if not sa or not sb:
    print(json.dumps({"_result": None})); sys.exit()
changed, vars_, first = [], [], None
for k, (c, ma, ka, ia) in sa.items():
    if k not in sb: continue
    _, mb, kb, ib = sb[k]
    ch = [m for m in ma if m in mb and ma[m] != mb[m]]
    if ch or set(ma) != set(mb):
        changed.append(c)
        seg = c.split("$")[1] if "$" in c else ""
        if seg and not re.search(r"__\d+|^\d+$", seg):
            vars_.append(seg.replace("_QMARK_", "?").replace("_BANG_", "!").replace("_", "-"))
        if first is None and ch:
            add = [x for x in ib[ch[0]] if x not in ia[ch[0]]]
            first = {"changed_methods": json.dumps(ch, separators=(",", ":")),
                     "added_constants": json.dumps(list(dict.fromkeys(x for x in kb if x not in ka))),
                     "added_invokes": json.dumps(list(dict.fromkeys(add)), separators=(",", ":"))}
f = {"changed_classes": json.dumps(changed, separators=(",", ":")), "changed_class_count": str(len(changed)),
     "changed_vars": json.dumps(vars_, separators=(",", ":")) if vars_ else "none"}
f.update(first or {})
print(json.dumps(f, indent=1))
