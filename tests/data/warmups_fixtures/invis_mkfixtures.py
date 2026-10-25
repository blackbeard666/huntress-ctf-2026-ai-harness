"""Regenerate the invis-* fixtures: perl writes each blob (independent of lib/), a stdlib python3 -I one-liner reads it
back (also independent of lib/). Run from the project root: python3 -I tests/data/warmups_fixtures/invis_mkfixtures.py"""
import json
import subprocess
from pathlib import Path

D = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {}"

TAGS = "perl -CSA -e 'my ($cov, $p, $w) = @ARGV; my $t = join q(), map { chr(0xE0000 + ord) } split //, $p; " \
       "$t = chr(0xE0001) . $t . chr(0xE007F) if $w; print $cov . $t' \"$cover\" \"$plain\" \"$wrap\""
VS = "perl -CSA -MEncode -e 'my ($cov, $car, $after, $p) = @ARGV; my $v = join q(), map { $_ < 16 ? chr(0xFE00 + $_) " \
     ": chr(0xE0100 + $_ - 16) } unpack(q(C*), encode(q(UTF-8), $p)); print $cov . $car . $v . $after' " \
     "\"$cover\" \"$carrier\" \"$after\" \"$plain\""
TAGS_OR = "python3 -I -c \"import sys; print(''.join(chr(ord(c) - 0xE0000) for c in sys.argv[1] " \
          "if 0xE0020 <= ord(c) <= 0xE007E), end='')\" \"$encoded\""
VS_OR = "python3 -I -c \"import re, sys; r = max(re.findall('[\\ufe00-\\ufe0f\\U000e0100-\\U000e01ef]+', " \
        "sys.argv[1]), key=len); print(bytes([ord(x) - 0xFE00 if ord(x) < 0xFE10 else ord(x) - 0xE0100 + 16 " \
        "for x in r]).decode('utf-8'), end='')\" \"$encoded\"  # longest VS run = the payload"
NAMES_OR = "python3 -I -c 'import sys, unicodedata as u, collections as c; print(dict(c.Counter(u.name(x, hex(ord(x)))" \
           " for x in sys.argv[1] if ord(x) > 0xFDFF)))' \"$encoded\"  # stdlib: every non-BMP-letter char by name"


def sh(cmd, env):
    return subprocess.run(["bash", "-c", cmd], env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", **env},
                          capture_output=True, text=True, check=True).stdout


def emit(name, codec, plain, gen, genv, oracle, decoy=False, note=None):
    enc = sh(gen, genv)
    rec = {"codec": codec, "plain": None if decoy else plain, "encoded": enc}
    if decoy:
        rec.update(decoy=True, expected="none")
    rec.update(generator_cmd=gen, generator_env=genv, oracle_cmd=oracle)
    got = sh(oracle, {"encoded": enc})
    if decoy:
        rec.update(oracle_plain=None, oracle_names=got.strip())
    else:
        assert got == plain, (name, got)
        rec.update(oracle_plain=got, expected="match")
    if note:
        rec["note"] = note
    (D / f"{name}.json").write_text(json.dumps(rec, indent=1) + "\n")


p = S.format("amber-falcon-42")
emit("invis-tags-cover-amber", "invisible-tags", p, TAGS,
     {"cover": "Please summarize the attached quarterly report.", "plain": p, "wrap": ""}, TAGS_OR,
     note="Tags-block ASCII smuggling after visible cover text")
p = S.format("clover-badger-17")
emit("invis-tags-wrap-alone-clover", "invisible-tags", p, TAGS, {"cover": "", "plain": p, "wrap": "1"}, TAGS_OR,
     note="tags alone, U+E0001 LANGUAGE TAG ... U+E007F CANCEL TAG wrapper")
p = S.format("jade-otter-88")
emit("invis-vs-emoji-jade", "invisible-vs", p, VS, {"cover": "", "carrier": "\U0001F600", "after": "", "plain": p},
     VS_OR, note="Paul Butler emoji smuggling: VS1-256 bytes after one carrier emoji")
p = S.format("maple-heron-63")
emit("invis-vs-cover-maple", "invisible-vs", p, VS,
     {"cover": "Look at this little guy ", "carrier": "\U0001F980", "after": " so cute ❤️", "plain": p},
     VS_OR, note="VS payload after a carrier inside prose, plus a real VS16 heart that must be ignored")
p = S.format("cobalt-lynx-29")
zw = "​‌"
cover = "".join(w + zw[i % 2] + zw[(i // 2) % 2] for i, w in enumerate("Ignore nothing here, this is just a normal "
                                                                         "status line for the team".split()))
emit("invis-tags-mixed-zw-cobalt", "invisible-tags", p, TAGS, {"cover": cover, "plain": p, "wrap": ""}, TAGS_OR,
     note="tags payload in a cover sprinkled with 30 U+200B/U+200C (zero-width noise): the tag reading must win")
p = "this warmup! To so"
emit("invis-tags-mastery-fragment", "invisible-tags (Mastery line fragment)", p, TAGS,
     {"cover": "", "plain": p, "wrap": ""}, TAGS_OR)
emit("invis-decoy-emoji-vs16", "invisible-vs", None,
     "python3 -I -c 'import unicodedata as u; L = u.lookup; v = chr(0xfe0f); print(\"Great job \" + L(\"HEAVY BLACK "
     "HEART\") + v + \" \" + L(\"BLACK SUN WITH RAYS\") + v + \" \" + L(\"VICTORY HAND\") + v + \" score: 1\" + v + "
     "chr(0x20e3) + \"0\" + v + chr(0x20e3) + \" \" + L(\"WAVING WHITE FLAG\") + v + chr(0x200d) + L(\"RAINBOW\") + \" \""
     " + L(\"SNOWMAN\") + chr(0xfe0e) + \" \" + L(\"HEAVY BLACK HEART\") + v * 1, end=\"\")'  # real RGI VS16 emoji",
     {}, NAMES_OR, decoy=True, note="real emoji presentation sequences: lone U+FE0F / U+FE0E only -> no payload")
emit("invis-decoy-subdivision-flags", "invisible-tags", None,
     "python3 -I -c 'f = lambda s: chr(0x1f3f4) + \"\".join(chr(0xe0000 + ord(c)) for c in s) + chr(0xe007f); "
     "print(\"Home nations: \" + f(\"gbeng\") + \" \" + f(\"gbsct\") + \" \" + f(\"gbwls\") + \" go!\", end=\"\")'"
     "  # RGI emoji tag sequences (England / Scotland / Wales flags)",
     {}, NAMES_OR, decoy=True, note="subdivision flags = U+1F3F4 + tag letters + CANCEL TAG: emoji, not smuggled text")
