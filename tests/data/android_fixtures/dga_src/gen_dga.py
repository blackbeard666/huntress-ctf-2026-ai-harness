#!/usr/bin/env python3
"""Generate the dga_* fixtures (coverage atlas rows 33, 69: the answer is "ANS-" + a hex prefix/suffix of a
MessageDigest / Mac result over app-visible inputs; no ANS-<16 hex> literal anywhere in the APK).
usage: gen_dga.py <variant: sha256_two_updates | hmac_last16 | md5_pkgname | decoy_random> <out.apk>
Writes Java sources (+ a compile-only android.content.Context stub), compiles with javac --release 8, converts ONLY
the app class with dex2jar's d2j-jar2dex, zips classes.dex + the manifest of a stock fixture with zipfile. The oracle
(oracle.sh) runs the SAME compiled class on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = "package com.huntress.mobile.d21.c33;\nimport java.security.MessageDigest;\nimport javax.crypto.Mac;\n" \
    "import javax.crypto.spec.SecretKeySpec;\nimport android.content.Context;\n"
HEX = """
  static String hex(byte[] d) {
    StringBuilder sb = new StringBuilder();
    for (byte b : d) sb.append(String.format("%02X", b & 0xff));
    return sb.toString();
  }
"""
SRC = {
    "sha256_two_updates": """
public final class Proof {%s
  public static String token(Context c) throws Exception {
    MessageDigest md = MessageDigest.getInstance("SHA-256");
    md.update("MOB-21-7c3e9a41".getBytes("UTF-8"));
    md.update("evidence-salt-ruby".getBytes("UTF-8"));
    return "ANS-" + hex(md.digest()).substring(0, 16);
  }
}
""" % HEX,
    "hmac_last16": """
public final class Proof {%s
  static final String KEY = "k3y-huntress-arena";
  public static String token(Context c) throws Exception {
    Mac m = Mac.getInstance("HmacSHA256");
    m.init(new SecretKeySpec(KEY.getBytes("UTF-8"), "HmacSHA256"));
    String h = hex(m.doFinal("case:4411".getBytes("UTF-8")));
    return "ANS-" + h.substring(h.length() - 16);
  }
}
""" % HEX,
    "md5_pkgname": """
public final class Proof {
  public static String token(Context c) throws Exception {
    byte[] d = MessageDigest.getInstance("MD5").digest(c.getPackageName().getBytes("UTF-8"));
    StringBuilder sb = new StringBuilder();
    for (byte b : d) sb.append(String.format("%02x", b));
    return ("ANS-" + sb.substring(0, 16)).toUpperCase().replace("ANS-", "ANS-");
  }
}
""",
    # near-miss: digest over SecureRandom bytes -- nothing app-visible goes in
    "decoy_random": """
public final class Proof {%s
  public static String token(Context c) throws Exception {
    byte[] r = new byte[32];
    new java.security.SecureRandom().nextBytes(r);
    return "ANS-" + hex(MessageDigest.getInstance("SHA-256").digest(r)).substring(0, 16);
  }
}
""" % HEX,
}
if variant not in SRC:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, stub, cls, scls = tmp / "src", tmp / "stub", tmp / "cls", tmp / "scls"
(src / "com/huntress/mobile/d21/c33").mkdir(parents=True)
(src / "com/huntress/mobile/d21/c33/Proof.java").write_text(P + SRC[variant])
(stub / "android/content").mkdir(parents=True)
(stub / "android/content/Context.java").write_text(
    "package android.content;\npublic abstract class Context { public abstract String getPackageName(); }\n")
cls.mkdir(); scls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(scls), str(stub / "android/content/Context.java")], check=True)
subprocess.run(["javac", "--release", "8", "-cp", str(scls), "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "digest", "hint": "the app hashes what it knows"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
