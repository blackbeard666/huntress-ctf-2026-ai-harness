#!/usr/bin/env python3
"""Generate the appstate_* fixtures (coverage atlas rows 16-18, 31, 100: v2 chain reading app-private state answered
as a FRESH INSTALL). A D23-style `Release.code(Context)` whose token is computed from SharedPreferences (unset key ->
the default arg, put + commit -> read back), an app SQLiteOpenHelper (onCreate CREATE / INSERT, ContentValues insert,
rawQuery with selection args, Cursor moves / typed getters) or Context.openOrCreateDatabase + execSQL, the
AndroidKeyStore (load(null), containsAlias false, size 0), ApplicationInfo.flags FLAG_ALLOW_BACKUP /
FLAG_USES_CLEARTEXT_TRAFFIC / FLAG_DEBUGGABLE from the manifest, and NetworkSecurityPolicy.isCleartextTrafficPermitted
from the networkSecurityConfig xml.
usage: gen_appstate.py <variant: fresh | legacy | decoy> <out.apk>
Build: javac --release 8 (app + android.* stubs) -> d2j-jar2dex; manifest + res/xml by apktool's aapt2 (compile + link
--min/--target-sdk-version); zipfile adds classes.dex; keytool RSA + apksigner v1+v2.
ORACLE (independent of lib.android): the host JVM runs Release.code() on stubs whose state is real: SQL executed by the
`sqlite3` CLI (every statement replayed into :memory:), a JCA provider "AndroidKeyStore" backed by an empty KeyStoreSpi
(the real java.security.KeyStore front end), a HashMap SharedPreferences; ApplicationInfo.flags and the cleartext policy
from `aapt2 dump xmltree` of the SIGNED APK's AndroidManifest.xml / res/xml/nsc.xml (parsed here, Android's
ManifestConfigSource / XmlConfigSource rules: allowBackup default true, cleartext default targetSdk < 28, most specific
<domain>, inner domain-config wins)."""
import re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PKG = {"fresh": "com.huntress.arena.state1", "legacy": "com.huntress.arena.state2", "decoy": "com.huntress.arena.state3"}[variant]
TSDK = {"fresh": 33, "legacy": 27, "decoy": 33}[variant]
STUBS = {
    "android/content/SharedPreferences.java": """package android.content;
public interface SharedPreferences { long getLong(String k, long d); int getInt(String k, int d); String getString(String k, String d);
  boolean getBoolean(String k, boolean d); boolean contains(String k); Editor edit();
  interface Editor { Editor putLong(String k, long v); Editor putInt(String k, int v); Editor putString(String k, String v);
    Editor putBoolean(String k, boolean v); void apply(); boolean commit(); } }""",
    "android/content/Prefs.java": """package android.content;
public class Prefs implements SharedPreferences { java.util.HashMap<String, Object> m = new java.util.HashMap<>();
  public long getLong(String k, long d) { return m.containsKey(k) ? (Long) m.get(k) : d; }
  public int getInt(String k, int d) { return m.containsKey(k) ? (Integer) m.get(k) : d; }
  public String getString(String k, String d) { return m.containsKey(k) ? (String) m.get(k) : d; }
  public boolean getBoolean(String k, boolean d) { return m.containsKey(k) ? (Boolean) m.get(k) : d; }
  public boolean contains(String k) { return m.containsKey(k); }
  public Editor edit() { final java.util.HashMap<String, Object> w = new java.util.HashMap<>(); final Prefs me = this; return new Editor() {
    public Editor putLong(String k, long v) { w.put(k, v); return this; } public Editor putInt(String k, int v) { w.put(k, v); return this; }
    public Editor putString(String k, String v) { w.put(k, v); return this; } public Editor putBoolean(String k, boolean v) { w.put(k, v); return this; }
    public void apply() { me.m.putAll(w); } public boolean commit() { me.m.putAll(w); return true; } }; } }""",
    "android/content/ContentValues.java": """package android.content;
public class ContentValues { public java.util.LinkedHashMap<String, Object> m = new java.util.LinkedHashMap<>();
  public void put(String k, String v) { m.put(k, v); } public void put(String k, Integer v) { m.put(k, v); }
  public void put(String k, Long v) { m.put(k, v); } }""",
    "android/database/Cursor.java": """package android.database;
public interface Cursor { boolean moveToFirst(); boolean moveToNext(); int getCount(); int getColumnIndex(String n);
  long getLong(int i); int getInt(int i); String getString(int i); void close(); }""",
    "android/database/Rows.java": """package android.database;
public class Rows implements Cursor { java.util.List<String[]> r; String[] cols; int pos = -1;
  public Rows(String[] cols, java.util.List<String[]> r) { this.cols = cols; this.r = r; }
  public boolean moveToFirst() { pos = 0; return !r.isEmpty(); } public boolean moveToNext() { pos++; return pos < r.size(); }
  public int getCount() { return r.size(); }
  public int getColumnIndex(String n) { for (int i = 0; i < cols.length; i++) if (cols[i].equalsIgnoreCase(n)) return i; return -1; }
  public long getLong(int i) { return Long.parseLong(r.get(pos)[i]); } public int getInt(int i) { return (int) getLong(i); }
  public String getString(int i) { return r.get(pos)[i]; } public void close() { } }""",
    "android/database/sqlite/SQLiteDatabase.java": """package android.database.sqlite;
public class SQLiteDatabase { public interface CursorFactory { }
  java.util.List<String> log = new java.util.ArrayList<>();
  static String lit(Object o) { return o instanceof String ? "'" + ((String) o).replace("'", "''") + "'" : String.valueOf(o); }
  static String bind(String q, Object[] a) { if (a == null) return q; StringBuilder b = new StringBuilder(); int k = 0;
    for (char ch : q.toCharArray()) { if (ch == '?') b.append(lit(a[k++])); else b.append(ch); } return b.toString(); }
  java.util.List<String[]> run(String q) { try {
      Process p = new ProcessBuilder("sqlite3", "-batch", "-header", "-separator", "\\u001f", ":memory:").start();
      java.io.Writer w = new java.io.OutputStreamWriter(p.getOutputStream(), "UTF-8");
      for (String s : log) w.write(s + ";\\n");
      w.write(".headers on\\n" + q + ";\\n"); w.close();
      java.io.BufferedReader rd = new java.io.BufferedReader(new java.io.InputStreamReader(p.getInputStream(), "UTF-8"));
      java.util.List<String[]> o = new java.util.ArrayList<>(); String l;
      while ((l = rd.readLine()) != null) o.add(l.split("\\u001f", -1));
      if (p.waitFor() != 0) throw new RuntimeException("sqlite3 failed: " + q); return o;
    } catch (Exception e) { throw new RuntimeException(e); } }
  public void execSQL(String q) { log.add(q); run("SELECT 1"); }
  public void execSQL(String q, Object[] a) { execSQL(bind(q, a)); }
  public android.database.Cursor rawQuery(String q, String[] a) { java.util.List<String[]> o = run(bind(q, a));
    if (o.isEmpty()) return new android.database.Rows(new String[0], o);
    return new android.database.Rows(o.get(0), o.subList(1, o.size())); }
  public long insert(String t, String hack, android.content.ContentValues cv) { StringBuilder c = new StringBuilder(), v = new StringBuilder();
    for (java.util.Map.Entry<String, Object> e : cv.m.entrySet()) { if (c.length() > 0) { c.append(","); v.append(","); }
      c.append("\\"").append(e.getKey()).append("\\""); v.append(lit(e.getValue())); }
    execSQL("INSERT INTO \\"" + t + "\\" (" + c + ") VALUES (" + v + ")");
    return Long.parseLong(rawQuery("SELECT MAX(rowid) FROM \\"" + t + "\\"", null).moveToFirst() ? run("SELECT MAX(rowid) FROM \\"" + t + "\\"").get(1)[0] : "-1"); } }""",
    "android/database/sqlite/SQLiteOpenHelper.java": """package android.database.sqlite;
public abstract class SQLiteOpenHelper { static java.util.HashMap<String, SQLiteDatabase> dbs = new java.util.HashMap<>();
  String n; public SQLiteOpenHelper(android.content.Context c, String n, SQLiteDatabase.CursorFactory f, int v) { this.n = n; }
  public SQLiteDatabase getWritableDatabase() { SQLiteDatabase d = dbs.get(n);
    if (d == null) { d = new SQLiteDatabase(); dbs.put(n, d); onCreate(d); } return d; }
  public abstract void onCreate(SQLiteDatabase db); public abstract void onUpgrade(SQLiteDatabase db, int a, int b); }""",
    "android/content/pm/ApplicationInfo.java": """package android.content.pm;
public class ApplicationInfo { public static final int FLAG_DEBUGGABLE = 2, FLAG_ALLOW_BACKUP = 0x8000, FLAG_USES_CLEARTEXT_TRAFFIC = 0x8000000;
  public int flags = Integer.decode(System.getProperty("ctx.flags")); }""",
    "android/security/NetworkSecurityPolicy.java": """package android.security;
public class NetworkSecurityPolicy { public static NetworkSecurityPolicy getInstance() { return new NetworkSecurityPolicy(); }
  public boolean isCleartextTrafficPermitted() { return Boolean.parseBoolean(System.getProperty("ct.base")); }
  public boolean isCleartextTrafficPermitted(String h) { return Boolean.parseBoolean(System.getProperty("ct." + h)); } }""",
    "android/content/Context.java": """package android.content;
public class Context { static Prefs prefs = new Prefs(); static java.util.HashMap<String, android.database.sqlite.SQLiteDatabase> dbs = new java.util.HashMap<>();
  public SharedPreferences getSharedPreferences(String n, int m) { return prefs; }
  public android.database.sqlite.SQLiteDatabase openOrCreateDatabase(String n, int m, android.database.sqlite.SQLiteDatabase.CursorFactory f) {
    if (!dbs.containsKey(n)) dbs.put(n, new android.database.sqlite.SQLiteDatabase()); return dbs.get(n); }
  public android.content.pm.ApplicationInfo getApplicationInfo() { return new android.content.pm.ApplicationInfo(); } }""",
}
MIX = """  static long mix(long h, long v) { h ^= v; h *= 0x100000001b3L; h ^= h >>> 29; return h; }
  static String hex(long h) { String s = Long.toHexString(h); while (s.length() < 16) s = "0" + s; return "ANS-" + s; }
"""
TAIL = """      KeyStore ks = KeyStore.getInstance("AndroidKeyStore");
      ks.load(null);
      h = mix(h, ks.containsAlias("arena_master") ? 11 : 13);
      h = mix(h, ks.size());
      int fl = c.getApplicationInfo().flags;
      h = mix(h, (fl & ApplicationInfo.FLAG_ALLOW_BACKUP) != 0 ? 1 : 2);
      h = mix(h, (fl & ApplicationInfo.FLAG_USES_CLEARTEXT_TRAFFIC) != 0 ? 3 : 4);
      h = mix(h, (fl & ApplicationInfo.FLAG_DEBUGGABLE) != 0 ? 5 : 6);
      NetworkSecurityPolicy p = NetworkSecurityPolicy.getInstance();
      h = mix(h, p.isCleartextTrafficPermitted() ? 1 : 2);
      h = mix(h, p.isCleartextTrafficPermitted("api.arena.test") ? 3 : 4);
      h = mix(h, p.isCleartextTrafficPermitted("secure.arena.test") ? 5 : 6);
      h = mix(h, p.isCleartextTrafficPermitted("cdn.example.com") ? 7 : 8);
      return hex(h);
"""
FRESH = """      long h = 0xcbf29ce484222325L;
      SharedPreferences sp = c.getSharedPreferences("arena_state", 0);
%(gate)s      h = mix(h, sp.getLong("first_run_ms", 1717171717L));
      h = mix(h, sp.getInt("launches", 0));
      h = mix(h, sp.getBoolean("onboarded", false) ? 7 : 3);
      h = mix(h, sp.getString("device_tag", "fresh-install").hashCode());
      sp.edit().putInt("launches", 1).putString("device_tag", "t-42").commit();
      h = mix(h, sp.getInt("launches", 9));
      h = mix(h, sp.getString("device_tag", "x").hashCode());
      SQLiteDatabase db = new Db(c).getWritableDatabase();
      ContentValues cv = new ContentValues();
      cv.put("name", "gamma");
      cv.put("score", "31");
      h = mix(h, db.insert("scores", null, cv));
      Cursor cur = db.rawQuery("SELECT COUNT(*), SUM(score), MAX(name) FROM scores WHERE score > ?", new String[] {"10"});
      if (cur.moveToFirst()) { h = mix(h, cur.getLong(0)); h = mix(h, cur.getInt(1)); h = mix(h, cur.getString(2).hashCode()); }
      cur.close();
      Cursor all = db.rawQuery("SELECT name, score FROM scores ORDER BY score DESC", null);
      int ni = all.getColumnIndex("name");
      while (all.moveToNext()) h = mix(h, all.getString(ni).hashCode() ^ all.getLong(1));
      all.close();
"""
LEGACY = """      long h = 0x84222325cbf29ce4L;
      SharedPreferences sp = c.getSharedPreferences("legacy", 0);
      h = mix(h, sp.getLong("install_ms", -5L));
      h = mix(h, sp.contains("install_ms") ? 1 : 0);
      sp.edit().putLong("install_ms", 99L).apply();
      h = mix(h, sp.getLong("install_ms", 0L));
      SQLiteDatabase db = c.openOrCreateDatabase("legacy.db", 0, null);
      db.execSQL("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v INTEGER)");
      db.execSQL("INSERT INTO kv VALUES ('seed', 4242)");
      db.execSQL("INSERT INTO kv VALUES (?, ?)", new Object[] {"salt", "99"});
      db.execSQL("INSERT OR REPLACE INTO kv VALUES ('seed', 4243)");
      Cursor cur = db.rawQuery("SELECT k, v FROM kv ORDER BY k", null);
      h = mix(h, cur.getCount());
      while (cur.moveToNext()) { h = mix(h, cur.getString(0).hashCode()); h = mix(h, cur.getLong(cur.getColumnIndex("v"))); }
      cur.close();
"""
GATE = """      if (!sp.getBoolean("onboarded", false)) return "welcome";
"""
BODY = {"fresh": FRESH % {"gate": ""}, "legacy": LEGACY, "decoy": FRESH % {"gate": GATE}}[variant]
APP = """package %(pkg)s;
import android.content.*;
import android.content.pm.ApplicationInfo;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.security.NetworkSecurityPolicy;
import java.security.KeyStore;
public final class Release {
  static Context ctx;
""" + MIX + """  public static String code(Context c) {
    ctx = c;
    try {
""" + BODY + TAIL + """    } catch (Exception e) { return "error"; }
  }
}"""
DB = """package %(pkg)s;
import android.database.sqlite.*;
final class Db extends SQLiteOpenHelper {
  Db(android.content.Context c) { super(c, "arena.db", null, 3); }
  public void onCreate(SQLiteDatabase db) {
    db.execSQL("CREATE TABLE scores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, score INTEGER)");
    db.execSQL("INSERT INTO scores(name, score) VALUES ('alpha', 17)");
    db.execSQL("INSERT INTO scores(name, score) VALUES (?, ?)", new Object[] {"beta", "5"});
  }
  public void onUpgrade(SQLiteDatabase db, int a, int b) { db.execSQL("DROP TABLE scores"); onCreate(db); }
}"""
PROBE = """package %(pkg)s;
public class Probe { public static void main(String[] a) throws Exception {
  java.security.Security.addProvider(new java.security.Provider("AKS", 1.0, "empty AndroidKeyStore") {
    { put("KeyStore.AndroidKeyStore", EmptySpi.class.getName()); } });
  System.out.println(Release.code(new android.content.Context())); } }"""
SPI = """package %(pkg)s;
public class EmptySpi extends java.security.KeyStoreSpi {
  public java.security.Key engineGetKey(String a, char[] p) { return null; }
  public java.security.cert.Certificate[] engineGetCertificateChain(String a) { return null; }
  public java.security.cert.Certificate engineGetCertificate(String a) { return null; }
  public java.util.Date engineGetCreationDate(String a) { return null; }
  public void engineSetKeyEntry(String a, java.security.Key k, char[] p, java.security.cert.Certificate[] c) { throw new UnsupportedOperationException(); }
  public void engineSetKeyEntry(String a, byte[] k, java.security.cert.Certificate[] c) { throw new UnsupportedOperationException(); }
  public void engineSetCertificateEntry(String a, java.security.cert.Certificate c) { throw new UnsupportedOperationException(); }
  public void engineDeleteEntry(String a) { }
  public java.util.Enumeration<String> engineAliases() { return java.util.Collections.emptyEnumeration(); }
  public boolean engineContainsAlias(String a) { return false; }
  public int engineSize() { return 0; }
  public boolean engineIsKeyEntry(String a) { return false; }
  public boolean engineIsCertificateEntry(String a) { return false; }
  public String engineGetCertificateAlias(java.security.cert.Certificate c) { return null; }
  public void engineStore(java.io.OutputStream o, char[] p) { }
  public void engineLoad(java.io.InputStream i, char[] p) { } }"""
APPATTR = {"fresh": ' android:allowBackup="false" android:networkSecurityConfig="@xml/nsc"',
           "legacy": "", "decoy": ' android:allowBackup="false" android:networkSecurityConfig="@xml/nsc"'}[variant]
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%s"
  android:versionCode="3" android:versionName="1.3">
  <application android:label="arena"%s/>
</manifest>""" % (PKG, APPATTR)
NSC = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="true">arena.test</domain>
    <domain-config cleartextTrafficPermitted="false">
      <domain includeSubdomains="false">secure.arena.test</domain>
    </domain-config>
  </domain-config>
</network-security-config>
"""

tmp = Path(tempfile.mkdtemp())
src, cls = tmp / "src", tmp / "cls"
pdir = PKG.replace(".", "/")
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2",
                "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "aapt2").chmod(0o755)
(tmp / "res/values").mkdir(parents=True)
(tmp / "res/values/strings.xml").write_text("<resources><string name=\"app\">arena</string></resources>")
if "nsc" in APPATTR:
    (tmp / "res/xml").mkdir()
    (tmp / "res/xml/nsc.xml").write_text(NSC)
(tmp / "AndroidManifest.xml").write_text(MAN)
subprocess.run([str(tmp / "aapt2"), "compile", "--dir", str(tmp / "res"), "-o", str(tmp / "res.zip")], check=True)
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I",
                str(tmp / "android-framework.jar"), "--min-sdk-version", "21", "--target-sdk-version", str(TSDK),
                "-o", str(tmp / "base.apk"), str(tmp / "res.zip")], check=True)
files = dict(STUBS)
files[f"{pdir}/Release.java"] = APP % {"pkg": PKG}
files[f"{pdir}/Db.java"] = DB % {"pkg": PKG}
files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG}
files[f"{pdir}/EmptySpi.java"] = SPI % {"pkg": PKG}
for rel, body in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(body)
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
app = tmp / "app"
shutil.copytree(cls, app)
for junk in ("android", *(p.relative_to(app) for p in (app / pdir).glob("Probe*.class")), f"{pdir}/EmptySpi.class"):
    p = app / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", app)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
subprocess.run(["keytool", "-genkeypair", "-keystore", str(tmp / "k.jks"), "-storepass", "android", "-keypass", "android",
                "-alias", "k", "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
                "-dname", f"CN=Arena {variant}, O=Huntress Fixtures, C=US"], check=True, capture_output=True)
with zipfile.ZipFile(tmp / "base.apk") as zin, zipfile.ZipFile(tmp / "unsigned.apk", "w", zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist():
        z.writestr(n, zin.read(n))
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
subprocess.run(["apksigner", "sign", "--ks", str(tmp / "k.jks"), "--ks-pass", "pass:android", "--min-sdk-version", "21",
                "--out", str(out), str(tmp / "unsigned.apk")], check=True)
# --- oracle: aapt2 xmltree of the signed APK -> flags + cleartext policy; host JVM (sqlite3 CLI, empty JCA keystore) ---
def xmltree(name):
    return subprocess.run([str(tmp / "aapt2"), "dump", "xmltree", "--file", name, str(out)], check=True,
                          capture_output=True, text=True).stdout
def attr(tree, a):
    m = re.search(r'A: http://schemas.android.com/apk/res/android:%s\(0x[0-9a-f]+\)=(?:\(type 0x\w+\))?"?([^"\s]+)"?' % a, tree)
    return m[1] if m else None
man = xmltree("AndroidManifest.xml")
tsdk = int(attr(man, "targetSdkVersion"), 0)
backup = (attr(man, "allowBackup") or "true").lower() not in ("false", "0x0")
ctr = attr(man, "usesCleartextTraffic")
cleartext = tsdk < 28 if ctr is None else ctr.lower() not in ("false", "0x0")
dbg = (attr(man, "debuggable") or "false").lower() not in ("false", "0x0")
flags = 0x38C8BE44 & ~0x0800800A | (0x8000 if backup else 0) | (0x08000000 if cleartext else 0) | (2 if dbg else 0)
hosts = ["api.arena.test", "secure.arena.test", "cdn.example.com"]
pol = {h: cleartext for h in hosts}
pol["base"] = cleartext
if attr(man, "networkSecurityConfig"):
    tree = xmltree("res/xml/nsc.xml")
    base, stack, doms, cur = tsdk < 28, [], [], None   # (indent, attr) per open domain-config
    for line in tree.splitlines():
        ind = len(line) - len(line.lstrip())
        while stack and stack[-1][0] >= ind:
            stack.pop()
        m = re.match(r"\s*E: ([\w-]+)", line)
        if m:
            if m[1] == "domain-config":
                stack.append([ind, None])
            cur = m[1]
            continue
        a = re.match(r"\s*A: (\w+)\(?.*?=(?:\(type 0x\w+\))?(\S+)", line)
        if a and a[1] == "cleartextTrafficPermitted":
            v = a[2].strip('"').lower() not in ("false", "0x0")
            if cur == "base-config":
                base = v
            elif stack:
                stack[-1][1] = v
        if a and a[1] == "includeSubdomains" and cur == "domain":
            doms.append([a[2].strip('"').lower() not in ("false", "0x0"), [x[1] for x in stack], None])
        t = re.match(r'\s*T: \'?"?([\w.-]+)', line)
        if t and cur == "domain" and doms and doms[-1][2] is None:
            doms[-1][2] = t[1]
    pol["base"] = base
    for h in hosts:
        best = max(((len(d), h == d, cfg) for sub, cfg, d in doms if h == d or sub and h.endswith("." + d)),
                   default=None, key=lambda x: x[:2])
        v = None
        for x in (best[2] if best else []):
            v = x if x is not None else v
        pol[h] = base if v is None else v
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shown = subprocess.run(["java", f"-Dctx.flags={flags:#x}", *[f"-Dct.{k}={str(v).lower()}" for k, v in pol.items()],
                        "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
shutil.rmtree(tmp)
print(f"pkg={PKG} tsdk={tsdk} backup={backup} cleartext={cleartext} policy={pol} oracle={shown}")
