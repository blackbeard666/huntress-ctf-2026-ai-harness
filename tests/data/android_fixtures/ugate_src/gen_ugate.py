"""Forced-update / minimum-version gate fixtures (coverage atlas row 109, MASVS-CODE-2). The binary manifest carries
versionCode / versionName (+ versionCodeMajor), assets/ JSON carries the update policy and one ANS token per branch.
  lexi_required   versionName 6.0.1 vs minVersion 6.0.10 -> update-required branch (row 109 regression)
  code_blocked_ok 6.0.10 / 60010 vs minVersionName 6.0.9, minVersionCode 60009, blocked list -> ok branch
                  (a lexicographic compare says '6.0.10' < '6.0.9' and takes the required branch)
  rules_longcode  versionCodeMajor 1 + versionCode 5 (longVersionCode 4294967301), versionName 2.10.0, rules list of
                  semver ranges -> the '>=2.10.0' rule (lexicographic picks '<2.9.0')
  decoy_nearmiss  code_blocked_ok layout, but the ok branch holds a 15-hex near-miss -> no valid token
usage: gen_ugate.py <variant> <out.apk>
WRITERS: apktool's bundled aapt2 `link` (binary manifest), python zipfile APK."""
import io, json, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
tmp = Path(tempfile.mkdtemp())
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)


def manifest(vc, vn, major=None):
    mj = f' android:versionCodeMajor="{major}"' if major is not None else ""
    (tmp / "AndroidManifest.xml").write_text(
        '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.huntress.arena.ugate.'
        f'{variant.replace("_", "")}" android:versionCode="{vc}" android:versionName="{vn}"{mj}>'
        '<application android:hasCode="false"/></manifest>')
    o = tmp / "m.zip"
    subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                    str(tmp / "android-framework.jar"), "-o", str(o)], check=True)
    with zipfile.ZipFile(o) as z:
        return z.read("AndroidManifest.xml")


files = {}
if variant == "lexi_required":
    files["AndroidManifest.xml"] = manifest(60001, "6.0.1")
    files["assets/config/update_policy.json"] = json.dumps({"schema": "app.update.v2", "force_update": {
        "minVersion": "6.0.10", "on_update_required": "ANS-60011a2b3c4d5e6f", "on_ok": "ANS-0b5e55ed00c0ffee",
        "store_url": "market://details?id=com.huntress.arena"}}, indent=1).encode()
elif variant in ("code_blocked_ok", "decoy_nearmiss"):
    files["AndroidManifest.xml"] = manifest(60010, "6.0.10")
    ok = "ANS-d00dfeed6010abcd" if variant == "code_blocked_ok" else "ANS-d00dfeed6010abc"
    files["assets/remote_config_defaults.json"] = json.dumps({"app_gate": {
        "minVersionName": "6.0.9", "minVersionCode": 60009, "blockedVersions": ["6.0.1", "6.0.11"],
        "required": "ANS-bad1e55c0de60090", "allowed": ok}, "theme": "dark"}, indent=1).encode()
elif variant == "rules_longcode":
    files["AndroidManifest.xml"] = manifest(5, "2.10.0", major=1)
    files["res/raw/version_rules.json"] = json.dumps({"rules": [
        {"versions": "<2.9.0", "value": "ANS-0101010101a2b9c0"},
        {"versions": ">=2.9.0 <2.10.0", "value": "ANS-0202020202a2b9c9"},
        {"versions": ">=2.10.0", "value": "ANS-2100c0de4f00d5aa"}]}, indent=1).encode()
else:
    raise SystemExit("unknown variant " + variant)
files["assets/README.txt"] = b"update gate fixture\n"
bio = io.BytesIO()
with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
    for k, v in files.items():
        z.writestr(k, v)
out.write_bytes(bio.getvalue())
