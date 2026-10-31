#!/usr/bin/env python3
"""Generate the idv_* fixtures (coverage atlas: puzzle-key-from-variant-identity). A v1 puzzle json with NO `key`: the
codec key is derived from the variant identity the app ships.
  build_xor    codec xor, key = bytes.fromhex(json `build`) (6 B repeating)
  case_hash    codec xor, key = String.hashCode("MOB-31-<10 HEX>") big-endian 4 B (case ref = a dex string constant)
  pkg_suffix   codec xor, key = bytes.fromhex(<12 hex package suffix>) (6 B repeating) (package = manifest com...d31.v<12 hex>)
  decoy_build  build_xor sealed under a NEAR-MISS build (last byte +1) -- the shipped build no longer opens it
usage: gen_idv.py <variant> <out.apk>
Build: the JVM (Seal.java, real String.hashCode / Integer.parseInt) seals a fixed ANS token into the puzzle json; javac
--release 8 + dex2jar d2j-jar2dex (Ids.java: case ref + secret consts) -> classes.dex; manifest by apktool's aapt2 link;
python zipfile assembles the APK.
ORACLE (independent of lib.android): Open.java on the host JVM reads the json via `unzip -p`, the package via
`aapt dump badging`, the case ref via `unzip -p classes.dex | strings | grep MOB-`, derives the key the same documented
way and prints the decoded plaintext; `expected` = that plaintext iff it fullmatches ANS-<16 hex>, else null."""
import json, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
ROOT = Path(__file__).resolve().parents[4]
ANS = {"build_xor": "ANS-6c1f0a9e44d2b7c3", "case_hash": "ANS-0f9e2d7a51c4b863", "pkg_suffix": "ANS-a4e9137c0d2f6b58",
       "decoy_build": "ANS-6c1f0a9e44d2b7c3"}[variant]
BUILD, SUFFIX, CASE, SECRET = "c47a19e2b05d", "9e3b5d71a2c4", "MOB-31-7F2A9C04E1", "SECRET-5D0C9E1F7A2B44E83C61"
MODE = {"build_xor": "build", "decoy_build": "build", "case_hash": "case", "pkg_suffix": "pkg"}[variant]
PKG = f"com.huntress.mobile.d31.v{SUFFIX}"
SEAL = r"""
public class Seal {
  static byte[] hx(String s) { byte[] b = new byte[s.length() / 2];
    for (int i = 0; i < b.length; i++) b[i] = (byte) Integer.parseInt(s.substring(2 * i, 2 * i + 2), 16); return b; }
  public static void main(String[] a) throws Exception {
    String mode = a[0], ans = a[1], id = a[2]; byte[] p = ans.getBytes("US-ASCII");
    byte[] k = mode.equals("build") ? hx(id) : mode.equals("pkg") ? hx(id.substring(id.length() - 12))
        : java.nio.ByteBuffer.allocate(4).putInt(id.hashCode()).array();
    byte[] o = new byte[p.length]; for (int i = 0; i < p.length; i++) o[i] = (byte) (p[i] ^ k[i % k.length]);
    System.out.print(java.util.Base64.getEncoder().encodeToString(o)); } }
"""
OPEN = SEAL.replace("class Seal", "class Open").replace(
    'String mode = a[0], ans = a[1], id = a[2]; byte[] p = ans.getBytes("US-ASCII");',
    'String mode = a[0], ans = a[1], id = a[2]; byte[] p = java.util.Base64.getDecoder().decode(ans);').replace(
    "System.out.print(java.util.Base64.getEncoder().encodeToString(o));", 'System.out.print(new String(o, "ISO-8859-1"));')
IDS = f"""package com.huntress.mobile.d31.v{SUFFIX};
public final class Ids {{ public static final String CASE_REF = "{CASE}"; public static final String CLIENT_SECRET = "{SECRET}";
  public static String caseRef() {{ return CASE_REF; }} public static String secret() {{ return CLIENT_SECRET; }} }}
"""
tmp = Path(tempfile.mkdtemp())
try:
    (tmp / "Seal.java").write_text(SEAL)
    (tmp / "Open.java").write_text(OPEN)
    subprocess.run(["javac", "--release", "8", "-d", str(tmp / "host"), str(tmp / "Seal.java"), str(tmp / "Open.java")], check=True)
    sid = {"build": BUILD if variant != "decoy_build" else BUILD[:-2] + "%02x" % (int(BUILD[-2:], 16) + 1),
           "case": CASE, "pkg": PKG}[MODE]
    data = subprocess.run(["java", "-cp", str(tmp / "host"), "Seal", MODE, ANS, sid], check=True, capture_output=True,
                          text=True).stdout
    puz = {"schema": "huntress.mobile.puzzle.v1", "day": 31, "codec": "xor", "data": data}
    if MODE == "build":
        puz["build"] = BUILD
    src = tmp / "src" / Path(*PKG.split("."))
    src.mkdir(parents=True)
    (src / "Ids.java").write_text(IDS)
    subprocess.run(["javac", "--release", "8", "-d", str(tmp / "cls"), str(src / "Ids.java")], check=True)
    shutil.make_archive(str(tmp / "app"), "zip", tmp / "cls")
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
                   check=True, capture_output=True)
    (tmp / "AndroidManifest.xml").write_text(f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{PKG}">
  <application android:label="Huntress"><activity android:name=".MainActivity" android:exported="true"/></application>
</manifest>""")
    subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                    "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
    (tmp / "aapt2").chmod(0o755)
    subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                    str(tmp / "android-framework.jar"), "-o", str(tmp / "base.apk")], check=True)
    with zipfile.ZipFile(tmp / "base.apk") as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for i in zin.infolist():
            z.writestr(i, zin.read(i))
        z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
        z.writestr("assets/huntress_puzzle.json", json.dumps(puz, separators=(",", ":")))
    # --- oracle: identity re-read from the built APK with unzip / aapt / strings, decoded by Open.java ---
    pj = json.loads(subprocess.run(["unzip", "-p", str(out), "assets/huntress_puzzle.json"], check=True,
                                   capture_output=True).stdout)
    if MODE == "build":
        oid = pj["build"]
    elif MODE == "pkg":
        oid = re.search(r"package: name='([^']+)'", subprocess.run(["aapt", "dump", "badging", str(out)],
                                                                    capture_output=True, text=True).stdout).group(1)
    else:
        dex = subprocess.run(["unzip", "-p", str(out), "classes.dex"], check=True, capture_output=True).stdout
        oid = re.search(r"MOB-\d+-[0-9A-F]+", subprocess.run(["strings", "-a"], input=dex, capture_output=True).stdout.decode()).group(0)
    plain = subprocess.run(["java", "-cp", str(tmp / "host"), "Open", MODE, pj["data"], oid], check=True,
                           capture_output=True).stdout.decode("latin-1")
    print(json.dumps({"identity": oid, "oracle_plain": plain,
                      "expected": plain if re.fullmatch(r"ANS-[0-9A-Fa-f]{16}", plain) else None}))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
