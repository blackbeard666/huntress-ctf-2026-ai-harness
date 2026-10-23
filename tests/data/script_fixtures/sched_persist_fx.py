"""Writes sched_persist_*.json: material = descriptor bytes from sched_persist_gen.sh (heredocs / stdlib plistlib writer),
expected = an INDEPENDENT reader (PyYAML 6, croniter 6 [pip --target tools/pylib-cron], systemd-analyze, configparser,
xml.dom.minidom, xml.etree on the plist, grep -oP), never lib.codec. Generator tooling (offline), not in-window code.
Usage: PYTHONPATH=tools/pylib-cron python3 -I sched_persist_fx.py <descriptor dir> <fixture dir>"""
import json
import os
import subprocess
import sys

d, out = sys.argv[1], sys.argv[2]
CRONLIB = os.path.abspath("tools/pylib-cron")  # run from the repo root
CRONP = ("python3 -I -c \"import sys,yaml,datetime as D;sys.path.insert(0,'tools/pylib-cron');from croniter import croniter;"
         "c=%s;i=croniter(c,D.datetime(2026,1,5));a=i.get_next(float);print(int(i.get_next(float)-a))\" %s")
CRONL = ("python3 -I -c \"import sys,datetime as D;sys.path.insert(0,'tools/pylib-cron');from croniter import croniter;"
         "c=' '.join(open(sys.argv[1]).read().split('\\n')[%d].split()[:5]);i=croniter(c,D.datetime(2026,1,5));"
         "a=i.get_next(float);print(int(i.get_next(float)-a))\" %s")
YON = "y=yaml.safe_load(open(sys.argv[1]));on=y.get(True,y.get('on'))"
SA_CAL = ("systemd-analyze calendar --iterations=2 \"$(sed -n 's/^OnCalendar=//p' %s)\" | grep -oP '(?<=\\(in UTC\\): ).*'"
          " | head -2 | xargs -I{} date -d {} +%%s | paste -sd' ' | awk '{print $2-$1}'")
cases = [  # name, file, transform (field[@what][!filename]), key, oracle shell command
    ("gha_cron_period", "gha_cron.yml", "period", None,
     CRONP % ("yaml.safe_load(open(sys.argv[1]))[True]['schedule'][0]['cron']", "gha_cron.yml")),
    ("gha_cron_expr", "gha_cron.yml", "cron", None,
     "python3 -I -c \"import yaml,sys;%s;print(on['schedule'][0]['cron'])\" gha_cron.yml" % YON),
    ("gha_workflow_run_self", "gha_loop.yml", "self_trigger", None,
     "python3 -I -c \"import yaml,sys;%s;print(str(y['name'] in on['workflow_run']['workflows']).lower())\" gha_loop.yml"
     % YON),
    ("gha_dispatch_kind", "gha_dispatch.yml", "kind", "gha_schedule,gha_workflow_run,gha_repository_dispatch",
     "python3 -I -c \"import yaml,sys;%s;r=' '.join(s.get('run','') for s in y['jobs']['pong']['steps']);"
     "print('gha_repository_dispatch' if 'repository_dispatch' in on and '/dispatches' in r else 'none')\" gha_dispatch.yml"
     % YON),
    ("gitlab_schedule_job", "gitlab.yml", "job", None,
     "python3 -I -c \"import yaml,sys;y=yaml.safe_load(open(sys.argv[1]));print([k for k,v in y.items() if isinstance(v,dict)"
     " and 'schedule' in str(v.get('rules'))][0])\" gitlab.yml"),
    ("azure_schedule_cron", "azure.yml", "schedule", None,
     "python3 -I -c \"import yaml,sys;print(yaml.safe_load(open(sys.argv[1]))['schedules'][0]['cron'])\" azure.yml"),
    ("k8s_cronjob_period", "cronjob.yaml", "interval", None,
     CRONP % ("yaml.safe_load(open(sys.argv[1]))['spec']['schedule']", "cronjob.yaml")),
    ("k8s_cronjob_attack", "cronjob.yaml", "technique", "T1053.003,T1053.005,T1053.006,T1053.007,T1543.002",
     "python3 -I -c \"import yaml,sys;print({'CronJob':'T1053.007'}[yaml.safe_load(open(sys.argv[1]))['kind']])\" "
     "cronjob.yaml  (ATT&CK: Container Orchestration Job)"),
    ("systemd_oncalendar_period", "updater.timer", "period@OnCalendar", None, SA_CAL % "updater.timer"),
    ("systemd_timer_unit", "updater.timer", "target", None,
     "python3 -I -c \"import configparser,sys;c=configparser.ConfigParser();c.read(sys.argv[1]);print(c['Timer']['Unit'])\""
     " updater.timer"),
    ("systemd_unitactive_period", "sync.timer", "period", None,
     "systemd-analyze timespan \"$(sed -n 's/^OnUnitActiveSec=//p' sync.timer)\" | awk '/μs:/{print $2/1000000}'"),
    ("systemd_restart_kind", "watchdog.service", "mechanism!watchdog.service", "systemd_timer,systemd_restart,cron",
     "python3 -I -c \"import configparser,sys;c=configparser.ConfigParser();c.read(sys.argv[1]);"
     "print('systemd_restart' if c['Service']['Restart']=='always' else 'none')\" watchdog.service"),
    ("crontab_reboot_target", "crontab", "command@@reboot!crontab", None,
     "awk '$1==\"@reboot\"{$1=\"\";sub(/^ /,\"\");print}' crontab"),
    ("crond_user_period", "cron.d_sysupd", "period!/etc/cron.d/sysupd", None, CRONL % (2, "cron.d_sysupd")),
    ("bash_embedded_crontab", "install.sh", "period!install.sh", None,
     "grep -oP 'echo \"\\K[^\"]+' install.sh | python3 -I -c \"import sys,datetime as D;sys.path.insert(0,'tools/pylib-cron');"
     "from croniter import croniter;i=croniter(' '.join(sys.stdin.read().split()[:5]),D.datetime(2026,1,5));"
     "a=i.get_next(float);print(int(i.get_next(float)-a))\""),
    ("launchd_startinterval", "com.apple.softwareupdate.agent.plist", "interval", None,
     "python3 -I -c \"import xml.etree.ElementTree as E,sys;k=E.parse(sys.argv[1]).getroot()[0];c=list(k);"
     "print([c[i+1].text for i in range(0,len(c),2) if c[i].text=='StartInterval'][0])\" "
     "com.apple.softwareupdate.agent.plist"),
    ("launchd_label", "com.apple.softwareupdate.agent.plist", "label", None,
     "python3 -I -c \"import xml.etree.ElementTree as E,sys;k=E.parse(sys.argv[1]).getroot()[0];c=list(k);"
     "print([c[i+1].text for i in range(0,len(c),2) if c[i].text=='Label'][0])\" com.apple.softwareupdate.agent.plist"),
    ("schtask_xml_repetition", "task.xml", "period", None,
     "python3 -I -c \"import xml.dom.minidom as M,sys,re;t=M.parseString(open(sys.argv[1]).read().replace('UTF-16','UTF-8'));"
     "v=t.getElementsByTagName('Interval')[0].firstChild.data;h,m,s=re.fullmatch(r'PT(?:(\\d+)H)?(?:(\\d+)M)?(?:(\\d+)S)?',v)"
     ".groups();print(int(h or 0)*3600+int(m or 0)*60+int(s or 0))\" task.xml"),
    ("schtask_xml_command", "task.xml", "command", None,
     "python3 -I -c \"import xml.dom.minidom as M,sys;t=M.parseString(open(sys.argv[1]).read().replace('UTF-16','UTF-8'));"
     "g=lambda n:t.getElementsByTagName(n)[0].firstChild.data;print(g('Command'),g('Arguments'))\" task.xml"),
    ("schtask_xml_boot", "boot_task.xml", "trigger", "TimeTrigger,LogonTrigger,BootTrigger",
     "python3 -I -c \"import xml.dom.minidom as M,sys;t=M.parseString(open(sys.argv[1]).read().replace('UTF-16','UTF-8'));"
     "print([n.tagName for n in t.getElementsByTagName('Triggers')[0].childNodes if n.nodeType==1][0])\" boot_task.xml"),
    ("schtasks_cli_period", "persist.bat", "period", None,
     "grep -oiP '/sc \\Kminute /mo \\d+' persist.bat | awk '{print $3*60}'"),
    ("wmi_within", "filter.mof", "interval", None, "grep -oP 'WITHIN \\K\\d+' filter.mof"),
    ("wmi_consumer_cmd", "filter.mof", "command", None,
     "grep -oP 'CommandLineTemplate = \"\\K[^\"]+' filter.mof | sed 's/\\\\\\\\/\\\\/g'"),
    ("runkey_reg_target", "run.reg", "target", None,
     "grep -oP '^\"OneDriveHelper\"=\"\\K[^\"]+' run.reg | sed 's/\\\\\\\\/\\\\/g'"),
    ("runonce_cli_name", "runonce.cmd", "name", None, "grep -oP '/v \\K\\S+' runonce.cmd"),
    ("decoy_gha_push_only", "gha_benign.yml", "period", None,
     "python3 -I -c \"import yaml,sys;%s;print('schedule' in on or 'workflow_run' in on)\" gha_benign.yml  # False" % YON),
    ("decoy_plain_service", "plain.service", "kind", None,
     "python3 -I -c \"import configparser,sys;c=configparser.ConfigParser();c.read(sys.argv[1]);print(c['Service']"
     "['Restart'])\" plain.service  # no -> not persistent"),
    ("decoy_numeric_notes", "notes.txt", "period!notes.txt", None,
     "crontab -T notes.txt 2>&1 || true  # not a crontab (prose with numbers)"),
    ("decoy_info_plist", "Info.plist", "kind", None,
     "python3 -I -c \"import xml.etree.ElementTree as E,sys;print([e.text for e in E.parse(sys.argv[1]).getroot()[0]"
     "][::2])\" Info.plist  # no Label/Program/StartInterval"),
    ("decoy_benign_mof", "benign.mof", "kind", None, "grep -c '__EventFilter\\|__IntervalTimer' benign.mof || true  # 0"),
]
for name, f, tr, key, oc in cases:
    src = open("%s/%s" % (d, f), "rb").read().decode("utf-8")
    decoy = name.startswith("decoy")
    run = oc.split("  #")[0].split("  (")[0].replace("'tools/pylib-cron'", repr(CRONLIB))
    res = subprocess.run(run, shell=True, cwd=d, capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin", "PYTHONPATH": ""})
    exp = res.stdout.strip().splitlines()[0] if res.stdout.strip() else None
    if not decoy and not exp:
        sys.exit("oracle failed for %s: %s" % (name, res.stderr))
    if key and exp and not decoy:
        assert exp in key.split(","), (name, exp)
    fx = {"material": src, "rep": "schedule_entries", "transform": tr, "key": key,
          "expected": None if decoy else exp, "decoy": decoy,
          "note": "ci-schedule-persistence-model: lib.codec.schedule_entries/persistence_answer via decode(rep="
                  "'schedule_entries', transform=<field>[@what][!filename], key=<accepted csv>)" +
                  (" ; decoy -> no persistence row -> None (oracle stdout: %r)" % res.stdout.strip()[:60] if decoy else ""),
          "generator_cmd": "sh tests/data/script_fixtures/sched_persist_gen.sh <dir>  (writes %s: hand-authored heredoc%s;"
                           " no lib code); sched_persist_fx.py writes the json" % (
                               f, " via stdlib plistlib.dumps" if f.endswith(".plist") else ""),
          "oracle_cmd": "(cd <dir> && %s)" % oc}
    with open("%s/sched_persist_%s.json" % (out, name), "w") as fh:
        json.dump(fx, fh, indent=1)
    print(name, "->", repr(fx["expected"]))
