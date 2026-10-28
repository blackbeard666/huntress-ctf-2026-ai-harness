#!/bin/sh
# usage: oracle.sh <fixture.apk>  -- independent reader: `aapt dump xmltree` lists the manifest components; a component is
# exported when exported=true, or it has an intent-filter, no exported attr and targetSdk < 31; one guarded by a
# permission declared protectionLevel signature (0x2/0x3) is not reachable by other apps. dex2jar turns classes.dex back
# into JVM classes and every exported component's entry methods are RUN on the JVM (android.* stubs); the dependency
# flaws they hit (Trace.LOG) are printed. Never touches lib.android.
set -e
apk=$(realpath "$1"); here=$(dirname "$(realpath "$0")"); root=$(realpath "$here/../../../..")
t=$(mktemp -d "${TMPDIR:-/tmp}/erxo.XXXX"); cd "$t"
aapt dump xmltree "$apk" AndroidManifest.xml > man.txt
python3 -I - man.txt > comps.txt <<'P'
import re, sys
lines = open(sys.argv[1]).read().splitlines()
pkg = next(re.search(r'"(.*?)"', l).group(1) for l in lines if l.strip().startswith("A: package="))
tsdk = next((int(l.split(")")[-1], 16) for l in lines if "targetSdkVersion" in l), 0)
sig = {re.search(r'name\(0x01010003\)="(.*?)"', lines[i - 1]).group(1) for i, l in enumerate(lines)
       if "protectionLevel" in l and int(l.split(")")[-1], 16) & 0xF in (2, 3)}
comps, cur = [], None
for l in lines:
    m = re.match(r"(\s*)E: (\S+)", l)
    if m:
        if m.group(2) in ("activity", "service", "receiver", "provider"):
            cur = {"ind": len(m.group(1)), "name": None, "exp": None, "perm": None, "filt": False}
            comps.append(cur)
        elif cur and len(m.group(1)) <= cur["ind"]:
            cur = None
        elif cur and m.group(2) == "intent-filter":
            cur["filt"] = True
        continue
    if cur is None:
        continue
    a = re.match(r'\s*A: android:(\w+)\(0x[0-9a-f]+\)=(?:"(.*?)"|\(type 0x\w+\)(0x[0-9a-f]+))', l)
    if a and a.group(1) == "name" and len(l) - len(l.lstrip()) == cur["ind"] + 2:
        cur["name"] = a.group(2)
    elif a and a.group(1) == "exported":
        cur["exp"] = int(a.group(3), 16) != 0
    elif a and a.group(1) == "permission":
        cur["perm"] = a.group(2)
for c in comps:
    exp = c["exp"] if c["exp"] is not None else (c["filt"] and tsdk < 31)
    if exp and c["perm"] not in sig:
        n = c["name"]
        print(pkg + n if n.startswith(".") else n if "." in n else pkg + "." + n)
P
echo "exported: $(tr '\n' ' ' < comps.txt)" >&2
"$root/tools/dex2jar/d2j-dex2jar.sh" -f -o app.jar "$apk" >/dev/null 2>&1
mkdir -p stub/android/os stub/android/content stub/android/app
cat > stub/android/os/Bundle.java <<'J'
package android.os; public class Bundle {}
J
cat > stub/android/os/IBinder.java <<'J'
package android.os; public interface IBinder {}
J
cat > stub/android/os/Handler.java <<'J'
package android.os; public class Handler { public boolean post(Runnable r) { r.run(); return true; } }
J
cat > stub/android/content/Intent.java <<'J'
package android.content; public class Intent {}
J
cat > stub/android/content/Context.java <<'J'
package android.content; public class Context {}
J
cat > stub/android/content/BroadcastReceiver.java <<'J'
package android.content; public abstract class BroadcastReceiver { public abstract void onReceive(Context c, Intent i); }
J
cat > stub/android/app/Activity.java <<'J'
package android.app; public class Activity extends android.content.Context { protected void onCreate(android.os.Bundle b) {} protected void onNewIntent(android.content.Intent i) {} }
J
cat > stub/android/app/Service.java <<'J'
package android.app; public abstract class Service extends android.content.Context { public int onStartCommand(android.content.Intent i, int f, int id) { return 0; } public abstract android.os.IBinder onBind(android.content.Intent i); }
J
cat > Run.java <<'J'
import java.lang.reflect.*; import java.nio.file.*;
public class Run { public static void main(String[] a) throws Exception {
  java.util.Set<String> entry = new java.util.HashSet<>(java.util.Arrays.asList("onCreate", "onNewIntent", "onStartCommand",
      "onBind", "onReceive", "query", "insert", "openFile", "call", "handleMessage"));
  for (String cn : Files.readAllLines(Paths.get("comps.txt"))) {
    Class<?> c = Class.forName(cn); Object o = c.getDeclaredConstructor().newInstance();
    for (Method m : c.getDeclaredMethods()) if (entry.contains(m.getName())) {
      m.setAccessible(true); Object[] args = new Object[m.getParameterCount()];
      for (int i = 0; i < args.length; i++) if (m.getParameterTypes()[i] == int.class) args[i] = 0;
      m.invoke(o, args); } }
  Class<?> tr = Class.forName(Files.readAllLines(Paths.get("pkg.txt")).get(0) + ".Trace");
  System.out.println("flaws hit -> " + tr.getField("LOG").get(null)); } }
J
grep -m1 'A: package=' man.txt | sed 's/.*package="\([^"]*\)".*/\1/' > pkg.txt
javac -d stubc $(find stub -name '*.java') && javac -cp app.jar:stubc Run.java && java -cp app.jar:stubc:. Run
cd /; rm -rf "$t"
