#!/usr/bin/env python3
"""dotnet-anti-tamper-obfuscation fixtures (dnprot_*): C# built by `dotnet build` (Roslyn), then byte-level protector
tricks applied by THIS script (stdlib only, never lib.binary):
  dnprot_confuser_antitamper.bin : [module: ConfusedBy("ConfuserEx v1.6.0+447341964f")] + [module: SuppressIldasm],
      2 renamed types (Thai letters via \\u escapes; one #Strings name overwritten with control bytes 01..05), a
      [ModuleInitializer] (Roslyn emits <Module>..cctor -> it) that xors Holder.Cfg with uint 0x5A3C9E17 (LE bytes,
      repeating from index 0); Cfg's FieldRVA data is the HCFG blob already xor'd; Payload.Beacon's IL body bytes are
      xor'd with the same key (an encrypted method body: invalid IL on disk).
  dnprot_dotfuscator_b64.bin : [assembly: Dotfuscator("Dotfuscator Community 6.5.3")] marker, a renamed type, HCFG as
      a base64 ldstr (UTF-16LE in #US), no module initializer.
  dnprot_decoy_plain.bin : plain C# exe, no protector, a xor'd blob but NO key anywhere (must not decode).
  dnprot_decoy_native.bin: /usr/bin/true (no CLI header).
usage: python3 dnprot_gen.py OUTDIR"""
import base64, json, os, pathlib, shutil, struct, subprocess, sys, tempfile, zlib

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
KEY = 0x5A3C9E17
KB = struct.pack("<I", KEY)


def blob(cfg, xk=0x00, ver=1):
    plain = json.dumps(cfg, separators=(",", ":")).encode()
    return b"HCFG" + struct.pack("<BBHI", ver, xk, len(plain), zlib.crc32(plain)) + bytes(c ^ xk for c in plain)


def build(name, src):
    w = pathlib.Path(tempfile.mkdtemp()) / name
    w.mkdir()
    (w / f"{name}.csproj").write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe'
        '</OutputType><Deterministic>true</Deterministic><DebugType>none</DebugType><ImplicitUsings>disable'
        '</ImplicitUsings><Nullable>disable</Nullable><NoWarn>SYSLIB0025;CS0618;CA2255</NoWarn></PropertyGroup></Project>\n')
    (w / "P.cs").write_text(src)
    subprocess.run(["dotnet", "build", "-c", "Release", "-o", "out"], cwd=w, check=True, stdout=subprocess.DEVNULL)
    return bytearray((w / "out" / f"{name}.dll").read_bytes())


def arr(b):
    return ",".join(f"0x{c:02x}" for c in b)


# 1) ConfuserEx-style anti-tamper
B1 = blob({"c2": "tamper.hunt.local:8443", "id": "AT-7731", "sleep": 45}, xk=0x2b)
enc = bytes(c ^ KB[i & 3] for i, c in enumerate(B1))
src1 = r'''using System; using System.Runtime.CompilerServices;
[module: SuppressIldasm]
[module: ConfusedBy("ConfuserEx v1.6.0+447341964f")]
[AttributeUsage(AttributeTargets.All)] internal sealed class ConfusedByAttribute : Attribute { public ConfusedByAttribute(string s) { } }
namespace Hunt {
  internal static class Holder { internal static readonly byte[] Cfg = new byte[] { %s }; }
  internal static class กขฃ {
    [ModuleInitializer] internal static void Init() {
      uint k = 0x5A3C9E17u; byte[] b = Holder.Cfg;
      for (int i = 0; i < b.Length; i++) b[i] ^= (byte)(k >> ((i & 3) << 3));
    }
  }
  internal static class QQRNM { internal static int Tick(int x) { return x * 7 + 3; } }
  internal static class Payload {
    internal static int Beacon(int a, int b) { int s = 0; for (int i = 0; i < a; i++) { s += (i * b) ^ 0x1337; s = (s << 3) | (s >> 29); } return s + QQRNM.Tick(a); }
  }
  internal static class Program { static int Main(string[] a) { return a.Length > 9 ? Payload.Beacon(a.Length, 3) : Holder.Cfg.Length; } }
}
''' % arr(enc)
d1 = build("TamperApp", src1)
i = d1.find(b"QQRNM\0")                       # renamed type: control-byte name, same length, in #Strings
assert i > 0 and d1.find(b"QQRNM\0", i + 1) < 0
d1[i:i + 5] = bytes([1, 2, 3, 4, 5])
# encrypted body: Beacon's fat-header IL; locate it by its unique 0x1337 constant (ldc.i4 37 13 00 00)
j = d1.find(b"\x20\x37\x13\x00\x00")
assert j > 0 and d1.find(b"\x20\x37\x13\x00\x00", j + 1) < 0
hs = max(k for k in range(j - 64, j) if d1[k] & 3 == 3 and d1[k + 1] >> 4 == 3)   # fat header: flags & 3 == 3, size 3
cs = struct.unpack_from("<I", d1, hs + 4)[0]
for k in range(cs + 12):
    d1[hs + k] ^= KB[k & 3]
(OUT / "dnprot_confuser_antitamper.bin").write_bytes(bytes(d1))

# 2) Dotfuscator marker + base64 ldstr
B2 = blob({"host": "dotf.hunt.local", "port": 9001, "tag": "DF-55"})
src2 = r'''using System;
[assembly: Dotfuscator("Dotfuscator Community 6.5.3")]
[AttributeUsage(AttributeTargets.Assembly)] internal sealed class DotfuscatorAttribute : Attribute { public DotfuscatorAttribute(string s) { } }
namespace a {
  internal static class аб { internal static string c() { return "%s"; } }
  internal static class Program { static int Main(string[] x) { return аб.c().Length; } }
}
''' % base64.b64encode(B2).decode()
(OUT / "dnprot_dotfuscator_b64.bin").write_bytes(bytes(build("DotfApp", src2)))

# 3) decoy: plain assembly, a 4-byte-xor'd blob but no key constant / no module initializer
B3 = blob({"decoy": True, "n": 1})
src3 = r'''using System;
namespace Plain {
  internal static class Data { internal static readonly byte[] Blob = new byte[] { %s }; }
  internal static class Program { static int Main(string[] a) { return Data.Blob.Length + a.Length; } }
}
''' % arr(bytes(c ^ b"\x99\x41\xc3\x0e"[i & 3] for i, c in enumerate(B3)))
(OUT / "dnprot_decoy_plain.bin").write_bytes(bytes(build("PlainApp", src3)))
shutil.copy("/usr/bin/true", OUT / "dnprot_decoy_native.bin")
print("ok", OUT)
