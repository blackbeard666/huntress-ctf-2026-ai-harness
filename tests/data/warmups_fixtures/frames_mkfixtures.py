"""Builds the indexed-fragments / run-count frame fixtures. encoded = a perl writer, oracle_plain = a separate perl
reader (neither touches lib/). Run: python3 -I tests/data/warmups_fixtures/frames_mkfixtures.py"""
import json
import subprocess
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {}"
R = "Wooo, nice work decoding this warmup!!! Too good, submit this exact answer to the Game Master: {}"
# perl writers: per-char index frames shuffled with List::Util (srand fixed), or runs of equal chars
GEN_IDX = r"""perl -CSD -MList::Util=shuffle -0777 -ne 'srand(%d);my @c=split//;my @i=shuffle(0..$#c);print join("%s",map{sprintf("%s",%s)}@i)'"""
GEN_RUN = r"""perl -CSD -0777 -ne 'my @o;while(/((.)\2*)/gs){push @o,sprintf("%s",%s)}print join("%s",@o)'"""
# perl readers: index frames -> sort numerically by the index; run frames -> payload x count
ORA_IDX = r"""perl -CSD -0777 -ne 'my %%h;while(/%s/gs){$h{$%s}=$%s}my @k=sort{$a<=>$b}keys %%h;my $b=$k[0];($k[$_]==$_+$b or exit 1) for 0..$#k;print map{$h{$_}}@k'"""
ORA_RUN = r"""perl -CSD -0777 -ne 'my $o="";while(/%s/gs){$o.=$%s x $%s}print $o'"""


def sh(cmd, data):
    r = subprocess.run(["bash", "-c", cmd], input=data.encode(), capture_output=True)
    return r.stdout.decode() if r.returncode == 0 else ""


def fx(name, codec, plain, gen, ora, encoded=None, decoy=False, note=None):
    enc = encoded if encoded is not None else sh(gen, plain)
    op = sh(ora, enc)
    d = {"codec": codec, "plain": None if decoy else plain, "encoded": enc, "generator_cmd": gen, "oracle_cmd": ora,
         "oracle_plain": op}
    if decoy:
        d.update(decoy=True, expected="none")
    else:
        assert op == plain, (name, op)
        d["expected"] = "match"
    if note:
        d["oracle_note"] = note
    (D / f"{name}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print(name, repr(enc[:60]), repr(op[:40]))


ci = ORA_IDX % (r"(?:^|,)(\d+):(.)(?=,\d+:|$)", "1", "2")
fx("frames-index-colon-0based-comma-amber", "frames-index", S.format("amber-heron-58"),
   GEN_IDX % (11, ",", "%d:%s", "$_,$c[$_]"), ci)
fx("frames-index-colon-1based-semicolon-cobalt", "frames-index", S.format("cobalt-lynx-31"),
   GEN_IDX % (23, ";", "%d:%s", "$_+1,$c[$_]"), ORA_IDX % (r"(?:^|;)(\d+):(.)(?=;\d+:|$)", "1", "2"))
fx("frames-index-at-space-jade", "frames-index", S.format("jade-otter-904"),
   GEN_IDX % (5, " ", "%s@%d", "$c[$_],$_"), ORA_IDX % (r"(.)@(\d+)(?: |$)", "2", "1"))
fx("frames-index-bracket-nosep-maple", "frames-index", S.format("maple-wren-77"),
   GEN_IDX % (9, "", "[%d]%s", "$_+1,$c[$_]"), ORA_IDX % (r"\[(\d+)\](.)", "1", "2"))
fx("frames-count-colon-comma-clover", "frames-count", R.format("clover-moose-1100"),
   GEN_RUN % ("%d:%s", "length($1),$2", ","), ORA_RUN % (r"(\d+):(.)(?:,|$)", "2", "1"))
fx("frames-count-star-comma-amber", "frames-count", R.format("amber-goose-300"),
   GEN_RUN % ("%s*%d", "$2,length($1)", ","), ORA_RUN % (r"(.)\*(\d+)(?:,|$)", "1", "2"))
# decoys: a gap in the index range (frame 7 dropped), a repeated index, prose with clock times / multiplications
full = sh(GEN_IDX % (11, ",", "%d:%s", "$_,$c[$_]"), S.format("amber-heron-58"))
fx("frames-decoy-index-gap", "frames-index", None, "perl writer above, then the frame tagged 7 removed", ci,
   encoded=",".join(f for f in full.split(",") if not f.startswith("7:")), decoy=True,
   note="indices 0..n with 7 missing: not a permutation of range(n) (the perl reader exits 1)")
fx("frames-decoy-index-repeat", "frames-index", None, "hand-written: index 2 appears twice, 3 never", ci,
   encoded="1:e,0:h,2:l,4:o,2:l", decoy=True, note="repeated index -> not a permutation (perl reader exits 1)")
fx("frames-decoy-prose-times", "frames-count", None, "hand-written prose: clock times and a*b products",
   ORA_RUN % (r"(\d+):(.)(?:,|$)", "2", "1"), encoded="Standup at 3:30, lunch 12:15, 4*5 tables, 2:1 odds.",
   decoy=True, note="the lenient perl reader picks fragments out of prose; the WHOLE text is no frame run")
