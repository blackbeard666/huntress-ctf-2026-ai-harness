#!/bin/bash
# .NET metadata-facts fixtures (d03 family): two dotnet-built IL assemblies + a decoy.  usage: bash dnmeta_gen.sh OUTDIR
#  dnmeta_exe_net10.bin : net10.0 Exe, AssemblyVersion 3.1.4.1, namespace Acme.Loader, static byte[] (FieldRVA via
#                         <PrivateImplementationDetails>), nested type, Main entry point
#  dnmeta_lib_net8.bin  : net8.0 Library (no entry point, no FieldRVA), default version 1.0.0.0
#  dnmeta_decoy_native.bin : a native ELF (no CLI header) -> every field "none"
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
mk() {  # mk <dir> <tfm> <outputtype> <extra props> <source>
  mkdir -p "$1"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>%s</TargetFramework><OutputType>%s</OutputType><Deterministic>true</Deterministic><DebugType>none</DebugType><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable>%s</PropertyGroup></Project>\n' "$2" "$3" "$4" > "$1/$1.csproj"
  printf '%s\n' "$5" > "$1/P.cs"
  (cd "$1" && dotnet build -c Release -o out >/dev/null); }
mk HuntLoader net10.0 Exe '<AssemblyName>HuntLoader</AssemblyName><AssemblyVersion>3.1.4.1</AssemblyVersion><FileVersion>3.1.4.1</FileVersion>' '
namespace Acme.Loader {
  internal static class Program {
    static readonly byte[] Key = { 0x48, 0x43, 0x46, 0x47, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };
    static int counter;
    static int Main(string[] a) { counter++; return Decode(a.Length) + Key.Length + Config.Inner.Depth(); }
    static int Decode(int n) { return n ^ 0x5A; }
  }
  internal sealed class Config {
    public string C2 = "203.0.113.9";
    public int Sleep { get; set; }
    internal static class Inner { public static int Depth() { return 2; } }
  }
}'
mk ShadowLib net8.0 Library '<AssemblyName>ShadowLib</AssemblyName>' '
namespace Shadow { public class Beacon { public int Interval; public void Ping() { } public string Name() { return "b"; } } }'
cp HuntLoader/out/HuntLoader.dll "$OUT/dnmeta_exe_net10.bin"
cp ShadowLib/out/ShadowLib.dll "$OUT/dnmeta_lib_net8.bin"
cp /usr/bin/true "$OUT/dnmeta_decoy_native.bin"
rm -rf "$W"
