"""Build equivalence fixtures from the GM-verified D16 single-solve answers (stdlib only, no lib.*).
Each member's plan is re-written as the v=3 'k=v|..' text the scripts carry (identity fields included, so the
canonicaliser must drop them). `expected` comes from the independent Counter oracle below, not from lib.codec.
Run: python3 -I tests/data/script_fixtures/equivalence/eq_gen.py"""
import collections, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EXP = ROOT / "challenges/day16/scripting-same-same-but-different/solver/cases/single_solve/expected.json"
GEN = "python3 -I tests/data/script_fixtures/equivalence/eq_gen.py  (D16 single 89161077 GM-verified expected.json -> v=3 k=v plans)"
ORACLE = ("python3 -I -c \"import json,collections as C;f=json.load(open(F));P={m:dict(x.split('=',1) for x in p.split('|')) "
          "for m,p in f['plans'].items()};[print(k,C.Counter(p.get(k) for p in P.values())) for k in "
          "('role','attack','adapter','next_language','steps','stage_profile','stage_count')]\"  (minority on a field "
          ">=2/3 unanimous = outlier; distinct (role,attack,adapter,next_language) tuples = plot classes)")
NAMES = {"stage-count": "stage_count", "next-language": "next_language", "campaign": "campaign_id",
         "file-path": "file_path", "host-profile": "host_profile", "obfuscation": "obfuscation_profile",
         "stage-profile": "stage_profile"}
EXT = {"applescript": "applescript", "autoit": "au3", "lua": "lua", "msbuild_xml": "proj", "perl": "pl", "php": "php",
       "ruby": "rb", "typescript": "ts", "wmi_mof": "mof"}


def oracle(plans):
    P = {m: dict(x.split("=", 1) for x in p.split("|")) for m, p in plans.items()}
    outl, diffs, maj = set(), {}, {}
    for k in ("role", "attack", "adapter", "next_language", "steps", "stage_profile", "stage_count"):
        c = collections.Counter(p.get(k) for p in P.values())
        top, n = c.most_common(1)[0]
        if n >= 2 / 3 * len(P):
            maj[k] = top
            for m, p in P.items():
                if p.get(k) != top:
                    diffs.setdefault(m, {})[k] = p.get(k)
    plot = {tuple(p.get(k) for k in sorted(maj)) for p in P.values()}
    full = {tuple(p.get(k) for k in ("role", "attack", "adapter", "next_language", "steps", "stage_profile",
                                     "stage_count")) for p in P.values()}
    return {"outliers": sorted(diffs), "diffs": diffs, "plot_class_count": len(plot), "class_count": len(full)}


e = json.loads(EXP.read_text())
mem = collections.defaultdict(dict)
for k, v in e.items():
    m = re.match(r"polyglot-([a-z_]+)-(benign-utility|downloader|launcher|staged-chain)-(.+)", k)
    if m:
        mem[(m[2], m[1])][m[3]] = v
for fam in ("benign-utility", "downloader", "launcher", "staged-chain"):
    plans = {}
    for (f, lang), fields in sorted(mem.items()):
        if f == fam:
            kv = ["v=3"] + [f"{NAMES.get(a, a.replace('-', '_'))}={b}" for a, b in fields.items()]
            plans[f"polyglot-{lang}-{fam}.{EXT[lang]}"] = "|".join(kv)
    fx = {"entry": "equivalence", "plans": plans, "expected": oracle(plans), "decoy": False,
          "generator_cmd": GEN, "oracle_cmd": ORACLE.replace("F", f"'tests/data/script_fixtures/equivalence/eq_d16_{fam}.json'")}
    (HERE / f"eq_d16_{fam}.json").write_text(json.dumps(fx, indent=1) + "\n")
    print(fam, fx["expected"]["outliers"], fx["expected"]["diffs"])
# decoy: one readable plan beside benign noise / truncated text -> fewer than 2 comparable plans -> None
dec = {"README.txt": "This folder holds sample scripts for the lab.", "notes.md": "# notes\nnothing here",
       "polyglot-php-downloader.php": next(iter(json.loads((HERE / "eq_d16_downloader.json").read_text())["plans"].values())),
       "trunc.lua": "v=3|camp"}
(HERE / "eq_decoy_one_plan.json").write_text(json.dumps(
    {"entry": "equivalence", "plans": dec, "expected": None, "decoy": True, "generator_cmd": GEN + " (decoy: 1 plan + noise)",
     "oracle_cmd": "python3 -I -c \"import json;f=json.load(open('tests/data/script_fixtures/equivalence/eq_decoy_one_plan.json'));"
                   "print(sum('role=' in p for p in f['plans'].values()))\"  (1 comparable plan < 2 -> no equivalence)"},
    indent=1) + "\n")
