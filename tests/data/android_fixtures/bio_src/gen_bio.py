#!/usr/bin/env python3
"""Generate the bio_* fixtures (coverage atlas row 92: MASVS-AUTH biometric / local-auth callback holds the secret).
usage: gen_bio.py <variant: crypto_androidx | event_framework | keyguard_result | decoy_nearmiss> <out.apk>
App classes + framework stubs (androidx.biometric.BiometricPrompt / android.hardware.biometrics.BiometricPrompt with their
AuthenticationCallback / AuthenticationResult / CryptoObject, KeyGenParameterSpec.Builder, KeyguardManager, Activity,
TextView, SharedPreferences backed by a static map, Log) are compiled with javac --release 8; app classes only ->
d2j-jar2dex. The manifest is compiled to binary AXML by apktool's bundled aapt2 link.
 crypto_androidx: VaultCallback extends androidx BiometricPrompt.AuthenticationCallback; onAuthenticationSucceeded:
                  null CryptoObject -> Log "event-only" and return; else getCipher().doFinal(ENC) xor KEY -> SharedPreferences
                  "token". onAuthenticationFailed logs a xor-encoded TRAP token (demoted).
 event_framework: AuthCb extends android.hardware.biometrics BiometricPrompt.AuthenticationCallback; onAuthenticationSucceeded
                  ignores the CryptoObject (event-bound) and Logs the decoded token; KeyVault builds a KeyGenParameterSpec
                  with setUserAuthenticationRequired(false) and no setInvalidatedByBiometricEnrollment.
 keyguard_result: MainActivity.onCreate KeyguardManager.createConfirmDeviceCredentialIntent + startActivityForResult(i, 42);
                  onActivityResult(42, RESULT_OK) setText(decoded token), any other result -> "cancelled".
 decoy_nearmiss:  crypto_androidx whose token and trap are 15-hex near misses.
The oracle (Probe, not shipped) runs on the host JVM: it calls the callbacks with an AuthenticationResult whose
CryptoObject is null and with one wrapping an identity Cipher (a javax.crypto.Cipher over a CipherSpi whose doFinal returns
its input), calls onAuthenticationFailed, and calls onActivityResult(42, -1, null); it prints each labelled value."""
import os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

variant, out = sys.argv[1], Path(sys.argv[2]).resolve()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOKENS = {"crypto_androidx": ("ANS-5d0e8b37a1c4f962", "ANS-0f1e2d3c4b5a6978"),
          "event_framework": ("ANS-b7c41e09d2a5f368", None),
          "keyguard_result": ("ANS-e2961fd0c4b8a753", None),
          "decoy_nearmiss": ("ANS-5d0e8b37a1c4f96", "ANS-0f1e2d3c4b5a697")}
PKG = "com.huntress.mobile.d25.bioauth"
BP = """package %s;
public class BiometricPrompt {
  public static class CryptoObject { final javax.crypto.Cipher c;
    public CryptoObject(javax.crypto.Cipher c) { this.c = c; } public javax.crypto.Cipher getCipher() { return c; } }
  public static class AuthenticationResult { final CryptoObject co;
    public AuthenticationResult(CryptoObject co) { this.co = co; } public CryptoObject getCryptoObject() { return co; } }
  public static abstract class AuthenticationCallback {
    public void onAuthenticationError(int code, CharSequence msg) { }
    public void onAuthenticationSucceeded(AuthenticationResult r) { }
    public void onAuthenticationFailed() { } }
}"""
STUBS = {
    "androidx/biometric/BiometricPrompt.java": BP % "androidx.biometric",
    "android/hardware/biometrics/BiometricPrompt.java": BP % "android.hardware.biometrics",
    "android/content/Context.java": """package android.content;
public class Context {
  public SharedPreferences getSharedPreferences(String n, int mode) { return new SharedPreferences(); }
  public Object getSystemService(String n) { return new android.app.KeyguardManager(); }
}""",
    "android/content/Intent.java": "package android.content;\npublic class Intent { }",
    "android/content/SharedPreferences.java": """package android.content;
public class SharedPreferences {
  public static final java.util.HashMap<String, String> STORE = new java.util.HashMap<String, String>();
  public Editor edit() { return new Editor(); }
  public static class Editor { public Editor putString(String k, String v) { STORE.put(k, v); return this; }
    public void apply() { } }
}""",
    "android/util/Log.java": """package android.util;
public final class Log { public static String LAST; public static int d(String t, String m) { LAST = m; return 0; } }""",
    "android/app/Activity.java": """package android.app;
public class Activity extends android.content.Context {
  public static final int RESULT_OK = -1;
  protected void onCreate(android.os.Bundle b) { }
  public void startActivityForResult(android.content.Intent i, int rq) { }
  protected void onActivityResult(int rq, int rc, android.content.Intent d) { }
  public android.view.View findViewById(int id) { return new android.widget.TextView(); }
}""",
    "android/app/KeyguardManager.java": """package android.app;
public class KeyguardManager { public android.content.Intent createConfirmDeviceCredentialIntent(CharSequence t, CharSequence d) {
  return new android.content.Intent(); } }""",
    "android/view/View.java": "package android.view;\npublic class View { }",
    "android/widget/TextView.java": """package android.widget;
public class TextView extends android.view.View { public static CharSequence LAST; public void setText(CharSequence s) { LAST = s; } }""",
    "android/os/Bundle.java": "package android.os;\npublic class Bundle { }",
    "android/security/keystore/KeyGenParameterSpec.java": """package android.security.keystore;
public class KeyGenParameterSpec { public static class Builder {
  public Builder(String alias, int purposes) { }
  public Builder setBlockModes(String... m) { return this; }
  public Builder setUserAuthenticationRequired(boolean b) { return this; }
  public Builder setInvalidatedByBiometricEnrollment(boolean b) { return this; }
  public KeyGenParameterSpec build() { return new KeyGenParameterSpec(); } } }""",
}
DEC = """  static String dec(byte[] e, int k) {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < e.length; i++) sb.append((char) ((e[i] ^ (k + i)) & 0xFF));
    return sb.toString();
  }"""
CRYPTO = """package %(pkg)s;
import androidx.biometric.BiometricPrompt;
public class VaultCallback extends BiometricPrompt.AuthenticationCallback {
  static final byte[] ENC = {%(enc)s};
  static final byte[] TRAP = {%(trap)s};
  final android.content.Context ctx = new android.content.Context();
%(dec)s
  @Override public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result) {
    BiometricPrompt.CryptoObject co = result.getCryptoObject();
    if (co == null || co.getCipher() == null) { android.util.Log.d("bio", "event-only"); return; }
    try {
      byte[] p = co.getCipher().doFinal(ENC);
      ctx.getSharedPreferences("vault", 0).edit().putString("token", dec(p, 0x29)).apply();
    } catch (Exception e) { android.util.Log.d("bio", "bad"); }
  }
  @Override public void onAuthenticationFailed() { android.util.Log.d("bio", dec(TRAP, 0x29)); }
  public static android.security.keystore.KeyGenParameterSpec spec() {
    return new android.security.keystore.KeyGenParameterSpec.Builder("vault", 3).setUserAuthenticationRequired(true)
        .setInvalidatedByBiometricEnrollment(true).build();
  }
}"""
EVENT = """package %(pkg)s;
import android.hardware.biometrics.BiometricPrompt;
public class AuthCb extends BiometricPrompt.AuthenticationCallback {
  static final byte[] ENC = {%(enc)s};
%(dec)s
  @Override public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result) {
    android.util.Log.d("bio", dec(ENC, 0x29));
  }
  @Override public void onAuthenticationError(int code, CharSequence msg) { android.util.Log.d("bio", "error " + code); }
}"""
KEYVAULT = """package %(pkg)s;
public class KeyVault {
  public static android.security.keystore.KeyGenParameterSpec spec() {
    return new android.security.keystore.KeyGenParameterSpec.Builder("vault", 3).setBlockModes("CBC")
        .setUserAuthenticationRequired(false).build();
  }
}"""
KEYGUARD = """package %(pkg)s;
public class MainActivity extends android.app.Activity {
  static final byte[] ENC = {%(enc)s};
%(dec)s
  @Override protected void onCreate(android.os.Bundle b) {
    super.onCreate(b);
    android.app.KeyguardManager km = (android.app.KeyguardManager) getSystemService("keyguard");
    startActivityForResult(km.createConfirmDeviceCredentialIntent("Unlock", "Confirm it's you"), 42);
  }
  @Override protected void onActivityResult(int rq, int rc, android.content.Intent d) {
    android.widget.TextView tv = (android.widget.TextView) findViewById(0x7f010001);
    if (rq == 42 && rc == RESULT_OK) tv.setText(dec(ENC, 0x29)); else tv.setText("cancelled");
  }
}"""
IDC = """  static javax.crypto.Cipher identity() throws Exception {
    javax.crypto.CipherSpi spi = new javax.crypto.CipherSpi() {
      protected void engineSetMode(String m) { } protected void engineSetPadding(String p) { }
      protected int engineGetBlockSize() { return 0; } protected int engineGetOutputSize(int n) { return n; }
      protected byte[] engineGetIV() { return null; } protected java.security.AlgorithmParameters engineGetParameters() { return null; }
      protected void engineInit(int o, java.security.Key k, java.security.SecureRandom r) { }
      protected void engineInit(int o, java.security.Key k, java.security.spec.AlgorithmParameterSpec s, java.security.SecureRandom r) { }
      protected void engineInit(int o, java.security.Key k, java.security.AlgorithmParameters s, java.security.SecureRandom r) { }
      protected byte[] engineUpdate(byte[] b, int o, int n) { return java.util.Arrays.copyOfRange(b, o, o + n); }
      protected int engineUpdate(byte[] b, int o, int n, byte[] out, int oo) { System.arraycopy(b, o, out, oo, n); return n; }
      protected byte[] engineDoFinal(byte[] b, int o, int n) { return java.util.Arrays.copyOfRange(b, o, o + n); }
      protected int engineDoFinal(byte[] b, int o, int n, byte[] out, int oo) { System.arraycopy(b, o, out, oo, n); return n; }
    };
    javax.crypto.Cipher c = new javax.crypto.Cipher(spi, new java.security.Provider("Identity", 1.0, "identity cipher") { }, "Identity") { };
    c.init(javax.crypto.Cipher.DECRYPT_MODE, new javax.crypto.spec.SecretKeySpec(new byte[16], "AES"));
    return c;
  }"""
PROBE_CRYPTO = """package %(pkg)s;
import androidx.biometric.BiometricPrompt;
public final class Probe {
%(idc)s
  public static void main(String[] a) throws Exception {
    VaultCallback cb = new VaultCallback();
    cb.onAuthenticationSucceeded(new BiometricPrompt.AuthenticationResult(null));
    System.out.println("crypto_null=" + android.content.SharedPreferences.STORE.get("token") + " log=" + android.util.Log.LAST);
    cb.onAuthenticationSucceeded(new BiometricPrompt.AuthenticationResult(new BiometricPrompt.CryptoObject(identity())));
    System.out.println("crypto_stub=" + android.content.SharedPreferences.STORE.get("token"));
    cb.onAuthenticationFailed();
    System.out.println("failed=" + android.util.Log.LAST);
  } }"""
PROBE_EVENT = """package %(pkg)s;
import android.hardware.biometrics.BiometricPrompt;
public final class Probe {
  public static void main(String[] a) throws Exception {
    new AuthCb().onAuthenticationSucceeded(new BiometricPrompt.AuthenticationResult(null));
    System.out.println("crypto_null=" + android.util.Log.LAST);
  } }"""
PROBE_KG = """package %(pkg)s;
public final class Probe {
  public static void main(String[] a) throws Exception {
    MainActivity m = new MainActivity();
    m.onActivityResult(42, -1, null);
    System.out.println("result_ok=" + android.widget.TextView.LAST);
    m.onActivityResult(42, 0, null);
    System.out.println("result_canceled=" + android.widget.TextView.LAST);
  } }"""
MAN = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="%(pkg)s">
  <uses-permission android:name="android.permission.USE_BIOMETRIC"/>
  <application android:label="Vault"><activity android:name=".MainActivity" android:exported="true">
    <intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
  </activity></application>
</manifest>"""
pdir = PKG.replace(".", "/")
tok, trap = TOKENS[variant]
enc_of = lambda s: ", ".join(str(((b ^ (0x29 + i)) & 0xFF) - 256 if ((b ^ (0x29 + i)) & 0xFF) > 127 else (b ^ (0x29 + i)) & 0xFF)
                             for i, b in enumerate(s.encode()))
if variant in ("crypto_androidx", "decoy_nearmiss"):
    files = {f"{pdir}/VaultCallback.java": CRYPTO, f"{pdir}/Probe.java": PROBE_CRYPTO}
elif variant == "event_framework":
    files = {f"{pdir}/AuthCb.java": EVENT, f"{pdir}/KeyVault.java": KEYVAULT, f"{pdir}/Probe.java": PROBE_EVENT}
else:
    files = {f"{pdir}/MainActivity.java": KEYGUARD, f"{pdir}/Probe.java": PROBE_KG}
subst = {"pkg": PKG, "enc": enc_of(tok), "trap": enc_of(trap) if trap else "", "dec": DEC, "idc": IDC}
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
src, cls = tmp / "src", tmp / "cls"
files.update(STUBS)
for rel, b in files.items():
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(b % subst if "%(" in b else b)
cls.mkdir()
subprocess.run(["javac", "--release", "8", "-d", str(cls), *map(str, src.rglob("*.java"))], check=True)
pr = subprocess.run(["java", "-cp", str(cls), f"{PKG}.Probe"], capture_output=True, text=True)
if pr.returncode:
    sys.exit(pr.stderr)
shown = pr.stdout.strip()
for junk in ("android", "androidx", *(p.relative_to(cls) for p in (cls / pdir).glob("Probe*.class"))):
    p = cls / junk
    shutil.rmtree(p) if p.is_dir() else p.unlink()
shutil.make_archive(str(tmp / "app"), "zip", cls)
subprocess.run([str(ROOT / "tools/dex2jar/d2j-jar2dex.sh"), "-f", "-o", str(tmp / "classes.dex"), str(tmp / "app.zip")],
               check=True, capture_output=True)
subprocess.run(["unzip", "-o", "-q", "-j", "/usr/local/bin/apktool.jar", "prebuilt/linux/aapt2", "prebuilt/android-framework.jar", "-d", str(tmp)], check=True)
(tmp / "AndroidManifest.xml").write_text(MAN % {"pkg": PKG})
(tmp / "aapt2").chmod(0o755)
subprocess.run([str(tmp / "aapt2"), "link", "--manifest", str(tmp / "AndroidManifest.xml"), "-I", str(tmp / "android-framework.jar"),
                "-o", str(tmp / "base.apk")], check=True)
with zipfile.ZipFile(tmp / "base.apk") as zin:
    manifest = zin.read("AndroidManifest.xml")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("AndroidManifest.xml", manifest)
    z.writestr("classes.dex", (tmp / "classes.dex").read_bytes())
shutil.rmtree(tmp)
print(f"host-JVM oracle: {shown}")
