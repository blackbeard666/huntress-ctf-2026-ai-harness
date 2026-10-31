"""Replay d30_single_facts.json: lib.binary.campaign_set_facts over the D30 single evidence must reproduce every
GM-confirmed per-group config and the derived set facts.  Run: .venv/bin/python tests/data/binary_fixtures/campaign_set/check_d30.py"""
import hashlib, json, os, sys
from pathlib import Path
R = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(R), str(R / "challenges/day30/binary-campaign-trail/solver")]
os.environ.setdefault("HCTF_SOLVER_PARALLEL", "0")
import solve as S, lib.binary as B  # noqa: E402
X = json.load(open(Path(__file__).with_name("d30_single_facts.json")))
ms = [(n, bytes(b)) for n, b in S.resolve(S.unzip((R / X["case"].split(" ")[0] / "artifacts/evidence.zip").read_bytes(),
                                                  lazy=False))]
F = B.campaign_set_facts(ms)
bad = [(g, k, v, F["groups"][g]["consensus"][k]) for g, c in X["consensus"].items() for k, v in c.items()
       if v is not None and v != (F["groups"][g]["consensus"][k] or "none")]
bad += [(k, X[k], F[k]) for k in ("distinct_campaign_count", "distinct_member_campaign_count") if X[k] != F[k]]
bad += [("campaign_by_day", F["campaign_by_day"])] if F["campaign_by_day"] != X["campaign_by_day"] else []
bad += [("shared", F["shared_campaign_groups"])] if F["shared_campaign_groups"] != X["shared_campaign_groups"] else []
sha = hashlib.sha256("\n".join(sorted(F["campaign_by_day"])).encode()).hexdigest()
bad += [("sha", sha)] if sha != X["campaigns_sorted_lf_sha256"] else []
print("FAIL", bad) if bad else print("ok d30 campaign set facts stable vs GM-confirmed configs")
sys.exit(1 if bad else 0)
