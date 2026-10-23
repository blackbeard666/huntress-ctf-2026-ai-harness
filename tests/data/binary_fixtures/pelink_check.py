"""Compare lib.binary.pe_link_facts / pe_link_pair on every pelink_*.json fixture. usage: python3 pelink_check.py"""
import glob, json, os, sys, time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import lib.binary as B  # noqa: E402

D = os.path.dirname(os.path.abspath(__file__))
bad = 0
for jf in sorted(glob.glob(os.path.join(D, "pelink_*.json"))):
    j = json.load(open(jf))
    data = open(jf[:-5] + ".bin", "rb").read()
    t = time.time()
    got = B.pe_link_facts(data)
    exp = j["expected_facts"]
    if exp is None:
        ok = got is None
        print(("ok  " if ok else "BAD ") + os.path.basename(jf), "None" if ok else got)
        bad += not ok
        continue
    if j.get("pair_with"):
        pr = B.pe_link_pair(data, open(os.path.join(D, j["pair_with"]), "rb").read()) or {}
        got = dict(got or {}, **{"pair:" + k: v for k, v in pr.items()})
    for k, v in exp.items():
        g = json.loads(json.dumps(got.get(k, "none")))
        if g != v:
            bad += 1
            print("BAD", os.path.basename(jf), k, "got", str(g)[:200], "want", str(v)[:200])
    hits = [h for h in B.hcfg_scan(data) if h.valid]
    if j["expected_config"] is not None and not (hits and hits[0].offset == j["expected_offset"]
                                                 and hits[0].config == j["expected_config"]):
        bad += 1
        print("BAD", os.path.basename(jf), "hcfg_scan", hits[:1])
    print("ok  " if not bad else "..  ", os.path.basename(jf), f"{time.time() - t:.3f}s")
sys.exit(1 if bad else 0)
