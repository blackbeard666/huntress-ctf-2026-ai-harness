#!/usr/bin/env python3
"""Generate the modcontract_* fixtures (D20 TT `moduleContract`: the host dex names a secondary payload as
`<entry>:<dotted class>` plus a member; the payload holds >1 ANS- candidate and the host-named member decides).
usage: gen_modcontract.py <variant: method | field_jar | decoy_nearmiss> <out.apk>
Writes Java sources, compiles host + payload together with javac --release 8, splits the classes into a host jar and a
payload jar, converts each with dex2jar's d2j-jar2dex, zips classes.dex + the payload (a bare dex or a jar holding
classes.dex) + a stock manifest with zipfile. The oracle (oracle.sh) runs the SAME payload classes on the JVM."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def chars(s):
    return ", ".join(str(ord(c)) for c in s)


IFACE = """package com.huntress.arena;
public interface ModuleContract { String moduleContract(); }
"""
HOST = """package com.huntress.arena;
public final class Loader {
  static final String MODULE = "%s";
  static final String CONTRACT_METHOD = "%s";
  public static String describe() { return "load " + MODULE + " and call " + CONTRACT_METHOD; }
}
"""
MOD_METHOD = """package com.huntress.arena.payload;
public final class Module implements com.huntress.arena.ModuleContract {
  public static final String LEGACY = "%s";
  public static final String ANSWER;
  static final String CONTRACT = "DAY20-SIGNED-MODULE:dynamic";
  static {
    char[] c = {%s};
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < c.length; i++) sb.append((char) (c[i] ^ 0x21));
    ANSWER = sb.toString();
  }
  public String moduleContract() { return ANSWER; }
  public static String stale() { return "ANS-" + "%s"; }
}
"""
if variant in ("method", "decoy_nearmiss"):
    ans = "ANS-3c9e07a1f4b2d865" if variant == "method" else "ANS-3c9e07a1f4b2d86"
    legacy = "ANS-0f1e2d3c4b5a6978" if variant == "method" else "ANS-0f1e2d3c4b5a697"
    stale = "77aa55cc33ee1100" if variant == "method" else "77aa55cc33ee110"
    entry = "assets/payload.dex"
    files = {"com/huntress/arena/ModuleContract": IFACE,
             "com/huntress/arena/Loader": HOST % (entry + ":com.huntress.arena.payload.Module", "moduleContract"),
             "com/huntress/arena/payload/Module": MOD_METHOD % (legacy, chars("".join(chr(ord(c) ^ 0x21) for c in ans)), stale)}
elif variant == "field_jar":
    entry = "assets/plugins/module.jar"
    files = {"com/huntress/arena/Loader": HOST % (entry + ":com.huntress.arena.ext.Plugin", "loadClass"),
             "com/huntress/arena/ext/Plugin": """package com.huntress.arena.ext;
public class Plugin {
  public static final String CONTRACT = "ANS-b5d2e8f10a7c4396";
  public String banner() { return "plugin " + "ANS-" + "aaaabbbbccccdddd".substring(0, 16).toUpperCase(); }
}
""",
             "com/huntress/arena/ext/Old": """package com.huntress.arena.ext;
public class Old { public static String token() { return "ANS-9081726354abcdef"; } }
"""}
else:
    sys.exit("variant?")
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
for name, body in files.items():
    (src / name).parent.mkdir(parents=True, exist_ok=True)
    (src / f"{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
host_j, pay_j = tmp / "host.jar", tmp / "pay.jar"
for jar, payload in ((host_j, False), (pay_j, True)):
    with zipfile.ZipFile(jar, "w") as z:
        for f in cls.rglob("*.class"):
            rel = f.relative_to(cls).as_posix()
            if ("/payload/" in rel or "/ext/" in rel) == payload:
                z.write(f, rel)
for jar in (host_j, pay_j):
    subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(jar.with_suffix(".dex")), str(jar)],
                   check=True, capture_output=True)
payload = (tmp / "pay.dex").read_bytes()
if entry.endswith(".jar"):
    with zipfile.ZipFile(tmp / "mod.jar", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("classes.dex", payload)
    payload = (tmp / "mod.jar").read_bytes()
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("assets/huntress_puzzle.json", '{"codec": "dynamic", "data": "%s"}' % entry)
    z.writestr("classes.dex", (tmp / "host.dex").read_bytes())
    z.writestr(entry, payload)
shutil.rmtree(tmp)
print(out)
