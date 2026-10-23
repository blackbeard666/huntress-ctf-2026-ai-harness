#!/bin/bash
# Reflection / dynamic loading of a second module: (1) a .NET console app carrying a compiled Payload.dll as a Costura-style
# manifest resource `costura.payload.dll.compressed` (raw deflate, DeflateStream) loaded by Assembly.Load(byte[]) +
# AppDomain.AssemblyResolve + GetType/GetMethod/Invoke/Activator; (2) a jar whose payload.bin is Secret.class xor'd with
# the 3-byte key "k3y", loaded by ClassLoader.defineClass; decoys: same shapes, the resource/entry holds no module.
# usage: source bin/env.sh; bash emb_gen.sh OUTDIR   (needs dotnet, javac, jar, python3 stdlib zlib for raw deflate)
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
blob() {   # blob <json> -> HCFG v1 key 0 len crc32 body (crc from gzip's trailer)
  local P="$1" LEN CRC; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' ')
  printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))"
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; }
rawdeflate() { python3 -I -c 'import sys,zlib; c=zlib.compressobj(9,zlib.DEFLATED,-15); sys.stdout.buffer.write(c.compress(sys.stdin.buffer.read())+c.flush())'; }
proj() {   # proj <dir> <OutputType> <ItemGroup xml>
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>%s</OutputType><Deterministic>true</Deterministic><AssemblyName>%s</AssemblyName></PropertyGroup><ItemGroup>%s</ItemGroup></Project>\n' "$2" "$1" "$3" > "$1/$1.csproj"; }

# 1. Payload.dll (HCFG as its own manifest resource) -> deflated into Host.exe as costura.payload.dll.compressed
mkdir -p Payload Host
blob '{"c2":"203.0.113.61:8443","campaign":"costura-load","sleep":25,"flag":"flag{4ss3mbly_l04d_byt3s}"}' > Payload/config.bin
cat > Payload/E.cs <<'CS'
namespace Payload { public class Entry { public string Run(string a) { return "payload:" + a; } } }
CS
proj Payload Library '<EmbeddedResource Include="config.bin" LogicalName="Payload.config.bin" />'
(cd Payload && dotnet build -c Release -o out >/dev/null)
rawdeflate < Payload/out/Payload.dll > Host/payload.dll.compressed
cat > Host/P.cs <<'CS'
using System; using System.IO; using System.IO.Compression; using System.Reflection;
static class P {
  static byte[] Res(string n) { using var s = typeof(P).Assembly.GetManifestResourceStream(n); using var d = new DeflateStream(s, CompressionMode.Decompress); using var m = new MemoryStream(); d.CopyTo(m); return m.ToArray(); }
  static void Main() {
    AppDomain.CurrentDomain.AssemblyResolve += (o, e) => Assembly.Load(Res("costura.payload.dll.compressed"));
    var asm = Assembly.Load(Res("costura.payload.dll.compressed"));
    var t = asm.GetType("Payload.Entry");
    var inst = Activator.CreateInstance(t);
    Console.WriteLine(t.GetMethod("Run").Invoke(inst, new object[] { "go" }));
  }
}
CS
proj Host Exe '<EmbeddedResource Include="payload.dll.compressed" LogicalName="costura.payload.dll.compressed" />'
(cd Host && dotnet build -c Release -o out >/dev/null)
cp Host/out/Host.dll "$OUT/emb_dotnet_costura.bin"
# decoy: same host shape, the costura resource inflates to text (no MZ/BSJB inside)
mkdir -p Decoy; printf 'not a module, just %s\n' "$(seq 1 40 | tr '\n' ' ')" | rawdeflate > Decoy/payload.dll.compressed
cp Host/P.cs Decoy/P.cs; proj Decoy Exe '<EmbeddedResource Include="payload.dll.compressed" LogicalName="costura.payload.dll.compressed" />'
(cd Decoy && dotnet build -c Release -o out >/dev/null)
cp Decoy/out/Decoy.dll "$OUT/emb_decoy_dotnet.bin"

# 2. jar: Loader defineClass()es payload.bin = Secret.class xor "k3y"; Secret holds the HCFG blob as a base64 constant
mkdir -p jar && cd jar
B64=$(blob '{"c2":"198.51.100.23:4444","campaign":"defineclass-xor","sleep":40,"flag":"flag{d3f1n3_cl4ss_x0r}"}' | base64 -w0)
printf 'public class Secret { public static final String CFG = "%s"; public String toString() { return "secret"; } }\n' "$B64" > Secret.java
cat > Loader.java <<'JV'
import java.io.*;
public class Loader extends ClassLoader {
  public static void main(String[] a) throws Exception {
    InputStream in = Loader.class.getResourceAsStream("/payload.bin"); byte[] b = in.readAllBytes(); byte[] k = "k3y".getBytes();
    for (int i = 0; i < b.length; i++) b[i] ^= k[i % k.length];
    Class<?> c = new Loader().defineClass("Secret", b, 0, b.length);
    Object o = c.getDeclaredConstructor().newInstance(); System.out.println(c.getMethod("toString").invoke(o));
  }
}
JV
javac --release 11 Secret.java Loader.java
python3 -I -c 'import sys; d=open("Secret.class","rb").read(); k=b"k3y"; sys.stdout.buffer.write(bytes(c^k[i%3] for i,c in enumerate(d)))' > payload.bin
jar cfe app.jar Loader Loader.class payload.bin && cp app.jar "$OUT/emb_jar_defineclass.bin"
# decoy: same loader, payload.bin is random bytes (no class under any short xor key)
head -c 1500 /dev/urandom > payload.bin && jar cfe decoy.jar Loader Loader.class payload.bin && cp decoy.jar "$OUT/emb_decoy_jar.bin"
cd /; rm -rf "$W"
