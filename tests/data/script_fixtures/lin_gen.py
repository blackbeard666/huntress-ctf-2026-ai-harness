"""Generator for the lin_* fixtures (lib.codec lineage / decode(rep='lineage')). stdlib only.
Writes each corpus as real files under OUT/<corpus>/ (python3 tests/data/script_fixtures/lin_gen.py OUT) and the
fixture json whose `expected` comes from the shell oracle (sed + base64 -d + awk / grep) run on those files."""
import base64, json, os, subprocess, sys

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))


def py_member(plan):
    return "import base64\n# inert analyst fixture\nPLAN = base64.b64decode('%s').decode()\n" % base64.b64encode(plan.encode()).decode()


def write(name, corpus):
    root = os.path.join(OUT, name)
    os.makedirs(root, exist_ok=True)
    for n, t in corpus.items():
        open(os.path.join(root, n), "w").write(t)
    return root


def sh(cmd, cwd):
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True).stdout.strip()


# decode every plan to "file<TAB>key<TAB>value" rows
ROWS = r"""for f in *.py; do sed -n "s/.*b64decode('\(.*\)').*/\1/p" "$f" | base64 -d | tr '|' '\n' | awk -v f="$f" '{i=index($0,"="); print f "\t" substr($0,1,i-1) "\t" substr($0,i+1)}'; done"""
# parent(M): producer whose next_stage == M, else same campaign token (after last '-') with stage == M.stage - 1
H_PARENT = ROWS + r""" | awk -F'\t' -v M="%s" '$2=="next_stage"{NS[$1]=$3} $2=="stage"{S[$1]=$3} $2=="language"{L[$1]=$3}
 $2=="campaign_id"{n=split($3,p,"-"); T[$1]=tolower(p[n])}
 END{for(f in NS) if(NS[f]==M){print (W=="lang"?L[f]:f); exit}
     for(f in T) if(f!=M && T[f]==T[M] && S[f]==S[M]-1){print (W=="lang"?L[f]:f); exit}}' W=%s"""
# decoy: a member holding a url whose host hex token is NOT its own campaign token
H_DECOY = ROWS + r""" | awk -F'\t' '$2=="campaign_id"{n=split($3,p,"-"); T[$1]=tolower(p[n])} $2=="url"{U[$1]=$3}
 END{for(f in U){h=U[f]; sub(/^[a-z]+:\/\//,"",h); sub(/\..*/,"",h); n=split(h,q,"-"); if(tolower(q[n])!=T[f]) print f}}' | sort | head -1"""
# docker: COPY --from=<stage> <leaf> -> the leaf COPY'd from the build context into <stage>
D_PARENT = r"""awk -v M="%s" 'toupper($1)=="FROM"{s=tolower($NF)} toupper($1)=="COPY" && $2 !~ /^--from=/{n=split($2,a,"/"); C[s]=a[n]}
 toupper($1)=="COPY" && $2 ~ /^--from=/{split($2,b,"="); n=split($3,a,"/"); if(a[n]==M) print C[tolower(b[2])]}' Dockerfile"""
# docker decoy: a .sh holding the builder's url but never COPY'd by the Dockerfile
D_DECOY = r"""u=$(grep -o 'https://[^ "]*' beacon.sh | head -1); for f in $(grep -lF "$u" *.sh); do grep -q "$f" Dockerfile || echo "$f"; done | head -1"""

fixtures = {}


def add(name, corpus_name, corpus, transform, key, oracle, decoy=False):
    root = write(corpus_name, corpus)
    exp = sh(oracle, root) or None
    fixtures[name] = dict(material=json.dumps(corpus, sort_keys=True), rep="lineage", transform=transform, key=key,
                          expected=None if decoy else exp, decoy=decoy,
                          generator_cmd="python3 tests/data/script_fixtures/lin_gen.py $TMPDIR/lingen  (stdlib base64 writer; corpus %s)" % corpus_name,
                          oracle_cmd="cd $TMPDIR/lingen/%s && %s" % (corpus_name, oracle))
    return exp


# 1. three members share the cdn-a1b2c3d4 host; only stage2.py has a static handoff edge (launcher next_stage).
#    mimic.js.py borrows the url but its campaign token 9f8e7d6c makes dropper.vbs.py (stage 1) its parent.
handoff = {
    "launcher.ps1.py": py_member("v=3|language=powershell|role=launcher|stage=1|campaign_id=PS-a1b2c3d4|next_stage=stage2.py|next_language=python|handoff_id=hx-a1b2c3d4-77|url=https://cdn-a1b2c3d4.example.invalid/drop"),
    "stage2.py": py_member("v=3|language=python|role=stager|stage=2|campaign_id=PY-a1b2c3d4|next_language=none|handoff_id=hx-a1b2c3d4-77|url=https://cdn-a1b2c3d4.example.invalid/stage"),
    "mimic.js.py": py_member("v=3|language=jscript|role=collector|stage=2|campaign_id=JS-9f8e7d6c|next_language=none|url=https://cdn-a1b2c3d4.example.invalid/stage"),
    "dropper.vbs.py": py_member("v=3|language=vbscript|role=dropper|stage=1|campaign_id=VB-9f8e7d6c|next_language=none|url=https://edge-9f8e7d6c.example.invalid/x"),
}
add("lin_handoff_parent", "handoff", handoff, "parent", "stage2.py", H_PARENT % ("stage2.py", "file"))
add("lin_semantic_parent_language", "handoff", handoff, "parent_language", "mimic.js.py", H_PARENT % ("mimic.js.py", "lang"))
add("lin_skin_deep_decoy_member", "handoff", handoff, "decoy", None, H_DECOY)

# 2. Dockerfile build stages: gen.py runs in `builder`, beacon.sh is COPY --from=builder; old_beacon.sh (an earlier
#    specimen) carries the same url but no build / handoff edge.
docker = {
    "Dockerfile": "FROM python:3.12-slim AS builder\nCOPY gen.py /src/gen.py\nRUN python3 /src/gen.py > /out/beacon.sh\n"
                  "FROM alpine:3.20 AS runtime\nCOPY --from=builder /out/beacon.sh /opt/beacon.sh\nCMD [\"/bin/sh\", \"/opt/beacon.sh\"]\n",
    "gen.py": py_member("v=3|language=python|role=builder|campaign_id=GEN-3c4d5e6f|next_language=bash|url=https://pkg-3c4d5e6f.example.invalid/b"),
    "beacon.sh": "#!/bin/sh\n# inert analyst fixture\nURL=\"https://pkg-3c4d5e6f.example.invalid/b\"\necho \"$URL\"\n",
    "old_beacon.sh": "#!/bin/sh\n# inert analyst fixture (earlier specimen)\nURL=\"https://pkg-3c4d5e6f.example.invalid/b\"\necho old \"$URL\"\n",
}
add("lin_docker_copy_from_parent", "docker", docker, "parent", "beacon.sh", D_PARENT % "beacon.sh")
add("lin_docker_skin_deep", "docker", docker, "decoy", None, D_DECOY)

# 3. decoy: shared url, no plans, no Dockerfile, no edges -> nothing to attribute (None)
benign = {"a.sh": "#!/bin/sh\necho https://example.invalid/x\n", "b.sh": "#!/bin/sh\necho https://example.invalid/x\n"}
add("lin_decoy_no_edges", "benign", benign, "parent", "b.sh", "grep -l 'next_stage\\|COPY --from' * || true", decoy=True)

for n, fx in fixtures.items():
    open(os.path.join(HERE, n + ".json"), "w").write(json.dumps(fx, indent=1) + "\n")
    print(n, fx["expected"])
