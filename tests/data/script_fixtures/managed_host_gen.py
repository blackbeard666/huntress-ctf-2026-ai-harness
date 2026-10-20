"""Generator for the managed-bridge-hosts fixtures (stdlib only: binascii hex, textwrap). Writes mh_*.{bat,ps1,asp,xoml,
ashx,cshtml,cs} next to this file. The plan text is hex-encoded with binascii.hexlify (independent of lib/codec.py)."""
import binascii
import pathlib

HERE = pathlib.Path(__file__).parent


def plan(host, lang, tag):
    return (f"v=3|language={lang}|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operation_graph|"
            f"host_profile={host}|obfuscation_profile=plain_hex|stage_profile=single_descriptor|next_language=jscript|"
            f"stage_count=2|steps=decode_configuration,return_configuration|campaign_id={tag}|"
            f"url=https://{tag.lower()}.example.invalid/stage|file_path=/tmp/huntress-{tag.lower()}/.stage")


def hx(p):
    return binascii.hexlify(p.encode()).decode()


def chunks(h, n=4):
    k = -(-len(h) // n)
    return [h[i:i + k] for i in range(0, len(h), k)]


out = {}
# 1. batch -> csc.exe: C# descriptor split over echo lines (carets escape > and &)
h = chunks(hx(plan("batch_csc_csharp", "csharp", "CSC-1a2b3c4d")))
out["mh_batch_csc_split.bat"] = "\r\n".join([
    "@echo off", "set OUT=%TEMP%\\s.cs",
    "echo using System; > %TEMP%\\s.cs",
    "echo public static class P { >> %TEMP%\\s.cs",
    f'echo   static string descriptor_1a2b3c4d = "{h[0]}" + >> %TEMP%\\s.cs',
    f'echo     "{h[1]}" + >> %TEMP%\\s.cs',
    f'echo     "{h[2]}" + >> %TEMP%\\s.cs',
    f'echo     "{h[3]}"; >> %TEMP%\\s.cs',
    "echo   static bool Gate(int a) { return a ^> 1 ^&^& a ^< 9; } >> %TEMP%\\s.cs",
    "echo } >> %TEMP%\\s.cs",
    "%WINDIR%\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe /nologo /out:%TEMP%\\s.exe %TEMP%\\s.cs", ""])
# 2. PowerShell Add-Type -TypeDefinition here-string, descriptor split over C# concatenation
h = chunks(hx(plan("powershell_add_type_csharp", "csharp", "ADDTYPE-5e6f7a8b")), 3)
out["mh_ps_addtype_split.ps1"] = "\n".join([
    "$src = @\"", "using System;", "public static class Bridge5e6f {",
    f'    public static string descriptor_5e6f7a8b = "{h[0]}"', f'        + "{h[1]}"', f'        + "{h[2]}";',
    "    public static string Run() { return \"modeled\"; }", "}", "\"@",
    "Add-Type -TypeDefinition $src -Language CSharp", "[Bridge5e6f]::Run() | Out-Null", ""])
# 3. classic ASP VBScript with a VB line-continued descriptor
h = chunks(hx(plan("asp_inline_vbscript", "vbscript", "ASP-9c0d1e2f")), 3)
out["mh_asp_classic_vbs.asp"] = "\r\n".join([
    '<%@ Language=VBScript %>', '<%', 'Option Explicit', 'Dim descriptor_9c0d1e2f',
    f'descriptor_9c0d1e2f = "{h[0]}" & _', f'    "{h[1]}" & _', f'    "{h[2]}"',
    'Response.Write "inert"', '%>', '<html><body>ok</body></html>', ""])
# 4. Workflow Compiler XOML with the C# in <x:Code> CDATA
h = chunks(hx(plan("xoml_inline_csharp", "csharp", "XOML-3a4b5c6d")), 3)
out["mh_xoml_cdata.xoml"] = "\n".join([
    '<SequentialWorkflowActivity x:Class="Bridge" x:Name="Bridge" '
    'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" '
    'xmlns="http://schemas.microsoft.com/winfx/2006/xaml/workflow">', "<x:Code><![CDATA[",
    f'    static string descriptor_3a4b5c6d = "{h[0]}" +', f'        "{h[1]}" +', f'        "{h[2]}";',
    "    public Bridge() { }", "]]></x:Code>", "</SequentialWorkflowActivity>", ""])
# 5. ashx WebHandler
h = hx(plan("ashx_inline_csharp", "csharp", "ASHX-7e8f9a0b"))
out["mh_ashx_webhandler.ashx"] = "\n".join([
    '<%@ WebHandler Language="C#" Class="H7e8f" %>', "using System.Web;",
    "public class H7e8f : IHttpHandler {", f'    static readonly string descriptor_7e8f9a0b = "{h}";',
    '    public void ProcessRequest(HttpContext c) { c.Response.Write("inert"); }',
    "    public bool IsReusable { get { return false; } }", "}", ""])
# 6. decoy: batch csc whose echoed C# carries only random-looking hex (no plan)
out["mh_decoy_batch_csc.bat"] = "\r\n".join([
    "@echo off", "echo public class Q { > q.cs",
    'echo   static string descriptor_00aa11bb = "' + "5f" * 8 + '" + >> q.cs',
    'echo     "' + binascii.hexlify(bytes(range(40, 120))).decode() + '"; >> q.cs', "echo } >> q.cs",
    "csc.exe /out:q.exe q.cs", ""])
# 7. decoy: benign Add-Type (no descriptor at all)
out["mh_decoy_addtype_benign.ps1"] = "\n".join([
    "Add-Type -TypeDefinition @'", "public static class W { public static int Add(int a, int b) { return a + b; } }",
    "'@", "[W]::Add(1, 2)", ""])
for fn, t in out.items():
    (HERE / fn).write_bytes(t.encode())
    print(fn)
