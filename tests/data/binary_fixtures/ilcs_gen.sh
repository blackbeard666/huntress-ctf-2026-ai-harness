#!/bin/bash
# .NET IL call-site fixtures ("trace every crossing"). usage: bash ilcs_gen.sh OUTDIR   (dotnet 10 SDK, offline restore)
#  ilcs_cs_net10.bin : C# net10.0 Exe: managed->managed calls (static/instance/virtual/ctor/generic MethodSpec), ldstr
#                      strings, static readonly byte[] (ldtoken + RuntimeHelpers.InitializeArray), P/Invoke getpid/write
#                      called from two managed methods, a lambda (closure class), switch/branch/try-finally bodies
#  ilcs_fs_net10.bin : F# net10.0 Exe: byte-array literal (T<n>_<len>Bytes@ .text blob), [<DllImport>] getpid/strlen
#  ilcs_decoy_managed.bin : C# library with bodies but no P/Invoke / array init -> native edges "[]", array_inits "[]"
#  ilcs_decoy_native.bin  : native ELF -> None ;  ilcs_decoy_trunc.bin : first 1024 bytes of ilcs_cs_net10.bin -> None
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
P='<Deterministic>true</Deterministic><DebugType>none</DebugType><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable><AllowUnsafeBlocks>true</AllowUnsafeBlocks>'
mkdir -p Cs Plain Fsx
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>Crossing</AssemblyName>%s</PropertyGroup></Project>\n' "$P" > Cs/Cs.csproj
cat > Cs/P.cs <<'CS'
using System; using System.Collections.Generic; using System.Runtime.InteropServices;
namespace Hunt.Cross {
  internal static unsafe class Native {
    [DllImport("libc")] internal static extern int getpid();
    [DllImport("libc", EntryPoint = "write")] internal static extern nint SysWrite(int fd, byte* buf, nuint count);
  }
  internal class Beacon {
    static readonly byte[] Key = { 0x48, 0x43, 0x46, 0x47, 1, 0x5a, 7, 0, 0xde, 0xad, 0xbe, 0xef, 0x10, 0x20, 0x30, 0x40, 0x50 };
    static readonly int[] Ports = { 443, 8443, 53, 80 };
    readonly string host;
    internal Beacon(string h) { host = h; }
    internal virtual int Pid() => Native.getpid();
    internal unsafe int Emit(string msg) {
      byte[] b = System.Text.Encoding.UTF8.GetBytes(msg + "\n");
      fixed (byte* p = b) return (int)Native.SysWrite(1, p, (nuint)b.Length);
    }
    internal int Sum() { int s = 0; foreach (var x in Ports) s += x; return s + Key.Length; }
    internal T Echo<T>(T v) => v;
    internal string Route(int k) {
      switch (k) { case 0: return "alpha"; case 1: return "bravo"; case 2: return host; default: return "c2.hunt.example"; }
    }
  }
  internal static class Program {
    static int Main(string[] a) {
      var b = new Beacon("hunt.example");
      var l = new List<string> { "one" };
      Func<int, int> f = x => x + b.Pid();
      int r;
      try { r = b.Emit("HCFG beacon " + b.Route(a.Length)) + b.Echo<int>(7) + f(1); }
      finally { Console.WriteLine("done"); }
      return r + b.Sum() + Native.getpid() + l.Count;
    }
  }
}
CS
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Library</OutputType><AssemblyName>Plain</AssemblyName>%s</PropertyGroup></Project>\n' "$P" > Plain/Plain.csproj
printf 'namespace Plain { public class Beacon { public int Interval; public string Native() { return "kernel32.dll" + Interval.ToString(); } public int Twice() { return Native().Length * 2; } } }\n' > Plain/P.cs
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>Fsx</AssemblyName><Deterministic>true</Deterministic><DebugType>none</DebugType></PropertyGroup><ItemGroup><Compile Include="P.fs" /></ItemGroup></Project>\n' > Fsx/Fsx.fsproj
cat > Fsx/P.fs <<'FS'
module Hunt.Fsx
open System.Runtime.InteropServices
[<DllImport("libc", CallingConvention = CallingConvention.Cdecl)>]
extern int getpid()
[<DllImport("libc", EntryPoint = "strlen", CharSet = CharSet.Ansi)>]
extern unativeint cstrlen([<MarshalAs(UnmanagedType.LPStr)>] string s)
let blob () = [| 0x48uy; 0x43uy; 0x46uy; 0x47uy; 0x01uy; 0x33uy; 0x05uy; 0x00uy; 0x11uy; 0x22uy; 0x33uy; 0x44uy; 0x55uy; 0x66uy |]
let probe (s: string) = int (cstrlen s) + int (getpid ())
[<EntryPoint>]
let main argv =
    let b = blob ()
    printfn "%s" "fsx crossing"
    probe "hcfg" + b.Length + argv.Length
FS
for d in Cs Plain Fsx; do (cd $d && dotnet build -c Release -o out >/dev/null); done
cp Cs/out/Crossing.dll "$OUT/ilcs_cs_net10.bin"
cp Fsx/out/Fsx.dll "$OUT/ilcs_fs_net10.bin"
cp Plain/out/Plain.dll "$OUT/ilcs_decoy_managed.bin"
cp /usr/bin/true "$OUT/ilcs_decoy_native.bin"
head -c 1024 "$OUT/ilcs_cs_net10.bin" > "$OUT/ilcs_decoy_trunc.bin"
rm -rf "$W"
