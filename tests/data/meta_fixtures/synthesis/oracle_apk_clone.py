"""Independent oracle for the APK clone/rebuild synthesis fixtures: per member `aapt dump badging` (package name,
versionCode, application-label), `apksigner verify --print-certs` (Signer #1 certificate SHA-256 digest) and
hashlib.sha256 of the file; members aapt rejects are not APKs. Prints every key as compact JSON.
usage: python3 -I oracle_apk_clone.py <kit.zip>"""
import hashlib, json, re, subprocess, sys, tempfile, zipfile, os

z = zipfile.ZipFile(sys.argv[1]); d = tempfile.mkdtemp(); rows = []
for n in z.namelist():
    p = os.path.join(d, n); open(p, "wb").write(z.read(n))
    r = subprocess.run(["aapt", "dump", "badging", p], capture_output=True, text=True)
    m = re.search(r"package: name='([^']*)' versionCode='(\d*)'", r.stdout)
    if r.returncode or not m:
        continue
    lab = re.search(r"^application-label:'(.*)'$", r.stdout, re.M)
    s = subprocess.run(["apksigner", "verify", "--print-certs", p], capture_output=True, text=True).stdout
    sg = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-f]{64})", s)
    rows.append(dict(name=n, pkg=m.group(1), vc=int(m.group(2) or 0), label=lab.group(1) if lab else None,
                     signer=sg.group(1) if sg else None, digest=hashlib.sha256(z.read(n)).hexdigest()))
out = {}
def grp(k):
    g = {}
    for r in rows:
        if r[k]: g.setdefault(r[k], []).append(r["name"])
    return {k2: sorted(v) for k2, v in sorted(g.items())} or "none"
out["package_groups"], out["signer_groups"] = grp("pkg"), grp("signer")
out["distinct_package_count"] = len({r["pkg"] for r in rows}) if rows else "none"
out["version_code_order"] = [r["name"] for r in sorted(rows, key=lambda r: (r["vc"], r["name"]))] or "none"
first = {}
for r in sorted(rows, key=lambda r: (r["vc"], r["name"])):
    first.setdefault(r["pkg"], r)
fam = {}
for r in rows:
    if r["label"]: fam.setdefault(r["label"], {}).setdefault(r["pkg"], []).append(r)
ref = {l: min(ps, key=lambda p: (-len(ps[p]), first[p]["vc"], p)) for l, ps in fam.items()}
clone, borrow = [], []
for r in rows:
    c = r["signer"] != first[r["pkg"]]["signer"]
    if r["label"] and ref[r["label"]] != r["pkg"]:
        borrow.append(r["name"]); c = c or r["signer"] != first[ref[r["label"]]]["signer"]
    if c: clone.append(r["name"])
out["clone_members"] = sorted(clone) or "none"
out["rebuild_members"] = sorted(a["name"] for a in rows if a["signer"] and any(
    b is not a and b["pkg"] == a["pkg"] and b["signer"] == a["signer"] and (b["vc"], b["digest"]) != (a["vc"], a["digest"])
    for b in rows)) or "none"
out["borrowed_label_member"] = (borrow[0] if len(borrow) == 1 else sorted(borrow)) if borrow else "none"
for k, v in out.items():
    print(k, v if isinstance(v, (str, int)) else json.dumps(v, separators=(",", ":")))
