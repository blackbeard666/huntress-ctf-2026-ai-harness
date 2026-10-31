"""Independent oracle for the corpus_graph fixtures: parses the toy corpus's k=v plans / PS variables itself and asks
networkx (bridges, articulation_points, edge_betweenness_centrality, connected components, descendants).
usage: python3 -I cg_oracle.py <fixture.json>  -> prints the answer for the fixture's transform/key."""
import json, re, sys
import networkx as nx

HOST = {"jsp_beanshell": ("jsp", "beanshell")}


def kv(s):
    return dict(p.split("=", 1) for p in str(s or "").split("|") if "=" in p)


def graphs(plans, texts):
    names = sorted(set(plans) | set(texts))
    lang = {m: kv(plans.get(m)).get("language") for m in names}
    L, M, D = nx.Graph(), nx.Graph(), nx.DiGraph()
    L.add_nodes_from(x for x in lang.values() if x)
    M.add_nodes_from(names)
    hid = {kv(plans.get(m)).get("handoff_id"): m for m in names if kv(plans.get(m)).get("handoff_id")}
    for m in names:
        p = kv(plans.get(m))
        ps = dict(re.findall(r"\$(\w+)\s*=\s*'([^']*)'", texts.get(m, "")))
        tgt = [hid[ps["HandoffId"]]] if ps.get("HandoffId") in hid else []
        if tgt:
            L.add_edge(lang[m], lang[tgt[0]]); D.add_edge(lang[m], lang[tgt[0]]); M.add_edge(m, tgt[0])
        elif p.get("next_language"):
            L.add_edge(lang[m], p["next_language"]); D.add_edge(lang[m], p["next_language"])
            M.add_edges_from((m, o) for o in names if lang[o] == p["next_language"] and o != m)
        if p.get("host_profile") in HOST:
            c, i = HOST[p["host_profile"]]
            L.add_edge(c, i); D.add_edge(c, i)
            M.add_edges_from((o, m) for o in names if lang[o] == c)
    camp = {}
    for m in names:
        if kv(plans.get(m)).get("campaign_id"):
            camp.setdefault(kv(plans[m])["campaign_id"], []).append(m)
    for ms in camp.values():
        for a in ms:
            for b in ms:
                if a < b:
                    M.add_edge(a, b); L.add_edge(lang[a], lang[b])
    return L, M, D, lang


def answer(fx):
    try:
        d = json.loads(fx["material"])
    except ValueError:
        return None
    L, M, D, lang = graphs(d.get("plans", {}), d.get("texts", {}))
    G = M if (fx.get("key") or "language").startswith("member") else L
    q = fx["transform"]
    dirn = lambda a, b: f"{a}>{b}" if D.has_edge(a, b) or (G is M) else f"{b}>{a}"
    if q == "bridge":
        br = list(nx.bridges(G))
        score = {}
        for e in br:   # the bridge that splits its component most evenly (2nd largest part after removal)
            H = G.copy(); H.remove_edge(*e)
            score[e] = sorted(len(c) for c in nx.connected_components(H))[-2]
        best = [e for e in br if score[e] == max(score.values())] if br else []
        if len(best) != 1:
            return None
        a, b = best[0]
        if G is M:   # member edge direction: host/exec from the jsp member
            return f"{a}>{b}" if lang[a] == "jsp" else f"{b}>{a}"
        return dirn(a, b)
    if q == "articulation":
        ap = list(nx.articulation_points(G))
        return ap[0] if len(ap) == 1 else None
    if q == "components":
        return str(nx.number_connected_components(G))
    if q == "max_betweenness_edge":
        eb = nx.edge_betweenness_centrality(G, normalized=False)
        (a, b), _ = max(eb.items(), key=lambda kv_: kv_[1])
        return dirn(a, b)
    if q == "most_reached_language":
        cnt = {}
        for m, p in d["plans"].items():
            if lang.get(m) and ("next_language" in kv(p) or "HandoffId" in d.get("texts", {}).get(m, "")):
                for v in nx.descendants(D, lang[m]) - {lang[m]}:
                    cnt[v] = cnt.get(v, 0) + 1
        return max(cnt, key=cnt.get)
    return None


if __name__ == "__main__":
    print(answer(json.load(open(sys.argv[1]))))
