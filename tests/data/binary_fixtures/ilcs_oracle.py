"""Independent oracle for the ilcs_* fixtures: parses `ilspycmd -il FILE` text (ICSharpCode.Decompiler's IL
disassembler) for methods / call sites / ldstr / ldtoken+InitializeArray / .data RVAs, and runs ilcs_us.cs
(System.Reflection.Metadata MetadataReader.UserStrings) for the #US heap. Prints the expected json dict.
usage (repo root, bin/env.sh sourced): python3 tests/data/binary_fixtures/ilcs_oracle.py FILE"""
import json, os, pathlib, re, subprocess, sys
import pefile

f = pathlib.Path(sys.argv[1]).resolve()
il = subprocess.run(["ilspycmd", "-il", str(f)], capture_output=True, text=True, check=True).stdout
H = pathlib.Path(__file__).resolve().parent
W = pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / "ilcs_us_oracle"
if not (W / "out" / "u.dll").exists():
    W.mkdir(parents=True, exist_ok=True)
    (W / "U.cs").write_text((H / "ilcs_us.cs").read_text())
    (W / "u.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework>'
                                '<OutputType>Exe</OutputType><AssemblyName>u</AssemblyName><ImplicitUsings>disable</ImplicitUsings>'
                                '</PropertyGroup></Project>\n')
    subprocess.run(["dotnet", "build", "-c", "Release", "-o", "out"], cwd=W, check=True, capture_output=True)
us = json.loads(subprocess.run(["dotnet", str(W / "out" / "u.dll"), str(f)], capture_output=True, text=True, check=True).stdout)


def member(sig):
    """'instance void class [asm]Ns.T`1<string, int32>/N::M<int>(args)' -> 'Ns.T`1/N::M'"""
    sig = re.sub(r"\[[^\]]*\]", "", sig.replace("'", ""))
    while True:   # drop generic argument lists innermost-first; compiler names (<Main>b__0, <>c) follow / : or space
        t = re.sub(r"(?<=[\w`>!])<[^<>]*>", "", sig)
        if t == sig:
            break
        sig = t
    head = sig[:sig.index("(")] if "(" in sig else sig
    return [w for w in head.split(" ") if "::" in w][-1]


pe = pefile.PE(str(f), fast_load=True)
cls, methods, edges, strs, inits, data_rva = [], [], [], [], [], {}
cur, pinv, depth, pend = None, set(), 0, None
for line in il.splitlines():
    s = line.strip()
    m = re.match(r"\.class .*?([^\s]+)$", s)
    if m:
        cls.append([m.group(1).replace("'", ""), depth]); continue
    if s.startswith(".method"):
        cur = {"pinv": "pinvokeimpl" in s, "body": False}; continue
    m = re.match(r"\} // end of method (.+)$", s)
    if m and cur is not None:
        name = "/".join(c[0] for c in cls) + "::" + m.group(1).split("::", 1)[1].replace("'", "")
        if cur["body"] and not cur["pinv"]:
            methods.append(name)
        for e in cur.get("e", []):
            edges.append([name] + e)
        for x in cur.get("s", []):
            strs.append(x)
        for x in cur.get("i", []):
            inits.append([name, x])
        cur = None; continue
    m = re.match(r"\} // end of class", s)
    if m:
        cls.pop(); continue
    m = re.match(r"\.data cil I_([0-9A-F]+) = bytearray", s)
    if m:
        data_rva[m.group(1)] = int(m.group(1), 16)
    m = re.match(r"IL_([0-9a-f]{4}): (call|callvirt|newobj|calli|jmp|ldftn|ldvirtftn|ldstr|ldtoken) (.*)$", s)
    if m and cur is not None:
        cur["body"] = True
        at, op, rest = int(m.group(1), 16), m.group(2), m.group(3)
        if op == "ldstr":
            cur.setdefault("s", []).append(json.loads(rest) if rest.startswith('"') else rest)
        elif op == "ldtoken":
            pend = (at, member(rest.split(" ", 1)[1])) if rest.startswith("field ") else None
        elif op == "calli":
            cur.setdefault("e", []).append([op, "calli"])
        else:
            tgt = member(rest)
            cur.setdefault("e", []).append([op, tgt])
            if pend and tgt.endswith(("RuntimeHelpers::InitializeArray", "RuntimeHelpers::CreateSpan")):
                cur.setdefault("i", []).append(pend)
            pend = None
        continue
    if re.match(r"IL_[0-9a-f]{4}:", s) and cur is not None:
        cur["body"] = True; pend = None
    elif s.startswith(".maxstack") and cur is not None:
        cur["body"] = True
fields = {}   # field name -> data rva from '.field ... at I_xxxx'
cls2 = []
for line in il.splitlines():
    s = line.strip()
    m = re.match(r"\.class .*?([^\s]+)$", s)
    if m:
        cls2.append(m.group(1).replace("'", "")); continue
    if s.startswith("} // end of class"):
        cls2.pop(); continue
    m = re.match(r"\.field .* ([^\s]+) at I_([0-9A-F]+)$", s)
    if m:
        fields["/".join(cls2) + "::" + m.group(1).replace("'", "")] = int(m.group(2), 16)
pins = [x for x in edges if False]
native = set()
for line in il.splitlines():
    pass
# a callee is native when ilspy printed its .method with pinvokeimpl
pnames = set()
cls3, curp = [], False
for line in il.splitlines():
    s = line.strip()
    m = re.match(r"\.class .*?([^\s]+)$", s)
    if m:
        cls3.append(m.group(1).replace("'", "")); continue
    if s.startswith("} // end of class"):
        cls3.pop(); continue
    if s.startswith(".method"):
        curp = "pinvokeimpl" in s
    m = re.match(r"\} // end of method (.+)$", s)
    if m:
        if curp:
            pnames.add("/".join(cls3) + "::" + m.group(1).split("::", 1)[1].replace("'", ""))
        curp = False
ns = lambda n: n   # noqa: E731
calls = [e for e in edges if e[1] not in ("ldftn", "ldvirtftn")]
dd = lambda xs: list(dict.fromkeys(map(tuple, xs)))   # noqa: E731
mset = set(methods)
pc = {}
for c, op, t in calls:
    if t in pnames:
        pc.setdefault(t.rsplit("::", 1)[1], []).append(c)
exp = {
    "il_methods": methods, "il_method_count": str(len(methods)),
    "managed_edges": [list(x) for x in dd([c, t] for c, op, t in calls if t in mset)],
    "native_edges": [list(x) for x in dd([c, t] for c, op, t in calls if t in pnames)],
    "external_edges": [list(x) for x in dd([c, t] for c, op, t in calls if t not in mset and t not in pnames and t != "calli")],
    "ldftn_edges": [list(x) for x in dd([c, t] for c, op, t in edges if op in ("ldftn", "ldvirtftn"))],
    "pinvoke_callers": {k: list(dict.fromkeys(v)) for k, v in pc.items()},
    "native_callers": list(dict.fromkeys(c for c, op, t in calls if t in pnames)),
    "call_edge_count": str(len(edges)), "calli_count": str(sum(op == "calli" for _, op, _ in edges)),
    "user_strings": us, "user_string_count": str(len(us)), "ldstr_strings": strs,
    "array_init_count": str(len(inits)),
    "array_inits_brief": [{"method": m_, "il": at, "field": fl, "rva": f"0x{fields[fl]:x}",
                           "offset": pe.get_offset_from_rva(fields[fl])} for m_, (at, fl) in inits],
}
for k in ("il_methods", "managed_edges", "native_edges", "external_edges", "ldftn_edges", "pinvoke_callers",
          "native_callers", "user_strings", "ldstr_strings", "array_inits_brief"):
    exp[k] = json.dumps(exp[k], separators=(",", ":"), ensure_ascii=False)
print(json.dumps(exp, indent=1, ensure_ascii=False))
