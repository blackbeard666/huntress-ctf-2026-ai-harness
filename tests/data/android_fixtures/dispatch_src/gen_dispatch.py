#!/usr/bin/env python3
"""Generate the dispatch_* fixtures (coverage atlas row 77: a reflective dispatch table keyed by a runtime string; the
key the app supplies comes from the manifest deep link / the puzzle json, and only that handler's value counts -- every
other handler returns a decoy token). usage: gen_dispatch.py <variant> <out.apk>
  map_deeplink    HashMap<String, Class> in <clinit>, Class.newInstance() -> Handler.run(); key = last segment of the
                  intent-filter pathPrefix (/route/gamma)
  switch_puzzle   Java string switch (hashCode -> sparse-switch -> equals) over an instance LinkedHashMap<String,
                  Handler> built in <init>; key = puzzle json {"dispatch": {"route": "east"}}
  names_index     String[] of class names indexed by an int, Class.forName(names[i]); key = puzzle json {"entry": 2}
  decoy_nearmiss  map_deeplink layout, pathPrefix selects /route/delta whose handler returns a 15-hex near-miss
javac --release 8 -> dex2jar d2j-jar2dex; manifest compiled by apktool's bundled aapt2 `link -I android-framework.jar`;
python zipfile assembles the apk. The oracle (oracle.sh) runs the SAME classes on the JVM with the key read by
`aapt dump xmltree` / python json."""
import json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = "com.huntress.mobile.d19.dispatch"
P = f"package {PKG};\n"


def xs(s, k):
    return ", ".join(str(ord(c) ^ k) for c in s)


def handler(name, tok, k=None):
    if k is None:
        body = f'return "{tok}";'
    else:
        body = (f"char[] t = {{{xs(tok, k)}}}; char[] o = new char[t.length];"
                f" for (int i = 0; i < t.length; i++) o[i] = (char) (t[i] ^ {k}); return new String(o);")
    return P + f"final class {name} implements Handler {{ public String run() {{ {body} }} }}\n"


files = {"Handler": P + "public interface Handler { String run(); }\n"}
puzzle = {"challenge": "dispatch", "hint": "the app picks a handler by key"}
path = "/route/home"
if variant in ("map_deeplink", "decoy_nearmiss"):
    files.update({"Ha": handler("Ha", "ANS-1a2b3c4d5e6f7081"), "Hb": handler("Hb", "ANS-9f8e7d6c5b4a3921", 0x11),
                  "Hg": handler("Hg", "ANS-d4c19b07e3a6f285", 0x2C),
                  "Hd": handler("Hd", "ANS-5c2e9a07d1b3f48", 0x07)})
    files["Router"] = P + """
public final class Router {
  static final java.util.Map<String, Class<?>> ROUTES = new java.util.HashMap<>();
  static { ROUTES.put("alpha", Ha.class); ROUTES.put("beta", Hb.class); ROUTES.put("gamma", Hg.class);
           ROUTES.put("delta", Hd.class); }
  public static String dispatch(String key) throws Exception {
    Class<?> c = ROUTES.get(key);
    if (c == null) return "unknown route";
    return ((Handler) c.newInstance()).run();
  }
}
"""
    path = "/route/gamma" if variant == "map_deeplink" else "/route/delta"
elif variant == "switch_puzzle":
    files.update({"N": handler("N", "ANS-0b1c2d3e4f5a6b7c"), "S": handler("S", "ANS-7766554433221100", 0x21),
                  "E": handler("E", "ANS-3e9d0c4a7b21f856", 0x5A), "W": handler("W", "ANS-aabbccddeeff0011", 0x3)})
    files["Dispatcher"] = P + """
public final class Dispatcher {
  private final java.util.Map<String, Handler> table = new java.util.LinkedHashMap<>();
  public Dispatcher() { table.put("n", new N()); table.put("s", new S()); table.put("e", new E()); table.put("w", new W()); }
  public String handle(String route) {
    String k;
    switch (route) {
      case "north": k = "n"; break;
      case "south": k = "s"; break;
      case "east": k = "e"; break;
      case "west": k = "w"; break;
      default: return "no route";
    }
    return table.get(k).run();
  }
}
"""
    puzzle["dispatch"] = {"route": "east"}
elif variant == "names_index":
    files.update({"A0": handler("A0", "ANS-0000aaaa1111bbbb"), "A1": handler("A1", "ANS-2222cccc3333dddd", 0x13),
                  "A2": handler("A2", "ANS-b7f04e19c2d86a53", 0x4D), "A3": handler("A3", "ANS-4444eeee5555ffff")})
    files["Picker"] = P + """
public final class Picker {
  private static final String[] NAMES = {"%s.A0", "%s.A1", "%s.A2", "%s.A3"};
  public static String pick(int i) throws Exception {
    return ((Handler) Class.forName(NAMES[i]).newInstance()).run();
  }
}
""" % ((PKG,) * 4)
    puzzle["entry"] = 2
else:
    sys.exit("variant?")

tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
pdir = src / PKG.replace(".", "/")
pdir.mkdir(parents=True)
for name, body in files.items():
    (pdir / f"{name}.java").write_text(body)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True)
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
os.chmod(tmp / "aapt2", 0o755)
(tmp / "AndroidManifest.xml").write_text(f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{PKG}">
  <application android:label="Dispatch">
    <activity android:name=".DeepLinkActivity" android:exported="true">
      <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="huntress" android:host="dispatch" android:pathPrefix="{path}"/>
      </intent-filter>
    </activity>
  </application>
</manifest>
""")
subprocess.run([str(tmp / "aapt2"), "link", "-o", str(tmp / "base.apk"), "-I", str(tmp / "android-framework.jar"),
                "--manifest", str(tmp / "AndroidManifest.xml")], check=True)
with zipfile.ZipFile(tmp / "base.apk") as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for i in zin.infolist():
        z.writestr(i, zin.read(i))
    z.writestr("assets/huntress_puzzle.json", json.dumps(puzzle))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(out)
