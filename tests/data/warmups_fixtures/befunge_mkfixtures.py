"""Offline generator for the Befunge / ><> fixtures: every `encoded` comes from a perl writer (the classic
`"<reversed>">:#,_@` line, a v/< multi-row grid, a 98 ;comment; form, the two-row ><> `r\\` / `o;!?l<` printer and a
'-quoted ><> return-row form), every `oracle_plain` from befunge_oracle.mjs (node, its own interpreter), never lib/.
Run: python3 tests/data/warmups_fixtures/befunge_mkfixtures.py"""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
LINE = "perl -e 'print chr(34), scalar reverse($ARGV[0]), chr(34), \">:#,_@\"' \"$plain\""
GRID = ("perl -e '$r = reverse $ARGV[0]; @c = unpack \"(a40)*\", $r; $c[0] = \"0\" . chr(34) . $c[0]; "
        "$c[$_] = chr(34) . $c[$_] for 1..$#c; $_ .= chr(34) for @c; "
        "for (@c) { printf \"%-44sv\\n\", \">$_\"; printf \"%-44s<\\n\", \"v\" } print \">:#,_\\@\"' \"$plain\"")
B98 = ("perl -e 'print \";perl befunge-98 writer;\", \"0\", chr(34), scalar reverse($ARGV[0]), chr(34), "
       "\">:#,_\\@\"' \"$plain\"")
FISHM = ("perl -e '$t = chr(34) . $ARGV[0] . chr(34) . \"r\\\\\"; print $t, \"\\n\", \" \" x (length($t) - 6), "
         "\"o;!?l<\"' \"$plain\"")
FISHQ = ("perl -e '$t = chr(39) . reverse($ARGV[0]) . chr(39) . \"v\"; print $t, \"\\n\", "
         "sprintf(\"%*s\", length($t) - 1, \"o;!?l\"), \"<\"' \"$plain\"")
O = "node tests/data/warmups_fixtures/befunge_oracle.mjs"
ART = r"""  ___  ___  _
 / _ \| __|| |   "@,
| (_) | _| | |__  ;o
 \___/|___||____|"""

CASES = [   # (name, codec, slug, generator, oracle, decoy)
    ("befunge-line-amber", "befunge-line", "amber-falcon-42", LINE, f"{O} b93", False),
    ("befunge-grid-jade", "befunge-grid", "jade-lynx-72", GRID, f"{O} b93", False),
    ("befunge-98-comment-cobalt", "befunge*", "cobalt-heron-17", B98, f"{O} b98", False),
    ("fish-mirror-maple", "fish-mirror", "maple-otter-35", FISHM, f"{O} fish", False),
    ("fish-squote-clover", "fish*", "clover-badger-88", FISHQ, f"{O} fish", False),
    ("befunge-decoy-ascii-art", "befunge*", "ivory-moose-51",
     "printf %s '" + ART.replace("'", "'\\''") + "'",
     f"{O} b93 / b98 / fish   # -> exits 1: a figlet-style banner never halts with text / is fishy", True),
    ("befunge-decoy-prose", "befunge*", "amber-viper-23",
     "printf %s 'Meet @ noon, bring 2 coffees; no sugar. Ok?'",
     f"{O} b93 / fish   # -> exits 1: prose with @ , ; o halts with no output / is fishy", True),
]

for name, codec, slug, gen, oracle, decoy in CASES:
    plain = None if decoy else S + slug
    env = dict(os.environ, plain=plain or "")
    enc = subprocess.run(gen, shell=True, env=env, capture_output=True, text=True, check=True).stdout
    outs = []
    for m in (["b93", "b98", "fish"] if decoy else [oracle.split()[2]]):
        r = subprocess.run(["node", str(HERE / "befunge_oracle.mjs"), m], cwd=ROOT, env=dict(os.environ, encoded=enc),
                           capture_output=True, text=True)
        outs.append(r.stdout if r.returncode == 0 else "")
    got = outs[0]
    assert (not any(outs)) if decoy else got == plain, (name, outs)
    fx = {"codec": codec, "plain": plain, "encoded": enc, "generator_cmd": gen, "oracle_cmd": oracle,
          "oracle_plain": got}
    if decoy:
        fx["decoy"] = True
    fx["expected"] = "none" if decoy else "match"
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1) + "\n")
    print(name, "ok")
