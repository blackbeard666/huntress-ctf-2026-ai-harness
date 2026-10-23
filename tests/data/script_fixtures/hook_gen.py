"""Build-manifest hook fixtures (Maven exec-maven-plugin argv split over <argument> / <commandlineArgs>).
Writer: stdlib xml.etree.ElementTree + base64 (UTF-16LE -EncodedCommand). Run from the repo root:
    python3 tests/data/script_fixtures/hook_gen.py"""
import base64
import gzip
import json
import xml.etree.ElementTree as ET
from pathlib import Path

D = Path(__file__).resolve().parent


def pom(name, executable, argv=None, cmdline=None, phase="generate-sources"):
    p = ET.Element("project", xmlns="http://maven.apache.org/POM/4.0.0")
    for k, v in (("modelVersion", "4.0.0"), ("groupId", "org.example.inert"), ("artifactId", "inert-fixture"),
                 ("version", "1.0.0")):
        ET.SubElement(p, k).text = v
    pl = ET.SubElement(ET.SubElement(ET.SubElement(p, "build"), "plugins"), "plugin")
    ET.SubElement(pl, "groupId").text = "org.codehaus.mojo"
    ET.SubElement(pl, "artifactId").text = "exec-maven-plugin"
    ET.SubElement(pl, "version").text = "3.1.0"
    ex = ET.SubElement(ET.SubElement(pl, "executions"), "execution")
    ET.SubElement(ex, "id").text = "bootstrap"
    ET.SubElement(ex, "phase").text = phase
    ET.SubElement(ET.SubElement(ex, "goals"), "goal").text = "exec"
    cf = ET.SubElement(ex, "configuration")
    ET.SubElement(cf, "executable").text = executable
    if argv:
        args = ET.SubElement(cf, "arguments")
        for a in argv:
            ET.SubElement(args, "argument").text = a
    if cmdline:
        ET.SubElement(cf, "commandlineArgs").text = cmdline
    ET.indent(p)
    (D / name).write_bytes(ET.tostring(p, encoding="utf-8", xml_declaration=True) + b"\n")


def enc(ps):
    return base64.b64encode(ps.encode("utf-16le")).decode()


P1 = ("v=3|language=maven|role=launcher|verdict=malicious|attack=T1195.002|adapter=exec_plugin|host_profile=maven_exec"
      "|stage_count=2|steps=build_hook,spawn_shell|campaign_id=MVN-5c1e9a02|url=https://mvn-5c1e9a02.example.invalid/stage"
      "|file_path=/tmp/huntress-mvn/.5c1e9a02.stage")
P2 = ("v=3|language=maven|role=staged_chain|verdict=suspicious|attack=T1059.001|adapter=exec_plugin|host_profile=maven_cmdline"
      "|obfuscation_profile=gzip_base64|stage_count=2|steps=build_hook,inflate,dispatch_process|campaign_id=MVN-e04b7d31"
      "|url=https://mvn-e04b7d31.example.invalid/next|file_path=C:\\ProgramData\\huntress-mvn\\e04b7d31.ps1")
ps1 = ("$descriptor_5c1e9a02 = '%s'; $s = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($descriptor_5c1e9a02)); "
       "$null = $s" % base64.b64encode(P1.encode()).decode())
pom("hook_pom_exec_args.xml", "powershell", ["-NoProfile", "-NonInteractive", "-EncodedCommand", enc(ps1)])
ps2 = ("$descriptor_e04b7d31 = '%s'; $m = New-Object IO.MemoryStream(,[Convert]::FromBase64String($descriptor_e04b7d31)); "
       "$s = (New-Object IO.StreamReader(New-Object IO.Compression.GZipStream($m, [IO.Compression.CompressionMode]::Decompress))).ReadToEnd(); "
       "$null = $s" % base64.b64encode(gzip.compress(P2.encode(), mtime=0)).decode())
pom("hook_pom_cmdline_gzip.xml", "pwsh", cmdline="-NoProfile -EncodedCommand " + enc(ps2), phase="validate")
P3 = ("v=3|language=maven|role=launcher|verdict=malicious|attack=T1195.002|adapter=exec_plugin|host_profile=maven_exec"
      "|obfuscation_profile=hex|stage_count=2|steps=build_hook,spawn_shell|campaign_id=MVN-9a31f6c4"
      "|url=https://mvn-9a31f6c4.example.invalid/drop|file_path=/tmp/huntress-mvn/.9a31f6c4.stage")
ps3 = ("$descriptor_9a31f6c4 = '%s'; $b = [byte[]]($descriptor_9a31f6c4 -split '(..)' -ne '' | %%{ [Convert]::ToByte($_, 16) }); "
       "$s = [Text.Encoding]::UTF8.GetString($b); $null = $s" % P3.encode().hex())
pom("hook_pom_enc_hex.xml", "powershell.exe", ["-nop", "-w", "hidden", "-enc", enc(ps3)], phase="initialize")
pom("hook_pom_decoy_benign.xml", "powershell", ["-NoProfile", "-EncodedCommand",
                                                 enc("Write-Host 'generating sources for inert-fixture build ok'")])

ORACLE = ("python3 -c \"import base64,gzip,re,sys,xml.etree.ElementTree as E;r=E.parse(sys.argv[1]).getroot();"
          "t=' '.join(x.text or '' for x in r.iter() if x.tag.split('}')[-1] in ('argument','commandlineArgs'));"
          "ps=base64.b64decode(re.search(r'-(?:EncodedCommand|enc)\\s+(\\S+)',t).group(1)).decode('utf-16-le');"
          "m=re.search(r\\\"descriptor_\\w+ = '([^']+)'\\\",ps);v=m.group(1) if m else '';"
          "b=bytes.fromhex(v) if re.fullmatch(r'[0-9a-f]+',v) else base64.b64decode(v);print((gzip.decompress(b) if b[:2]==b'\\x1f\\x8b' else b).decode() or None, end='')\" tests/data/script_fixtures/")
GEN = "python3 tests/data/script_fixtures/hook_gen.py  # stdlib xml.etree.ElementTree pom writer + base64 UTF-16LE -EncodedCommand"
for n, plain, decoy, note in (("hook_pom_exec_args", P1, False, "<argument> list, base64 descriptor"),
                              ("hook_pom_cmdline_gzip", P2, False, "<commandlineArgs>, gzip+base64 descriptor"),
                              ("hook_pom_enc_hex", P3, False, "<argument> list, -enc abbreviation, hex descriptor"),
                              ("hook_pom_decoy_benign", None, True, "benign Write-Host build hook, no descriptor")):
    (D / f"{n}.json").write_text(json.dumps({
        "file": f"{n}.xml", "expected_plain": plain, "decoy": decoy,
        "generator_cmd": f"{GEN}  ({note})", "oracle_cmd": ORACLE + f"{n}.xml"}, indent=1) + "\n")
