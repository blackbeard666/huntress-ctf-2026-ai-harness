"""Offline generator for the Brainfuck token-dialect fixtures: every `encoded` comes from a perl writer (a Brainfuck
program -- the GM's D26 per-byte delta style or a 10x multiply-loop style -- re-spelled by a perl token table) and every
`oracle_plain` from bfd_oracle.mjs (node: esolangs token tables + its own interpreter), never lib/.
Run: python3 tests/data/warmups_fixtures/bfd_mkfixtures.py"""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
DELTA = ("perl -e '$p=0; for $c (unpack \"C*\", $ARGV[0]) { $d=$c-$p; print $d>0 ? \"+\" x $d : \"-\" x -$d, \".\"; "
         "$p=$c }' \"$plain\"")
LOOPS = ("perl -e 'for $c (unpack \"C*\", $ARGV[0]) { print \"+\" x 10, \"[>\", \"+\" x int($c/10), \"<-]>\", "
         "\"+\" x ($c%10), \".[-]<\" }' \"$plain\"")


def spell(table, sep=" "):
    """perl stage re-spelling each Brainfuck command by `table` ({cmd: token})."""
    kv = ",".join("q(%s)=>q(%s)" % (k, v) for k, v in table.items())
    return " | perl -ne 'chomp; %%m=(%s); print join(q(%s), map { $m{$_} } split //)'" % (kv, sep)


OPS = "><+-.,[]"
OOK = dict(zip(OPS, ["Ook. Ook?", "Ook? Ook.", "Ook. Ook.", "Ook! Ook!", "Ook! Ook.", "Ook. Ook!", "Ook! Ook?",
                     "Ook? Ook!"]))
BLUB = {k: v.replace("Ook", "Blub") for k, v in OOK.items()}
SHORT = {k: v.replace("Ook", "").replace(" ", "") for k, v in OOK.items()}
COW = dict(zip(OPS, "moO mOo MoO MOo Moo oom MOO moo".split()))
PIKA = dict(zip(OPS, "pipi pichu pi ka pikachu pikapi pika chu".split()))
ALPH = dict(zip(OPS, "aceijops"))
REV = dict(zip(OPS, "<>-+.,[]"))
BIN = dict(zip(OPS, "000 001 010 011 100 101 110 111".split()))
ROAD = dict(zip(OPS, "Meep mEep meEp meeP MEep mEEp meEP MeeP".split()))
FARM = {"+": "moo", "-": "baa", ".": "oink"}
O = "node tests/data/warmups_fixtures/bfd_oracle.mjs"

CASES = [   # (name, codec, slug, generator, oracle, decoy)
    ("bfd-ook-delta-amber", "bf-ook", "amber-falcon-42", DELTA + spell(OOK), f"{O} ook", False),
    ("bfd-ook-loops-jade", "bf-ook", "jade-lynx-72", LOOPS + spell(OOK), f"{O} ook", False),
    ("bfd-blub-delta-maple", "bf-blub", "maple-otter-35", DELTA + spell(BLUB), f"{O} ook", False),
    ("bfd-ookshort-run-loops-cobalt", "bf-ook-short-run", "cobalt-heron-17", LOOPS + spell(SHORT, ""), f"{O} ook",
     False),
    ("bfd-cow-delta-clover", "bf-cow", "clover-badger-88", DELTA + spell(COW), f"{O} cow", False),
    ("bfd-cow-loops-ivory", "bf-cow", "ivory-moose-51", LOOPS + spell(COW), f"{O} cow", False),
    ("bfd-pikalang-delta-amber", "bf-pikalang", "amber-viper-23", DELTA + spell(PIKA), f"{O} pikalang", False),
    ("bfd-pikalang-loops-jade", "bf-pikalang", "jade-falcon-64", LOOPS + spell(PIKA), f"{O} pikalang", False),
    ("bfd-alphuck-loops-maple", "bf-alphuck", "maple-lynx-19", LOOPS + spell(ALPH, ""), f"{O} alphuck", False),
    ("bfd-reversefuck-delta-cobalt", "bf-reversefuck", "cobalt-otter-77", DELTA + spell(REV, ""), f"{O} reversefuck",
     False),
    ("bfd-binaryfuck-loops-clover", "bf-binaryfuck", "clover-heron-31", LOOPS + spell(BIN), f"{O} binaryfuck", False),
    ("bfd-tokenmap-roadrunner-loops-ivory", "bf-token-map", "ivory-badger-46", LOOPS + spell(ROAD),
     f"{O} map '{json.dumps({v: k for k, v in ROAD.items()})}'", False),
    ("bfd-tokenmap-farm-delta-amber", "bf-token-map", "amber-moose-58", DELTA + spell(FARM),
     f"{O} map '{json.dumps({v: k for k, v in FARM.items()})}'", False),
    ("bfd-decoy-english-prose", "bf-dialect*", "jade-viper-12",
     "printf %s 'Ook. Ook? said the librarian, and the orangutan went back to sorting the stacks.'",
     f"{O} ook   # -> throws: the marks pair into a junk program, the line is prose", True),
    ("bfd-decoy-morse", "bf-dialect*", "maple-falcon-90",
     "perl -e '%m=(N=>\"-.\",i=>\"..\",c=>\"-.-.\",e=>\".\",w=>\".--\",o=>\"---\",r=>\".-.\",k=>\"-.-\"); "
     "print join(\" \", map { $_ eq \" \" ? \"/\" : $m{$_} } split //, \"Nice work\")'",
     "printf %s \"$encoded\"   # International Morse (dits/dahs, '/' word gap): no Ook word, no 3..8-token BF map",
     True),
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
        oplain = enc if oerr or not oplain else oplain
        assert oplain != plain, name
    else:
        assert oplain == plain, (name, oplain, oerr)
    d = {"codec": codec, "plain": None if decoy else plain, "encoded": enc, "generator_cmd": gen, "oracle_cmd": oracle,
         "oracle_plain": oplain}
    d.update({"decoy": True, "expected": "none"} if decoy else {"expected": "match"})
    (HERE / f"{name}.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print(name, len(enc))
