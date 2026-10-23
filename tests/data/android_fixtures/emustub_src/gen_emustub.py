#!/usr/bin/env python3
"""Generate the emustub_* fixtures (coverage atlas row 48: emulator detection beyond Build fields -- telephony, sensors,
battery, qemu pipes, /proc/cpuinfo -- whose RESULTS key the answer, so only a retail-phone evaluation recovers it).
usage: gen_emustub.py <variant: tele_sensor | battery_qemu | decoy_emulator> <out.apk>
Java app + android.* framework stubs are compiled with javac; the stubs model a retail phone on T-Mobile (IMEI-shaped
device id, PHONE_TYPE_GSM, SIM_STATE_READY, 24 vendor sensors, battery 63 % / 28.5 C / unplugged); java.io.File is the
host JVM's own (no /dev/qemu_pipe, /dev/goldfish_pipe ... on the host). /proc/cpuinfo is read through Guard.CPU, which
the oracle harness (Probe, not shipped) points at a retail arm64 cpuinfo, since the build host's own one says
'hypervisor'. Stage 1 runs Guard.key() on the JVM, the token is xor'd with that key here, stage 2 recompiles Vault and
the JVM prints Vault.reveal() (the oracle). App classes only -> d2j-jar2dex -> zipfile.
decoy_emulator: tele_sensor bytes keyed for the EMULATOR stubs (Android / 15555215554 / Goldfish sensors), so the
retail path yields garbage."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"tele_sensor": "ANS-7c3e91a0d54b28f6", "battery_qemu": "key=ANS-e2049b7f1c6da385",
          "decoy_emulator": "ANS-91f6c2e7b0a4d358"}
PKG = "com.huntress.mobile.d22.emuq"
RETAIL = dict(dev="352099001761481", sub="310260417291538", line="+12065550147", op="T-Mobile", ptype=1, sim=5,
              nsens=24, vendor="STMicro", level=63, temp=285, plugged=0, status=3, charging="false")
EMU = dict(dev="000000000000000", sub="310260000000000", line="15555215554", op="Android", ptype=1, sim=5,
           nsens=6, vendor="The Android Open Source Project", level=100, temp=0, plugged=1, status=2, charging="true")
STUBS = {
    "android/content/Context.java": """package android.content;
public class Context {
  public static final String TELEPHONY_SERVICE = "phone", SENSOR_SERVICE = "sensor", BATTERY_SERVICE = "batterymanager";
  public Object getSystemService(String n) {
    if (n.equals("phone")) return new android.telephony.TelephonyManager();
    if (n.equals("sensor")) return new android.hardware.SensorManager();
    if (n.equals("batterymanager")) return new android.os.BatteryManager();
    return null;
  }
  public Intent registerReceiver(BroadcastReceiver r, IntentFilter f) { return new Intent(); }
}""",
    "android/content/BroadcastReceiver.java": "package android.content;\npublic abstract class BroadcastReceiver { }",
    "android/content/IntentFilter.java": "package android.content;\npublic class IntentFilter { public IntentFilter(String a) { } }",
    "android/content/Intent.java": """package android.content;
public class Intent {
  public static final String ACTION_BATTERY_CHANGED = "android.intent.action.BATTERY_CHANGED";
  public int getIntExtra(String k, int d) {
    if (k.equals("level")) return %(level)d; if (k.equals("scale")) return 100; if (k.equals("temperature")) return %(temp)d;
    if (k.equals("plugged")) return %(plugged)d; if (k.equals("status")) return %(status)d; return d;
  }
}""",
    "android/app/Activity.java": "package android.app;\npublic class Activity extends android.content.Context { }",
    "android/telephony/TelephonyManager.java": """package android.telephony;
public class TelephonyManager {
  public static final int PHONE_TYPE_GSM = 1, SIM_STATE_READY = 5;
  public String getDeviceId() { return "%(dev)s"; }
  public String getImei() { return "%(dev)s"; }
  public String getSubscriberId() { return "%(sub)s"; }
  public String getLine1Number() { return "%(line)s"; }
  public String getNetworkOperatorName() { return "%(op)s"; }
  public String getSimOperatorName() { return "%(op)s"; }
  public int getPhoneType() { return %(ptype)d; }
  public int getSimState() { return %(sim)d; }
}""",
    "android/hardware/Sensor.java": """package android.hardware;
public class Sensor {
  public static final int TYPE_ALL = -1, TYPE_ACCELEROMETER = 1, TYPE_GYROSCOPE = 4;
  String v; public Sensor(String v) { this.v = v; }
  public String getVendor() { return v; }
  public String getName() { return v + " sensor"; }
}""",
    "android/hardware/SensorManager.java": """package android.hardware;
public class SensorManager {
  public java.util.List<Sensor> getSensorList(int t) {
    java.util.List<Sensor> l = new java.util.ArrayList<Sensor>();
    for (int i = 0; i < %(nsens)d; i++) l.add(new Sensor("%(vendor)s"));
    return l;
  }
  public Sensor getDefaultSensor(int t) { return new Sensor("%(vendor)s"); }
}""",
    "android/os/BatteryManager.java": """package android.os;
public class BatteryManager {
  public static final int BATTERY_PROPERTY_CAPACITY = 4;
  public int getIntProperty(int p) { return p == 4 ? %(level)d : Integer.MIN_VALUE; }
  public boolean isCharging() { return %(charging)s; }
}""",
}
GUARD = {
    "tele_sensor": """package %(pkg)s;
import java.util.List;
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorManager;
import android.telephony.TelephonyManager;
public final class Guard {
  public static int key(Context c) {
    TelephonyManager tm = (TelephonyManager) c.getSystemService(Context.TELEPHONY_SERVICE);
    int s = 0x3C1;
    String id = tm.getDeviceId();
    s = s * 31 + (id == null || id.startsWith("000000") ? 3 : id.length());
    s = s * 31 + tm.getImei().hashCode();
    s = s * 31 + (tm.getSubscriberId().equals("310260000000000") ? 7 : tm.getSubscriberId().length());
    s = s * 31 + (tm.getLine1Number().startsWith("155552155") ? 11 : 13);
    s ^= tm.getNetworkOperatorName().hashCode();
    s = s * 31 + (tm.getSimOperatorName().equalsIgnoreCase("android") ? 17 : 19);
    s = s * 31 + tm.getPhoneType() * 3 + tm.getSimState();
    SensorManager sm = (SensorManager) c.getSystemService(Context.SENSOR_SERVICE);
    List<Sensor> all = sm.getSensorList(Sensor.TYPE_ALL);
    s = s * 31 + (all.size() >= 20 ? 23 : 29);
    for (Sensor x : all) if (x.getVendor().contains("Goldfish") || x.getVendor().contains("AOSP")
        || x.getName().contains("Goldfish")) { s = ~s; break; }
    s = s * 31 + (sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER) == null ? 31 : 37);
    return s;
  }
}""",
    "battery_qemu": """package %(pkg)s;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.BatteryManager;
public class Guard extends Activity {
  static String CPU = "/proc/cpuinfo";
  static final String[] PIPES = {"/dev/qemu_pipe", "/dev/socket/qemud", "/system/lib/libc_malloc_debug_qemu.so",
      "/sys/qemu_trace", "/dev/goldfish_pipe", "/system/bin/qemu-props"};
  static boolean cpuEmu() {
    try {
      BufferedReader r = new BufferedReader(new FileReader(CPU));
      String l;
      boolean e = false;
      while ((l = r.readLine()) != null) if (l.contains("Goldfish") || l.contains("hypervisor")) e = true;
      r.close();
      return e;
    } catch (Exception x) { return true; }
  }
  public int key() {
    int k = 0x61;
    for (String p : PIPES) k = k * 13 + (new File(p).exists() ? 5 : 9);
    k = k * 13 + (cpuEmu() ? 5 : 9);
    Intent b = registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
    int lvl = b.getIntExtra("level", -1) * 100 / b.getIntExtra("scale", -1);
    k = k * 13 + lvl;
    k = k * 13 + b.getIntExtra("temperature", 0);
    k = k * 13 + (b.getIntExtra("plugged", -1) != 0 ? 5 : 9);
    BatteryManager bm = (BatteryManager) getSystemService(Context.BATTERY_SERVICE);
    k = k * 13 + bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY);
    k = k * 13 + (bm.isCharging() ? 5 : 9);
    return k;
  }
}""",
}
GUARD["decoy_emulator"] = GUARD["tele_sensor"]
VAULT_STATIC = """package %(pkg)s;
public final class Vault {
  static final byte[] ENC = {%(enc)s};
  public static String reveal(android.content.Context ctx) {
    int k = Guard.key(ctx);
    char[] c = new char[ENC.length];
    for (int i = 0; i < c.length; i++) c[i] = (char) ((ENC[i] ^ (k >>> ((i %% 4) * 8)) ^ i) & 0xFF);
    return new String(c);
  }
}"""
VAULT_ACT = """package %(pkg)s;
public final class Vault extends Guard {
  static final byte[] ENC = {%(enc)s};
  public String reveal() {
    int k = key();
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < ENC.length; i++) sb.append((char) ((ENC[i] - i * 3 ^ k >> (i %% 3)) & 0xFF));
    return sb.toString();
  }
}"""
PROBE = """package %(pkg)s;
public final class Probe { public static void main(String[] a) throws Exception {
  java.io.File cpu = java.io.File.createTempFile("cpuinfo", ".txt");
  java.io.FileWriter w = new java.io.FileWriter(cpu);
  w.write("processor\\t: 0\\nBogoMIPS\\t: 49.15\\nFeatures\\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm lrcpc dcpop asimddp\\nCPU implementer\\t: 0x41\\nCPU architecture: 8\\nCPU variant\\t: 0x1\\nCPU part\\t: 0xd05\\nCPU revision\\t: 0\\n");
  w.close();
  %(setcpu)s
  %(body)s
  cpu.delete(); } }"""
act = variant == "battery_qemu"
pdir = PKG.replace(".", "/")


def build(prof, enc, body):
    tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    src, cls = tmp / "src", tmp / "cls"
    files = {k: v % prof if "%(" in v else v for k, v in STUBS.items()}
    files[f"{pdir}/Guard.java"] = GUARD[variant] % {"pkg": PKG}
    files[f"{pdir}/Vault.java"] = (VAULT_ACT if act else VAULT_STATIC) % {"pkg": PKG, "enc": ", ".join(map(str, enc))}
    files[f"{pdir}/Probe.java"] = PROBE % {"pkg": PKG, "body": body, "setcpu": "Guard.CPU = cpu.getPath();" if act else ""}
    for rel, b in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(b)
    cls.mkdir()
    subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
    run = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
    return tmp, cls, run


call = "new Vault().%s()" if act else "Vault.%s(new android.content.Context())"
tmp, _, k = build(EMU if variant == "decoy_emulator" else RETAIL, [],
                  "System.out.println(" + (call % "key" if act else "Guard.key(new android.content.Context())") + ");")
shutil.rmtree(tmp)
k = int(k)
plain = TOKENS[variant].encode()
if act:  # inverse of ((e - 3i) ^ (k >> (i%3))) & 0xFF == p
    enc = [(((p ^ (k >> (i % 3))) & 0xFF) + 3 * i + 128) % 256 - 128 for i, p in enumerate(plain)]
else:
    enc = [((p ^ (k >> ((i % 4) * 8)) ^ i) & 0xFF ^ 0x80) - 0x80 for i, p in enumerate(plain)]
# oracle: the JVM on the RETAIL stubs prints what a real phone shows
tmp, cls, shown = build(RETAIL, enc, "System.out.println(" + call % "reveal" + ");")
for junk in ("android", f"{pdir}/Probe.class"):
    p = cls / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
with zipfile.ZipFile(HERE.parent / "skc_decoy_cbc_wrong_key.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(f"key={k} retail-JVM reveal()={shown!r}")
