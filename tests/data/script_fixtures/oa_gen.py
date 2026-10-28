"""Generator for the oa_* fixtures (lib.codec order_anomalies / decode(rep='order_anomaly')). stdlib + `zip`/`zipinfo`.
Writes each corpus as real plan files under OUT/<corpus>/ (python3 tests/data/script_fixtures/oa_gen.py OUT), zips
the zip-mtime corpus with Info-ZIP after `touch -d`, and takes every `expected` from a shell oracle (awk / grep /
zipinfo) run on those files -- never from lib.codec. The step oracle is a GM-observed reference list of step
sequences (D20-D28 plans), not the tier model the extractor uses."""
import json, os, subprocess, sys

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
# step sequences the GM shipped verbatim in D20-D28 v=3 plans (reference for the oracle)
GM_STEPS = ["acquire_remote>write_file>dispatch_process", "decode_embedded>write_file>dispatch_process",
            "profile_host>decode_configuration>dispatch_language", "acquire_remote>dispatch_process",
            "read_file>transmit_remote", "profile_host>acquire_remote>write_file>change_mode>dispatch_process",
            "decode_configuration>return_configuration", "locate_local>dispatch_process"]


def sh(cmd, cwd):
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True).stdout.strip()


def write(name, corpus):
    root = os.path.join(OUT, name)
    os.makedirs(root, exist_ok=True)
    for n, t in corpus.items():
        open(os.path.join(root, n), "w").write(t + "\n")
    open(os.path.join(root, "gm_steps.txt"), "w").write("\n".join(GM_STEPS) + "\n")
    return root


ROWS = r"""for f in *.plan; do tr '|' '\n' < "$f" | awk -v f="$f" '{i=index($0,"="); print f "\t" substr($0,1,i-1) "\t" substr($0,i+1)}'; done"""
# member whose steps are not a GM-observed sequence
O_STEP_MEMBER = ROWS + r""" | awk -F'\t' '$2=="steps"{print $1 "\t" $3}' | while IFS=$'\t' read f s; do grep -qxF "$s" gm_steps.txt || echo "$f"; done"""
# first position (1-based) where that member's steps differ from the GM sequence with the same multiset of tokens
O_STEP_POS = ROWS + r""" | awk -F'\t' '$2=="steps"{print $3}' | while read s; do grep -qxF "$s" gm_steps.txt && continue; k=$(echo "$s" | tr '>' '\n' | sort | tr '\n' ' '); while read g; do [ "$(echo "$g" | tr '>' '\n' | sort | tr '\n' ' ')" = "$k" ] || continue; paste <(echo "$s" | tr '>' '\n') <(echo "$g" | tr '>' '\n') | awk -v W=%s -F'\t' '$1!=$2{print (W=="pos"?NR:$1); exit}'; done < gm_steps.txt; done"""
# producer whose next_stage names a member of lower-or-equal stage
O_BACK = ROWS + r""" | awk -F'\t' '$2=="stage"{S[$1]=$3} $2=="next_stage"{N[$1]=$3} END{for(f in N) if((N[f]".plan") in S && S[N[f]".plan"]<=S[f]) print (W=="target"?N[f]".plan":f)}' W=%s"""
# zip: the single member whose removal leaves the zipinfo mtimes non-decreasing along the stage order
O_ZIP = r"""zipinfo -T ev.zip | awk '$NF ~ /\.plan$/{print $NF "\t" $(NF-1)}' | sort > t.tsv; """ + ROWS + \
    r""" | awk -F'\t' '$2=="stage"{print $1 "\t" $3}' | sort | join -t$'\t' - t.tsv | sort -t$'\t' -k2,2n""" + \
    r""" | awk -F'\t' '{f[NR]=$1; t[NR]=$3} END{for(i=1;i<=NR;i++){ok=1; p=""; for(j=1;j<=NR;j++){if(j==i) continue; if(p!="" && t[j]<p) ok=0; p=t[j]} if(ok){c++; w=f[i]}} if(c==1) print w}'"""

fixtures = {}


def add(name, corpus_name, transform, key, oracle, decoy=False, zip_infos=None):
    root = os.path.join(OUT, corpus_name)
    exp = sh(oracle, root) or None
    plans = {n: open(os.path.join(root, n)).read().strip() for n in sorted(os.listdir(root)) if n.endswith(".plan")}
    mat = {"plans": plans, "zip_infos": zip_infos} if zip_infos else plans
    fixtures[name] = dict(material=json.dumps(mat, sort_keys=True), rep="order_anomaly", transform=transform, key=key,
                          expected=None if decoy else exp, decoy=decoy,
                          generator_cmd="python3 tests/data/script_fixtures/oa_gen.py $TMPDIR/oagen  (stdlib plan writer"
                                        + ("; touch -d + Info-ZIP zip" if zip_infos else "") + "; corpus %s)" % corpus_name,
                          oracle_cmd="cd $TMPDIR/oagen/%s && %s" % (corpus_name, oracle))


# 1. one member ships a GM sequence with two steps swapped (dispatch_process ahead of write_file)
write("swapped", {
    "loader.plan": "v=3|language=powershell|role=loader|stage=1|stage_count=3|steps=acquire_remote>dispatch_process>write_file|next_stage=stager",
    "stager.plan": "v=3|language=python|role=stager|stage=2|stage_count=3|steps=decode_embedded>write_file>dispatch_process|next_stage=runner",
    "runner.plan": "v=3|language=bash|role=runner|stage=3|stage_count=3|steps=profile_host>decode_configuration>dispatch_language|next_language=none",
    "exfil.plan": "v=3|language=jscript|role=collector|stage=3|stage_count=2|steps=read_file>transmit_remote|next_language=none"})
add("oa_swapped_steps_member", "swapped", "member", None, O_STEP_MEMBER)
add("oa_swapped_steps_token", "swapped", "step", None, O_STEP_POS % "tok")
add("oa_swapped_steps_position", "swapped", "position", None, O_STEP_POS % "pos")

# 2. a handoff pointing backwards: relay (stage 3) names first (stage 1) as its next stage
write("backward", {
    "first.plan": "v=3|language=vbscript|role=dropper|stage=1|stage_count=2|steps=acquire_remote>dispatch_process|next_stage=second",
    "second.plan": "v=3|language=powershell|role=loader|stage=2|stage_count=3|steps=decode_embedded>write_file>dispatch_process|next_stage=relay",
    "relay.plan": "v=3|language=python|role=relay|stage=3|stage_count=2|steps=locate_local>dispatch_process|next_stage=first"})
add("oa_handoff_backward_member", "backward", "member", "handoff_backward", O_BACK % "src")
add("oa_handoff_backward_target", "backward", "target", "handoff_backward", O_BACK % "target")

# 3. zip member mtimes: stage 2 was modified last, after stages 3 and 4 (one write out of order)
root = write("zipped", {
    "a_entry.plan": "v=3|language=batch|role=launcher|stage=1|stage_count=2|steps=acquire_remote>dispatch_process",
    "b_middle.plan": "v=3|language=perl|role=stager|stage=2|stage_count=3|steps=acquire_remote>write_file>dispatch_process",
    "c_final.plan": "v=3|language=lua|role=collector|stage=3|stage_count=2|steps=read_file>transmit_remote",
    "d_tail.plan": "v=3|language=php|role=reporter|stage=4|stage_count=2|steps=decode_configuration>return_configuration"})
for n, d in (("a_entry.plan", "2026-01-01 10:00:00"), ("b_middle.plan", "2026-01-01 13:30:00"),
             ("c_final.plan", "2026-01-01 11:30:00"), ("d_tail.plan", "2026-01-01 12:45:00")):
    sh("TZ=UTC touch -d '%s' %s" % (d, n), root)
sh("rm -f ev.zip; TZ=UTC zip -q -X ev.zip *.plan", root)
zi = {}
for line in sh("TZ=UTC zipinfo -T ev.zip", root).splitlines():   # yyyymmdd.hhmmss name
    p = line.split()
    if p and p[-1].endswith(".plan"):
        d = p[-2]
        zi[p[-1]] = "%s-%s-%sT%s:%s:%s" % (d[:4], d[4:6], d[6:8], d[9:11], d[11:13], d[13:15])
add("oa_zip_mtime_member", "zipped", "member", None, "TZ=UTC; " + O_ZIP, zip_infos=zi)

# 4. decoy: every plan in canonical order, handoffs forward, equal (GM-default) mtimes -> nothing out of order
write("inorder", {
    "one.plan": "v=3|language=powershell|role=loader|stage=1|stage_count=3|steps=acquire_remote>write_file>dispatch_process|next_stage=two",
    "two.plan": "v=3|language=python|role=stager|stage=2|stage_count=3|steps=decode_embedded>write_file>dispatch_process|next_language=bash",
    "three.plan": "v=3|language=bash|role=runner|stage=3|stage_count=3|steps=profile_host>decode_configuration>dispatch_language|next_language=none"})
add("oa_decoy_in_order", "inorder", "member", None, O_STEP_MEMBER + "; " + O_BACK % "src", decoy=True,
    zip_infos={"one.plan": "2026-01-01T00:00:00", "two.plan": "2026-01-01T00:00:00", "three.plan": "2026-01-01T00:00:00"})

for n, fx in fixtures.items():
    open(os.path.join(HERE, n + ".json"), "w").write(json.dumps(fx, indent=1) + "\n")
    print(n, fx["expected"])
