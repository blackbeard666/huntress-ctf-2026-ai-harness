"""Generator for the prior-language host battery (target prior-language-host-battery; sibling of the D20
`host-classic-asp-vbscript.vbs`). stdlib only (base64, binascii, gzip, json): each host wraps a D1-D20-style v=3 plan
as a descriptor / marker in the host's own syntax. Writes pho_*.* + pho_*.json next to this file; every json carries an
independent shell oracle (base64 / xxd / iconv / jq-free python json) that the generator runs to prove `expected_plain`."""
import base64
import binascii
import gzip
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).parent


def plan(host, lang, tag):
    return (f"v=3|language={lang}|role=staged_chain|verdict=suspicious|attack=T1059|adapter=operation_graph|"
            f"host_profile={host}|obfuscation_profile=base64|stage_profile=two_stage_download_execute|"
            f"next_language=powershell|stage_count=2|steps=acquire_remote,dispatch_process|campaign_id={tag}|"
            f"url=https://{tag.lower()}.example.invalid/stage|file_path=/tmp/huntress-{tag.lower()}/.stage")


b64 = lambda s: base64.b64encode(s.encode() if isinstance(s, str) else s).decode()
hx = lambda s: binascii.hexlify(s.encode()).decode()
gzb64 = lambda s: base64.b64encode(gzip.compress(s.encode(), mtime=0)).decode()
enc16 = lambda s: base64.b64encode(s.encode("utf-16-le")).decode()


def halves(s, n=2):
    k = -(-len(s) // n)
    return [s[i:i + k] for i in range(0, len(s), k)]


FX = []   # (file, bytes, expected_plain|None, decoy, profile, generator note, oracle)

# 1. classic ASP, <script language="JScript" runat="server">, base64 descriptor split over `+`
p = plan("classic_asp", "jscript", "ASPJS-1f2e3d4c"); h = halves(b64(p))
FX.append(("pho_asp_jscript_runat.asp", "\r\n".join([
    '<html><body>', '<script language="JScript" runat="server">',
    f'var descriptor_1f2e3d4c = "{h[0]}" +', f'    "{h[1]}";',
    'function buildPlan_1f2e3d4c() { return descriptor_1f2e3d4c; }', 'Response.Write("inert-analysis-fixture");',
    '</script>', '</body></html>', ""]), p, False, "classic_asp", "stdlib base64.b64encode, split in 2",
    """grep -oE '"[A-Za-z0-9+/=]{20,}"' pho_asp_jscript_runat.asp | tr -d '"\\n' | base64 -d"""))
# 2. classic ASP <%@ Language=JScript %> + `//` marker (hex) + descriptor
p = plan("classic_asp", "jscript", "ASPJD-5a6b7c8d")
FX.append(("pho_asp_jscript_directive.asp", "\r\n".join([
    '<%@ Language=JScript %>', '<%', f'// HUNTRESS_ANALYSIS_V1:HEX-{hx(p)}',
    'var descriptor_5a6b7c8d;', f'descriptor_5a6b7c8d = "{hx(p)}";', 'Response.Write("inert-analysis-fixture");',
    '%>', ""]), p, False, "classic_asp", "stdlib binascii.hexlify",
    """grep -oE '"[0-9a-f]{20,}"' pho_asp_jscript_directive.asp | tr -d '"\\n' | xxd -r -p"""))
# 3. Windows Script Component: VBScript in CDATA, `& _` continued base64 descriptor
p = plan("wsc_component", "vbscript", "WSC-0a1b2c3d"); h = halves(b64(p), 3)
FX.append(("pho_wsc_vbscript.wsc", "\r\n".join([
    '<?xml version="1.0"?>', '<component>',
    '<registration description="Inert" progid="Inert.Fixture" version="1.00" classid="{AAAA1111-0000-0000-0000-0000FEEDACDC}">',
    '</registration>', '<public><method name="Exec"/></public>', '<script language="VBScript">', '<![CDATA[',
    'Dim descriptor_0a1b2c3d', f'descriptor_0a1b2c3d = "{h[0]}" & _', f'    "{h[1]}" & _', f'    "{h[2]}"',
    'Function Exec()', '  Exec = descriptor_0a1b2c3d', 'End Function', ']]>', '</script>', '</component>', ""]),
    p, False, "wsc_component", "stdlib base64.b64encode, split in 3 (VB `& _` continuation)",
    """grep -oE '"[A-Za-z0-9+/=]{20,}"' pho_wsc_vbscript.wsc | tr -d '"\\n' | base64 -d"""))
# 4. systemd unit: ExecStart=/bin/bash -c '..' (hex descriptor, `%%` systemd escape), no marker
p = plan("systemd_unit", "bash", "SYSD-9e8d7c6b")
FX.append(("pho_systemd_bash.service", "\n".join([
    '[Unit]', 'Description=inert analysis fixture', '', '[Service]', 'Type=oneshot',
    f"ExecStart=/bin/bash -c 'descriptor_9e8d7c6b=\"{hx(p)}\"; printf %%s \"$descriptor_9e8d7c6b\" | xxd -r -p >/dev/null'",
    '', '[Install]', 'WantedBy=multi-user.target', ""]), p, False, "systemd_unit", "stdlib binascii.hexlify",
    """grep -oE '[0-9a-f]{40,}' pho_systemd_bash.service | xxd -r -p"""))
# 5. crontab line: bash -c "..." with backslash-escaped inner quotes, gzip+base64 descriptor
p = plan("cron_entry", "bash", "CRON-3c4d5e6f")
FX.append(("pho_cron_bash.cron", "\n".join([
    'SHELL=/bin/bash', 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin', '# m h dom mon dow command',
    f'*/15 * * * * bash -c "descriptor_3c4d5e6f=\\"{gzb64(p)}\\"; echo \\$descriptor_3c4d5e6f | base64 -d | gunzip >/dev/null"',
    ""]), p, False, "cron_entry", "python3 gzip.compress(mtime=0) | base64",
    """grep -oE 'H4sI[A-Za-z0-9+/=]+' pho_cron_bash.cron | base64 -d | gunzip"""))
# 6. .desktop entry: Exec=sh -c "..", single-quoted base64 descriptor
p = plan("desktop_entry", "sh", "XDG-7a8b9c0d")
FX.append(("pho_desktop_sh.desktop", "\n".join([
    '[Desktop Entry]', 'Type=Application', 'Name=Inert Fixture',
    f"""Exec=sh -c "descriptor_7a8b9c0d='{b64(p)}'; echo $descriptor_7a8b9c0d | base64 -d >/dev/null\"""",
    'X-GNOME-Autostart-enabled=true', ""]), p, False, "desktop_entry", "stdlib base64.b64encode",
    """grep -oE "'[A-Za-z0-9+/=]{20,}'" pho_desktop_sh.desktop | tr -d "'" | base64 -d"""))
# 7. Jupyter notebook (nbformat 4 JSON): Python implicit-concat descriptor inside JSON-escaped source lines
p = plan("jupyter_notebook", "python", "IPYNB-2b3c4d5e"); h = halves(b64(p))
nb = {"cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# inert analysis fixture"]},
                {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
                    "import base64\n", "descriptor_2b3c4d5e = (\n", f"    \"{h[0]}\"\n", f"    \"{h[1]}\"\n", ")\n",
                    "def build_plan_2b3c4d5e():\n", "    return base64.b64decode(descriptor_2b3c4d5e)"]}],
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
      "nbformat": 4, "nbformat_minor": 5}
FX.append(("pho_jupyter_python.ipynb", json.dumps(nb, indent=1) + "\n", p, False, "jupyter_notebook",
           "python3 json.dumps(nbformat-4 dict) + stdlib base64",
           """python3 -c "import json,re,base64,sys;s=''.join(json.load(open('pho_jupyter_python.ipynb'))['cells'][1]['source']);print(base64.b64decode(''.join(re.findall(r'\\"([A-Za-z0-9+/=]{20,})\\"',s))).decode(),end='')\""""))
# 8. Electron preload.js: contextBridge object-literal descriptor (hex)
p = plan("electron_preload", "node", "ELEC-6d7e8f90")
FX.append(("pho_electron_preload.js", "\n".join([
    "// package.json: { \"main\": \"main.js\" }  -> webPreferences.preload = path.join(__dirname, 'preload.js')",
    "const { contextBridge } = require('electron');", "contextBridge.exposeInMainWorld('inert', {",
    f"  descriptor_6d7e8f90: '{hx(p)}',", "  plan: () => Buffer.from(module.exports.d || '', 'hex').toString(),", "});",
    ""]), p, False, "electron_preload", "stdlib binascii.hexlify",
    """grep -oE "'[0-9a-f]{40,}'" pho_electron_preload.js | tr -d "'" | xxd -r -p"""))
# 9. Nmap NSE: description = [[..]] + `--` marker + Lua long-bracket descriptor
p = plan("nmap_nse", "lua", "NSE-4e5f6a7b")
FX.append(("pho_nmap_nse.nse", "\n".join([
    'local stdnse = require "stdnse"', 'description = [[', 'Inert analysis fixture.', ']]',
    f'-- HUNTRESS_ANALYSIS_V1:B64-{b64(p)}', 'categories = {"safe"}', f'local descriptor_4e5f6a7b = [[{b64(p)}]]',
    'portrule = function(host, port) return false end', 'action = function(host, port) return descriptor_4e5f6a7b end',
    ""]), p, False, "nmap_nse", "stdlib base64.b64encode",
    """grep -oE '\\[\\[[A-Za-z0-9+/=]{20,}\\]\\]' pho_nmap_nse.nse | tr -d '[]' | base64 -d"""))
# 10. NSE without marker: long-bracket descriptor only (hex)
p = plan("nmap_nse", "lua", "NSE-8a9b0c1d")
FX.append(("pho_nmap_nse_bare.nse", "\n".join([
    'description = [[ Inert analysis fixture. ]]', 'categories = {"safe"}',
    f'local descriptor_8a9b0c1d = [==[{hx(p)}]==]', 'portrule = function() return false end',
    'action = function() return descriptor_8a9b0c1d end', ""]), p, False, "nmap_nse", "stdlib binascii.hexlify",
    """grep -oE '[0-9a-f]{40,}' pho_nmap_nse_bare.nse | xxd -r -p"""))
# 11. Redis EVAL: Lua inside a redis-cli double-quoted argument, `\\"` escaped literal
p = plan("redis_eval", "lua", "REDIS-0c1d2e3f")
FX.append(("pho_redis_eval.redis", "\n".join([
    '# redis-cli -h 127.0.0.1 < this file', 'PING',
    f'EVAL "local descriptor_0c1d2e3f = \\"{b64(p)}\\" return redis.call(\'SET\', KEYS[1], descriptor_0c1d2e3f)" 1 inert:key',
    ""]), p, False, "redis_eval", "stdlib base64.b64encode",
    """grep -oE '[A-Za-z0-9+/=]{60,}' pho_redis_eval.redis | base64 -d"""))
# 12. Task Scheduler XML (UTF-16LE + BOM, as schtasks /query /xml exports): powershell.exe -enc <UTF-16LE b64>
p = plan("scheduled_task_xml", "powershell", "TASK-5f6a7b8c")
inner = f"$descriptor_5f6a7b8c = '{hx(p)}'\n$null = $descriptor_5f6a7b8c"
xml = "\r\n".join([
    '<?xml version="1.0" encoding="UTF-16"?>',
    '<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">',
    '  <RegistrationInfo><Description>inert analysis fixture</Description></RegistrationInfo>',
    '  <Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers>',
    '  <Actions Context="Author">', '    <Exec>', '      <Command>powershell.exe</Command>',
    f'      <Arguments>-NoProfile -WindowStyle Hidden -enc {enc16(inner)}</Arguments>', '    </Exec>', '  </Actions>',
    '</Task>', ""])
FX.append(("pho_task_xml_ps.xml", "\ufeff" + xml, p, False, "scheduled_task_xml",
           "python3 str.encode('utf-16-le') | base64 (-enc), whole XML written UTF-16LE with BOM",
           """iconv -f UTF-16 -t UTF-8 pho_task_xml_ps.xml | grep -oP '(?<=-enc )[A-Za-z0-9+/=]+' | base64 -d | iconv -f UTF-16LE -t UTF-8 | grep -oE '[0-9a-f]{40,}' | xxd -r -p"""))
# 13. GPO psscripts.ini (UTF-16LE + BOM): Parameters=-enc ..
p = plan("gpo_scripts_ini", "powershell", "GPO-9d0e1f2a")
inner = f"$descriptor_9d0e1f2a = \"{b64(p)}\""
ini = "\r\n".join(["", "[Startup]", "0CmdLine=powershell.exe", f"0Parameters=-NoP -NonI -enc {enc16(inner)}", ""])
FX.append(("pho_gpo_psscripts.ini", "\ufeff" + ini, p, False, "gpo_scripts_ini",
           "python3 str.encode('utf-16-le') | base64 (-enc), ini written UTF-16LE with BOM",
           """iconv -f UTF-16 -t UTF-8 pho_gpo_psscripts.ini | grep -oP '(?<=-enc )[A-Za-z0-9+/=]+' | base64 -d | iconv -f UTF-16LE -t UTF-8 | grep -oE '[A-Za-z0-9+/=]{40,}' | base64 -d"""))
# ---- decoys
FX.append(("pho_decoy_wsc_benign.wsc", "\r\n".join([
    '<?xml version="1.0"?>', '<component>', '<registration progid="Inert.Benign" version="1.00"/>',
    '<script language="VBScript"><![CDATA[', f'Dim descriptor_00000000 : descriptor_00000000 = "{b64("hello from a benign component, nothing to see here")}"',
    ']]></script>', '</component>', ""]), None, True, "wsc_component", "stdlib base64 of a benign sentence",
    """grep -oE '"[A-Za-z0-9+/=]{20,}"' pho_decoy_wsc_benign.wsc | tr -d '"' | base64 -d | grep -c '^v=3' || true"""))
p = plan("cron_entry", "bash", "CRON-deadbeef")
FX.append(("pho_decoy_cron_truncgz.cron",
           f'0 * * * * bash -c "descriptor_deadbeef=\\"{gzb64(p)[:40]}\\"; true"\n', None, True, "cron_entry",
           "python3 gzip+base64 of a plan, truncated to 40 chars (no complete stream)",
           """grep -oE 'H4sI[A-Za-z0-9+/=]+' pho_decoy_cron_truncgz.cron | base64 -d 2>/dev/null | gunzip 2>&1 | grep -c '^v=3' || true"""))
xml = "\r\n".join(['<?xml version="1.0" encoding="UTF-16"?>',
                   '<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"><Actions><Exec>',
                   '<Command>powershell.exe</Command>', f'<Arguments>-enc {enc16("Get-Date | Out-Null")}</Arguments>',
                   '</Exec></Actions></Task>', ""])
FX.append(("pho_decoy_task_xml_benign.xml", "\ufeff" + xml, None, True, "scheduled_task_xml",
           "python3 utf-16-le base64 of `Get-Date | Out-Null`, XML written UTF-16LE with BOM",
           """iconv -f UTF-16 -t UTF-8 pho_decoy_task_xml_benign.xml | grep -oP '(?<=-enc )[A-Za-z0-9+/=]+' | base64 -d | iconv -f UTF-16LE -t UTF-8"""))

for fn, text, exp, decoy, prof, gen, oracle in FX:
    utf16 = fn in ("pho_task_xml_ps.xml", "pho_gpo_psscripts.ini", "pho_decoy_task_xml_benign.xml")
    (HERE / fn).write_bytes(text.encode("utf-16-le") if utf16 else text.encode())
    got = subprocess.run(["bash", "-c", oracle], cwd=HERE, capture_output=True, text=True).stdout
    if exp is not None:
        assert got == exp, (fn, got[:80])
    else:
        assert "v=3" not in got, (fn, got[:80])
    stem = fn.rsplit(".", 1)[0]
    (HERE / f"{stem}.json").write_text(json.dumps({
        "expected_plain": exp, "decoy": decoy, "profile_guess": prof,
        "generator_cmd": f"python3 tests/data/script_fixtures/prior_host_gen.py  # {gen}, written as {fn}",
        "oracle_cmd": oracle}, indent=1) + "\n")
print("ok", len(FX))
