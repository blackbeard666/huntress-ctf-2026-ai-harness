"""Writes the corpus_graph fixtures (stdlib json): a 6-member toy corpus -- PS -> python via $HandoffId, python ->
jsp, jsp -> powershell (the cycle), a jsp_beanshell-hosted beanshell member (the one bridge, host jsp>beanshell), a
second PS member, a plan-less note -- plus decoys (non-JSON text; two equally balanced bridges = no unique answer).
expected comes from cg_oracle.py (networkx).  usage: python3 -I cg_gen.py <outdir>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cg_oracle  # noqa: E402

out = sys.argv[1]
TOY = {
    "plans": {
        "set1/a.ps1": "v=3|language=powershell|next_language=python|campaign_id=camp-77",
        "set1/b.py": "v=3|language=python|handoff_id=PSPY-0A1B|next_language=jsp|campaign_id=camp-77",
        "set1/e.jsp": "v=3|language=jsp|next_language=powershell",
        "set1/d.bsh": "v=3|language=beanshell|host_profile=jsp_beanshell",
        "set1/f.ps1": "v=3|language=powershell|next_language=python",
    },
    "texts": {
        "set1/a.ps1": "$HandoffId = 'PSPY-0A1B'\n$Interpreter = 'python.exe'\n",
        "set1/g.txt": "inert analyst note\n",
    },
}
TIE = {"plans": {   # path powershell-python-jscript-vbscript-perl: 4 bridges, two equally balanced -> no answer
    "p.ps1": "v=3|language=powershell|next_language=python",
    "q.py": "v=3|language=python|next_language=jscript",
    "r.js": "v=3|language=jscript|next_language=vbscript",
    "s.vbs": "v=3|language=vbscript|next_language=perl",
    "t.pl": "v=3|language=perl"}}
fx = [
    ("cg_toy_bridge", TOY, "bridge", "language", False),
    ("cg_toy_articulation", TOY, "articulation", "language", False),
    ("cg_toy_betweenness", TOY, "max_betweenness_edge", "language", False),
    ("cg_toy_most_reached", TOY, "most_reached_language", "language", False),
    ("cg_toy_member_bridge", TOY, "bridge", "member", False),
    ("cg_toy_member_components", TOY, "components", "member", False),
    ("cg_decoy_tie", TIE, "bridge", "language", True),
    ("cg_decoy_text", "$HandoffId = 'PSPY-0A1B'  # a script, not a corpus", "bridge", "language", True),
]
for name, corpus, q, lvl, decoy in fx:
    d = {"decoy": decoy, "material": corpus if isinstance(corpus, str) else json.dumps(corpus, indent=1, sort_keys=True),
         "rep": "corpus_graph", "transform": q, "key": lvl, "expected": None,
         "note": "corpus-language-graph-bridge: lib.codec.corpus_graph + graph_answer over a toy {plans, texts} corpus",
         "generator_cmd": "python3 -I tests/data/script_fixtures/cg_gen.py tests/data/script_fixtures  (stdlib json)",
         "oracle_cmd": f"python3 -I tests/data/script_fixtures/cg_oracle.py tests/data/script_fixtures/{name}.json"
                       "  (own k=v parsing + networkx bridges/articulation_points/edge_betweenness/descendants)"}
    if not decoy:
        d["expected"] = cg_oracle.answer(d)
    else:
        assert cg_oracle.answer(d) is None, name
    with open(os.path.join(out, name + ".json"), "w") as f:
        json.dump(d, f, indent=1)
        f.write("\n")
    print(name, d["expected"])
