#!/bin/bash
# HCFG in a container slot instead of a code/data literal: PE RT_RCDATA (Win32 .res compiled by llvm-rc, linked by Roslyn),
# .NET manifest resource (dotnet <EmbeddedResource>), jar non-class entry (javac + jar, deflated), overlay appended past the
# last section of an ELF (gcc) / PE (Roslyn dll).  usage: bash rsrc_gen.sh OUTDIR   (needs dotnet, llvm-rc-18, gcc, javac, jar)
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
blob() {   # blob <json> [bad] -> HCFG v1 key 0 len crc32 body on stdout (crc from gzip's trailer; bad -> crc zeroed)
  local P="$1" LEN CRC; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' '); [ -n "$2" ] && CRC=00000000
  printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))"
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; }
dll() {    # dll <name> <csproj ItemGroup xml> -> $W/<name>/out/<name>.dll
  mkdir -p "$1"; printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Library</OutputType><Deterministic>true</Deterministic>%s</PropertyGroup><ItemGroup>%s</ItemGroup></Project>\n' "$3" "$2" > "$1/$1.csproj"
  echo 'namespace Cfg { public static class C { public static int V() => 7; } }' > "$1/C.cs"
  (cd "$1" && dotnet build -c Release -o out >/dev/null); }

# 1. PE RT_RCDATA named HCFG (resource data start == magic)
blob '{"c2":"203.0.113.40:8443","campaign":"rsrc-rcdata","sleep":45,"flag":"flag{rcd4t4_in_rsrc}"}' > rc.blob
mkdir -p rcdata && printf 'HCFG RCDATA "%s"\nVERS RCDATA { "not-a-config\\0" }\n' "$W/rc.blob" > rcdata/r.rc
llvm-rc-18 -fo rcdata/r.res rcdata/r.rc
dll rcdata '<Compile Include="C.cs" />' "<Win32Resource>r.res</Win32Resource><EnableDefaultCompileItems>false</EnableDefaultCompileItems>"
cp rcdata/out/rcdata.dll "$OUT/rsrc_pe_rcdata.bin"

# 2. .NET manifest resource config.bin (4-byte length prefix in the CLI Resources blob, then the blob)
mkdir -p manifest; blob '{"c2":"198.51.100.77:9001","campaign":"manifest-res","sleep":20,"flag":"flag{m4n1f3st_r3s0urc3}"}' > manifest/config.bin
dll manifest '<EmbeddedResource Include="config.bin" LogicalName="Cfg.config.bin" />'
cp manifest/out/manifest.dll "$OUT/rsrc_dotnet_manifest.bin"

# 3. PE overlay: a resource-free dll + 'OVL1' + 4 pad bytes + blob appended
dll plain ''
{ cat plain/out/plain.dll; printf 'OVL1\0\0\0\0'; blob '{"c2":"192.0.2.15:443","campaign":"pe-overlay","sleep":60,"flag":"flag{p4st_th3_l4st_s3ct10n}"}'; } > "$OUT/rsrc_pe_overlay.bin"

# 4. ELF overlay: gcc -s binary + 16 pad bytes + blob appended
printf 'int main(void){return 0;}\n' > t.c; gcc -O2 -s -o t.elf t.c
{ cat t.elf; head -c 16 /dev/zero | tr '\0' '\245'; blob '{"c2":"198.51.100.9:53","campaign":"elf-overlay","sleep":15,"flag":"flag{4pp3nd3d_bl0b}"}'; } > "$OUT/rsrc_elf_overlay.bin"
# decoy: the same ELF, nothing appended
cp t.elf "$OUT/rsrc_decoy_elf.bin"

# 5. jar with a deflated config.bin next to Main.class
mkdir -p jar && printf 'public class Main { public static void main(String[] a) { System.out.println("hi"); } }\n' > jar/Main.java
(cd jar && javac --release 11 Main.java && blob '{"c2":"203.0.113.88:7443","campaign":"jar-entry","sleep":30,"flag":"flag{n0n_cl4ss_3ntry}","pad":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}' > config.bin && jar cfe app.jar Main Main.class config.bin)
cp jar/app.jar "$OUT/rsrc_jar_config.bin"
# decoy: same layout, config.bin is an HCFG blob with a zeroed crc
mkdir -p jard && cp jar/Main.class jard/ && (cd jard && blob '{"c2":"203.0.113.88:7443","campaign":"jar-decoy","sleep":30}' bad > config.bin && jar cfe app.jar Main Main.class config.bin)
cp jard/app.jar "$OUT/rsrc_decoy_jar.bin"
# 6. jar whose non-class entry assets/config.txt holds the blob as base64 text (deflated: no stored anchor survives)
mkdir -p jarb/assets && cp jar/Main.class jarb/ && (cd jarb && { printf 'cfg='; blob '{"c2":"192.0.2.200:8080","campaign":"jar-b64-entry","sleep":90,"flag":"flag{b64_1n51d3_d3fl4t3}"}' | base64 -w0; printf '\nmode=quiet\n'; } > assets/config.txt && jar cfe app.jar Main Main.class assets/config.txt)
cp jarb/app.jar "$OUT/rsrc_jar_b64entry.bin"
rm -rf "$W"
