#!/usr/bin/env python3
"""Generate the binder_* fixtures (coverage atlas: bound Service / AIDL / Messenger transaction code -> reply value).
usage: gen_binder.py <variant: aidl_stub | messenger | decoy_nearmiss> <out.apk>
The app (an exported bound service whose AIDL `IVault$Stub extends Binder` overrides onTransact, or whose Messenger
Handler switches on msg.what) and android.os.* framework stubs (a working Parcel queue, Message / Bundle / Messenger)
are compiled with javac --release 8. The token sits xor'd in a byte[] the transaction decodes only when the request
carries the interface descriptor + the right string / int arguments. The oracle (Probe, not shipped) is a CLIENT run by
the host JVM: it marshals the request exactly as a real caller would (writeInterfaceToken, writeInt, writeString /
Bundle putString + replyTo) and prints what the service writes back. App classes only -> d2j-jar2dex -> zipfile.
decoy_nearmiss: the aidl_stub layout whose secret transaction replies with a 15-hex near miss."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"aidl_stub": "ANS-5d0b7e29c4a1f863", "messenger": "ANS-b83f06d2e9a1c475", "decoy_nearmiss": "ANS-0e7c91a4d26b3f5"}
PKG = "com.huntress.mobile.d23.ipc"
KEY = 0x5A
STUBS = {
    "android/os/IInterface.java": "package android.os;\npublic interface IInterface { IBinder asBinder(); }",
    "android/os/IBinder.java": """package android.os;
public interface IBinder {
  int FIRST_CALL_TRANSACTION = 1, INTERFACE_TRANSACTION = 0x5F4E5446, FLAG_ONEWAY = 1;
}""",
    "android/os/RemoteException.java": "package android.os;\npublic class RemoteException extends Exception { }",
    "android/os/Binder.java": """package android.os;
public class Binder implements IBinder {
  public void attachInterface(IInterface o, String d) { }
  public static int getCallingUid() { return 10123; }
  protected boolean onTransact(int code, Parcel data, Parcel reply, int flags) throws RemoteException { return false; }
}""",
    "android/os/Parcel.java": """package android.os;
public final class Parcel {
  public final java.util.ArrayList<Object> q = new java.util.ArrayList<Object>(); int rd = 0;
  public static Parcel obtain() { return new Parcel(); }
  public void writeInterfaceToken(String d) { q.add(d); }
  public void enforceInterface(String d) { if (!d.equals(q.get(rd++))) throw new SecurityException("Binder invocation to an incorrect interface"); }
  public void writeNoException() { q.add(0); }
  public void writeString(String s) { q.add(s); }
  public void writeInt(int v) { q.add(v); }
  public String readString() { return (String) q.get(rd++); }
  public int readInt() { return (Integer) q.get(rd++); }
  public void recycle() { }
}""",
    "android/os/Bundle.java": """package android.os;
public class Bundle {
  public final java.util.TreeMap<String, Object> m = new java.util.TreeMap<String, Object>();
  public void putString(String k, String v) { m.put(k, v); }
  public String getString(String k) { return (String) m.get(k); }
  public void putInt(String k, int v) { m.put(k, v); }
  public int getInt(String k) { Object o = m.get(k); return o == null ? 0 : (Integer) o; }
}""",
    "android/os/Message.java": """package android.os;
public final class Message {
  public int what, arg1, arg2; public Object obj; public Messenger replyTo; Bundle data;
  public static Message obtain() { return new Message(); }
  public static Message obtain(Handler h, int what) { Message m = new Message(); m.what = what; return m; }
  public static Message obtain(Handler h, int what, Object obj) { Message m = obtain(h, what); m.obj = obj; return m; }
  public Bundle getData() { if (data == null) data = new Bundle(); return data; }
  public Bundle peekData() { return data; }
  public void setData(Bundle b) { data = b; }
}""",
    "android/os/Handler.java": """package android.os;
public class Handler {
  public Handler() { }
  public void handleMessage(Message msg) { }
}""",
    "android/os/Messenger.java": """package android.os;
public final class Messenger {
  public Handler target; public Message got;
  public Messenger(Handler h) { target = h; }
  public void send(Message m) throws RemoteException { got = m; if (target != null) target.handleMessage(m); }
  public IBinder getBinder() { return null; }
}""",
    "android/content/Intent.java": "package android.content;\npublic class Intent { }",
    "android/app/Service.java": """package android.app;
public abstract class Service { public abstract android.os.IBinder onBind(android.content.Intent i); }""",
}
AIDL = """package %(pkg)s;
public interface IVault extends android.os.IInterface {
  String ping() throws android.os.RemoteException;
  String getSecret(int version, String pass) throws android.os.RemoteException;
  public static abstract class Stub extends android.os.Binder implements IVault {
    private static final String DESCRIPTOR = "com.huntress.mobile.d23.ipc.IVault";
    static final int TRANSACTION_ping = android.os.IBinder.FIRST_CALL_TRANSACTION + 0;
    static final int TRANSACTION_rotate = android.os.IBinder.FIRST_CALL_TRANSACTION + 1;
    static final int TRANSACTION_getSecret = android.os.IBinder.FIRST_CALL_TRANSACTION + 6;
    public Stub() { this.attachInterface(this, DESCRIPTOR); }
    public android.os.IBinder asBinder() { return this; }
    @Override public boolean onTransact(int code, android.os.Parcel data, android.os.Parcel reply, int flags)
        throws android.os.RemoteException {
      switch (code) {
        case INTERFACE_TRANSACTION: reply.writeString(DESCRIPTOR); return true;
        case TRANSACTION_ping: {
          data.enforceInterface(DESCRIPTOR);
          String r = this.ping();
          reply.writeNoException(); reply.writeString(r); return true;
        }
        case TRANSACTION_rotate: {
          data.enforceInterface(DESCRIPTOR);
          reply.writeNoException(); reply.writeString("rotated-" + data.readInt()); return true;
        }
        case TRANSACTION_getSecret: {
          data.enforceInterface(DESCRIPTOR);
          int ver = data.readInt();
          String pass = data.readString();
          String r = this.getSecret(ver, pass);
          reply.writeNoException(); reply.writeString(r); return true;
        }
      }
      return super.onTransact(code, data, reply, flags);
    }
  }
}"""
VAULT_SVC = """package %(pkg)s;
public class VaultService extends android.app.Service {
  static final byte[] ENC = {%(enc)s};
  static String open(int k) {
    char[] c = new char[ENC.length];
    for (int i = 0; i < ENC.length; i++) c[i] = (char) ((ENC[i] ^ k) & 0xFF);
    return new String(c);
  }
  public static final class Impl extends IVault.Stub {
    public String ping() { return "pong"; }
    public String getSecret(int version, String pass) {
      if (version != 5) return "upgrade-client";
      if (!"hunter2-vault".equals(pass)) return "denied";
      return open(version * 17 + 0x1D);
    }
  }
  public android.os.IBinder onBind(android.content.Intent i) { return new Impl(); }
}"""
MSG_SVC = """package %(pkg)s;
public class VaultService extends android.app.Service {
  static final int MSG_HELLO = 0x10, MSG_STATUS = 0x200, MSG_REVEAL = 0x7001, MSG_REVEAL_REPLY = 0x7002;
  static final byte[] ENC = {%(enc)s};
  static final class IncomingHandler extends android.os.Handler {
    @Override public void handleMessage(android.os.Message msg) {
      android.os.Message r;
      switch (msg.what) {
        case MSG_HELLO: r = android.os.Message.obtain(null, MSG_HELLO, "hello-back"); break;
        case MSG_STATUS: r = android.os.Message.obtain(null, MSG_STATUS, "status:idle"); break;
        case MSG_REVEAL: {
          android.os.Bundle in = msg.getData();
          String pin = in.getString("pin");
          if (pin == null || !pin.equals("4729")) { r = android.os.Message.obtain(null, MSG_REVEAL_REPLY, "bad-pin"); break; }
          StringBuilder sb = new StringBuilder();
          for (int i = 0; i < ENC.length; i++) sb.append((char) ((ENC[i] ^ (%(key)d + i)) & 0xFF));
          android.os.Bundle out = new android.os.Bundle();
          out.putString("token", sb.toString());
          r = android.os.Message.obtain(null, MSG_REVEAL_REPLY);
          r.setData(out);
          break;
        }
        default: return;
      }
      try { if (msg.replyTo != null) msg.replyTo.send(r); } catch (android.os.RemoteException e) { }
    }
  }
  final android.os.Messenger messenger = new android.os.Messenger(new IncomingHandler());
  public android.os.IBinder onBind(android.content.Intent i) { return messenger.getBinder(); }
}"""
PROBE_AIDL = """package %(pkg)s;
public final class Probe { public static void main(String[] a) throws Exception {
  android.os.Parcel data = android.os.Parcel.obtain(), reply = android.os.Parcel.obtain();
  data.writeInterfaceToken("com.huntress.mobile.d23.ipc.IVault"); data.writeInt(5); data.writeString("hunter2-vault");
  new VaultService.Impl().onTransact(7, data, reply, 0);
  System.out.println(reply.q.get(1));
} }"""
PROBE_MSG = """package %(pkg)s;
public final class Probe { public static void main(String[] a) throws Exception {
  final android.os.Messenger back = new android.os.Messenger(null);
  android.os.Message m = android.os.Message.obtain(null, 0x7001);
  m.getData().putString("pin", "4729"); m.replyTo = back;
  new VaultService().messenger.send(m);
  System.out.println(back.got.getData().getString("token"));
} }"""

pdir = PKG.replace(".", "/")
plain = TOKENS[variant].encode()
if variant == "messenger":
    enc = [((b ^ (KEY + i)) & 0xFF) for i, b in enumerate(plain)]
    files = {f"{pdir}/VaultService.java": MSG_SVC, f"{pdir}/Probe.java": PROBE_MSG}
else:
    k = (5 * 17 + 0x1D) & 0xFF
    enc = [b ^ k for b in plain]
    files = {f"{pdir}/IVault.java": AIDL, f"{pdir}/VaultService.java": VAULT_SVC, f"{pdir}/Probe.java": PROBE_AIDL}
enc = [e - 256 if e > 127 else e for e in enc]
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
files.update(STUBS)
for rel, b in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(b % {"pkg": PKG, "enc": ", ".join(map(str, enc)), "key": KEY} if "%(" in b else b)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
shown = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], check=True, capture_output=True, text=True).stdout.strip()
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
print(f"client-JVM reply={shown!r}")
