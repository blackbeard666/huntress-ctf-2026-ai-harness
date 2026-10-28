"""Generator for the csum_* fixtures (lib.codec corpus_summary / decode(rep='corpus_summary')). stdlib only.
Writes a synthetic 12-member corpus as real files under OUT/<corpus>/ (python3 tests/data/script_fixtures/csum_gen.py OUT)
and each fixture's `expected` from a shell oracle (sed + base64 -d + awk / sort) run on those files."""
import base64, json, os, subprocess, sys

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))


def py_member(plan):
    return "import base64\n# inert analyst fixture\nPLAN = base64.b64decode('%s').decode()\n" % base64.b64encode(plan.encode()).decode()


def plan(lang, role, attack, camp, nxt, host):
    return "v=3|language=%s|role=%s|attack=%s|campaign_id=%s|next_language=%s|host_profile=%s" % (
        lang, role, attack, camp, nxt, host)


CORPUS = {
    "launcher.ps1.py": py_member(plan("powershell", "launcher", "T1059.001", "PS-a1b2c3d4", "python", "workstation")),
    "stage.py": py_member(plan("python", "staged_chain", "T1105", "PY-a1b2c3d4", "jscript", "workstation")),
    "run.js.py": py_member(plan("jscript", "downloader", "T1105", "JS-a1b2c3d4", "batch", "server")),
    "go.bat.py": py_member(plan("batch", "launcher", "T1059.003", "BT-a1b2c3d4", "vbscript", "standalone")),
    "fin.vbs.py": py_member(plan("vbscript", "collector", "T1005", "VB-a1b2c3d4", "none", "standalone")),
    "util1.pl.py": py_member(plan("perl", "benign_utility", "none", "none", "none", "standalone")),
    "util2.rb.py": py_member(plan("ruby", "benign_utility", "none", "none", "none", "standalone")),
    "fetch.lua.py": py_member(plan("lua", "downloader", "T1105", "LU-9f8e7d6c", "powershell", "server")),
    "web.php.py": py_member(plan("php", "staged_chain", "T1059", "PH-9f8e7d6c", "python", "server")),
    "boot.tcl.py": py_member(plan("tcl", "launcher", "T1059", "TC-0badc0de", "bash", "workstation")),
    "grab.sh.py": py_member(plan("bash", "collector", "T1005", "SH-0badc0de", "none", "workstation")),
    "util3.ts.py": py_member(plan("typescript", "benign_utility", "none", "none", "none", "standalone")),
}
DECOY = {"readme.txt": "nothing to see\n", "hello.py": "print('hello world')\n", "notes.md": "# notes\n"}

ROWS = r"""for f in *.py *.txt *.md; do [ -f "$f" ] || continue; sed -n "s/.*b64decode('\(.*\)').*/\1/p" "$f" | base64 -d | tr '|' '\n' | awk -v f="$f" '{i=index($0,"="); print f "\t" substr($0,1,i-1) "\t" substr($0,i+1)}'; done"""
JOIN = r"""LC_ALL=C sort -u | paste -sd, - | sed 's/,/, /g'"""
ORACLES = {
    "count": ROWS + r""" | awk -F'\t' -v K="%s" -v V="%s" '$2==K && $3==V' | wc -l""",
    "handoff_to": ROWS + r""" | awk -F'\t' -v V="%s" '$2=="language"{L[$1]=$3} $2=="next_language"{N[$1]=$3} END{for(f in N) if(N[f]==V) print L[f]}' | """ + JOIN,
    "languages_for_role": ROWS + r""" | awk -F'\t' -v V="%s" '$2=="language"{L[$1]=$3} $2=="role"{R[$1]=$3} END{for(f in R) if(R[f]==V) print L[f]}' | """ + JOIN,
    "campaign_members": ROWS + r""" | awk -F'\t' -v V="%s" '$2=="campaign_id"{n=split($3,p,"-"); if(tolower(p[n])==V) print $1}' | """ + JOIN,
    # longest simple path over the language-level next_language edges (recursive DFS in awk)
    "longest_chain": ROWS + r""" | awk -F'\t' '$2=="language"{L[$1]=$3} $2=="next_language"{N[$1]=$3}
 function dfs(a, p, d,   b) { on[a]=1; if (d>bd) {bd=d; bp=p}; for (b in E) if (E[b]==1 && index(b, a SUBSEP)==1) { split(b, x, SUBSEP); if (!on[x[2]]) dfs(x[2], p ">" x[2], d+1) }; on[a]=0 }
 END{for(f in N) if(N[f]!="none") E[L[f], N[f]]=1; bd=0; for(f in L) dfs(L[f], L[f], 1); print bp}'""",
}

fixtures = {}


def sh(cmd, cwd):
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True).stdout.strip()


def add(name, corpus_name, corpus, transform, key, oracle, decoy=False):
    root = os.path.join(OUT, corpus_name)
    os.makedirs(root, exist_ok=True)
    for n, t in corpus.items():
        open(os.path.join(root, n), "w").write(t)
    exp = sh(oracle, root) or None
    fixtures[name] = dict(material=json.dumps(corpus, sort_keys=True), rep="corpus_summary", transform=transform,
                          key=key, expected=None if decoy else exp, decoy=decoy,
                          generator_cmd="python3 tests/data/script_fixtures/csum_gen.py $TMPDIR/csumgen  (stdlib base64 writer; 12-member corpus %s)" % corpus_name,
                          oracle_cmd="cd $TMPDIR/csumgen/%s && %s" % (corpus_name, oracle))
    return exp


add("csum_count_benign_utility", "c12", CORPUS, "count", "role=benign_utility", ORACLES["count"] % ("role", "benign_utility"))
add("csum_count_host_server", "c12", CORPUS, "count", "host_profile=server", ORACLES["count"] % ("host_profile", "server"))
add("csum_handoff_to_python", "c12", CORPUS, "handoff_to", "python", ORACLES["handoff_to"] % "python")
add("csum_languages_for_role_launcher", "c12", CORPUS, "languages_for_role", "launcher", ORACLES["languages_for_role"] % "launcher")
add("csum_campaign_members", "c12", CORPUS, "campaign_members", "a1b2c3d4", ORACLES["campaign_members"] % "a1b2c3d4")
add("csum_longest_chain", "c12", CORPUS, "longest_chain", None, ORACLES["longest_chain"])
add("csum_decoy_no_plans", "decoy", DECOY, "count", "role=benign_utility",
    "grep -l b64decode * || echo none", decoy=True)

for name, fx in fixtures.items():
    json.dump(fx, open(os.path.join(HERE, name + ".json"), "w"), indent=1)
    print(name, repr(fx["expected"]))
