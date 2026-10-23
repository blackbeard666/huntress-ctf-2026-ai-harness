#!/bin/bash
# COM-interop fixtures (com-interop-typelib family): dotnet-built IL assemblies + decoys.  usage: bash cominterop_gen.sh OUTDIR
#  cominterop_exe_net10.bin : [ComImport] interfaces (IUnknown / IDispatch+DispId / default dual / CoClass), a [ComImport]
#                             coclass, ole32 CoCreateInstance + oleaut32 GetActiveObject P/Invokes, GetTypeFromCLSID/ProgID
#  cominterop_lib_net8.bin  : [GeneratedComInterface] (source-generated COM) + [ComVisible] class with [Guid]/[ProgId]
#  cominterop_decoy_plain.bin : CLI assembly with no COM at all -> every field "none"
#  cominterop_decoy_native.bin: native ELF -> every field "none"
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
mk() {  # mk <dir> <tfm> <outputtype> <extra props> <source>
  mkdir -p "$1"
  printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>%s</TargetFramework><OutputType>%s</OutputType><Deterministic>true</Deterministic><DebugType>none</DebugType><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable><AllowUnsafeBlocks>true</AllowUnsafeBlocks><NoWarn>CA1416;SYSLIB1096</NoWarn>%s</PropertyGroup></Project>\n' "$2" "$3" "$4" > "$1/$1.csproj"
  printf '%s\n' "$5" > "$1/P.cs"
  (cd "$1" && dotnet build -c Release -o out >/dev/null); }
mk ComLoader net10.0 Exe '<AssemblyName>ComLoader</AssemblyName>' '
using System; using System.Runtime.InteropServices;
[assembly: Guid("5a1d2c3b-4e5f-4a6b-9c7d-8e9fa0b1c2d3")]
namespace Hunt.Com {
  [ComImport, Guid("0E0B1C2D-3A4B-4C5D-8E9F-A0B1C2D3E4F5"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  internal interface IBeacon {
    void Connect([MarshalAs(UnmanagedType.LPWStr)] string host, int port);
    int Status();
    void Exfil(IntPtr buf, int len);
    [PreserveSig] int Sleep(uint ms);
  }
  [ComImport, Guid("B196B286-BAB4-101A-B69C-00AA00341D07"), InterfaceType(ComInterfaceType.InterfaceIsIDispatch)]
  internal interface IScriptHost {
    [DispId(1)] void Run(string code);
    [DispId(7)] string Name { get; }
  }
  [ComImport, Guid("9f8e7d6c-5b4a-4938-a271-605f4e3d2c1b"), CoClass(typeof(TaskClass))]
  internal interface ITaskDual { void Start(); void Stop(); int Pid { get; set; } }
  [ComImport, Guid("72C24DD5-D70A-438B-8A42-98424B88AFB8")]
  internal class TaskClass { }
  internal static class Native {
    [DllImport("ole32.dll")] internal static extern int CoCreateInstance(ref Guid rclsid, IntPtr outer, uint ctx, ref Guid riid, out IntPtr ppv);
    [DllImport("oleaut32.dll", PreserveSig = false)] internal static extern void GetActiveObject(ref Guid rclsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object ppunk);
  }
  internal static class Program {
    static int Main(string[] a) {
      var clsid = new Guid("13709620-C279-11CE-A49E-444553540000");
      var iid = typeof(IBeacon).GUID;
      if (a.Length > 9) { Native.CoCreateInstance(ref clsid, IntPtr.Zero, 1, ref iid, out IntPtr p); }
      var t = Type.GetTypeFromCLSID(new Guid("F935DC22-1CF0-11D0-ADB9-00C04FD58A0B"));
      var s = Type.GetTypeFromProgID("WScript.Shell");
      return (t == null ? 0 : 1) + (s == null ? 0 : 2);
    }
  }
}'
mk ComPlugin net8.0 Library '<AssemblyName>ComPlugin</AssemblyName>' '
using System; using System.Runtime.InteropServices; using System.Runtime.InteropServices.Marshalling;
namespace Plug {
  [GeneratedComInterface, Guid("3c1e5a7b-9d2f-4b6e-8a0c-1f2e3d4c5b6a")]
  public partial interface ICollector { int Collect(int kind); void Flush(); }
  [ComVisible(true), Guid("D4C3B2A1-1111-2222-3333-444455556666"), ProgId("Plug.Agent"), ClassInterface(ClassInterfaceType.None)]
  public class Agent { public void Ping() { } }
  [GeneratedComClass] public partial class Collector : ICollector { public int Collect(int kind) { return kind; } public void Flush() { } }
}'
mk Plain net8.0 Library '<AssemblyName>Plain</AssemblyName>' '
namespace P { public class C { public int X; public int F() { return X; } } }'
cp ComLoader/out/ComLoader.dll "$OUT/cominterop_exe_net10.bin"
cp ComPlugin/out/ComPlugin.dll "$OUT/cominterop_lib_net8.bin"
cp Plain/out/Plain.dll "$OUT/cominterop_decoy_plain.bin"
cp /usr/bin/true "$OUT/cominterop_decoy_native.bin"
rm -rf "$W"
