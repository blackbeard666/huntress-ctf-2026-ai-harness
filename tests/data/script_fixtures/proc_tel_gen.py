"""Process-telemetry fixtures (target process-telemetry-windows). Stdlib writers only: xml.sax.saxutils.escape with
wevtutil's &quot; rendering, json.dumps (winlogbeat NDJSON), Splunk k=v with \\" escaping.
Run: python3 -I proc_tel_gen.py <outdir>"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
NS = "http://schemas.microsoft.com/win/2004/08/events/event"


def enc(plan, k=0x5A):
    return bytes(b ^ k for b in plan.encode()).hex()


def ev_xml(eid, ts, data, prov="Microsoft-Windows-Sysmon", chan="Microsoft-Windows-Sysmon/Operational", rid=1):
    d = "".join(f"<Data Name='{k}'>{escape(str(v), {chr(34): '&quot;'})}</Data>" for k, v in data)
    return (f"<Event xmlns='{NS}'><System><Provider Name='{prov}'/><EventID>{eid}</EventID>"
            f"<TimeCreated SystemTime='{ts}'/><EventRecordID>{rid}</EventRecordID><Channel>{chan}</Channel>"
            f"<Computer>WS-0042.corp.example</Computer></System><EventData>{d}</EventData></Event>")


P1 = ("v=3|language=powershell|role=loader|verdict=malicious|attack=T1059.001|adapter=process_telemetry|"
      "stage_count=2|steps=spawn_child,decode_stage|campaign_id=PT-7c41aa02|url=https://pt-7c41aa02.example.invalid/s")
P2 = ("v=3|language=batch|role=launcher|verdict=malicious|attack=T1059.003|adapter=security_4688|stage_count=2|"
      "steps=spawn_cmd,decode_stage|campaign_id=PT-2d9e1b70|url=https://pt-2d9e1b70.example.invalid/c")
P3 = ("v=3|language=powershell|role=stager|verdict=malicious|attack=T1105|adapter=splunk_kv|stage_count=1|"
      "steps=fetch_stage|campaign_id=PT-51f0c3e9|url=https://pt-51f0c3e9.example.invalid/k")
BENIGN = "theme=dark|font=Consolas|autosave=on|interval=300|window=Notepad|telemetry=off"


def cmd(ident, plan):
    return (f'powershell.exe -NoP -W Hidden -Command "$Codec_{ident} = "hex_compact|xor_5a|"; '
            f'$Material_{ident} = "{enc(plan)}"; Write-Output $Material_{ident}"')


def main():
    # 1) Sysmon EID 1 / 5 (+ EID 3 noise) exported XML, wevtutil-style &quot; escaping
    pc = cmd("7c41aa02", P1)
    evs = [
        ev_xml(1, "2026-10-18T09:12:01.1234567Z", [
            ("RuleName", "-"), ("UtcTime", "2026-10-18 09:12:01.123"),
            ("ProcessGuid", "{6f1e2a10-1a2b-6712-0a01-000000002a00}"), ("ProcessId", "6700"),
            ("Image", r"C:\Windows\System32\cmd.exe"), ("CommandLine", r'cmd.exe /c "C:\Users\Public\run.cmd"'),
            ("User", r"CORP\alice"), ("IntegrityLevel", "Medium"),
            ("Hashes", "SHA256=4D3C2B1A00000000000000000000000000000000000000000000000000000001"),
            ("ParentProcessGuid", "{6f1e2a10-1a2b-6712-0901-000000002a00}"), ("ParentProcessId", "4120"),
            ("ParentImage", r"C:\Windows\explorer.exe"), ("ParentCommandLine", r"C:\Windows\Explorer.EXE")], rid=1),
        ev_xml(3, "2026-10-18T09:12:02.0000000Z", [
            ("Image", r"C:\Windows\System32\cmd.exe"), ("DestinationIp", "203.0.113.9"),
            ("DestinationPort", "443")], rid=2),
        ev_xml(1, "2026-10-18T09:12:03.5000000Z", [
            ("RuleName", "-"), ("UtcTime", "2026-10-18 09:12:03.500"),
            ("ProcessGuid", "{6f1e2a10-1a2b-6712-0b01-000000002a00}"), ("ProcessId", "7012"),
            ("Image", r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"), ("CommandLine", pc),
            ("User", r"CORP\alice"), ("IntegrityLevel", "High"), ("Hashes", "MD5=00112233445566778899AABBCCDDEEFF"),
            ("ParentProcessGuid", "{6f1e2a10-1a2b-6712-0a01-000000002a00}"), ("ParentProcessId", "6700"),
            ("ParentImage", r"C:\Windows\System32\cmd.exe"),
            ("ParentCommandLine", r'cmd.exe /c "C:\Users\Public\run.cmd"')], rid=3),
        ev_xml(5, "2026-10-18T09:12:09.0000000Z", [
            ("UtcTime", "2026-10-18 09:12:09.000"), ("ProcessGuid", "{6f1e2a10-1a2b-6712-0b01-000000002a00}"),
            ("ProcessId", "7012"), ("Image", r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"),
            ("User", r"CORP\alice")], rid=4),
    ]
    (OUT / "proc_sysmon1_xml.xml").write_text("<Events>\n" + "\n".join(evs) + "\n</Events>\n")

    # 2) Security 4688 / 4689 through winlogbeat 8 (ECS + winlog.event_data), NDJSON
    c2 = cmd("2d9e1b70", P2)
    rows = [
        {"@timestamp": "2026-10-18T10:01:00.000Z", "event": {"code": "4688", "action": "created-process",
                                                             "type": ["start"]},
         "process": {"pid": 6700, "executable": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                     "command_line": c2, "parent": {"pid": 1008, "executable": r"C:\Windows\System32\cmd.exe"}},
         "user": {"name": "bob", "domain": "CORP"},
         "winlog": {"event_id": "4688", "channel": "Security", "provider_name": "Microsoft-Windows-Security-Auditing",
                    "event_data": {"SubjectUserName": "bob", "SubjectDomainName": "CORP", "NewProcessId": "0x1a2c",
                                   "NewProcessName": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                                   "TokenElevationType": "%%1938", "ProcessId": "0x3f0", "CommandLine": c2,
                                   "ParentProcessName": r"C:\Windows\System32\cmd.exe",
                                   "MandatoryLabel": "S-1-16-12288"}}},
        {"@timestamp": "2026-10-18T10:01:07.000Z", "event": {"code": "4689", "action": "exited-process",
                                                             "type": ["end"]},
         "process": {"pid": 6700, "executable": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"},
         "winlog": {"event_id": "4689", "channel": "Security",
                    "event_data": {"SubjectUserName": "bob", "SubjectDomainName": "CORP", "Status": "0x0",
                                   "ProcessId": "0x1a2c",
                                   "ProcessName": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"}}},
    ]
    (OUT / "proc_4688_winlogbeat.ndjson").write_text("".join(json.dumps(r) + "\n" for r in rows))

    # 3) Splunk-style key=value (XmlWinEventLog field names), one event per line, \" inside quoted values
    def kv(d):
        return " ".join(f'{k}="{v}"' if " " in str(v) or '"' in str(v) else f"{k}={v}"
                        for k, v in ((k, str(v).replace('"', '\\"')) for k, v in d.items()))
    c3 = cmd("51f0c3e9", P3)
    lines = [kv({"_time": "2026-10-18T11:00:00Z", "host": "WS-0042", "source": "XmlWinEventLog:Security",
                 "EventCode": "4688", "SubjectUserName": "carol", "SubjectDomainName": "CORP",
                 "NewProcessId": "0x2b5c", "NewProcessName": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                 "ProcessId": "0x11f4", "ParentProcessName": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                 "CommandLine": c3, "MandatoryLabel": "S-1-16-8192"}),
             kv({"_time": "2026-10-18T11:00:05Z", "host": "WS-0042", "source": "XmlWinEventLog:Security",
                 "EventCode": "4689", "SubjectUserName": "carol", "ProcessId": "0x2b5c",
                 "ProcessName": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "Status": "0x0"})]
    (OUT / "proc_4688_splunk.log").write_text("\n".join(lines) + "\n")

    # 4) DECOY: same Sysmon EID 1 XML shape, the escaped descriptor carries a benign config (no v=3 plan)
    (OUT / "proc_decoy_benign_xml.xml").write_text("<Events>\n" + ev_xml(1, "2026-10-18T12:00:00.0000000Z", [
        ("UtcTime", "2026-10-18 12:00:00.000"), ("ProcessGuid", "{6f1e2a10-1a2b-6712-0c01-000000002a00}"),
        ("ProcessId", "5120"), ("Image", r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"),
        ("CommandLine", cmd("0badf00d", BENIGN)), ("ParentProcessId", "4120"),
        ("ParentImage", r"C:\Windows\explorer.exe")]) + "\n</Events>\n")

    # 5) DECOY: Sysmon EID 3 / 22 only (network telemetry, no process create / terminate events)
    (OUT / "proc_decoy_netonly.xml").write_text("<Events>\n" + "\n".join([
        ev_xml(3, "2026-10-18T12:05:00.0000000Z", [("Image", r"C:\Windows\System32\curl.exe"),
                                                   ("ProcessId", "900"), ("DestinationIp", "198.51.100.7"),
                                                   ("DestinationPort", "80")]),
        ev_xml(22, "2026-10-18T12:05:01.0000000Z", [("Image", r"C:\Windows\System32\curl.exe"),
                                                    ("ProcessId", "900"), ("QueryName", "cdn.example.invalid")])])
        + "\n</Events>\n")


if __name__ == "__main__":
    main()
