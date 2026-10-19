"""Process-tree fixtures (target process-tree-model). Stdlib writers only: xml.sax.saxutils.escape (wevtutil &quot;
rendering) for Security 4688 / 4689 XML, json.dumps for Sysmon EID 1 / 5 flat NDJSON. The tree ground truth (TRUTH) is
what this script built, not what lib/codec.py reads. Run: python3 -I ptree_gen.py <outdir>"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
NS = "http://schemas.microsoft.com/win/2004/08/events/event"
SEC = "Microsoft-Windows-Security-Auditing"
P1 = ("v=3|language=powershell|role=loader|verdict=malicious|attack=T1059.001|adapter=security_4688|stage_count=2|"
      "steps=spawn_child,decode_stage|campaign_id=PT-9a13e5c2|url=https://pt-9a13e5c2.example.invalid/t")
P2 = ("v=3|language=powershell|role=stager|verdict=malicious|attack=T1105|adapter=process_telemetry|stage_count=1|"
      "steps=fetch_stage|campaign_id=PT-3e7b0d41|url=https://pt-3e7b0d41.example.invalid/g")
BENIGN = "theme=dark|font=Consolas|autosave=on|interval=300|window=Notepad|telemetry=off"


def cmd(ident, plan):
    enc = bytes(b ^ 0x5A for b in plan.encode()).hex()
    return (f'powershell.exe -NoP -W Hidden -Command "$Codec_{ident} = "hex_compact|xor_5a|"; '
            f'$Material_{ident} = "{enc}"; Write-Output $Material_{ident}"')


def ev(eid, ts, data, rid):
    d = "".join(f"<Data Name='{k}'>{escape(str(v), {chr(34): '&quot;'})}</Data>" for k, v in data)
    return (f"<Event xmlns='{NS}'><System><Provider Name='{SEC}'/><EventID>{eid}</EventID>"
            f"<TimeCreated SystemTime='{ts}'/><EventRecordID>{rid}</EventRecordID><Channel>Security</Channel>"
            f"<Computer>WS-0042.corp.example</Computer></System><EventData>{d}</EventData></Event>")


def p4688(ts, new, creator, image, cl, rid, pimage=None):
    data = [("SubjectUserName", "alice"), ("SubjectDomainName", "CORP"), ("NewProcessId", new),
            ("NewProcessName", image), ("TokenElevationType", "%%1938"), ("ProcessId", creator), ("CommandLine", cl),
            ("MandatoryLabel", "S-1-16-8192")]
    if pimage:
        data.append(("ParentProcessName", pimage))
    return ev(4688, ts, data, rid)


def p4689(ts, pid, image, rid):
    return ev(4689, ts, [("SubjectUserName", "alice"), ("Status", "0x0"), ("ProcessId", pid), ("ProcessName", image)],
              rid)


S32 = "C:\\Windows\\System32\\"


def sec_log(plan_cmd):
    # pid 0x1a2c is reused: cmd.exe exits, WINWORD.EXE gets the same pid; powershell's creator 0x1a2c is WINWORD.EXE.
    # wscript.exe 0xbb8 exits before rundll32.exe (creator 0xbb8) starts -> rundll32 is an 'exited' orphan.
    return [
        p4688("2026-10-18T08:00:00.0000000Z", "0x1004", "0x2f0", "C:\\Windows\\explorer.exe", "C:\\Windows\\Explorer.EXE", 1),
        p4688("2026-10-18T08:00:05.0000000Z", "0xbb8", "0x1004", S32 + "wscript.exe", "wscript.exe C:\\Users\\Public\\a.js", 2),
        p4688("2026-10-18T08:00:10.0000000Z", "0x1a2c", "0x1004", S32 + "cmd.exe", "cmd.exe /c dir", 3),
        p4689("2026-10-18T08:00:12.0000000Z", "0xbb8", S32 + "wscript.exe", 4),
        p4689("2026-10-18T08:00:15.0000000Z", "0x1a2c", S32 + "cmd.exe", 5),
        p4688("2026-10-18T08:01:00.0000000Z", "0x1a2c", "0x1004",
              "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE", "WINWORD.EXE /n invoice.docm", 6),
        p4688("2026-10-18T08:01:30.0000000Z", "0x22b0", "0x1a2c", S32 + "WindowsPowerShell\\v1.0\\powershell.exe",
              plan_cmd, 7),
        p4688("2026-10-18T08:01:31.0000000Z", "0x2468", "0x22b0", S32 + "conhost.exe", "conhost.exe 0xffffffff -ForceV1", 8),
        p4688("2026-10-18T08:02:00.0000000Z", "0x3344", "0xbb8", S32 + "rundll32.exe", "rundll32.exe C:\\Users\\Public\\x.dll,Run", 9),
    ]


TRUTH_SEC = {
    "nodes": 7, "roots": ["explorer.exe", "rundll32.exe"], "orphans": {"explorer.exe": "missing", "rundll32.exe": "exited"},
    "parent_of": {"powershell.exe": "WINWORD.EXE", "conhost.exe": "powershell.exe", "WINWORD.EXE": "explorer.exe",
                  "cmd.exe": "explorer.exe", "explorer.exe": "none", "rundll32.exe": "none"},
    "children_of": {"explorer.exe": ["wscript.exe", "cmd.exe", "WINWORD.EXE"], "conhost.exe": "none"},
    "depth_of": {"conhost.exe": "3", "explorer.exe": "0"}, "max_depth": "3",
    "chain_conhost": ["explorer.exe", "WINWORD.EXE", "powershell.exe", "conhost.exe"],
}

G = "{{5c1d7e20-aa01-6712-{:04x}-000000003100}}".format


def sysmon(eid, ts, guid, pid, image, cl=None, pguid=None, ppid=None, pimage=None):
    r = {"EventID": eid, "Computer": "WS-0042.corp.example", "UtcTime": ts, "ProcessGuid": guid, "ProcessId": pid,
         "Image": image}
    if eid == 1:
        r.update({"CommandLine": cl, "User": "CORP\\bob", "IntegrityLevel": "Medium", "ParentProcessGuid": pguid,
                  "ParentProcessId": ppid, "ParentImage": pimage})
    return r


def sysmon_log():
    # pid 4242 is reused (cmd.exe then svchost.exe, different ProcessGuid); taskhostw.exe names a ParentProcessGuid
    # that is never in the log -> 'missing' orphan; services.exe's parent guid is also absent (missing orphan, root).
    svc, cm, sv = G(1), G(2), G(4)
    return [
        sysmon(1, "2026-10-18 09:00:00.000", svc, 700, S32 + "services.exe", "services.exe", G(0), 600, S32 + "wininit.exe"),
        sysmon(1, "2026-10-18 09:00:01.000", cm, 4242, S32 + "cmd.exe", "cmd.exe /c start", svc, 700, S32 + "services.exe"),
        sysmon(1, "2026-10-18 09:00:02.000", G(3), 5000, S32 + "whoami.exe", "whoami /all", cm, 4242, S32 + "cmd.exe"),
        sysmon(5, "2026-10-18 09:00:03.000", cm, 4242, S32 + "cmd.exe"),
        sysmon(1, "2026-10-18 09:00:10.000", sv, 4242, S32 + "svchost.exe", "svchost.exe -k netsvcs", svc, 700,
               S32 + "services.exe"),
        sysmon(1, "2026-10-18 09:00:11.000", G(5), 5100, S32 + "WindowsPowerShell\\v1.0\\PowerShell.exe",
               cmd("3e7b0d41", P2), sv, 4242, S32 + "svchost.exe"),
        sysmon(1, "2026-10-18 09:00:20.000", G(6), 5200, S32 + "taskhostw.exe", "taskhostw.exe", G(99), 1300,
               S32 + "svchost.exe"),
    ]


TRUTH_SYS = {
    "nodes": 6, "roots": ["services.exe", "taskhostw.exe"],
    "orphans": {"services.exe": "missing", "taskhostw.exe": "missing"},
    "parent_of": {"whoami.exe": "cmd.exe", "powershell.exe": "svchost.exe", "svchost.exe": "services.exe"},
    "children_of": {"services.exe": ["cmd.exe", "svchost.exe"], "cmd.exe": "whoami.exe"},
    "depth_of": {"PowerShell.exe": "2"}, "max_depth": "2",
    "chain_powershell": ["services.exe", "svchost.exe", "PowerShell.exe"],
}


def main():
    (OUT / "ptree_4688_pidreuse.xml").write_text("<Events>\n" + "\n".join(sec_log(cmd("9a13e5c2", P1))) + "\n</Events>\n")
    (OUT / "ptree_sysmon_guid.ndjson").write_text("".join(json.dumps(r) + "\n" for r in sysmon_log()))
    (OUT / "ptree_decoy_benign_tree.xml").write_text(
        "<Events>\n" + "\n".join(sec_log(cmd("0badf00d", BENIGN))) + "\n</Events>\n")
    print(json.dumps({"sec": TRUTH_SEC, "sysmon": TRUTH_SYS}))


if __name__ == "__main__":
    main()
