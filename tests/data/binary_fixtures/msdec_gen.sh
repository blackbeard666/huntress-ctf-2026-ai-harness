#!/bin/bash
# Managed string decryptors hiding an HCFG blob (base64 text of it): the program calls a static decryptor in place of ldstr.
#  msdec_cs_b64xor    C#: string D(string) = UTF8.GetString(FromBase64String(s) ^ static byte[] K (.cctor))  -> plain = base64(HCFG)
#  msdec_cs_bytes     C#: string D(byte[]) = new string(char[] b[i] ^ (i*7+0x33))                           -> plain = base64(HCFG)
#  msdec_vb_chrw      VB.NET: Function D(s) : r &= ChrW(AscW(s.Chars(i)) - 3)                               -> plain = base64(HCFG)
#  msdec_java_xor     javac: static String a(String) = char[] ^ KEY[i % KEY.length] (static int[] in <clinit>)
#  msdec_decoy_cs_badcrc  same as msdec_cs_b64xor with a zeroed crc (decoy)
# usage: bash msdec_gen.sh OUTDIR   (dotnet 10 SDK, javac); writes <name>.bin + <name>.plain (the program's own output)
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
blob() {   # blob <json> [bad] -> HCFG v1 key 0 len crc32 body (crc from gzip's trailer; bad -> crc zeroed), base64
  local P="$1" LEN CRC; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' '); [ -n "$2" ] && CRC=00000000
  { printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))"
    printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; } | base64 -w0; }
csproj() { printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><Deterministic>true</Deterministic><DebugType>none</DebugType></PropertyGroup></Project>\n' > "$1"; }
build() { (cd "$1" && dotnet build -c Release -o out >/dev/null) && dotnet "$1/out/app.dll" > "$1/plain.txt"; }
# 1. C# Base64+XOR (static byte[] key from .cctor); the ciphertext is the base64 of the xor'd base64(HCFG) text
B=$(blob '{"c2":"198.51.100.14:8443","campaign":"managed-b64xor","sleep":20,"flag":"flag{d3crypt0r_1n_th3_m0dul3}"}')
P1=$(printf '%s' "$B" | perl -e 'local $/; $_=<STDIN>; my @k=(0x13,0x37,0x42,0x99); my $i=0; print join("", map { chr(ord($_) ^ $k[$i++ % 4]) } split //, $_);' | base64 -w0)
mkdir -p cs1; csproj cs1/app.csproj
cat > cs1/P.cs <<CS
using System; using System.Text;
static class S { static readonly byte[] K = { 0x13, 0x37, 0x42, 0x99 };
  public static string D(string s) { byte[] b = Convert.FromBase64String(s); for (int i = 0; i < b.Length; i++) b[i] ^= K[i % K.Length]; return Encoding.UTF8.GetString(b); } }
static class P { static void Main() { Console.WriteLine(S.D("$P1")); Console.WriteLine(S.D("$(printf 'GET /beacon' | perl -e 'local $/; $_=<STDIN>; my @k=(0x13,0x37,0x42,0x99); my $i=0; print join("", map { chr(ord($_) ^ $k[$i++ % 4]) } split //, $_);' | base64 -w0)")); } }
CS
build cs1; cp cs1/out/app.dll "$OUT/msdec_cs_b64xor.bin"; head -1 cs1/plain.txt > "$OUT/msdec_cs_b64xor.plain"
# decoy: identical program, zeroed crc
BD=$(blob '{"c2":"198.51.100.14:8443","campaign":"managed-decoy","sleep":20}' bad)
PD=$(printf '%s' "$BD" | perl -e 'local $/; $_=<STDIN>; my @k=(0x13,0x37,0x42,0x99); my $i=0; print join("", map { chr(ord($_) ^ $k[$i++ % 4]) } split //, $_);' | base64 -w0)
mkdir -p cs4; cp cs1/app.csproj cs4/; sed "s|$P1|$PD|" cs1/P.cs > cs4/P.cs
build cs4; cp cs4/out/app.dll "$OUT/msdec_decoy_cs_badcrc.bin"; head -1 cs4/plain.txt > "$OUT/msdec_decoy_cs_badcrc.plain"

# 2. C# (byte[]) -> string, key (i*7+0x33)&0xff, new string(char[])
B=$(blob '{"c2":"203.0.113.88:443","campaign":"managed-bytes","sleep":35,"flag":"flag{byt3_4rr4y_d3crypt0r}"}')
A2=$(printf '%s' "$B" | perl -e 'local $/; $_=<STDIN>; my $i=0; print join(",", map { sprintf("0x%02x", ord($_) ^ (($i++*7+0x33)&255)) } split //, $_);')
mkdir -p cs2; csproj cs2/app.csproj
cat > cs2/P.cs <<CS
using System;
static class S { public static string D(byte[] b) { char[] c = new char[b.Length]; for (int i = 0; i < b.Length; i++) c[i] = (char)(b[i] ^ (byte)(i * 7 + 0x33)); return new string(c); } }
static class P { static void Main() { Console.WriteLine(S.D(new byte[] { $A2 })); Console.WriteLine(S.D(new byte[] { 0x7b, 0x5b, 0x47 })); } }
CS
build cs2; cp cs2/out/app.dll "$OUT/msdec_cs_bytes.bin"; head -1 cs2/plain.txt > "$OUT/msdec_cs_bytes.plain"

# 3. VB.NET ChrW/AscW arithmetic
B=$(blob '{"c2":"192.0.2.150:8080","campaign":"managed-vb","sleep":50,"flag":"flag{chrw_4r1thm3t1c_vb}"}')
S3=$(printf '%s' "$B" | perl -pe 's/(.)/chr(ord($1)+3)/ge')
mkdir -p vb; printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><Deterministic>true</Deterministic><DebugType>none</DebugType><RootNamespace>app</RootNamespace><AssemblyName>app</AssemblyName></PropertyGroup></Project>\n' > vb/app.vbproj
cat > vb/M.vb <<VB
Module M
    Function D(ByVal s As String) As String
        Dim r As String = ""
        For i As Integer = 0 To s.Length - 1
            r &= ChrW(AscW(s.Chars(i)) - 3)
        Next
        Return r
    End Function
    Sub Main()
        Console.WriteLine(D("$S3"))
        Console.WriteLine(D("kwws=22h{dpsoh1frp"))
    End Sub
End Module
VB
build vb; cp vb/out/app.dll "$OUT/msdec_vb_chrw.bin"; head -1 vb/plain.txt > "$OUT/msdec_vb_chrw.plain"

# 4. javac: static String a(String) with a static int[] xor table
B=$(blob '{"c2":"203.0.113.201:9001","campaign":"managed-jvm","sleep":40,"flag":"flag{zkm_styl3_x0r_t4bl3}"}')
J4=$(printf '%s' "$B" | perl -e 'local $/; $_=<STDIN>; my @k=(0x21,0x4f,0x0d,0x6b,0x17); my $i=0; print join("", map { sprintf("\\%03o", ord($_) ^ $k[$i++ % 5]) } split //, $_);')
mkdir -p jv && cat > jv/A.java <<JV
public class A {
    private static final int[] KEY = {0x21, 0x4f, 0x0d, 0x6b, 0x17};
    static String a(String s) { char[] c = s.toCharArray(); for (int i = 0; i < c.length; i++) c[i] = (char) (c[i] ^ KEY[i % KEY.length]); return new String(c); }
    public static void main(String[] v) { System.out.println(a("$J4")); System.out.println(a("\111\073\171\033\055")); }
}
JV
(cd jv && javac --release 11 A.java && java -cp . A > plain.txt); cp jv/A.class "$OUT/msdec_java_xor.bin"; head -1 jv/plain.txt > "$OUT/msdec_java_xor.plain"
rm -rf "$W"
