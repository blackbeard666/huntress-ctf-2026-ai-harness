"""Offline generator for the Deadfish fixtures: every `encoded` comes from a perl writer (delta = i/d runs from the
last byte then o; square = the cheaper of a run or run-to-r, s, run-to-n), re-lettered for XKCD (x k c d) / upper case
by tr, and every `oracle_plain` from deadfish_oracle.mjs (node, its own interpreter), never lib/.
Run: python3 tests/data/warmups_fixtures/deadfish_mkfixtures.py"""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
DELTA = ("perl -e '$v=0; for $n (unpack \"C*\", $ARGV[0]) { print $n>=$v ? \"i\" x ($n-$v) : \"d\" x ($v-$n), \"o\"; "
         "$v=$n }' \"$plain\"")
SQUARE = ("perl -e 'sub run { my ($a,$b)=@_; $b>=$a ? \"i\" x ($b-$a) : \"d\" x ($a-$b) } $v=0; "
          "for $n (unpack \"C*\", $ARGV[0]) { $best=run($v,$n); for $r (0..15) { $c=run($v,$r).\"s\".run($r*$r,$n); "
          "$best=$c if length($c) < length($best) } print $best, \"o \"; $v=$n }' \"$plain\"")
XKCD = " | tr idso xdkc"
UPPER = " | tr a-z A-Z"
O = "node tests/data/warmups_fixtures/deadfish_oracle.mjs"

CASES = [   # (name, codec, slug, generator, oracle, decoy)
    ("deadfish-delta-amber", "deadfish-delta", "amber-falcon-42", DELTA, f"{O} idso", False),
    ("deadfish-square-sp-jade", "deadfish-square-sp", "jade-lynx-72", SQUARE, f"{O} idso", False),
    ("deadfish-upper-square-cobalt", "deadfish-square-sp-upper", "cobalt-heron-17", SQUARE + UPPER, f"{O} idso", False),
    ("deadfish-xkcd-delta-maple", "deadfish-xkcd-delta", "maple-otter-35", DELTA + XKCD, f"{O} xkcd", False),
    ("deadfish-xkcd-square-clover", "deadfish-xkcd-square-sp", "clover-badger-88", SQUARE + XKCD, f"{O} xkcd", False),
    ("deadfish-decoy-dido-words", "deadfish*", "ivory-moose-51",
     "printf %s 'dido is odd so i do did so ids odds'",
     f"{O} idso   # -> exits 1: English words of i/d/s/o print control bytes, not text", True),
    ("deadfish-decoy-xkcd-words", "deadfish*", "amber-viper-23",
     "printf %s 'XKCD dxkc ccd kxd'",
     f"{O} xkcd   # -> exits 1: letters of the XKCD set that print control bytes", True),
]


def sh(cmd, env):
    r = subprocess.run(["bash", "-c", cmd], env=env, capture_output=True, text=True, timeout=60)
    if r.returncode:
        return None, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "error"
    return r.stdout, None


for name, codec, slug, gen, oracle, decoy in CASES:
    plain = S + slug
    env = dict(os.environ, plain=plain)
    enc, err = sh(gen, env)
    assert enc, (name, err)
    enc = enc.strip()
    oplain, oerr = sh(oracle, dict(env, encoded=enc))
    if decoy:
        assert oerr, (name, oplain)
        oplain = enc
    else:
        assert oplain == plain, (name, oplain, oerr)
    d = {"codec": codec, "plain": None if decoy else plain, "encoded": enc, "generator_cmd": gen, "oracle_cmd": oracle,
         "oracle_plain": oplain}
    d.update({"decoy": True, "expected": "none"} if decoy else {"expected": "match"})
    (HERE / f"{name}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print(name, len(enc))
