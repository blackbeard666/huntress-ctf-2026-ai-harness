"""Independent oracle: stdlib email.parser (compat32) headers + networkx connected_components + email.utils dates.
usage: python3 oracle_threads.py ZIP  -> JSON of groups / sorted / count / duplicates / roots"""
import io, json, re, sys, zipfile
from email.parser import BytesHeaderParser
from email.utils import parsedate_to_datetime
import networkx as nx

z = zipfile.ZipFile(sys.argv[1])
rows = []
for n in z.namelist():
    if not n.endswith(".eml"):
        continue
    h = BytesHeaderParser().parsebytes(z.read(n))
    ids = lambda v: re.findall(r"<[^<>\s]+>", str(v or ""))
    rows.append((parsedate_to_datetime(h["Date"]).timestamp(), n, ids(h["Message-ID"])[0],
                 ids(h["References"]) + ids(h["In-Reply-To"])))
rows.sort()
keep, dups, seen = [], [], set()
for r in rows:
    (dups if r[2] in seen else keep).append(r); seen.add(r[2])
G = nx.Graph()
for _, n, mid, refs in keep:
    G.add_node(mid); G.add_edges_from((mid, x) for x in refs)
comps = [c for c in nx.connected_components(G)]
groups = []
for c in comps:
    g = [r for r in keep if r[2] in c]
    if g: groups.append(g)
groups.sort(key=lambda g: (g[0][0], g[0][1]))
present = {r[2] for r in keep}
roots = [next((r[1] for r in g if not (set(r[3]) & present)), g[0][1]) for g in groups]
names = [[r[1] for r in g] for g in groups]
print(json.dumps({"groups": names, "sorted": sorted(sorted(g) for g in names), "count": len(names),
                  "duplicates": sorted(r[1] for r in dups), "roots": roots}, separators=(",", ":")))
