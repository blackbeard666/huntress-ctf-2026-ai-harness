"""Process-tree-reconcile fixtures (target process-tree-reconcile). Stdlib writers only: xml.sax.saxutils.escape
(wevtutil &quot; rendering) for mixed Sysmon EID 1 + Security 4688 XML, json.dumps for flat Sysmon NDJSON carrying a
CreatorProcessId field. TRUTH_* is the declared-vs-observed answer this script built (it wrote the spoof), not what
lib/codec.py reads. Run: python3 -I ptrec_gen.py <outdir>"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
NS = "http://schemas.microsoft.com/win/2004/08/events/event"
P1 = ("v=3|language=powershell|role=loader|verdict=malicious|attack=T1134.004|adapter=sysmon_4688|stage_count=2|"
      "steps=spawn_child,spoof_parent|campaign_id=PR-4c1e9a07|url=https://pr-4c1e9a07.example.invalid/s")
P2 = ("v=3|language=powershell|role=stager|verdict=malicious|attack=T1134.004|adapter=process_telemetry|"
      "stage_count=1|steps=spoof_parent|campaign_id=PR-b83d2f15|url=https://pr-b83d2f15.example.invalid/c")
BENIGN = "theme=light|font=Cascadia|autosave=on|interval=120|window=Terminal|telemetry=off"
S32 = "C:\\Windows\\System32\\"
PS = S32 + "WindowsPowerShell\\v1.0\\powershell.exe"
G = "{{7a20c3e1-bb02-6712-{:04x}-000000004200}}".format


def cmd(ident, plan):
    enc = bytes(b ^ 0x5A for b in plan.encode()).hex()
    return (f'powershell.exe -NoP -W Hidden -Command "$Codec_{ident} = "hex_compact|xor_5a|"; '
            f'$Material_{ident} = "{enc}"; Write-Output $Material_{ident}"')


def ev(provider, eid, ts, data, rid, channel):
    d = "".join(f"<Data Name='{k}'>{escape(str(v), {chr(34): '&quot;'})}</Data>" for k, v in data)
    return (f"<Event xmlns='{NS}'><System><Provider Name='{provider}'/><EventID>{eid}</EventID>"
            f"<TimeCreated SystemTime='{ts}'/><EventRecordID>{rid}</EventRecordID><Channel>{channel}</Channel>"
            f"<Computer>WS-0077.corp.example</Computer></System><EventData>{d}</EventData></Event>")


def sm1(ts, guid, pid, image, cl, pguid, ppid, pimage, rid):
    return ev("Microsoft-Windows-Sysmon", 1, ts.replace(" ", "T") + "0000Z",
              [("RuleName", "-"), ("UtcTime", ts), ("ProcessGuid", guid), ("ProcessId", pid), ("Image", image),
               ("CommandLine", cl), ("User", "CORP\\carol"), ("IntegrityLevel", "Medium"),
               ("ParentProcessGuid", pguid), ("ParentProcessId", ppid), ("ParentImage", pimage)],
              rid, "Microsoft-Windows-Sysmon/Operational")


def s4688(ts, new, creator, image, cl, pimage, rid):
    return ev("Microsoft-Windows-Security-Auditing", 4688, ts.replace(" ", "T") + "0000Z",
              [("SubjectUserName", "carol"), ("SubjectDomainName", "CORP"), ("NewProcessId", new),
               ("NewProcessName", image), ("TokenElevationType", "%%1938"), ("ProcessId", creator),
               ("CommandLine", cl), ("ParentProcessName", pimage), ("MandatoryLabel", "S-1-16-8192")],
              rid, "Security")


def both(ts, guid, pid, image, cl, pguid, ppid, pimage, rid, creator=None, cimage=None):
    """One process: Sysmon EID 1 (recorded parent) + its 4688 (creator = the real parent; same unless spoofed)."""
    return [sm1(ts, guid, pid, image, cl, pguid, ppid, pimage, rid),
            s4688(ts[:-1] + "9", hex(pid), hex(creator if creator is not None else ppid), image, cl,
                  cimage or pimage, rid + 1)]


WORD = "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"
RUNDLL = "rundll32.exe C:\\Users\\Public\\x.dll,Run"


def mixed_log(plan_cmd, spoof=True):
    # rundll32.exe (5200): Sysmon says parent explorer.exe (2000, guid 1) -- the spoofed PPID; its 4688 creator
    # ProcessId 0x1004 = powershell.exe, the process that really created it. notepad.exe is undeclared.
    # explorer.exe's parent (userinit, guid 0 / pid 1800) is never logged -> missing orphan.
    rows = []
    rows += both("2026-10-18 08:00:00.100", G(1), 2000, "C:\\Windows\\explorer.exe", "C:\\Windows\\Explorer.EXE",
                 G(0), 1800, S32 + "userinit.exe", 10)
    rows += both("2026-10-18 08:01:00.100", G(2), 3000, WORD, "WINWORD.EXE /n invoice.docm", G(1), 2000,
                 "C:\\Windows\\explorer.exe", 20)
    rows += both("2026-10-18 08:01:30.100", G(3), 4100, PS, plan_cmd, G(2), 3000, WORD, 30)
    if spoof:
        rows += both("2026-10-18 08:01:40.100", G(4), 5200, S32 + "rundll32.exe", RUNDLL, G(1), 2000,
                     "C:\\Windows\\explorer.exe", 40, creator=4100, cimage=PS)
    else:
        rows += both("2026-10-18 08:01:40.100", G(4), 5200, S32 + "rundll32.exe", RUNDLL, G(3), 4100, PS, 40)
    rows += both("2026-10-18 08:02:10.100", G(5), 6000, S32 + "notepad.exe", "notepad.exe", G(1), 2000,
                 "C:\\Windows\\explorer.exe", 50)
    return "<Events>\n" + "\n".join(rows) + "\n</Events>\n"


DECL_MIXED = [["WINWORD.EXE", "powershell.exe", "powershell.exe -NoP -W Hidden -Command ..."],
              ["powershell.exe", "rundll32.exe", RUNDLL],
              ["powershell.exe", "schtasks.exe", "schtasks.exe /create /tn upd /tr C:\\Users\\Public\\u.exe"]]
TRUTH_MIXED = {
    "parent_mismatch": [{"child": "rundll32.exe", "declared_parent": "powershell.exe", "recorded_parent": "explorer.exe",
                         "real_parent_if_known": "powershell.exe", "pid": "5200", "guid": G(4)[1:-1]}],
    "matched": ["powershell.exe", "rundll32.exe"], "declared_only": ["schtasks.exe"], "observed_only": ["notepad.exe"],
    "orphans": ["explorer.exe"], "attack": "T1134.004",
}
TRUTH_DECOY = {"parent_mismatch": [], "matched": ["powershell.exe", "rundll32.exe"], "declared_only": ["schtasks.exe"],
               "observed_only": ["notepad.exe"], "orphans": ["explorer.exe"], "attack": "none"}


def creator_log():
    # flat Sysmon-style NDJSON with a CreatorProcessId field: powershell.exe (4400) records ParentProcessId 812 /
    # ParentImage svchost.exe, but CreatorProcessId 3300 = wscript.exe, which the source declares as its parent.
    def r(ts, guid, pid, image, cl, pguid, ppid, pimage, creator=None):
        d = {"EventID": 1, "UtcTime": ts, "ProcessGuid": guid, "ProcessId": pid, "Image": image, "CommandLine": cl,
             "ParentProcessGuid": pguid, "ParentProcessId": ppid, "ParentImage": pimage, "User": "CORP\\dave"}
        if creator is not None:
            d["CreatorProcessId"] = creator
        return json.dumps(d) + "\n"
    return "".join([
        r("2026-10-18 10:00:00.000", G(11), 700, S32 + "services.exe", "services.exe", G(10), 600, S32 + "wininit.exe"),
        r("2026-10-18 10:00:01.000", G(12), 812, S32 + "svchost.exe", "svchost.exe -k netsvcs", G(11), 700,
          S32 + "services.exe"),
        r("2026-10-18 10:05:00.000", G(13), 2000, "C:\\Windows\\explorer.exe", "C:\\Windows\\Explorer.EXE", G(10), 1800,
          S32 + "userinit.exe"),
        r("2026-10-18 10:06:00.000", G(14), 3300, S32 + "wscript.exe", "wscript.exe C:\\Users\\Public\\drop.js", G(13),
          2000, "C:\\Windows\\explorer.exe", creator=2000),
        r("2026-10-18 10:06:02.000", G(15), 4400, PS, cmd("b83d2f15", P2), G(12), 812, S32 + "svchost.exe",
          creator=3300),
    ])


DECL_CREATOR = [["explorer.exe", "wscript.exe", None], ["wscript.exe", "powershell.exe", None]]
TRUTH_CREATOR = {
    "parent_mismatch": [{"child": "powershell.exe", "declared_parent": "wscript.exe", "recorded_parent": "svchost.exe",
                         "real_parent_if_known": "wscript.exe", "pid": "4400", "guid": G(15)[1:-1]}],
    "matched": ["wscript.exe", "powershell.exe"], "declared_only": [], "attack": "T1134.004",
}


def main():
    (OUT / "ptrec_sysmon4688_spoof.xml").write_text(mixed_log(cmd("4c1e9a07", P1)))
    (OUT / "ptrec_creator_field.ndjson").write_text(creator_log())
    (OUT / "ptrec_decoy_consistent.xml").write_text(mixed_log(cmd("0badc0de", BENIGN), spoof=False))
    print(json.dumps({"mixed": TRUTH_MIXED, "creator": TRUTH_CREATOR, "decoy": TRUTH_DECOY}))


if __name__ == "__main__":
    main()
