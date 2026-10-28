"""Independent oracle: jadx + unzip read the APK; Maven VersionRange (tools/maven-artifact), node semver
(tools/npm/node_modules/semver) and python `packaging` judge each advisory row. Prints the affected rows' ANS tokens."""
import json, re, subprocess, sys, tempfile, zipfile
from pathlib import Path
from packaging.specifiers import SpecifierSet
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
apk = sys.argv[1]
z = zipfile.ZipFile(apk)
libs = {}  # name -> (version, [tokens])
for n in z.namelist():
    if n.endswith("pom.properties"):
        kv = dict(l.split("=", 1) for l in z.read(n).decode().splitlines() if "=" in l)
        libs[f"{kv['groupId']}:{kv['artifactId']}"] = (kv["version"], [])
if "classes.dex" in z.namelist():
    o = Path(tempfile.mkdtemp())
    subprocess.run([str(ROOT / "bin/jadx"), "-q", "-d", str(o), apk], check=False, capture_output=True)
    for bc in (o / "sources").rglob("BuildConfig.java"):
        pkg = ".".join(bc.parent.relative_to(o / "sources").parts)
        ver = re.search(r'VERSION_NAME = "([^"]+)"', bc.read_text()).group(1)
        toks = re.findall(r"ANS-[0-9a-f]{16}", "".join(p.read_text() for p in bc.parent.glob("*.java")))
        libs[pkg] = (ver, toks)
def mvn(v, r):
    return subprocess.run(["java", "-cp", str(ROOT / "tools/maven-artifact/maven-artifact-3.9.6.jar") + ":" + str(ROOT / "tools/maven-artifact/commons-lang3-3.12.0.jar"), str(HERE / "AdvRange.java"),
                           v, r], capture_output=True, text=True, check=True).stdout.strip() == "true"
def npm(v, r):
    js = "const s=require(process.argv[1]);console.log(s.satisfies(s.coerce(process.argv[2],{includePrerelease:true})&&process.argv[2].split('.').length<3?s.coerce(process.argv[2]):process.argv[2],process.argv[3]))"
    return subprocess.run([str(ROOT / "tools/node/bin/node"), "-e", js, str(ROOT / "tools/npm/node_modules/semver"), v, r],
                          capture_output=True, text=True, check=True).stdout.strip() == "true"
rows = []
for n in z.namelist():
    if n.startswith("assets/") and n.endswith(".json"):
        d = json.loads(z.read(n))
        for a in (d["advisories"] if isinstance(d, dict) else d):
            if "package" in a and isinstance(a["package"], str):
                rows.append((a["package"], a["affected"], [a["proof"]]))
            for af in a.get("affected", []) if isinstance(a.get("affected"), list) else []:
                nm = af["package"]["name"]
                if "vulnerable_versions" in af:
                    rows.append((nm, ("py", af["vulnerable_versions"]), []))
                for rg in af.get("ranges", []):
                    ev = {k: v for e in rg["events"] for k, v in e.items()}
                    rows.append((nm, f"<{ev['fixed']}" if ev.get("introduced") == "0" else f">={ev['introduced']} <{ev['fixed']}", []))
for pkg, rng, toks in rows:
    ver, ltoks = libs[pkg]
    if isinstance(rng, tuple):
        ok = SpecifierSet(rng[1]).contains(ver, prereleases=True)
    elif rng[0] in "[(":
        ok = mvn(ver, rng)
    else:
        ok = npm(ver, rng)
    print(pkg, ver, rng, "AFFECTED" if ok else "not-affected", *(toks + ltoks) if ok else "")
