"""Independent oracle for the suffix-route fixtures: networkx (graph) + collections.Counter (counts) over the k=v plans
of corpus.json, per the corpus-graph rules: execution = next_stage -> member; host = host container -> member language
(hta>vbscript, jsp>beanshell, jenkins_pipeline>groovy); evidence = two members sharing a campaign_id; all folded to the
language level.  Run: python3 -I sr_oracle.py corpus.json  -> {answer_id: expected|null}"""
import json
import sys
from collections import Counter

import networkx as nx

d = json.load(open(sys.argv[1]))
plans = {m: dict(kv.split("=", 1) for kv in p.split("|")) for m, p in d["plans"].items()}
leaf = lambda m: m.rsplit("/", 1)[-1]
HOST = {"hta": "hta", "jsp_beanshell": "jsp", "jenkins_pipeline": "jenkins_pipeline"}
lang = {m: p["language"] for m, p in plans.items()}
G = nx.Graph()
G.add_nodes_from(lang.values())
exec_edges = []
for m, p in plans.items():
    tgt = [o for o in plans if leaf(o) == p.get("next_stage")]
    if tgt:
        exec_edges.append((m, tgt[0]))
        G.add_edge(lang[m], lang[tgt[0]], d=(lang[m], lang[tgt[0]]))
    if p.get("host_profile"):
        G.add_edge(HOST[p["host_profile"]], lang[m], d=(HOST[p["host_profile"]], lang[m]))
by_c = {}
for m, p in plans.items():
    by_c.setdefault(p.get("campaign_id"), []).append(m)
for c, ms in by_c.items():
    for i, a in enumerate(ms):
        for b in ms[i + 1:]:
            if c and lang[a] != lang[b] and not G.has_edge(lang[a], lang[b]):
                G.add_edge(lang[a], lang[b], d=(lang[a], lang[b]))
base = nx.number_connected_components(G)
best, score = None, -1
for u, v in nx.bridges(G):
    H = G.copy()
    H.remove_edge(u, v)
    s = sorted(len(c) for c in nx.connected_components(H))[-2]
    best, score = ((G[u][v]["d"], s) if s > score else (best, score))
print(json.dumps({
    "capstone-graph-bridge": ">".join(best),
    "vbscript-host-language": HOST[plans["evidence.zip/c.vbs"]["host_profile"]],
    "python-parent": leaf(next(a for a, b in exec_edges if leaf(b) == "b.py")),
    "corpus-distinct-languages": str(len(Counter(lang.values()))),
    "powershell-loader-profile": plans["evidence.zip/a.ps1"]["loader_profile"],
    "graph-component-count": str(base),
    "capstone-entropy-score": None,
    "powershell-mutation-vector": None,
}))
