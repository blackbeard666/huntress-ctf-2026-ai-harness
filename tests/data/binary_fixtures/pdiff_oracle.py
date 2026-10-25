"""Independent oracle: zipfile extract + JDK javap -c -p / -v over two jars -> expected jvm_patch_diff facts
(CP #indexes dropped, javap // comments compared, branch operands compared by opcode only).
usage: python3 pdiff_oracle.py A.jar B.jar ROLE_A ROLE_B"""
import json, os, re, subprocess, sys, tempfile, zipfile
def side(jar, role):
    d = tempfile.mkdtemp(); out = {}
    try:
        z = zipfile.ZipFile(jar)
    except zipfile.BadZipFile:
        return None
    z.extractall(d)
    for n in z.namelist():
        if not n.endswith(".class"): continue
        cls = n[:-6]; p = os.path.join(d, n)
        txt = subprocess.run(["javap", "-c", "-p", p], capture_output=True, text=True).stdout
        v = subprocess.run(["javap", "-v", "-p", p], capture_output=True, text=True).stdout
        bs = v.split("BootstrapMethods:")[-1].split("ScalaInlineInfo")[0] if "BootstrapMethods:" in v else ""
        bsm = [x for blk in re.split(r"\n\s+\d+: #\d+ ", bs) if "LambdaMetafactory" in blk.split("\n")[0]
               for x in re.findall(r"REF_invoke\w+ \S+\.([^.:]+):", blk)[1:2]]
        meths, cur = {}, None
        for line in txt.splitlines():
            m = re.match(r"^  \S.*\);$", line) or re.match(r"^  .*static \{\};$", line)
            if m: cur = line.strip(); meths[cur] = []; continue
            m = re.match(r"^\s+(\d+): (\w+)\s*(.*)$", line)
            if m and cur:
                op, rest = m.group(2), m.group(3)
                c = re.sub(r"#\d+", "", rest.split("//", 1)[1]).strip() if "//" in rest else re.sub(r"#\d+", "", rest).strip()
                if op.startswith(("if", "goto")): c = ""
                meths[cur].append((op.replace("ldc_w", "ldc"), c.replace(role, "R").replace(role.lower(), "r")))
        out[cls.replace(role, "R")] = (cls, os.path.getsize(p), meths, bsm)
    return out
A, B, ra, rb = sys.argv[1:5]
sa, sb = side(A, ra), side(B, rb)
if not sa or not sb:
    print(json.dumps({"_result": None})); sys.exit()
def inv(ins, cls):
    r = []
    for op, c in ins:
        if op.startswith("invoke") and op != "invokedynamic":
            t = re.sub(r"^(Interface)?Method ", "", c).split(":")[0].replace('"', "")
            t = t if "." in t else cls + "." + t
            if t not in r: r.append(t)
    return r
js = lambda v: json.dumps(v, separators=(",", ":"))
res = {}
for k, (ca, sza, ma, bsa) in sa.items():
    cb, szb, mb, bsb = sb[k]
    ch = [m for m in ma if m.replace(ra, rb) in mb and ma[m] != mb[m.replace(ra, rb)]]
    if not ch: continue
    m = ch[0]; xa, xb = ma[m], mb[m.replace(ra, rb)]
    ia, ib = inv(xa, ca), inv(xb, cb)
    ia = [x.replace(ra, "R") for x in ia]; ibn = [x.replace(rb, "R") for x in ib]
    res = {"changed_class": ca, "changed_methods_javap": ch, "method_count_a": str(len(ma)), "method_count_b": str(len(mb)),
           "instruction_count_a": str(len(xa)), "instruction_count_b": str(len(xb)),
           "classfile_size_a": str(sza), "classfile_size_b": str(szb),
           "added_invokes": js([x for x, y in zip(ib, ibn) if y not in ia]),
           "removed_invokes": js([x for x in inv(xa, ca) if x.replace(ra, "R") not in ibn]),
           "added_lambdas": js(list(dict.fromkeys(re.sub(r"\$adapted$", "", x) for x in bsb if x not in bsa))),
           "unchanged_methods_javap": [x for x in ma if x not in ch]}
print(json.dumps(res, indent=1))
