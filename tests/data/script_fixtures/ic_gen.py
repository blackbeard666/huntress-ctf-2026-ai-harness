"""Generator for the ic_* fixtures (lib.codec indicator_collisions / indicator_answer). stdlib only.
Writes each corpus as real files under OUT/<fixture>/<member> (python3 tests/data/script_fixtures/ic_gen.py OUT) and
the fixture json whose expected_* values come from the shell oracle (sed + base64 -d + awk) run on those files."""
import base64, json, os, subprocess, sys

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))


def py_member(plan):
    return "import base64\n# inert analyst fixture\nPLAN = base64.b64decode('%s').decode()\n" % base64.b64encode(plan.encode()).decode()


def write(fx, corpus):
    root = os.path.join(OUT, fx)
    for n, t in corpus.items():
        os.makedirs(os.path.dirname(os.path.join(root, n)), exist_ok=True)
        open(os.path.join(root, n), "w").write(t)
    return root


def sh(cmd, cwd):
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True).stdout.strip()


# oracle: decode every member's plan (sed + base64 -d), then awk. Per set (dirname): TRUE = a url/handoff value held by
# two members where one's next_language is the other's language; DECOY = a url whose host hex token does not start with
# the member's own campaign token (campaign_id after the last '-'), or a consumer's handoff_id that its producer does not pass.
ORACLE = r"""find . -name '*.py' | sort | while read f; do sed -n "s/.*b64decode('\(.*\)').*/\1/p" "$f" | { base64 -d; echo; } | tr '|' '\n' | sed "s|^|${f#./}\t|"; done | awk -F'\t' '
{ split($2, kv, "="); k = kv[1]; v = substr($2, length(k) + 2); f = $1; d = f; sub(/\/[^\/]*$/, "", d); if (d == f) d = ".";
  if (k == "language") L[f] = v; else if (k == "next_language") N[f] = v;
  else if (k == "campaign_id") { n = split(v, p, "-"); C[f] = tolower(p[n]) }
  else if (k ~ /url$/ || k == "handoff_id") { cnt++; F[cnt] = f; K[cnt] = k; V[cnt] = v; D[cnt] = d } }
END { for (i = 1; i <= cnt; i++) { t = 0;
    for (j = 1; j <= cnt; j++) if (j != i && D[j] == D[i] && V[j] == V[i] && (N[F[j]] == L[F[i]] || N[F[i]] == L[F[j]])) t = 1;
    if (t) { print "TRUE\t" F[i] "\t" K[i] "\t" V[i]; continue }
    h = V[i]; sub(/^[a-z]+:\/\//, "", h); sub(/[\/.].*/, "", h); n = split(h, hp, "-"); tok = tolower(hp[n]);
    if (K[i] == "handoff_id") { c = 0; for (j = 1; j <= cnt; j++) if (D[j] == D[i] && K[j] == "handoff_id" && N[F[j]] == L[F[i]]) c = 1;
      if (c) print "DECOY\t" F[i] "\t" K[i] "\t" V[i]; continue }
    if (index(tok, C[F[i]]) != 1) print "DECOY\t" F[i] "\t" K[i] "\t" V[i] } }' | sort"""
DEC = "sed -n \"s/.*b64decode('\\(.*\\)').*/\\1/p\" %s | base64 -d"
fixtures = {}


def finish(name, c, text_member, extra):
    root = write(name, c)
    o = [ln.split("\t") for ln in sh(ORACLE, root).splitlines() if ln]
    plain = sh(DEC % text_member, root) if text_member else None
    fx = dict(corpus=c, text=c[text_member] if text_member else "print('hello world')\n", expected_plain=plain or None,
              expected_true=sorted([r[1], r[2], r[3]] for r in o if r[0] == "TRUE"),
              expected_decoys=sorted([r[1], r[2], r[3]] for r in o if r[0] == "DECOY"),
              generator_cmd="python3 tests/data/script_fixtures/ic_gen.py $TMPDIR/icgen  (stdlib base64 writer)",
              oracle_cmd=ORACLE + "  # plain: " + (DEC % text_member if text_member else "n/a"),
              checks="lib.codec.indicator_collisions(plans of corpus) true/decoys == expected_true/expected_decoys "
                     "[member, key, value]; indicator_answer(res, member, field)")
    fx.update(extra)
    fixtures[name] = fx


# 1. erlang producer -> powershell consumer share the url host; the erlang plan also plants a look-alike of the older
#    python member's cdn url differing in ONE hex char (27ca567aa1 -> 27ca567aa2)
c = {
    "polyglot-erlang-staged-chain.escript.py": py_member(
        "v=3|language=erlang|role=staged_chain|next_language=powershell|campaign_id=ERLANG-89cfcb90"
        "|url=https://erlang-89cfcb9034.example.invalid/stage|fallback_url=https://cdn-27ca567aa2.example.invalid/16a153a3b9bf.bin"),
    "polyglot-powershell-launcher.ps1.py": py_member(
        "v=3|language=powershell|role=launcher|next_language=none|campaign_id=POWERSHELL-89cfcb90"
        "|url=https://erlang-89cfcb9034.example.invalid/stage"),
    "python-collection.py": py_member(
        "v=3|language=python|role=uploader|next_language=none|campaign_id=PYTHON-27ca567aa1"
        "|url=https://cdn-27ca567aa1.example.invalid/16a153a3b9bf.bin"),
}
finish("ic_shared_host_onehex", c, "polyglot-erlang-staged-chain.escript.py",
       dict(expected_answers=[["polyglot-erlang-staged-chain.escript.py", "decoy-count", "1"],
                              ["polyglot-erlang-staged-chain.escript.py", "handoff-target",
                               "polyglot-powershell-launcher.ps1.py"],
                              ["polyglot-powershell-launcher.ps1.py", "true-indicator",
                               "https://erlang-89cfcb9034.example.invalid/stage"]]))

# 2. two sets with the same stems: set 1's handoff id is a true link; set 2's consumer carries set 1's id with one
#    hex char changed while its producer passes its own -> the consumer's copy is a decoy (resolved per set)
c = {}
for s, hid, cons in ((1, "PSPY-1F2E3D4C5B6A7980", "PSPY-1F2E3D4C5B6A7980"),
                     (2, "PSPY-0A9B8C7D6E5F4031", "PSPY-1F2E3D4C5B6A7981")):
    c[f"evidence-0{s}.zip/invoke-python-stage.py"] = py_member(
        f"v=3|language=powershell|role=relay|next_language=python|campaign_id=POWERSHELL-{s}a2b3c4d|handoff_id={hid}")
    c[f"evidence-0{s}.zip/4c1097.py"] = py_member(
        f"v=3|language=python|role=launcher|next_language=none|campaign_id=PYTHON-{s}a2b3c4d|handoff_id={cons}")
finish("ic_handoff_sets", c, "evidence-02.zip/4c1097.py", {})

# 3. DECOY: no plan anywhere -> nothing to classify
c = {"a.py": "print('hello world')\n", "b.ps1": "Write-Output 'hello'\n"}
finish("ic_decoy_noplans", c, None, dict(decoy=True, expected_plain=None))

for n, fx in fixtures.items():
    json.dump(fx, open(os.path.join(HERE, n + ".json"), "w"), indent=1)
    print(n, "true", fx["expected_true"], "decoys", fx["expected_decoys"])
