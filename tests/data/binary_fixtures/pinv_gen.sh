#!/bin/bash
# .NET P/Invoke bridge fixtures (D22 theme). usage: bash pinv_gen.sh OUTDIR   (dotnet 10 SDK, offline restore)
#  pinv_cs_net10.bin : C# net10.0 Exe: [DllImport("libc")] getpid, kernel32.dll GetModuleHandleW (SetLastError, Unicode),
#                      ExactSpelling/BestFit/StdCall MessageBoxA, [LibraryImport] partial (generated __PInvoke stub),
#                      delegate* unmanaged[Cdecl] call, [UnmanagedCallersOnly] export, NativeLibrary.Load/GetExport +
#                      Marshal.GetDelegateForFunctionPointer
#  pinv_fs_net10.bin : F# net10.0 Exe: [<DllImport("libc", CallingConvention = Cdecl)>] getpid / strlen (marshal LPStr)
#  pinv_decoy_managed.bin : a C# library with no P/Invoke at all -> counts "0", lists "[]", per-method "none"
#  pinv_decoy_native.bin  : native ELF (no CLI header) -> None everywhere
#  pinv_decoy_trunc.bin   : first 1024 bytes of pinv_cs_net10.bin (CLI header points past EOF) -> None everywhere
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
P='<Deterministic>true</Deterministic><DebugType>none</DebugType><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable><AllowUnsafeBlocks>true</AllowUnsafeBlocks>'
mkdir -p Bridge Plain Fsb
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>Bridge</AssemblyName>%s</PropertyGroup></Project>\n' "$P" > Bridge/Bridge.csproj
cat > Bridge/P.cs <<'CS'
using System; using System.Runtime.InteropServices; using System.Runtime.CompilerServices;
namespace Hunt.Bridge {
  internal static unsafe partial class Native {
    [DllImport("libc")] internal static extern int getpid();
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    internal static extern IntPtr GetModuleHandleW(string lpModuleName);
    [DllImport("user32.dll", EntryPoint = "MessageBoxA", ExactSpelling = true, BestFitMapping = false,
               ThrowOnUnmappableChar = true, CallingConvention = CallingConvention.StdCall, CharSet = CharSet.Ansi)]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static extern bool ShowBox(IntPtr hWnd, [MarshalAs(UnmanagedType.LPStr)] string text, string caption, uint type);
    [DllImport("libc", EntryPoint = "write", CallingConvention = CallingConvention.Cdecl)]
    internal static extern nint SysWrite(int fd, byte* buf, nuint count);
    [LibraryImport("libc", EntryPoint = "getppid")] internal static partial int GetParentPid();
    [UnmanagedCallersOnly(EntryPoint = "hunt_callback")] internal static int Callback(int x) => x * 2;
  }
  delegate int PidFn();
  internal static unsafe class Program {
    static int Main(string[] a) {
      IntPtr h = NativeLibrary.Load("libc.so.6");
      IntPtr f = NativeLibrary.GetExport(h, "getpid");
      var d = Marshal.GetDelegateForFunctionPointer<PidFn>(f);
      delegate* unmanaged[Cdecl]<int> fp = (delegate* unmanaged[Cdecl]<int>)f;
      return Native.getpid() + Native.GetParentPid() + fp() + d() + a.Length;
    }
  }
}
CS
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Library</OutputType><AssemblyName>Plain</AssemblyName>%s</PropertyGroup></Project>\n' "$P" > Plain/Plain.csproj
printf 'namespace Plain { public class Beacon { public int Interval; public string Native() { return "kernel32.dll"; } } }\n' > Plain/P.cs
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>Fsb</AssemblyName><Deterministic>true</Deterministic><DebugType>none</DebugType></PropertyGroup><ItemGroup><Compile Include="P.fs" /></ItemGroup></Project>\n' > Fsb/Fsb.fsproj
cat > Fsb/P.fs <<'FS'
module Hunt.Fsb
open System.Runtime.InteropServices
[<DllImport("libc", CallingConvention = CallingConvention.Cdecl)>]
extern int getpid()
[<DllImport("libc", EntryPoint = "strlen", CharSet = CharSet.Ansi)>]
extern unativeint cstrlen([<MarshalAs(UnmanagedType.LPStr)>] string s)
[<EntryPoint>]
let main argv = int (getpid ()) + int (cstrlen "hcfg") + argv.Length
FS
for d in Bridge Plain Fsb; do (cd $d && dotnet build -c Release -o out >/dev/null); done
cp Bridge/out/Bridge.dll "$OUT/pinv_cs_net10.bin"
cp Fsb/out/Fsb.dll "$OUT/pinv_fs_net10.bin"
cp Plain/out/Plain.dll "$OUT/pinv_decoy_managed.bin"
cp /usr/bin/true "$OUT/pinv_decoy_native.bin"
head -c 1024 "$OUT/pinv_cs_net10.bin" > "$OUT/pinv_decoy_trunc.bin"
rm -rf "$W"
