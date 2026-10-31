"""Generator for the capstone-new-suffix-on-old-families fixtures (stdlib only): a toy 6-member corpus of k=v plans and
a finale-style contract whose ids are NEW suffixes on old families. Expected values come from sr_oracle.py (networkx +
collections, an independent reader), never from lib.codec.   Run: python3 sr_gen.py <outdir>"""
import json
import subprocess
import sys
from pathlib import Path

PLANS = {
    "evidence.zip/a.ps1": "v=3|role=loader|language=powershell|next_language=python|next_stage=b.py|"
                          "campaign_id=campaign-aa11|attack=T1059.001|loader_profile=reflective_stub",
    "evidence.zip/b.py": "v=3|role=loader|language=python|next_language=vbscript|next_stage=c.vbs|"
                         "campaign_id=campaign-aa11|attack=T1059.006",
    "evidence.zip/c.vbs": "v=3|role=dropper|language=vbscript|next_language=none|host_profile=hta|"
                          "campaign_id=campaign-bb22|attack=T1059.005",
    "evidence.zip/d.bsh": "v=3|role=benign_utility|language=beanshell|next_language=none|host_profile=jsp_beanshell|"
                          "campaign_id=campaign-bb22|attack=none",
    "evidence.zip/e.groovy": "v=3|role=dropper|language=groovy|next_language=none|host_profile=jenkins_pipeline|"
                             "campaign_id=campaign-bb22|attack=T1059",
    "evidence.zip/f.lua": "v=3|role=benign_utility|language=lua|next_language=none|attack=none",
}
Q = lambda i, text, art, kind="string": {"id": i, "question": text, "artifact": art,
                                         "answer_format": {"kind": kind}, "normalization": "trim"}
QUESTIONS = [
    Q("capstone-graph-bridge", "Rebuild the complete execution, host and evidence graph at the language level: which "
      "edge holds everything together? Answer src>dst.", "evidence.zip", "ordered_tokens"),
    Q("vbscript-host-language", "Which host container language runs c.vbs?", "evidence.zip -> c.vbs"),
    Q("python-parent", "Which member is the parent of b.py in the execution chain?", "evidence.zip -> b.py"),
    Q("corpus-distinct-languages", "How many distinct languages appear across the corpus?", "evidence.zip", "integer"),
    Q("powershell-loader-profile", "What loader profile does a.ps1 declare?", "evidence.zip -> a.ps1"),
    Q("graph-component-count", "How many connected components does the language graph have?", "evidence.zip",
      "integer"),
    # unknowns: must stay unanswered
    Q("capstone-entropy-score", "What is the Shannon entropy score of the corpus?", "evidence.zip", "string"),
    Q("powershell-mutation-vector", "Which mutation vector does a.ps1 use?", "evidence.zip -> a.ps1"),
]
STEPS = {"capstone-graph-bridge": "graph", "vbscript-host-language": "graph", "python-parent": "graph",
         "corpus-distinct-languages": "corpus", "powershell-loader-profile": "plan", "graph-component-count": "graph"}


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "corpus.json").write_text(json.dumps({"plans": PLANS, "contract": {"questions": QUESTIONS}}, indent=1))
    exp = json.loads(subprocess.check_output([sys.executable, "-I", str(Path(__file__).with_name("sr_oracle.py")),
                                              str(out / "corpus.json")]))
    mat = json.dumps({"contract": {"questions": QUESTIONS}, "plans": PLANS}, separators=(",", ":"))
    gen = "python3 tests/data/script_fixtures/sr_gen.py $TMPDIR/srgen  (stdlib k=v plans + contract json)"
    orc = "python3 -I tests/data/script_fixtures/sr_oracle.py $TMPDIR/srgen/corpus.json  (networkx bridges/" \
          "components + collections.Counter)"
    here = Path(__file__).parent
    for aid, val in exp.items():
        fx = {"_doc": "capstone-new-suffix-on-old-families: decode(material, 'suffix_route', <answer id>) routes an id "
                      "the carried solver leaves unanswered (plan > graph > corpus > lineage > none)",
              "material": mat, "rep": "suffix_route", "transform": aid, "key": None, "expected": val,
              "expected_step": STEPS.get(aid), "decoy": val is None, "generator_cmd": gen, "oracle_cmd": orc}
        (here / f"sr_{aid.replace('-', '_')}.json").write_text(json.dumps(fx, indent=1) + "\n")
    (here / "sr_contract.json").write_text(json.dumps({
        "_doc": "whole-contract fixture: route_contract(contract, plans) must answer exactly expected_routes (unknown "
                "ids absent) with the steps in expected_steps, in < 0.5 s; transform = one id so the lane gate checks it",
        "material": mat, "rep": "suffix_route", "transform": "capstone-graph-bridge", "key": None,
        "expected": exp["capstone-graph-bridge"], "decoy": False,
        "expected_routes": {k: v for k, v in exp.items() if v is not None}, "expected_steps": STEPS,
        "unanswered": [k for k, v in exp.items() if v is None],
        "generator_cmd": gen, "oracle_cmd": orc}, indent=1) + "\n")
    return exp


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1))
