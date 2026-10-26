"""Offline generator for the full-Brainfuck fixtures: every `encoded` comes from a perl writer (multiply loops with
comment text, the shared-10x-loop text generator, wrap-below-0, 16-bit-only, ',' reads, a base64(gzip) peel) and every
`oracle_plain` from bff_oracle.mjs (node: its own char-at-a-time interpreter), never lib/.
Run: python3 tests/data/warmups_fixtures/bff_mkfixtures.py"""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
# n = a*b + c per byte, a comment word naming the char between programs
MUL = ("perl -e 'for $c (unpack \"C*\", $ARGV[0]) { $a=int(sqrt($c)); $b=int($c/$a); $r=$c-$a*$b; "
       "print \"char \", ($c==32 ? \"space\" : chr($c)=~/[A-Za-z]/ ? chr($c) : \"sym\"), \" \", \">\", \"+\" x $a, \"[<\", "
       "\"+\" x $b, \">-]<\", \"+\" x $r, \".[-]\\n\" }' \"$plain\"")
# shared 10x loop seeds one cell per distinct byte, then move/trim/print, 72-col lines
GEN = ("perl -e '@b=unpack \"C*\", $ARGV[0]; %s=map {$_=>1} @b; @d=sort {$a<=>$b} keys %s; %i=(); "
       "$o=\"+\" x 10 . \"[\"; for $k (0..$#d) { $i{$d[$k]}=$k+1; $v{$d[$k]}=int($d[$k]/10)*10; "
       "$o.=\">\" . \"+\" x int($d[$k]/10) } $o.=\"<\" x @d . \"-]\"; $p=0; for $c (@b) { $q=$i{$c}; "
       "$o.= $q>$p ? \">\" x ($q-$p) : \"<\" x ($p-$q); $p=$q; $e=$c-$v{$c}; $o.= $e>0 ? \"+\" x $e : \"-\" x -$e; "
       "$v{$c}=$c; $o.=\".\" } $o=~s/(.{72})/$1\\n/g; print $o' \"$plain\"")
# reach each byte from 0 by going BELOW zero (8-bit wrap), comment banner first
WRAP = ("perl -e 'print \"This program wraps below zero\\n\"; for $c (unpack \"C*\", $ARGV[0]) { "
        "print \"-\" x (256-$c), \".[-]\\n\" }' \"$plain\"")
# 16-bit only: cell0 = 4n, then [>+<----] -> n (8-bit cells give n mod 64)
B16 = ("perl -e 'for $c (unpack \"C*\", $ARGV[0]) { print \"+\" x (4*$c), \"[>+<----]>.[-]<\\n\" }' \"$plain\"")
# ',' at EOF stores -1 (the EOF=-1 convention): ,+ zeroes the cell, then +n.
EOFM1 = ("perl -e 'for $c (unpack \"C*\", $ARGV[0]) { print \",+\", \"+\" x $c, \".[-]\" }' \"$plain\"")
# base64(gzip(text generator)): a peel layer over the BF soup
PEEL = GEN + " | gzip -9n -c | base64 -w0"
O = "node tests/data/warmups_fixtures/bff_oracle.mjs"

CASES = [   # (name, codec, slug, generator, oracle, decoy)
    ("bff-mul-comments-amber", "bf-full-mul", "amber-falcon-42", MUL, O, False),
    ("bff-textgen-jade", "bf-full-gen", "jade-lynx-72", GEN, O, False),
    ("bff-wrap-below-zero-maple", "bf-full", "maple-otter-35", WRAP, O, False),
    ("bff-16bit-cobalt", "bf-full", "cobalt-heron-17", B16, f"{O} bits=16", False),
    ("bff-eof-minus1-clover", "bf-full", "clover-badger-88", EOFM1, f"{O} eof=-1", False),
    ("bff-b64-gzip-ivory", "bf-full", "ivory-moose-51", PEEL, f"{O} peel=b64gz", False),
    ("bff-decoy-morse", "bf-full*", "x", "printf %s '-. .. -.-. . / .-- --- .-. -.- / -.. . -.-. --- -.. .. -. --.'",
     f"{O}   # -> junk bytes (Morse '.'/'-' run as BF prints 0xff..): not claimed", True),
    ("bff-decoy-hello-world", "bf-full*", "x",
     "printf %s '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.'",
     f"{O}   # -> 'Hello World!\\n': valid BF but no warmup sentence / slug -> not claimed", True),
]

for name, codec, slug, gen, oracle, decoy in CASES:
    plain = None if decoy else S + slug
    env = {**os.environ, "plain": plain or ""}
    enc = subprocess.run(["bash", "-c", gen], env=env, capture_output=True, text=True, check=True).stdout
    env["encoded"] = enc
    orc = subprocess.run(["bash", "-c", oracle.split("   #")[0]], env=env, capture_output=True, text=True).stdout
    if not decoy:
        assert orc == plain, (name, orc[:80])
    fx = {"codec": codec, "plain": plain, "encoded": enc, "generator_cmd": gen, "oracle_cmd": oracle,
          "oracle_plain": orc, "decoy": decoy, "expected": "none" if decoy else orc}
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1, ensure_ascii=False) + "\n")
    print(name, len(enc), repr(orc[:50]))
