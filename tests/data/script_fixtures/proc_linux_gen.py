"""Process-telemetry-linux fixtures. Writers: real procps `ps` / psmisc `pstree` (live processes whose argv carry the
descriptor), stdlib json.dumps (osquery results log NDJSON), csv.writer (Procmon CSV, QUOTE_ALL), and the auditd raw
record syntax (bytes.hex() for EXECVE argv with spaces/quotes and PROCTITLE NUL-joined argv -- what the kernel emits).
Run: python3 -I proc_linux_gen.py <outdir>"""
import csv
import io
import json
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(sys.argv[1])


def enc(plan, k=0x5A):
    return bytes(b ^ k for b in plan.encode()).hex()


P1 = ("v=3|language=bash|role=loader|verdict=malicious|attack=T1059.004|adapter=auditd_execve|stage_count=2|"
      "steps=spawn_child,decode_stage|campaign_id=PL-3a91c0d4|url=https://pl-3a91c0d4.example.invalid/a")
P2 = ("v=3|language=python|role=stager|verdict=malicious|attack=T1105|adapter=osquery_process_events|stage_count=1|"
      "steps=fetch_stage|campaign_id=PL-6e02b7f1|url=https://pl-6e02b7f1.example.invalid/o")
P3 = ("v=3|language=powershell|role=launcher|verdict=malicious|attack=T1059.001|adapter=procmon_csv|stage_count=2|"
      "steps=spawn_child,decode_stage|campaign_id=PL-0c5d2e88|url=https://pl-0c5d2e88.example.invalid/p")
P5 = ("v=3|language=bash|role=loader|verdict=malicious|attack=T1059.004|adapter=sysmon_linux|stage_count=2|"
      "steps=spawn_child,decode_stage|campaign_id=PL-4d7e2a10|url=https://pl-4d7e2a10.example.invalid/x")
P4 = ("v=3|language=bash|role=dropper|verdict=malicious|attack=T1059.004|adapter=ps_forest|stage_count=1|"
      "steps=decode_stage|campaign_id=PL-91aa4b3c|url=https://pl-91aa4b3c.example.invalid/f")


def sh_cmd(ident, plan):
    return f'Codec_{ident}="hex_compact|xor_5a|"; Material_{ident}="{enc(plan)}"; echo "$Material_{ident}"'


def audit(serial, pid, ppid, argv, exe, ts="1760785200.123"):
    def a(v):
        return f'"{v}"' if all(0x21 <= ord(c) < 0x7F and c != '"' for c in v) else v.encode().hex().upper()
    st = f"msg=audit({ts}:{serial}):"
    return "\n".join([
        f"type=SYSCALL {st} arch=c000003e syscall=59 success=yes exit=0 a0=55d0 a1=55d1 a2=55d2 a3=0 items=2 "
        f"ppid={ppid} pid={pid} auid=1000 uid=1000 gid=1000 euid=1000 suid=1000 fsuid=1000 egid=1000 sgid=1000 "
        f"fsgid=1000 tty=pts0 ses=3 comm={a(exe.rsplit('/', 1)[-1])} exe={a(exe)} subj=unconfined key=\"exec\"",
        f"type=EXECVE {st} argc={len(argv)} " + " ".join(f"a{i}={a(v)}" for i, v in enumerate(argv)),
        f"type=CWD {st} cwd=\"/home/alice\"",
        f"type=PATH {st} item=0 name={a(exe)} inode=1 dev=08:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL",
        f"type=PROCTITLE {st} proctitle=" + "\x00".join(argv).encode()[:128].hex().upper()])


def main():
    # 1) auditd raw log: bash -c '<descriptor>' (argv[2] has spaces/quotes -> hex) under sshd -> bash
    log = "\n".join([audit(901, 4100, 4000, ["-bash"], "/usr/bin/bash", "1760785190.001"),
                     audit(902, 4242, 4100, ["bash", "-c", sh_cmd("3a91c0d4", P1)], "/usr/bin/bash"),
                     "type=SYSCALL msg=audit(1760785201.500:903): arch=c000003e syscall=257 success=yes exit=3 "
                     "ppid=4100 pid=4242 comm=\"bash\" exe=\"/usr/bin/bash\" key=(null)"]) + "\n"
    (OUT / "proc_linux_auditd.log").write_text(log)
    # 2) decoy auditd: only openat/connect syscalls, no execve, benign hex proctitle
    dec = ("type=SYSCALL msg=audit(1760785300.010:950): arch=c000003e syscall=42 success=yes exit=0 ppid=1 pid=700 "
           "comm=\"curl\" exe=\"/usr/bin/curl\" key=\"net\"\ntype=SOCKADDR msg=audit(1760785300.010:950): "
           "saddr=02000050C0A80001\ntype=PROCTITLE msg=audit(1760785300.010:950): proctitle="
           + "\x00".join(["curl", "-s", "https://updates.example.invalid/check?theme=dark"]).encode().hex().upper()
           + "\n")
    (OUT / "proc_linux_auditd_decoy.log").write_text(dec)
    # 3) osquery process_events results log (NDJSON, json.dumps escapes the quotes)
    rows = [{"name": "pack_proc_process_events", "hostIdentifier": "lnx-07", "calendarTime":
             "Sat Oct 18 11:00:00 2026 UTC", "unixTime": 1760785200, "epoch": 0, "counter": i, "numerics": False,
             "columns": c, "action": "added"} for i, c in enumerate([
                 {"pid": "5100", "parent": "1", "path": "/usr/sbin/cron", "cmdline": "/usr/sbin/cron -f",
                  "uid": "0", "cwd": "/", "time": "1760785190"},
                 {"pid": "5150", "parent": "5100", "path": "/usr/bin/python3", "uid": "0", "cwd": "/tmp",
                  "time": "1760785200", "cmdline": "python3 -c 'Codec_6e02b7f1 = \"hex_compact|xor_5a|\"; "
                  f"Material_6e02b7f1 = \"{enc(P2)}\"; print(Material_6e02b7f1)'"}])]
    (OUT / "proc_linux_osquery.ndjson").write_text("".join(json.dumps(r) + "\n" for r in rows))
    # 4) Procmon CSV (csv.writer QUOTE_ALL doubles the command line's quotes)
    b = io.StringIO()
    w = csv.writer(b, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    w.writerow(["Time of Day", "Process Name", "PID", "Operation", "Path", "Result", "Detail"])
    pc = (f'powershell.exe -NoP -Command "$Codec_0c5d2e88 = "hex_compact|xor_5a|"; $Material_0c5d2e88 = '
          f'"{enc(P3)}"; Write-Output $Material_0c5d2e88"')
    w.writerow(["11:00:00.1000000 AM", "WINWORD.EXE", "3120", "RegQueryValue", r"HKCU\Software\Microsoft\Office",
                "SUCCESS", "Type: REG_SZ, Length: 12, Data: 16.0"])
    w.writerow(["11:00:01.2000000 AM", "WINWORD.EXE", "3120", "Process Create",
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "SUCCESS",
                f"PID: 6812, Command line: {pc}"])
    w.writerow(["11:00:01.2100000 AM", "powershell.exe", "6812", "Process Start", "", "SUCCESS",
                f"Parent PID: 3120, Command line: {pc}, Current directory: C:\\Users\\bob\\, Environment: "])
    w.writerow(["11:00:09.0000000 AM", "powershell.exe", "6812", "Process Exit", "", "SUCCESS",
                "Exit Status: 0, User Time: 0.1 seconds, Kernel Time: 0.0 seconds"])
    (OUT / "proc_linux_procmon.csv").write_text(b.getvalue())
    # 5) Sysmon for Linux EID 1 in syslog (xml.sax.saxutils.escape renders the argv quotes as &quot;)
    from xml.sax.saxutils import escape
    sc = "/bin/sh -c " + sh_cmd("4d7e2a10", P5)

    def sx(rid, data):
        d = "".join(f"<Data Name=\"{k}\">{escape(v, {chr(34): '&quot;'})}</Data>" for k, v in data)
        return (f"Oct 18 11:00:0{rid} lnx-07 sysmon: <Event><System><Provider Name=\"Linux-Sysmon\" Guid=\"{{ff032593-"
                f"a8d3-4f13-b0d6-01fc615a0f97}}\"/><EventID>1</EventID><Version>5</Version><Level>4</Level><Task>1</Task>"
                f"<TimeCreated SystemTime=\"2026-10-18T11:00:0{rid}.000000000Z\"/><EventRecordID>{rid}</EventRecordID>"
                f"<Channel>Linux-Sysmon/Operational</Channel><Computer>lnx-07</Computer></System><EventData>{d}"
                f"</EventData></Event>")
    (OUT / "proc_linux_sysmon.log").write_text("\n".join([
        sx(1, [("UtcTime", "2026-10-18 11:00:01.000"), ("ProcessGuid", "{9d0b2c11-0001-0000-1000-000000000000}"),
               ("ProcessId", "7300"), ("Image", "/usr/bin/bash"), ("CommandLine", "bash"), ("User", "alice"),
               ("ParentProcessId", "7200"), ("ParentImage", "/usr/sbin/sshd"), ("ParentCommandLine", "sshd: alice")]),
        sx(2, [("UtcTime", "2026-10-18 11:00:02.000"), ("ProcessGuid", "{9d0b2c11-0002-0000-1000-000000000000}"),
               ("ProcessId", "7342"), ("Image", "/bin/dash"), ("CommandLine", sc), ("User", "alice"),
               ("ParentProcessId", "7300"), ("ParentImage", "/usr/bin/bash"), ("ParentCommandLine", "bash")])]) + "\n")
    # 6) real ps / pstree forest: sh(descriptor in argv) -> sleep, under a bash parent
    s = sh_cmd("91aa4b3c", P4).replace('echo "$Material_91aa4b3c"', "sleep 30; :")
    # the parent gets the descriptor through $X so it appears once (in sh's argv), not in bash's too
    p = subprocess.Popen(["bash", "-c", 'sh -c "$X" & sleep 30; wait'], env={"X": s, "PATH": "/usr/bin:/bin"})
    time.sleep(0.7)
    try:
        q = subprocess.run(["ps", "-o", "pid=", "--ppid", str(p.pid)], capture_output=True, text=True).stdout.split()
        q += subprocess.run(["ps", "-o", "pid=", "--ppid", ",".join(q)], capture_output=True, text=True).stdout.split()
        pids = ",".join([str(p.pid)] + q)
        ps1 = subprocess.run(["ps", "uf", "-p", pids], capture_output=True, text=True).stdout   # auxf columns
        (OUT / "proc_linux_ps_auxf.txt").write_text(ps1)
        (OUT / "proc_linux_ps_eo.txt").write_text(subprocess.run(
            ["ps", "-o", "pid,ppid,user,cmd", "--forest", "-p", pids], capture_output=True, text=True).stdout)
        (OUT / "proc_linux_pstree.txt").write_text(subprocess.run(
            ["pstree", "-p", str(p.pid)], capture_output=True, text=True).stdout)
        (OUT / "proc_linux_pstree_a.txt").write_text(subprocess.run(
            ["pstree", "-apl", str(p.pid)], capture_output=True, text=True).stdout)
        print("root pid", p.pid)
    finally:
        subprocess.run(["pkill", "-P", str(p.pid)])
        p.kill()


main()
