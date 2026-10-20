"""Independent oracle for sfx_*.bin (offline, NOT lib.binary): 7-Zip `7z l -slt` (archive Type/Offset, member Paths in
archive order, zip local-header Offsets), `7z e -so | sha256` (member content), `readelf -hW` (stub image end =
e_shoff + e_shnum * e_shentsize). usage: python3 sfx_oracle.py <file.bin> [password]  -> expected JSON on stdout"""
import hashlib, json, re, subprocess, sys

f, pw = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
run = lambda *a: subprocess.run(a, capture_output=True, stdin=subprocess.DEVNULL)  # noqa: E731
h = run("readelf", "-hW", f).stdout.decode()
g = lambda k: int(re.search(k + r":\s+(\d+)", h).group(1))  # noqa: E731
img = g("Start of section headers") + g("Number of section headers") * g("Size of section headers")
out = run("/usr/bin/7z", "l", "-slt", "-p" + pw, f).stdout.decode()
if "Type = " not in out or re.search(r"Type = ELF", out):
    print(json.dumps({"archive_offset": "none"}))
    sys.exit(0)
top, _, body = out.partition("----------\n")
fmt = re.search(r"^Type = (\S+)", top, re.M).group(1).lower()
base = int((re.search(r"^Offset = (\d+)", top, re.M) or [0, 0])[1])
recs = [dict(re.findall(r"^(\S[^=]*?) = (.*)$", r, re.M)) for r in body.split("\n\n") if "Path = " in r]
files = [r for r in recs if r.get("Folder") != "+" and not r.get("Attributes", "").startswith("D")]
names = [r["Path"] for r in files]
off = base + min(int(r["Offset"]) for r in recs) if fmt == "zip" else base
sha = {}
for n in names:
    p = run("/usr/bin/7z", "e", "-so", "-p" + pw, f, n)
    sha[n] = hashlib.sha256(p.stdout).hexdigest() if p.returncode == 0 else None
exp = {"archive_format": fmt, "archive_offset": off, "stub_size": off, "image_end": img,
       "archive_at_image_end": off == img}
if fmt != "7z":
    hm = next((n for n in names if "hcfg" in n.lower()), None)
    exp.update(member_count=len(names), member_names=names, member_sha256=sha, first_member=names[0],
               hcfg_member=hm, hcfg_member_sha256=sha.get(hm))
print(json.dumps(exp))
