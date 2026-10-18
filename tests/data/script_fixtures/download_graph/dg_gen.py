"""Build download-graph fixtures from the GM-verified D17 single (Fetch Quest) url / file-path answers (stdlib only,
no lib.*). Each member's plan is v=3 'k=v|..' text; language / next_language / next_stage links are added here to form
the cross-file chain. `expected` comes from tsort (chain order), cut|sort -u|wc -l (distinct hosts), awk (the member
whose host nobody shares) and jq (edge counts) run below, never from lib.codec.
Run: python3 -I tests/data/script_fixtures/download_graph/dg_gen.py"""
import json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D17 = ROOT / "challenges/day17/scripting-fetch-quest"
GEN = "python3 -I tests/data/script_fixtures/download_graph/dg_gen.py  (D17 single GM-verified url/file-path -> plans; "
c = json.loads((D17 / "single_solve/contract.json").read_text())
e = json.loads((D17 / "solver/cases/single_solve/expected.json").read_text())
urls, paths = {}, {}
for q in c["questions"]:
    i, m = q["id"], q.get("artifact", "").split("->")[-1].strip()
    if i in e and i.endswith("-url") and not i.endswith("-upload-url"):
        urls[m] = e[i]
    if i in e and i.endswith("-file-path"):
        paths[m] = e[i]
U, P = sorted(urls.items()), sorted(paths.items())


def sh(cmd, stdin=""):
    return subprocess.run(["bash", "-c", cmd], input=stdin, capture_output=True, text=True, check=True).stdout.strip()


def write(name, plans, expected, gen, oracle, decoy=False):
    fx = {"entry": "download_graph", "plans": plans, "expected": expected, "decoy": decoy,
          "generator_cmd": GEN + gen + ")", "oracle_cmd": oracle}
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")


def edges_tsv(plans, a, b):
    """'src dst' lines for tsort from the plan text itself (awk over k=v pairs, not lib.codec)."""
    txt = "\n".join(f"{m}\t{p}" for m, p in plans.items())
    return sh(f"awk -F'\\t' '{{n=split($2,f,\"|\"); s=\"\"; d=\"\"; for(i=1;i<=n;i++){{split(f[i],kv,\"=\");"
              f" if(kv[1]==\"{a}\") s=kv[2]; if(kv[1]==\"{b}\") d=kv[2]}}; if(s!=\"\" && d!=\"\" && s!=d) print s, d}}'", txt)


# A: 4 members, language chain jscript>powershell>python>bash via next_language; each fetches a D17 url and writes a
#    D17 file_path; distinct hosts from cut -d/ -f3.
langs = ["jscript", "powershell", "python", "bash"]
names = ["loader.js", "stage2.ps1", "stage3.py", "final.sh"]
A = {}
for k, (m, ln) in enumerate(zip(names, langs)):
    nxt = langs[k + 1] if k + 1 < len(langs) else ln
    A[m] = (f"v=3|language={ln}|role=downloader|next_language={nxt}|stage_count={len(langs) - k}"
            f"|steps=acquire_remote,write_file,dispatch_process|url={U[k][1]}|file_path={P[k][1]}")
lang_edges = edges_tsv(A, "language", "next_language")
chain = sh("tsort", lang_edges + "\n").split()
hosts = int(sh("cut -d/ -f3 | sort -u | wc -l", "\n".join(U[k][1] for k in range(4)) + "\n"))
n_edges = int(sh("grep -oE '[|](url|file_path|next_language|next_stage)=' | wc -l", "\n".join(A.values()) + "\n"))
n_write = int(sh("grep -oE '[|]file_path=' | wc -l", "\n".join(A.values()) + "\n"))
write("dg_lang_chain_d17", A, {"chain": ">".join(chain), "root": names[0], "leaf": names[-1], "hosts": hosts,
                               "edges": n_edges, "write_edges": n_write},
      "4 members language->next_language jscript..bash, D17 urls/file-paths",
      f"awk language/next_language pairs | tsort -> {'>'.join(chain)}; cut -d/ -f3 | sort -u | wc -l -> {hosts}; "
      f"grep -oE '[|](url|file_path|next_language|next_stage)=' | wc -l -> {n_edges} edges; grep -oE '[|]file_path=' | wc -l -> {n_write}")

# B: next_stage names the next member (no languages); two members share one host (same D17 url host twice), the third
#    fetches from its own host -> unique_host is that member.
B = {"a-dropper.vbs": f"v=3|role=dropper|url={U[4][1]}|file_path={P[4][1]}|steps=acquire_remote,write_file|next_stage=b-runner.ps1",
     "b-runner.ps1": f"v=3|role=launcher|url={U[4][1].rsplit('/', 1)[0]}/second.dat|steps=acquire_remote,write_file|file_path={P[5][1]}|next_stage=c-final.py",
     "c-final.py": f"v=3|role=stager|url={U[6][1]}|steps=acquire_remote,dispatch_process"}
mchain = sh("tsort", edges_tsv({m: f"self={m}|{p}" for m, p in B.items()}, "self", "next_stage") + "\n").split()
uniq = sh("awk -F'\\t' '{split($2,u,\"url=\"); split(u[2],h,\"/\"); c[h[3]]++; m[h[3]]=$1} END{for(k in c) if(c[k]==1) print m[k]}'",
          "\n".join(f"{m}\t{p}" for m, p in B.items()))
write("dg_next_stage_shared_host", B, {"member_chain": ">".join(mchain), "root": mchain[0], "leaf": mchain[-1],
                                       "unique_host": uniq, "hosts": 2, "stages": 2},
      "3 members linked by next_stage member names, two share a D17 url host",
      f"awk self/next_stage pairs | tsort -> {'>'.join(mchain)}; awk host tally (count==1) -> {uniq}")

# C (decoy): powershell hands off to TWO different languages (branch) and no member shares a host -> no linear chain,
#    no unique-host answer.
C = {"x.ps1": f"v=3|language=powershell|next_language=python|url={U[7][1]}",
     "y.ps1": f"v=3|language=powershell|next_language=bash|url={U[8][1]}",
     "z.txt": "v=3|role=benign|steps=recognize_syntax"}
br = sh("cut -d' ' -f1 | sort | uniq -d", edges_tsv(C, "language", "next_language") + "\n")
write("dg_decoy_branch", C, {"chain": None, "member_chain": None, "unique_host": None, "root": None},
      "powershell -> python AND powershell -> bash; benign member without graph fields",
      f"awk language/next_language pairs | cut -d' ' -f1 | sort | uniq -d -> {br!r} (a branching source: no single chain)",
      decoy=True)
print("ok", chain, mchain, uniq, br)
