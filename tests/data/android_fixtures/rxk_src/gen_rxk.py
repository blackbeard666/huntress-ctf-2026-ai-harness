"""Rolling-keystream fixtures (coverage atlas row 70). The ciphertext comes from Enc.java (java.util.Random and the
families' encrypt side, run on the JVM -- independent of lib.android); the APK is written with zipfile; the dex fixture
is javac --release 8 + dex2jar d2j-jar2dex. Usage: gen_rxk.py <mode> <out.apk> <plaintext>"""
import json, os, subprocess, sys, tempfile, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
mode, out, plain = sys.argv[1], sys.argv[2], sys.argv[3]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
subprocess.run(["javac", "--release", "8", "-d", str(tmp / "enc"), str(HERE / "Enc.java")], check=True)
emode = mode.replace("decoy_", "")
hx, b64, lst, jarr = subprocess.run(["java", "-cp", str(tmp / "enc"), "Enc", emode, plain], check=True,
                                   capture_output=True, text=True).stdout.split()
files = {"AndroidManifest.xml": b"<manifest package=\"com.huntress.rxk\"/>"}
if emode == "index_xor":
    files["assets/huntress_puzzle.json"] = json.dumps({"codec": "rolling", "data": hx, "hint": "decryptByte(i)"}).encode()
elif emode == "java_random":
    files["assets/huntress_puzzle.json"] = json.dumps({"codec": "prng_xor", "data": b64, "seed": 20261018}).encode()
elif emode == "cfb":
    files["assets/huntress_puzzle.json"] = json.dumps({"codec": "chain", "data": [int(x) for x in lst.split(",")],
                                                      "key": 119}).encode()
elif emode == "rotl_xor":
    files["assets/huntress_puzzle.json"] = json.dumps({"codec": "xor", "data": b64, "key": 167}).encode()
elif emode == "repkey_i":
    src = tmp / "src" / "com" / "huntress" / "rxk"
    src.mkdir(parents=True)
    (src / "Vault.java").write_text(
        "package com.huntress.rxk;\npublic class Vault {\n"
        "    static final byte[] ENC = {" + jarr + "};\n"
        "    static final String K = \"Hx9!q\";\n"
        "    static int decryptByte(int i) { return (ENC[i] ^ K.charAt(i % K.length()) ^ i) & 0xFF; }\n"
        "    public static String reveal() { StringBuilder s = new StringBuilder();\n"
        "        for (int i = 0; i < ENC.length; i++) s.append((char) decryptByte(i)); return s.toString(); }\n}\n")
    subprocess.run(["javac", "--release", "8", "-d", str(tmp / "cls"), str(src / "Vault.java")], check=True)
    subprocess.run(["jar", "cf", str(tmp / "app.jar"), "-C", str(tmp / "cls"), "."], check=True)
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.jar")],
                   check=True, capture_output=True)
    files["classes.dex"] = (tmp / "classes.dex").read_bytes()
    files["assets/huntress_puzzle.json"] = json.dumps({"codec": "native", "data": "see Vault.reveal()"}).encode()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items():
        z.writestr(n, b)
print(hx)
