"""Build observed-fetch log fixtures for lib.codec.observed_fetches / fetch_processes (stdlib writers, no lib.*):
Sysmon EID 3/22 exported XML (wevtutil qe /f:xml shape) and JSON (winlogbeat + Get-WinEvent|ConvertTo-Json shapes),
IIS W3C '#Fields:', squid native access.log, Apache vhost_combined + proxy CONNECT. `expected` comes from an independent
reader (xml.etree XPath / jq / gawk), never from lib.codec.
Run: python3 -I tests/data/script_fixtures/netlogs/netlog_gen.py"""
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = "http://schemas.microsoft.com/win/2004/08/events/event"


def sysmon_xml(events):
    root = ET.Element("Events")
    for eid, data in events:
        ev = ET.SubElement(root, "Event", xmlns=NS)
        sy = ET.SubElement(ev, "System")
        ET.SubElement(sy, "Provider", Name="Microsoft-Windows-Sysmon")
        ET.SubElement(sy, "EventID").text = str(eid)
        ed = ET.SubElement(ev, "EventData")
        for k, v in data.items():
            ET.SubElement(ed, "Data", Name=k).text = v
    return ET.tostring(root, encoding="unicode")


EV = [(1, {"Image": r"C:\Windows\System32\cmd.exe", "CommandLine": "cmd /c whoami"}),
      (22, {"Image": r"C:\Users\bob\AppData\Roaming\upd.exe", "QueryName": "cdn.stage-two.example",
            "QueryResults": "type:  5 edge.cdnhost.example;::ffff:203.0.113.70;", "QueryStatus": "0"}),
      (3, {"Image": r"C:\Users\bob\AppData\Roaming\upd.exe", "Protocol": "tcp", "SourceIp": "10.0.0.5",
           "DestinationIsIpv6": "false", "DestinationIp": "203.0.113.77", "DestinationHostname": "-",
           "DestinationPort": "443"}),
      (3, {"Image": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "Protocol": "tcp",
           "SourceIp": "10.0.0.5", "DestinationIp": "198.51.100.9", "DestinationHostname": "pay.loader-x.example",
           "DestinationPort": "8080"}),
      (3, {"Image": r"C:\Windows\System32\mshta.exe", "Protocol": "tcp", "SourceIp": "10.0.0.5",
           "DestinationIp": "192.0.2.44", "DestinationHostname": "", "DestinationPort": "80"})]


def py_oracle(path):
    code = ("import sys,json,xml.etree.ElementTree as E;n='{%s}';r=E.parse(sys.argv[1]).getroot();o={}\n"
            "for e in r.iter(n+'Event'):\n"
            " i=e.find(n+'System/'+n+'EventID').text;d={x.get('Name'):(x.text or '') for x in e.iter(n+'Data')}\n"
            " v=d.get('QueryName') if i=='22' else ((d.get('DestinationHostname') or '-').strip('-') or "
            "d.get('DestinationIp')) if i=='3' else None\n"
            " v and o.setdefault(v,d['Image'])\n"
            "print(json.dumps(o))") % NS
    cmd = ["python3", "-I", "-c", code, str(path)]
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout), \
        "python3 -I -c '<xml.etree: Event/System/EventID 3 -> DestinationHostname (or DestinationIp when -/empty), " \
        "22 -> QueryName; value -> Data[Image]>' " + path.name


def jq(path, prog, slurp=False):
    fl = ["-c", "-s"] if slurp else ["-c"]
    out = subprocess.run(["jq", *fl, prog, str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out), f"jq {' '.join(fl)} '{prog}' {path.name}"


def gawk(path, prog):
    out = subprocess.run(["gawk", prog, str(path)], capture_output=True, text=True, check=True).stdout
    return {ln: None for ln in out.splitlines() if ln}, f"gawk '{prog}' {path.name}"


def write(name, ext, blob, gen, oracle, decoy=False):
    p = HERE / f"{name}.{ext}"
    p.write_text(blob)
    exp, ocmd = oracle(p)
    fx = {"entry": "observed_fetches", "file": p.name, "expected": {"values": sorted(exp)},
          "expected_images": {k: v for k, v in exp.items() if v}, "decoy": decoy,
          "generator_cmd": "python3 -I tests/data/script_fixtures/netlogs/netlog_gen.py  (" + gen + ")",
          "oracle_cmd": ocmd}
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")
    print(name, json.dumps(fx["expected"]), fx["expected_images"])


write("nl_sysmon_xml", "xml", sysmon_xml(EV),
      "xml.etree writer, wevtutil-style <Events><Event xmlns=..> with EID 1/22/3/3/3", py_oracle)
write("nl_decoy_sysmon_eid1", "xml", sysmon_xml([EV[0], (11, {"Image": r"C:\x.exe",
                                                              "TargetFilename": r"C:\Users\bob\http_cache.txt"})]),
      "xml.etree writer: only EID 1 process-create + EID 11 file-create, no network event", py_oracle, decoy=True)

# winlogbeat NDJSON
wl = [{"@timestamp": "2026-10-18T10:00:0%dZ" % i, "event": {"code": str(eid)},
       "winlog": {"event_id": eid, "provider_name": "Microsoft-Windows-Sysmon", "event_data": d}} for i, (eid, d) in
      enumerate(EV)]
JQ = ('[.[] | select(.winlog.event_id==3 or .winlog.event_id==22) | .winlog.event_data | '
      '{(if .QueryName then .QueryName elif ((.DestinationHostname // "-") | test("^-?$")) then .DestinationIp '
      'else .DestinationHostname end): .Image}] | add')
write("nl_sysmon_winlogbeat", "events.json", "\n".join(json.dumps(x) for x in wl) + "\n",
      "json.dumps winlogbeat NDJSON (winlog.event_id + winlog.event_data)", lambda p: jq(p, JQ, slurp=True))

# Get-WinEvent | ConvertTo-Json: Id + rendered Message
gw = []
for eid, d in EV:
    title = {1: "Process Create:", 3: "Network connection detected:", 22: "Dns query:"}[eid]
    gw.append({"Id": eid, "ProviderName": "Microsoft-Windows-Sysmon", "LevelDisplayName": "Information",
               "Message": title + "\r\n" + "".join(f"{k}: {v}\r\n" for k, v in d.items())})
JQ2 = ('[.[] | select(.Id==3 or .Id==22) | [.Message | split("\\r\\n")[] | capture("^(?<key>\\\\w+): ?(?<value>.*)$")] '
       '| from_entries | {(if .QueryName then .QueryName elif (.DestinationHostname | test("^-?$")) then .DestinationIp '
       'else .DestinationHostname end): .Image}] | add')
write("nl_sysmon_getwinevent", "events.json", json.dumps(gw, indent=2),
      "json.dumps of a Get-WinEvent|ConvertTo-Json array (Id + rendered Message 'Key: value' lines)",
      lambda p: jq(p, JQ2))

iis = ("#Software: Microsoft Internet Information Services 10.0\n#Version: 1.0\n#Date: 2026-10-18 10:00:00\n"
       "#Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port cs-username c-ip cs(User-Agent) "
       "cs(Referer) cs-host sc-status sc-substatus sc-win32-status time-taken\n"
       "2026-10-18 10:00:01 10.1.1.20 GET /owa/auth/x.js - 443 - 10.0.0.5 "
       "Mozilla/5.0+(Windows+NT+10.0) - mail.corp-victim.example 200 0 0 15\n"
       "2026-10-18 10:00:02 10.1.1.20 POST /aspnet_client/shell.aspx cmd=whoami 443 - 10.0.0.66 "
       "curl/8.4.0 - mail.corp-victim.example 200 0 0 31\n"
       "2026-10-18 10:00:03 10.1.1.20 GET /favicon.ico - 80 - 10.0.0.7 Mozilla/5.0 - - 404 0 2 1\n")
AW_IIS = ('/^#Fields:/{for(i=2;i<=NF;i++)f[$i]=i-1;next} /^#/{next} {h=$f["cs-host"];if(h=="-")h=$f["s-ip"];'
          'q=$f["cs-uri-query"];print "http://" h $f["cs-uri-stem"] (q=="-"?"":"?" q)}')
write("nl_iis_w3c", "log", iis, "printf IIS 10 W3C extended log (#Fields header, cs-host '-' on one line)",
      lambda p: gawk(p, AW_IIS))

squid = ("1760781601.123    245 10.0.0.5 TCP_MISS/200 10234 GET http://dl.payload-host.example/a/stage2.bin - "
         "HIER_DIRECT/198.51.100.20 application/octet-stream\n"
         "1760781602.456  60012 10.0.0.5 TCP_TUNNEL/200 5512 CONNECT c2.tunnel-x.example:443 - "
         "HIER_DIRECT/203.0.113.9 -\n"
         "1760781603.001      0 10.0.0.8 TCP_DENIED/403 3900 GET http://blocked.example/ - HIER_NONE/- text/html\n")
AW_SQ = '{u=$7; if($6=="CONNECT"){sub(/:[0-9]+$/,"",u)} print u}'
write("nl_squid_native", "log", squid, "printf squid native access.log (MISS GET, CONNECT tunnel, DENIED)",
      lambda p: gawk(p, AW_SQ))

vh = ('www.shop-victim.example:443 10.0.0.5 - - [18/Oct/2026:10:00:01 +0000] "GET /wp-content/uploads/x.php?c=id '
      'HTTP/1.1" 200 512 "-" "python-requests/2.31"\n'
      'files.shop-victim.example:80 10.0.0.6 - - [18/Oct/2026:10:00:02 +0000] "GET /kit/drop.ps1 HTTP/1.1" 200 2048 '
      '"-" "WindowsPowerShell/5.1"\n'
      '10.0.0.9 - - [18/Oct/2026:10:00:03 +0000] "CONNECT exfil.proxy-out.example:8443 HTTP/1.1" 200 0 "-" "curl/8"\n')
AW_VH = ('{if($1 ~ /^[0-9.]+$/){split($7,a,":");print a[1];next} split($1,h,":");'
         'print (h[2]=="443"?"https":"http") "://" h[1] (h[2]=="443"||h[2]=="80"?"":":" h[2]) $8}')
write("nl_apache_vhost_combined", "log", vh,
      "printf Apache vhost_combined (%v:%p %h %l %u %t \"%r\" ...) + a combined proxy CONNECT line",
      lambda p: gawk(p, AW_VH))
write("nl_decoy_prose_log", "log",
      "2026-10-18 10:00:01 INFO service started on port 8080\n2026-10-18 10:00:02 WARN disk 91% full\n"
      "#Comment: nothing fetched here\n",
      "printf app log with no request / URL / host field",
      lambda p: gawk(p, '/https?:\\/\\//{print}'), decoy=True)
