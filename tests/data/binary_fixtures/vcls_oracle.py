"""Independent oracle for vcls_* twins: binutils objdump -d (Intel) of `target*` functions, or JDK javap -c -p of the
jar's classes -> the added/removed calls, mnemonics and invokes that witness the planted fix. Does not import lib.
usage: python3 vcls_oracle.py A.bin B.bin"""
import collections, json, os, re, subprocess, sys, tempfile, zipfile


def native(p):
    t = subprocess.run(["objdump", "-d", "-M", "intel", "--no-show-raw-insn", p], capture_output=True, text=True)
    if t.returncode:
        return None
    ins, cur = collections.Counter(), None
    for line in t.stdout.splitlines():
        m = re.match(r"^[0-9a-f]+ <(\w+)>:$", line)
        if m:
            cur = m.group(1) if m.group(1).startswith("target") else None
            continue
        m = re.match(r"^\s+[0-9a-f]+:\s+(\S+)\s*(.*)$", line)
        if m and cur:
            mn, op = m.groups()
            ins["call " + re.sub(r"@plt|<|>|^[0-9a-f]+ ", "", op)] += mn == "call"
            ins[mn] += 1
    return ins


def jvm(p):
    try:
        z = zipfile.ZipFile(p)
    except (zipfile.BadZipFile, OSError):
        return None
    d = tempfile.mkdtemp(); z.extractall(d); ins = collections.Counter()
    for n in z.namelist():
        if n.endswith(".class"):
            out = subprocess.run(["javap", "-c", "-p", os.path.join(d, n)], capture_output=True, text=True).stdout
            for m in re.finditer(r"^\s+\d+: (\w+)\s*(?:#\S+\s*)?(?://\s*\w+ (\S+))?", out, re.M):
                ins[m.group(1)] += 1
                if m.group(2) and m.group(1).startswith("invoke"):
                    ins[re.sub(r"\w+(Vulnerable|Corrected)", "R", m.group(2).split(":")[0])] += 1
    return ins


a, b = sys.argv[1:3]
sa = native(a) if open(a, "rb").read(4) == b"\x7fELF" else jvm(a)
sb = native(b) if open(b, "rb").read(4) == b"\x7fELF" else jvm(b)
if sa is None or sb is None:
    print(json.dumps({"comparable": False}))
else:
    print(json.dumps({"added": sorted(k for k in sb if sb[k] > sa.get(k, 0) and sb[k]),
                      "removed": sorted(k for k in sa if sa[k] > sb.get(k, 0) and sa[k])}))
