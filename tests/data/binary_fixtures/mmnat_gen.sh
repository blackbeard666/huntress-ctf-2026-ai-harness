#!/bin/bash
# Native code carried by / inside a managed assembly (mixed-mode-native-in-managed). usage: bash mmnat_gen.sh OUTDIR
# (dotnet 10 SDK + offline packs, pefile).  Fixtures:
#  mmnat_shellcode_x64.bin : C# net10.0 Exe, PlatformTarget x64 (Machine 0x8664, COR flags ILONLY): x86 shellcode byte[]s
#                            (a static readonly field + a method-local array) copied into mmap/VirtualAlloc memory with
#                            Marshal.Copy and run via Marshal.GetDelegateForFunctionPointer; a decoy key byte[] elsewhere
#  mmnat_mixed_x86_synth.bin : same source, PlatformTarget x86 (PE32, i386, ILONLY|32BITREQUIRED), then pefile-patched into
#                            a synthetic C++/CLI-style mixed-mode image: ILONLY cleared (flags 0x2) + a VTableFixups
#                            directory (2 entries) written into .text slack (MSVC /clr is unavailable on Linux)
#  mmnat_r2r_x64.bin       : same source, dotnet publish -p:PublishReadyToRun=true (crossgen2 native code, RTR header)
#  mmnat_decoy_plain.bin   : C# library with a byte[] table but no allocation P/Invoke -> shellcode_count 0, mixed false
#  mmnat_decoy_native.bin  : native ELF (no CLI header) -> None ; mmnat_decoy_trunc.bin : first 1024 bytes -> None
set -e
OUT=$(realpath "${1:-.}"); W=$(mktemp -d); cd "$W"
RID=$(dotnet --info | awk '/ RID:/{print $2; exit}')
P='<Deterministic>true</Deterministic><DebugType>none</DebugType><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable><AllowUnsafeBlocks>true</AllowUnsafeBlocks>'
cat > P.cs <<'CS'
using System; using System.Runtime.InteropServices;
namespace Hunt.Mixed {
  static class Native {
    [DllImport("kernel32.dll")] internal static extern IntPtr VirtualAlloc(IntPtr addr, UIntPtr size, uint type, uint protect);
    [DllImport("libc", EntryPoint = "mmap")] internal static extern IntPtr Mmap(IntPtr addr, UIntPtr len, int prot, int flags, int fd, IntPtr off);
  }
  [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate int RetFn();
  static class Tables {
    static readonly byte[] Key = { 0x5a, 0x13, 0xc7, 0x88, 0x01, 0xfe, 0x42, 0x9d, 0x3c, 0x77, 0xe0, 0x21, 0xb4, 0x6f, 0x90, 0x0d };
    internal static int Sum() { int s = 0; foreach (byte b in Key) s += b; return s; }
  }
  static class Loader {
    // mov eax, 0x41424344 ; xor eax, 0x01020304 ; add eax, 7 ; ret
    static readonly byte[] Stage = { 0xB8, 0x44, 0x43, 0x42, 0x41, 0x35, 0x04, 0x03, 0x02, 0x01, 0x83, 0xC0, 0x07, 0xC3 };
    static IntPtr Alloc(int n) => OperatingSystem.IsWindows()
      ? Native.VirtualAlloc(IntPtr.Zero, (UIntPtr)(uint)n, 0x3000, 0x40)
      : Native.Mmap(IntPtr.Zero, (UIntPtr)4096u, 7, 0x22, -1, IntPtr.Zero);
    internal static int Run(byte[] sc) {
      IntPtr p = Alloc(sc.Length);
      Marshal.Copy(sc, 0, p, sc.Length);
      return Marshal.GetDelegateForFunctionPointer<RetFn>(p)();
    }
    internal static int First() => Run(Stage);
    internal static int Second() {
      // xor eax, eax ; mov ecx, 5 ; L: add eax, ecx ; loop L ; add eax, 0x1300 ; ret
      byte[] sc = { 0x31, 0xC0, 0xB9, 0x05, 0x00, 0x00, 0x00, 0x01, 0xC8, 0xE2, 0xFC, 0x05, 0x00, 0x13, 0x00, 0x00, 0xC3 };
      return Run(sc);
    }
  }
  static class Program {
    static void Main(string[] a) {
      if (a.Length > 0) { Console.WriteLine(Tables.Sum()); return; }
      Console.WriteLine(Loader.First()); Console.WriteLine(Loader.Second());
    }
  }
}
CS
for d in x64 x86 r2r; do mkdir -p $d; cp P.cs $d/; done
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>Mm</AssemblyName><PlatformTarget>x64</PlatformTarget>%s</PropertyGroup></Project>\n' "$P" > x64/Mm.csproj
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>Mm</AssemblyName><PlatformTarget>x86</PlatformTarget>%s</PropertyGroup></Project>\n' "$P" > x86/Mm.csproj
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>Mm</AssemblyName><RuntimeIdentifier>%s</RuntimeIdentifier><SelfContained>false</SelfContained>%s</PropertyGroup></Project>\n' "$RID" "$P" > r2r/Mm.csproj
mkdir -p Plain
printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Library</OutputType><AssemblyName>Plain</AssemblyName>%s</PropertyGroup></Project>\n' "$P" > Plain/Plain.csproj
printf 'namespace Plain { public static class T { static readonly byte[] K = { 0xB8, 0x01, 0x00, 0x00, 0x00, 0xC3, 9, 8, 7, 6 }; public static int S() { int s = 0; foreach (byte b in K) s += b; return s; } } }\n' > Plain/P.cs
(cd x64 && dotnet build -c Release -o out >/dev/null)
(cd x86 && dotnet build -c Release -o out >/dev/null)
(cd r2r && dotnet publish -c Release -o out -p:PublishReadyToRun=true >/dev/null)
(cd Plain && dotnet build -c Release -o out >/dev/null)
cp x64/out/Mm.dll "$OUT/mmnat_shellcode_x64.bin"
cp r2r/out/Mm.dll "$OUT/mmnat_r2r_x64.bin"
cp Plain/out/Plain.dll "$OUT/mmnat_decoy_plain.bin"
cp /bin/true "$OUT/mmnat_decoy_native.bin"
head -c 1024 x64/out/Mm.dll > "$OUT/mmnat_decoy_trunc.bin"
# synthetic mixed mode: clear ILONLY (keep 32BITREQUIRED) and add a VTableFixups table {rva u32, count u16, type u16} x2
# + its slots (MethodDef tokens) in the zero slack after .text's VirtualSize; written with pefile, not lib.binary
python3 - x86/out/Mm.dll "$OUT/mmnat_mixed_x86_synth.bin" <<'PY'
import sys, struct, pefile
pe = pefile.PE(sys.argv[1]); d = bytearray(open(sys.argv[1], "rb").read())
cli = pe.OPTIONAL_HEADER.DATA_DIRECTORY[14]; co = pe.get_offset_from_rva(cli.VirtualAddress)
t = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".text")
rva = (t.VirtualAddress + t.Misc_VirtualSize + 15) & ~15; assert rva + 32 <= t.VirtualAddress + t.SizeOfRawData
off = pe.get_offset_from_rva(rva); slots = rva + 16
d[off:off + 32] = struct.pack("<IHHIHH", slots, 2, 0x01, slots + 8, 1, 0x05) + struct.pack("<III", 0x06000001, 0x06000002, 0x06000003) + b"\0" * 4
struct.pack_into("<I", d, co + 16, 0x2)                         # Flags: COMIMAGE_FLAGS_32BITREQUIRED only (ILONLY clear)
struct.pack_into("<II", d, co + 48, rva, 16)                    # VTableFixups directory: 2 entries
toff = t.get_file_offset() + 8; struct.pack_into("<I", d, toff, rva + 32 - t.VirtualAddress)   # .text VirtualSize covers it
open(sys.argv[2], "wb").write(bytes(d))
PY
# oracle data: the x64 program really runs both shellcodes (mmap + Marshal.Copy + GetDelegateForFunctionPointer)
echo "RUN x64:"; dotnet x64/out/Mm.dll; echo "decoy key sum:"; dotnet x64/out/Mm.dll k
