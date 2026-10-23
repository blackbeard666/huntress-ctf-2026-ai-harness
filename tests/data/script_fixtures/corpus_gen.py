"""Generator for the corpus_* fixtures (lib.codec corpus_links / link_value / stage_outlier). stdlib only.
Writes each corpus as real files under OUT/<fixture>/<member> (python3 tests/data/script_fixtures/corpus_gen.py OUT)
and the fixture json whose `expected_*` values come from the shell oracle (awk/sed/base64 -d) run on those files."""
import base64, json, os, subprocess, sys

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))


def py_member(plan):
    return "import base64\n# inert analyst fixture\nPLAN = base64.b64decode('%s').decode()\n" % base64.b64encode(plan.encode()).decode()


def ps_precursor(hid, nxt):
    return ("# inert typed PowerShell-to-Python handoff precursor\n$HandoffId = '%s'\n$Interpreter = 'python.exe'\n"
            "$NextStage = '%s'\n$ArgumentVector = @($NextStage, '--handoff-id', $HandoffId)\n"
            "$ExecutionPlan = [pscustomobject]@{\n    Adapter = 'Start-Process'\n    Interpreter = $Interpreter\n"
            "    Arguments = $ArgumentVector\n    HandoffId = $HandoffId\n    Executed = $false\n}\n" % (hid, nxt))


def write(fx, corpus):
    root = os.path.join(OUT, fx)
    for n, t in corpus.items():
        os.makedirs(os.path.dirname(os.path.join(root, n)), exist_ok=True)
        open(os.path.join(root, n), "w").write(t)
    return root


def sh(cmd, cwd):
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True).stdout.strip()


DEC = "sed -n \"s/.*b64decode('\\(.*\\)').*/\\1/p\" %s | base64 -d"
fixtures = {}

# 1. two sets with the same member stems: each set's precursor passes its own handoff id to 4c1097.py
c = {}
for s, hid in ((1, "PSPY-1F2E3D4C5B6A7980"), (2, "PSPY-0A9B8C7D6E5F4031")):
    c[f"evidence-0{s}.zip/invoke-python-stage.ps1"] = ps_precursor(hid, "4c1097.py")
    c[f"evidence-0{s}.zip/4c1097.py"] = py_member(
        f"v=2|steps=decode_configuration,locate_interpreter,dispatch_next_stage|adapter=python_to_wscript|stage_count=3"
        f"|campaign_id=campaign-{s}a2b3c4d5e|file_path=C:/ProgramData/HuntressLab/.update-{s}a2b3c4d5e.py|next_stage=local-dispatch.vbs")
    c[f"evidence-0{s}.zip/local-dispatch.vbs"] = "' inert\nDim cfg : cfg = \"locate_local,dispatch_process\"\n"
root = write("corpus_handoff_sets", c)
oracle = "awk -F\"'\" '/^\\$HandoffId/{print FILENAME\"\\t\"$2}' */invoke-python-stage.ps1 && " + DEC % "evidence-02.zip/4c1097.py"
o = sh(oracle, root).splitlines()
fixtures["corpus_handoff_sets"] = dict(
    corpus=c, text=c["evidence-02.zip/4c1097.py"], expected_plain=o[2],
    expected_link_values=[{"dst": o[0].split("\t")[0].replace("invoke-python-stage.ps1", "4c1097.py"), "key": "handoff_id",
                           "value": o[0].split("\t")[1]},
                          {"dst": o[1].split("\t")[0].replace("invoke-python-stage.ps1", "4c1097.py"), "key": "handoff_id",
                           "value": o[1].split("\t")[1]},
                          {"dst": "4c1097.py", "key": "handoff_id", "value": None}],
    expected_links_contains=[["evidence-02.zip/invoke-python-stage.ps1", "evidence-02.zip/4c1097.py", "next_stage", "4c1097.py"],
                             ["evidence-02.zip/4c1097.py", "evidence-02.zip/local-dispatch.vbs", "next_stage", "local-dispatch.vbs"]],
    expected_links_absent=[["evidence-01.zip/invoke-python-stage.ps1", "evidence-02.zip/4c1097.py"]],
    expected_outlier=None, oracle_cmd=oracle)

# 2. eight v=3 levels: stage_profile fixes steps/stage_count; level-6 declares two_stage_download_execute with stage_count=3
prof = {"single_descriptor": ("decode_configuration,return_configuration", 2),
        "two_stage_download_execute": ("acquire_remote,dispatch_process", 2),
        "cross_language_handoff": ("profile_host,decode_configuration,dispatch_language", 3),
        "three_stage_decode_write_launch": ("decode_embedded,write_file,dispatch_process", 3)}
c = {}
for i, p in enumerate(list(prof) * 3):
    steps, n = prof[p]
    if i == 5:
        n = 3
    c[f"level-{i + 1}.py"] = py_member(
        f"v=3|language=python|role=staged_chain|verdict=suspicious|attack=T1059.006|stage_profile={p}|next_language=jscript"
        f"|stage_count={n}|steps={steps}|campaign_id=PYTHON-{i:02d}c0ffee|url=https://python-{i:02d}c0ffee.example.invalid/stage")
root = write("corpus_outlier_profile", c)
oracle = ("for f in level-*.py; do printf '%s\\t' $f; " + DEC % "$f" + " | tr '|' '\\n' | grep -E '^(stage_profile|stage_count)=' "
          "| paste -sd' '; done | awk -F'\\t' '{n[$2]++; f[$2]=$1} END{for(k in n) if(n[k]==1) print f[k]}'")
fixtures["corpus_outlier_profile"] = dict(corpus=c, text=c["level-6.py"],
                                          expected_plain=sh(DEC % "level-6.py", root),
                                          expected_outlier=sh(oracle, root), oracle_cmd=oracle)

# 3. a relay whose declared next stage is absent from the set (the only dangling link) next to linked siblings
c = {"relay-a.ps1": ps_precursor("PSPY-AAAA000011112222", "stage-a.py"),
     "stage-a.py": py_member("v=2|steps=locate_local,dispatch_process|adapter=interpreter_argv|stage_count=1|next_stage=stage-b.py"),
     "stage-b.py": py_member("v=2|steps=decode_configuration,return_configuration|adapter=none|stage_count=1"),
     "relay-z.ps1": ps_precursor("PSPY-ZZZZ999988887777", "stage-77e55f4a64.py")}
root = write("corpus_missing_target", c)
oracle = ("for f in *.ps1; do t=$(awk -F\"'\" '/^\\$NextStage/{print $2}' $f); [ -e \"$t\" ] || echo $f; done")
fixtures["corpus_missing_target"] = dict(corpus=c, text=c["stage-a.py"], expected_plain=sh(DEC % "stage-a.py", root),
                                         expected_outlier=sh(oracle, root), oracle_cmd=oracle,
                                         expected_link_values=[{"dst": "stage-a.py", "key": "handoff_id",
                                                                "value": sh("awk -F\"'\" '/^\\$HandoffId/{print $2}' relay-a.ps1", root)}])

# 4. DECOY: same stems, but no member names another, no handoff id, plans agree -> no links, no outlier
c = {"invoke-python-stage.ps1": "# benign\n$Interpreter = 'python.exe'\nWrite-Output 'hello'\n",
     "4c1097.py": "print('hello world')\n", "notes.txt": "nothing to see\n"}
write("corpus_decoy_nolinks", c)
fixtures["corpus_decoy_nolinks"] = dict(corpus=c, text=c["4c1097.py"], expected_plain=None, decoy=True,
                                        expected_links_contains=[], expected_link_values=[{"dst": "4c1097.py", "key": "handoff_id", "value": None}],
                                        expected_outlier=None, oracle_cmd="grep -l -E 'NextStage|HandoffId|next_stage' * || echo none")

for name, fx in fixtures.items():
    fx["generator_cmd"] = "python3 tests/data/script_fixtures/corpus_gen.py $TMPDIR/cgen  (stdlib base64 + PowerShell-shaped precursor text)"
    fx["checks"] = "lib.codec.corpus_links(corpus) / link_value(dst, key, corpus) / stage_outlier(plans of corpus, edges)"
    json.dump(fx, open(os.path.join(HERE, name + ".json"), "w"), indent=1)
    print(name, {k: v for k, v in fx.items() if k.startswith("expected")})
