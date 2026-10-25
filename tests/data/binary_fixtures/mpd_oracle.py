"""Independent oracle for the mpd_* fixtures (.NET twin patch diff): `ilspycmd -il` text of A and B (ICSharpCode
IL disassembler), methods keyed by class + name + parameter list, IL lines compared with IL_xxxx labels replaced by
instruction indices; counts from the text (.try handlers, *.ovf ops, ldlen -> compare, brtrue/brfalse after dup or a
class-typed ldloc / ldnull+ceq) and the MVID from dnfile's Module row. Prints the expected_facts json.
usage (repo root, bin/env.sh sourced): python3 tests/data/binary_fixtures/mpd_oracle.py A B"""
import json, re, subprocess, sys

PRIM = re.compile(r"^(bool|char|u?int(8|16|32|64)|float(32|64)|native u?int|valuetype .*)$")


def methods(path):
    try:
        il = subprocess.run(["ilspycmd", "-il", path], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None
    out, cls, cur, lines, stack = {}, None, None, il.splitlines(), []
    for n, ln in enumerate(lines):
        m = re.match(r"^\t*\.class .*? ('[^']+'|[\w.$`<>@-]+)(<.*>)?\s*$", ln)
        if m:   # nested types: Outer/Inner (ilspy closes each with '} // end of class')
            stack.append(m.group(1).strip("'"))
            cls = "/".join(stack)
            continue
        if re.match(r"^\t*\} // end of class", ln) and stack:
            stack.pop()
            cls = "/".join(stack)
            continue
        if ln.startswith("\t.method"):
            j = n + 1
            while "(" not in lines[j]:
                j += 1
            h = lines[j].strip()
            name = re.search(r"([\w.$<>@'`-]+) \(", h).group(1).strip("'")
            cur = {"name": f"{cls}::{name}", "key": f"{cls}::{h}", "il": [], "locals": [], "eh": [], "ops": []}
            out[cur["key"]] = cur
            continue
        if cur is None:
            continue
        s = ln.strip()
        lm = re.match(r"^\[(\d+)\] (.+?),?$", s)
        if lm:
            cur["locals"].append(lm.group(2))
        if s in ("finally", "fault") or s.startswith(("catch ", "filter")):
            cur["eh"].append(s.split()[0])
        im = re.match(r"^IL_([0-9a-f]{4}): (\S+)\s*(.*)$", s)
        if im:
            cur["il"].append((int(im.group(1), 16), im.group(2), im.group(3)))
    for m in out.values():
        idx = {o: i for i, (o, _, _) in enumerate(m["il"])}
        m["norm"] = [(op, re.sub(r"IL_([0-9a-f]{4})", lambda x: f"#{idx.get(int(x.group(1), 16))}", arg))
                     for _, op, arg in m["il"]] + [("eh", e) for e in m["eh"]]
        m["ops"] = [op for _, op, _ in m["il"]]
        nul = bnd = 0
        for i, (op, arg) in enumerate(m["norm"]):
            prev, pa = m["norm"][i - 1] if i else ("", "")
            if op.startswith(("brtrue", "brfalse")):
                if prev == "dup":
                    nul += 1
                lm = re.match(r"^ldloc(?:\.s)?\.?(\d+)?$", prev)
                if lm:
                    k = int(lm.group(1) if lm.group(1) else pa)
                    nul += k < len(m["locals"]) and not PRIM.match(m["locals"][k])
            if op == "ldnull" and i + 1 < len(m["norm"]) and m["norm"][i + 1][0] in ("ceq", "cgt.un"):
                nul += 1
            if op == "ldlen":
                for op2, _ in m["norm"][i + 1:i + 4]:
                    if re.match(r"^(c(eq|gt|lt)|b(eq|ne|ge|gt|le|lt))", op2):
                        bnd += 1
                        break
                    if not op2.startswith(("conv.", "ldarg", "ldloc", "ldc.")):
                        break
        m["null"], m["bounds"] = nul, bnd
        m["ovf"] = sum(o in ("add.ovf", "add.ovf.un", "sub.ovf", "sub.ovf.un", "mul.ovf", "mul.ovf.un") for o in m["ops"])
    return out


def mvid(path):
    import dnfile
    return str(dnfile.dnPE(path).net.mdtables.Module[0].Mvid)


a, b = sys.argv[1], sys.argv[2]
A, B = methods(a), methods(b)
if not A or not B:
    print(json.dumps({"changed_methods": None, "fix_kind": None}))
    sys.exit(0)
ch = [k for k in A if k in B and A[k]["norm"] != B[k]["norm"]]
js = lambda v: json.dumps(v, separators=(",", ":"))   # noqa: E731
oa = [o for k in ch for o in A[k]["ops"]]
ob = [o for k in ch for o in B[k]["ops"]]
d = {q: sum(B[k][q] - A[k][q] for k in ch) for q in ("null", "bounds", "ovf")}
deh = sum(len(B[k]["eh"]) - len(A[k]["eh"]) for k in ch)
kind = "none" if not ch else "null_guard" if d["null"] > 0 else "bounds_check" if d["bounds"] > 0 else \
    "checked_arithmetic" if d["ovf"] > 0 else "exception_handling" if deh > 0 else \
    "constant_change" if all(A[k]["ops"] == B[k]["ops"] for k in ch) else "logic_change"
f = {"changed_methods": js([A[k]["name"] for k in ch]), "changed_method_count": str(len(ch)),
     "changed_method": A[ch[0]]["name"] if ch else "none",
     "eh_clause_count_a": str(len(A[ch[0]]["eh"])) if ch else "none",
     "eh_clause_count_b": str(len(B[ch[0]]["eh"])) if ch else "none",
     "added_opcodes": js(sorted({o for o in ob if ob.count(o) > oa.count(o)})),
     "removed_opcodes": js(sorted({o for o in oa if oa.count(o) > ob.count(o)})),
     "null_guard_added": js(d["null"] > 0), "bounds_check_added": js(d["bounds"] > 0),
     "checked_arithmetic_added": js(d["ovf"] > 0), "try_catch_added": js(deh > 0), "fix_kind": kind,
     "mvid_changed": js(mvid(a) != mvid(b))}
print(json.dumps(f, indent=1))
