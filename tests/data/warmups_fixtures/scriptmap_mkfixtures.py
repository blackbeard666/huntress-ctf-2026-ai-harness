"""Offline generator for the script-letter-map fixtures (not in-window code).
Writer = GNU sed `y///` (UTF-8 locale) over a per-script table; reader = perl -CSD `tr///` with the inverse table
(non-injective tables, e.g. runes c/k/q -> one glyph, read the glyph as its first letter: the oracle checks the slug).
Run: python3 tests/data/warmups_fixtures/scriptmap_mkfixtures.py"""
import json
import os
import random
import subprocess
from pathlib import Path

D = Path(__file__).resolve().parent
TPL = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
ENV = dict(os.environ, LC_ALL="C.UTF-8")
LC = "abcdefghijklmnopqrstuvwxyz"


def sh(cmd, inp):
    return subprocess.run(["bash", "-c", cmd], input=inp.encode(), capture_output=True, env=ENV, check=True).stdout.decode()


def sed_cmd(lower, upper, extra=""):
    return f"sed 'y/{LC}{LC.upper()}/{lower}{upper}/{extra}'"


def perl_inv(lower, upper, extra=""):
    seen, src, dst = set(), "", ""
    for g, c in zip(lower + upper, LC + LC.upper()):
        if g not in seen:
            seen.add(g)
            src, dst = src + g, dst + c
    return f"perl -CSD -Mutf8 -pe '{extra}tr/{src}/{dst}/'"


def fixture(name, plain, lower, upper=None, sed_extra="", perl_extra="", decoy=False, note=""):
    upper = upper or lower
    gen = sed_cmd(lower, upper, sed_extra)
    enc = sh(f"printf %s \"$0\" | {gen}".replace('"$0"', "'" + plain.replace("'", "'\\''") + "'"), "")
    orc = perl_inv(lower, upper, perl_extra) + " | tr A-Z a-z"
    oracle = sh(orc, enc)
    rec = {"codec": "script-letter-map", "plain": None if decoy else plain, "encoded": enc,
           "generator_cmd": f"printf %s \"$plain\" | {gen}  # GNU sed y/// letter -> glyph table" + (f"; {note}" if note else ""),
           "oracle_cmd": f"printf %s \"$encoded\" | {orc}  # perl tr/// inverse table (lowercased; a shared glyph reads as its first letter)",
           "oracle_plain": oracle, "expected": "none" if decoy else "match"}
    if decoy:
        rec["decoy"] = True
    (D / f"scriptmap-{name}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")
    return enc, oracle


FUTH = "ᚨᛒᚲᛞᛖᚠᚷᚺᛁᛃᚲᛚᛗᚾᛟᛈᚲᚱᛊᛏᚢᚹᚹᛉᛃᛉ"
GREEK_L = "αβκδεφγηιξκλμνοπθρστυβωχψζ"
GREEK_U = "ΑΒΚΔΕΦΓΗΙΞΚΛΜΝΟΠΘΡΣΤΥΒΩΧΨΖ"
CYR_L = "абцдефгхийклмнопярстувщжыз"
CYR_U = "АБЦДЕФГХИЙКЛМНОПЯРСТУВЩЖЫЗ"
OGHAM = "ᚐᚁᚉᚇᚓᚃᚌᚆᚔᚔᚉᚂᚋᚅᚑᚚᚊᚏᚄᚈᚒᚃᚃᚕᚔᚎ"
TIFI = "ⴰⴱⵛⴷⴻⴼⴳⵀⵉⵊⴽⵍⵎⵏⵧⵒⵇⵔⵙⵜⵓⵠⵡⵅⵢⵣ"
OITAL = "𐌀𐌁𐌂𐌃𐌄𐌚𐌂𐌇𐌉𐌉𐌊𐌋𐌌𐌍𐌏𐌐𐌒𐌓𐌔𐌕𐌖𐌅𐌅𐌗𐌖𐌆"

if __name__ == "__main__":
    out = [
        fixture("futhark-jade", TPL + "jazzy-falcon-31", FUTH),
        fixture("futhark-runic-sep-maple", TPL + "golden-forest-58", FUTH, sed_extra="; s/ /᛫/g", perl_extra="s/᛫/ /g; ",
                note="runic single punctuation U+16EB as the word divider"),
        fixture("greek-cased-amber", TPL + "quick-falcon-42", GREEK_L, GREEK_U),
        fixture("cyrillic-cased-cobalt", TPL + "zesty-juniper-07", CYR_L, CYR_U),
        fixture("ogham-space-clover", TPL + "misty-quartz-63", OGHAM, sed_extra="; s/ / /g; s/^/᚛/; s/$/᚜/",
                perl_extra="s/[᚛᚜]//g; s/ / /g; ", note="Ogham space mark U+1680 + feather marks"),
        fixture("tifinagh-ivory", TPL + "spiffy-canyon-19", TIFI),
        fixture("old-italic-ruby", TPL + "jolly-waterfall-24", OITAL),
    ]
    rng = random.Random(2026)
    shav = [chr(c) for c in range(0x10450, 0x10480)]
    rng.shuffle(shav)
    out.append(fixture("random-shavian-silver", TPL + "fancy-quilt-88", "".join(shav[:26]),
                       note="Shavian block U+10450.. shuffled (random.Random(2026)): an arbitrary glyph alphabet"))
    syms = [chr(c) for c in range(0x2600, 0x2660) if chr(c) not in "☀"]
    rng.shuffle(syms)
    out.append(fixture("random-symbols-onyx", TPL + "witty-zippy-quill-50", "".join(syms[:26]),
                       note="Miscellaneous Symbols U+2600.. shuffled (random.Random(2026))"))
    des_l = [chr(c) for c in range(0x10428, 0x10450)]
    idx = list(range(40))
    rng.shuffle(idx)
    out.append(fixture("random-deseret-cased-hazel", TPL + "daisy-quiet-fern-12", "".join(des_l[i] for i in idx[:26]),
                       "".join(chr(ord(des_l[i]) - 40) for i in idx[:26]),
                       note="Deseret letters (cased: U+10400 upper / U+10428 lower) shuffled, NOT the phonetic reading"))
    # decoys
    fixture("decoy-crib-only-runes", TPL.rstrip(": ") + ".", FUTH, decoy=True, note="the crib without a slug")
    fixture("decoy-other-sentence-greek", "The quick brown fox jumps over the lazy dog near the old stone bridge at dawn: "
            "bright-harbor-11", GREEK_L, GREEK_U, decoy=True, note="a different sentence: the crib does not align")
    rus = "Привет, мир! Это обычный русский текст без всякого шифра, просто проза для проверки декодера: ёлка-12"
    (D / "scriptmap-decoy-russian-prose.json").write_text(json.dumps({
        "codec": "script-letter-map", "plain": None, "encoded": rus, "decoy": True, "expected": "none",
        "generator_cmd": "printf %s \"$encoded\"  # genuine Russian prose (no letter map of the warmups sentence)",
        "oracle_cmd": "printf %s \"$encoded\" | uconv -x Cyrillic-Latin  # ICU reads 'Privet, mir! Ėto obyčnyj ...' != the warmups sentence",
        "oracle_plain": sh("uconv -x Cyrillic-Latin", rus)}, ensure_ascii=False, indent=1) + "\n")
    for e, o in out:
        print(o[-40:])
