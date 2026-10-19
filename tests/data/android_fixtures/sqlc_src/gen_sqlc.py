#!/usr/bin/env python3
"""Generate the sqlc_* fixtures (coverage atlas row 76: a SQLCipher-encrypted assets/*.db, passphrase a dex constant).
usage: PYTHONPATH=tools/pysqlcipher3 gen_sqlc.py <variant: v4_dex | v3_so_b64 | decoy_wrong_pw> <out.apk>
The db is written by the real SQLCipher library (pip sqlcipher3-binary 0.6.0, SQLCipher 4.12 community; v3 via
PRAGMA cipher_compatibility = 3). Outer classes.dex = javac --release 8 + dex2jar d2j-jar2dex. v3_so_b64 marks
SQLCipher with a lib/arm64-v8a/libsqlcipher.so entry (no dex reference) and stores the token base64'd."""
import base64, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
import sqlcipher3

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOK = {"v4_dex": "ANS-6d1e83b0f4a92c57", "v3_so_b64": "ANS-a04c9e17d3b26f85", "decoy_wrong_pw": "ANS-2b7f05c8e91da634"}[variant]
PW = {"v4_dex": "Vq9#mL2!secureDb", "v3_so_b64": "k3yStore-2026", "decoy_wrong_pw": "Vq9#mL2!secureDc"}[variant]
DEX_PW = "Vq9#mL2!secureDb" if variant == "decoy_wrong_pw" else PW  # decoy: the dex holds a near-miss passphrase
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))

db = tmp / "vault.db"
con = sqlcipher3.connect(str(db))
con.execute("PRAGMA key = '%s'" % PW.replace("'", "''"))
if variant == "v3_so_b64":
    con.execute("PRAGMA cipher_compatibility = 3")
con.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT, body TEXT)")
body = base64.b64encode(TOK.encode()).decode() if variant == "v3_so_b64" else TOK
con.executemany("INSERT INTO notes (title, body) VALUES (?, ?)",
                [("welcome", "nothing to see here"), ("flag", body), ("filler", "x" * 300)])
con.commit()
con.close()

src, cls = tmp / "src/com/huntress/mobile/vault", tmp / "cls"
src.mkdir(parents=True)
cls.mkdir()
ref = '' if variant == "v3_so_b64" else 'Class.forName("net.sqlcipher.database.SQLiteDatabase");'
(src / "Vault.java").write_text("""package com.huntress.mobile.vault;
public final class Vault {
  static final String DB_PASS = "%s";
  public static String open(String dir) throws Exception {
    %s
    return dir + "/assets/vault.db" + DB_PASS;
  }
}
""" % (DEX_PW, ref))
subprocess.run(["javac", "--release", "8", "-d", str(cls), str(src / "Vault.java")], check=True)
shutil.make_archive(str(tmp / "cls"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "cls.zip")],
               check=True, capture_output=True)
with zipfile.ZipFile(HERE.parent / "acd_aes_cbc_ivprefix.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"challenge": "vault", "hint": "the notes are encrypted at rest"}')
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
    z.writestr("assets/vault.db", db.read_bytes())
    if variant == "v3_so_b64":
        z.writestr("lib/arm64-v8a/libsqlcipher.so", b"\x7fELF\x02\x01\x01" + b"\0" * 57 + b"sqlcipher_codec_ctx\0")
shutil.rmtree(tmp)
print(out)
