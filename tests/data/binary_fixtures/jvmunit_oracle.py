"""Independent oracle for the jvm_unit_* fixtures (no lib code): class-level facts from jvm_oracle.py (javap -v -p),
the unit's primary class picked by `javap -v` SourceFile / this_class name, and the HCFG from javap's constant-pool
`= Utf8 <text>` lines decoded with stdlib base64 + zlib.crc32.
usage: python3 jvmunit_oracle.py <fixture.bin> <unit e.g. Relay.java>  -> prints the expected JSON dict"""
import base64, json, re, struct, subprocess, sys, tempfile, zipfile, zlib, os
path, unit = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
data = open(path, "rb").read()
def javap(b):
    f = tempfile.mktemp(suffix=".class"); open(f, "wb").write(b)
    return subprocess.run(["javap", "-v", "-p", f], capture_output=True, text=True).stdout
classes = {n: zipfile.ZipFile(path).read(n) for n in zipfile.ZipFile(path).namelist() if n.endswith(".class")} \
    if data[:2] == b"PK" else {"<bare>": data}
prim = None
for n, b in classes.items():
    t = javap(b)
    src = re.search(r'^SourceFile: "([^"]+)"', t, re.M)
    this = re.search(r"^\s*this_class: #\d+\s*// (\S+)", t, re.M)
    if this and (this.group(1).rsplit("/", 1)[-1] == unit.rsplit(".", 1)[0]):
        prim = (n if n != "<bare>" else this.group(1) + ".class", b, t)
out = {}
if prim:
    ent, b, t = prim
    args = [sys.executable, os.path.join(here, "jvm_oracle.py"), path] + ([ent] if data[:2] == b"PK" else [])
    cf = json.loads(subprocess.run(args, capture_output=True, text=True).stdout)
    out.update(method_count=cf["method_count"], methods=cf["methods"], this_class=cf["this_class"],
               primary_classfile=ent, primary_method_count=cf["method_count"], primary_methods=cf["methods"])
    rec = None
    for s in re.findall(r"= Utf8\s+(\S{80,})$", t, re.M):
        if re.fullmatch(r"[A-Za-z0-9+/]+=*", s):
            r = base64.b64decode(s)
            ver, key, ln, crc = r[4], r[5], *struct.unpack("<HI", r[6:12])
            p = bytes(c ^ key for c in r[12:12 + ln])
            if r[:4] == b"HCFG" and zlib.crc32(p) == crc:
                rec = (ver, key, crc, json.loads(p)); break
    if rec:
        out.update(hcfg_found="true", hcfg_version=str(rec[0]), xor_key_hex=f"0x{rec[1]:02x}", crc32_hex=f"0x{rec[2]:08x}",
                   **{f"config_{k}": v for k, v in rec[3].items()})
else:
    out.update(primary_classfile="none", primary_method_count="none", primary_methods="none", hcfg_found="false",
               config_campaign="none", xor_key_hex="none")
print(json.dumps(out, indent=1))
