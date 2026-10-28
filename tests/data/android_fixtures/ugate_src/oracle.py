"""Independent oracle: `aapt dump xmltree` (Debian aapt) reads versionCode / versionCodeMajor / versionName, zipfile +
json read the policy, python `packaging.version.Version` / `SpecifierSet` judge it (npm-style 'a b' -> 'a,b').
Prints the ANS token(s) of the branch the APK's version takes."""
import json, re, subprocess, sys, zipfile
from packaging.specifiers import SpecifierSet
from packaging.version import Version

apk = sys.argv[1]
xt = subprocess.run(["aapt", "dump", "xmltree", apk, "AndroidManifest.xml"], capture_output=True, text=True,
                    check=True).stdout
attr = lambda n: (re.search(rf"android:{n}\(0x[0-9a-f]+\)=(?:\(type 0x10\)0x([0-9a-f]+)|\"([^\"]*)\")", xt) or [None])
m = attr("versionCode")
vc = int(m.group(1), 16)
mj = attr("versionCodeMajor")
lvc = (int(mj.group(1), 16) << 32 | vc) if mj and mj[0] else vc
vn = Version(attr("versionName").group(2))
ANS = re.compile(r"ANS-[0-9a-f]{16}(?![0-9a-f])")
z = zipfile.ZipFile(apk)
res = []
for n in z.namelist():
    if n.endswith(".json"):
        d = json.loads(z.read(n))
        if "force_update" in d:
            g = d["force_update"]
            res.append(g["on_update_required"] if vn < Version(g["minVersion"]) else g["on_ok"])
        if "app_gate" in d:
            g = d["app_gate"]
            req = vn < Version(g["minVersionName"]) or lvc < g["minVersionCode"] or \
                any(vn == Version(b) for b in g["blockedVersions"])
            res.append(g["required"] if req else g["allowed"])
        for r in d.get("rules", []):
            if vn in SpecifierSet(",".join(r["versions"].split())):
                res.append(r["value"])
print(f"versionCode={vc} longVersionCode={lvc} versionName={vn}")
print(" ".join(t for t in res if ANS.fullmatch(t)) or "none")
