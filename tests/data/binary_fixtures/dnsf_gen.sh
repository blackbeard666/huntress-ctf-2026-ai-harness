#!/bin/bash
# .NET publish flavours carrying an HCFG blob: framework-dependent single-file bundle (dotnet publish PublishSingleFile, stored
# entries), COMPRESSED bundles written by the SDK's own Microsoft.NET.HostModel Bundler (BundleOptions.EnableCompression -- the
# writer behind EnableCompressionInSingleFile, used directly so the fixture stays ~100 KB without a self-contained runtime),
# a ReadyToRun dll (PublishReadyToRun) and a plain IL dll.  usage: bash dnsf_gen.sh OUTDIR   (needs dotnet 10 SDK + packs)
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
RID=$(dotnet --info | awk '/ RID:/{print $2; exit}'); SDK=$(dotnet --list-sdks | tail -1 | sed 's/^\([^ ]*\) \[\(.*\)\]/\2\/\1/')
blob() {   # blob <json> [bad] -> HCFG v1 key 0 len crc32 body (crc from gzip's trailer; bad -> crc zeroed)
  local P="$1" LEN CRC; LEN=$(printf '%s' "$P" | wc -c)
  CRC=$(printf '%s' "$P" | gzip -c | tail -c8 | head -c4 | od -An -tx4 | tr -d ' '); [ -n "$2" ] && CRC=00000000
  printf 'HCFG\x01\x00'; printf "\\x$(printf %02x $((LEN&255)))\\x$(printf %02x $((LEN>>8)))"
  printf "\\x${CRC:6:2}\\x${CRC:4:2}\\x${CRC:2:2}\\x${CRC:0:2}"; printf '%s' "$P"; }
app() {    # app <dir> <C# field decl> [msbuild props...] -> dotnet publish into <dir>/out ; IL dll kept in <dir>/il.dll
  local D=$1 F=$2; shift 2; mkdir -p "$D"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><Deterministic>true</Deterministic><RuntimeIdentifier>%s</RuntimeIdentifier><SelfContained>false</SelfContained><DebugType>none</DebugType></PropertyGroup></Project>\n' "$RID" > "$D/app.csproj"
  printf 'static class P { %s static void Main() { System.Console.WriteLine(B.Length); } }\n' "$F" > "$D/P.cs"
  (cd "$D" && dotnet publish -c Release -o out "$@" >/dev/null && cp obj/Release/net10.0/$RID/app.dll il.dll); }
bytes() { od -An -v -tu1 | tr -s ' \n' ',' | sed 's/^,//; s/,$//'; }
# Bundler driver: bnd <apphost> <outdir> <compress 0|1> <file:bundlepath>...
mkdir -p bnd && printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType></PropertyGroup><ItemGroup><Reference Include="Microsoft.NET.HostModel"><HintPath>%s/Microsoft.NET.HostModel.dll</HintPath></Reference></ItemGroup></Project>\n' "$SDK" > bnd/bnd.csproj
cat > bnd/B.cs <<'EOF'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using Microsoft.NET.HostModel.Bundle;
static class B { static void Main(string[] a) {
  var opts = a[2] == "1" ? BundleOptions.EnableCompression | BundleOptions.BundleAllContent : BundleOptions.None;
  var specs = new List<FileSpec> { new FileSpec(a[0], "app") };
  for (int i = 3; i < a.Length; i++) { var p = a[i].Split(':'); specs.Add(new FileSpec(p[0], p[1])); }
  Console.WriteLine(new Bundler("app", a[1], opts, OSPlatform.Linux, Architecture.X64, new Version(10, 0)).GenerateBundle(specs)); } }
EOF
(cd bnd && dotnet build -c Release -o out >/dev/null)
bundle() { local A=$1 O=$2; mkdir -p "$O"; dotnet bnd/out/bnd.dll "$A/obj/Release/net10.0/$RID/apphost" "$O" 1 "$A/il.dll:app.dll" "$A/out/app.runtimeconfig.json:app.runtimeconfig.json" >/dev/null; }

# 1. framework-dependent single-file (stored entries): blob = static byte[] (FieldRVA data inside the embedded app.dll)
B1=$(blob '{"c2":"203.0.113.61:8443","campaign":"singlefile-stored","sleep":30,"flag":"flag{b4ndl3d_n0t_h1dd3n}"}' | bytes)
app sf "static readonly byte[] B = { $B1 };" -p:PublishSingleFile=true
cp sf/out/app "$OUT/dnsf_singlefile_stored.bin"
# 2. compressed bundle, same kind of byte[] blob -> raw deflate entry
B2=$(blob '{"c2":"198.51.100.23:443","campaign":"singlefile-deflate","sleep":45,"flag":"flag{d3fl4t3d_1n_th3_bundl3}"}' | bytes)
app cz "static readonly byte[] B = { $B2 };"; bundle cz czb; cp czb/app "$OUT/dnsf_bundle_deflate.bin"
# 3. compressed bundle, blob as a base64 C# string literal (UTF-16LE in the #US heap of the deflated dll)
S3=$(blob '{"c2":"192.0.2.77:9443","campaign":"singlefile-b64","sleep":60,"flag":"flag{us_h34p_1n_4_bundl3}"}' | base64 -w0)
app cs "static readonly string B = \"$S3\";"; bundle cs csb; cp csb/app "$OUT/dnsf_bundle_us_b64.bin"
# decoy: compressed bundle whose byte[] blob has a zeroed crc
B4=$(blob '{"c2":"198.51.100.23:443","campaign":"singlefile-decoy","sleep":45}' bad | bytes)
app cd "static readonly byte[] B = { $B4 };"; bundle cd cdb; cp cdb/app "$OUT/dnsf_decoy_bundle_badcrc.bin"
# 4. ReadyToRun dll (crossgen2) and the plain IL dll of the same source
B5=$(blob '{"c2":"203.0.113.5:8080","campaign":"readytorun","sleep":15,"flag":"flag{r2r_st1ll_p3_cl1}"}' | bytes)
app r2r "static readonly byte[] B = { $B5 };" -p:PublishReadyToRun=true
cp r2r/out/app.dll "$OUT/dnsf_r2r.bin"; cp r2r/il.dll "$OUT/dnsf_il.bin"
# DNSF_INPUTS=<tar>: keep the IL dll each bundle embeds (dnsf_oracle.py finds them in the bundles by content)
for d in sf cz cs cd; do cp $d/il.dll "$W/${d}_il.dll"; done
[ -n "$DNSF_INPUTS" ] && tar -C "$W" -cf "$DNSF_INPUTS" sf_il.dll cz_il.dll cs_il.dll cd_il.dll
rm -rf "$W"
