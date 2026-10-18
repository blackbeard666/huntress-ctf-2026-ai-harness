"""Build network-evidence-reconcile fixtures from the GM-verified D17 single (Fetch Quest) url / upload-url answers
(stdlib only, no lib.*). Each member's plan is the v=3 'k=v|..' text; the observed side is written with stdlib json
(HAR) / a TSV writer (Zeek http.log) / dict records, with one fetch dropped or added. `expected` comes from the
jq / awk / sed + comm oracles run below, never from lib.codec.
Run: python3 -I tests/data/script_fixtures/reconcile/rc_gen.py"""
import json, subprocess, zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D17 = ROOT / "challenges/day17/scripting-fetch-quest"
GEN = "python3 -I tests/data/script_fixtures/reconcile/rc_gen.py  (D17 single b996e1ea GM-verified url/upload-url -> plans; "
c = json.loads((D17 / "single_solve/contract.json").read_text())
e = json.loads((D17 / "solver/cases/single_solve/expected.json").read_text())
plans, urls = {}, {}
for q in c["questions"]:
    i = q["id"]
    if i in e and (i.endswith("-url")):
        m = q["artifact"].split("->")[-1].strip()
        f = "upload_url" if i.endswith("-upload-url") else "url"
        role = e.get(i[:-len("-upload-url" if f == "upload_url" else "-url")] + "-role", "unknown")
        plans[m] = f"v=3|role={role}|{f}={e[i]}|host_id=host-{zlib.crc32(m.encode()):010d}|next_stage=stage-{len(plans)}.ps1"
        urls[m] = e[i]
members = sorted(urls)
drop = members[5]


def sh(cmd, stdin):
    return subprocess.run(["bash", "-c", cmd], input=stdin, capture_output=True, text=True, check=True).stdout


def declared_file():
    p = HERE / "_declared.txt"
    p.write_text("\n".join(sorted(urls.values())) + "\n")
    return p


def write(name, observed, expected, gen, oracle, decoy=False):
    fx = {"entry": "reconcile", "plans": plans, "observed": observed, "expected": expected, "decoy": decoy,
          "generator_cmd": GEN + gen + ")", "oracle_cmd": oracle}
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")


dec = declared_file()
# A: HAR, one member's fetch missing; another url spelled with an uppercase host and an explicit :443
har_urls = [u for m, u in sorted(urls.items()) if m != drop]
har_urls[0] = har_urls[0].replace("https://", "https://").split("/", 3)
har_urls[0] = f"https://{har_urls[0][2].upper()}:443/{har_urls[0][3]}"
har = {"log": {"version": "1.2", "creator": {"name": "rc_gen", "version": "1"},
               "entries": [{"request": {"method": "GET", "url": u, "headers": []}, "response": {"status": 200}}
                           for u in har_urls]}}
oracle_a = ("jq -r '.log.entries[].request.url' | sed -E 's#^(https?://)([^/:]+)(:443|:80)?#\\1\\L\\2#' | sort -u "
            "| comm -3 _declared.txt -")
out = sh(f"cd {HERE} && " + oracle_a, json.dumps(har)).split("\n")
one = [x.strip() for x in out if x.strip()]
write("rc_har_drop", json.dumps(har), {"indicator": one[0] if len(one) == 1 else None,
                                        "unfetched": [m for m, u in urls.items() if u in one], "one_sided": len(one)},
      "HAR via json.dumps, member %s dropped, host case/:443 respelled" % drop,
      "jq -r '.log.entries[].request.url' <HAR | sed -E 's#^(https?://)([^/:]+)(:443|:80)?#\\1\\L\\2#' | sort -u | "
      "comm -3 declared.txt -  -> %r" % one)
# B: Zeek http.log, every fetch seen + one extra request nobody declared
extra_host, extra_uri = "cdn-ffee00aa11.example.invalid", "/0badc0ffee00.bin"
rows = []
for u in sorted(urls.values()):
    h, p = u.split("://", 1)[1].split("/", 1)
    rows.append(("1792240000.0", "Cxx", "10.0.0.5", "49152", "203.0.113.7", "80", "GET", h, "/" + p))
rows.insert(17, ("1792240001.0", "Cyy", "10.0.0.5", "49153", "203.0.113.9", "80", "GET", extra_host, extra_uri))
zeek = ("#separator \\x09\n#path\thttp\n#fields\tts\tuid\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tmethod\thost\turi\n"
        "#types\ttime\tstring\taddr\tport\taddr\tport\tstring\tstring\tstring\n"
        + "".join("\t".join(r) + "\n" for r in rows) + "#close\t2026-10-17-00-00-00\n")
oracle_b = ("awk -F'\\t' '!/^#/{print $8 $9}' | sort -u > _obs.txt; sed -E 's#^https?://##' _declared.txt | sort -u "
            "| comm -13 - _obs.txt")
one_b = [x for x in sh(f"cd {HERE} && " + oracle_b, zeek).split("\n") if x]
write("rc_zeek_extra", zeek, {"indicator": ["http://" + x for x in one_b][0] if len(one_b) == 1 else None,
                              "unfetched": [], "one_sided": len(one_b)},
      "Zeek http.log TSV written by hand, every declared fetch + one undeclared GET",
      "awk -F'\\t' '!/^#/{print $8 $9}' http.log | sort -u | comm -13 <(sed -E 's#^https?://##' declared.txt|sort -u) - "
      " -> %r (observed-only; Zeek http is http://)" % one_b)
# C: network_indicators()-style records, defanged; the dropped member's host only shows up as a DNS query
recs = [{"kind": "http", "url": u.replace("https://", "hxxps://").replace(".example.", "[.]example[.]"),
         "src_member": "proxy.csv"} for m, u in sorted(urls.items()) if m != drop]
recs.append({"kind": "dns", "host": urls[drop].split("/")[2].replace(".", "[.]"), "src_member": "dns.log"})
oracle_c = ("jq -r '.[]|select(.kind==\"http\").url' | sed -e 's/^hxxp/http/' -e 's/\\[\\.\\]/./g' | sort -u | "
            "comm -23 _declared.txt -")
one_c = [x for x in sh(f"cd {HERE} && " + oracle_c, json.dumps(recs)).split("\n") if x]
write("rc_records_defanged_dnsonly", recs,
      {"indicator": one_c[0] if len(one_c) == 1 else None, "unfetched": [m for m, u in urls.items() if u in one_c],
       "one_sided": len(one_c), "hosts_declared_only": 0},
      "dict records, hxxps + [.] defanged, member %s only as a DNS query" % drop,
      "jq -r '.[]|select(.kind==\"http\").url' recs.json | sed -e 's/^hxxp/http/' -e 's/\\[\\.\\]/./g' | sort -u | "
      "comm -23 declared.txt -  -> %r (URL never fetched; its host resolved, so host level has no one-sided)" % one_c)
# D (decoy): every declared fetch observed exactly -> nothing one-sided
full = [{"kind": "http", "url": u} for u in sorted(urls.values())]
oracle_d = "jq -r '.[].url' | sort -u | comm -3 _declared.txt - | wc -l"
n_d = int(sh(f"cd {HERE} && " + oracle_d, json.dumps(full)).strip())
write("rc_decoy_all_seen", full, {"indicator": None, "unfetched": [], "one_sided": n_d},
      "dict records of every declared url, nothing dropped", "jq -r '.[].url' | sort -u | comm -3 declared.txt - | wc -l"
      "  -> %d" % n_d, decoy=True)
# E (decoy): evidence without any network indicator -> no report
write("rc_decoy_no_network", "proxy log rotated; no requests recorded\n", None, "plain text without URLs/hosts",
      "grep -cE 'https?://|^host:' <evidence  -> 0 (no observed side, cannot reconcile)", decoy=True)
for p in ("_declared.txt", "_obs.txt"):
    (HERE / p).unlink(missing_ok=True)
print(len(plans), "plans; drop", drop, "| A", one, "| B", one_b, "| C", one_c, "| D", n_d)
