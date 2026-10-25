"""Generate charnames-*.json: encoded by Perl (charnames / Unicode::UCD) or Python unicodedata.name, read back by the
OTHER implementation (or Python's own string-literal parser for \\N{} escapes). Run from the repo root."""
import json
import os
import subprocess
from pathlib import Path

D = Path(__file__).resolve().parent


def P(slug):
    return f"Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {slug}"


def sh(cmd, stdin):
    r = subprocess.run(["bash", "-c", cmd], input=stdin, capture_output=True, text=True, env={**os.environ, "LC_ALL": "C.UTF-8"})
    return r.stdout, r.returncode, r.stderr.strip()


PERL_COMMA = "perl -CSD -Mcharnames=:full -0777 -ne 'print join(\", \", map { charnames::viacode(ord) } split //)'"
PERL_ESC = "perl -CSD -Mcharnames=:full -0777 -ne 'print map { \"\\\\N{\" . charnames::viacode(ord) . \"}\" } split //'"
PERL_UCD = ("perl -CSD -MUnicode::UCD=charinfo -0777 -ne 'print join(\"\\n\", map { my $i = charinfo(ord); join(\";\", "
            "map { $i->{$_} } qw(code name category combining bidi decomposition decimal digit numeric mirrored unicode10 "
            "comment upper lower title)) } split //)'")
PERL_UPLUS = "perl -CSD -Mcharnames=:full -0777 -ne 'print join(\"\\n\", map { sprintf(\"U+%04X %s\", ord, charnames::viacode(ord)) } split //)'"
PY_LOWER = "python3 -I -c 'import sys, unicodedata as u; print(\"\\n\".join(u.name(c).lower() for c in sys.stdin.read()), end=\"\")'"

PY_LOOKUP = ("python3 -I -c 'import sys, unicodedata as u; print(\"\".join(u.lookup(x) for x in sys.stdin.read().split(\", \")), end=\"\")'")
PY_LITERAL = "python3 -I -c 'import sys, ast; print(ast.literal_eval(chr(34) + sys.stdin.read() + chr(34)), end=\"\")'"
PY_UCD = "python3 -I -c 'import sys; print(\"\".join(chr(int(l.split(\";\")[0], 16)) for l in sys.stdin.read().split(\"\\n\")), end=\"\")'"
PERL_VIANAME_UPLUS = ("perl -CSD -Mcharnames=:full -ne 'chomp; my ($cp, $n) = /^U\\+([0-9A-F]+) (.+)$/ or die; "
                      "my $c = charnames::string_vianame($n); die \"mismatch $_\" unless $c eq chr(hex $cp); print $c'")
PERL_VIANAME_LOWER = "perl -CSD -Mcharnames=:full -ne 'chomp; my $c = charnames::string_vianame(uc $_); die \"bad $_\" unless defined $c; print $c'"

CASES = [
    ("charnames-comma", "charnames-comma-perl-amber", P("amber-otter-41"), PERL_COMMA, PY_LOOKUP),
    ("charnames-esc", "charnames-esc-perl-cobalt", P("cobalt-heron-77"), PERL_ESC, PY_LITERAL),
    ("charnames-unicodedata", "charnames-unicodedata-perlucd-jade", P("jade-falcon-12"), PERL_UCD, PY_UCD),
    ("charnames-uplus", "charnames-uplus-perl-maple", P("maple-badger-90"), PERL_UPLUS, PERL_VIANAME_UPLUS),
    ("charnames-lower", "charnames-lower-newline-python-clover", P("clover-lynx-05"), PY_LOWER, PERL_VIANAME_LOWER),
]
for codec, fname, plain, gen, orc in CASES:
    enc, rc, err = sh(gen, plain)
    assert rc == 0 and enc, (fname, err)
    op, rc, err = sh(orc, enc)
    assert rc == 0 and op == plain, (fname, err, op[:80])
    json.dump({"codec": codec, "plain": plain, "encoded": enc, "generator_cmd": f"printf %s \"$plain\" | {gen}",
               "oracle_cmd": f"printf %s \"$encoded\" | {orc}", "oracle_plain": op, "expected": "match"},
              open(D / f"{fname}.json", "w"), indent=1, ensure_ascii=False)

DECOYS = [
    ("charnames-decoy-caps-prose", "PLEASE FILE THE REPORT, THEN CALL THE FRONT OFFICE, SPACE IS LIMITED, THANK YOU",
     "hand-written English prose in capitals, comma-separated like a name list", PY_LOOKUP),
    ("charnames-decoy-one-bad-name", "LATIN CAPITAL LETTER N, LATIN SMALL LETTER I, LATIN SMALL LETTER CEE, SPACE",
     "hand-written name list with one non-existent name (LATIN SMALL LETTER CEE)", PY_LOOKUP),
    ("charnames-decoy-uplus-mismatch", "U+0041 LATIN CAPITAL LETTER B\nU+0042 LATIN CAPITAL LETTER B\nU+0043 LATIN CAPITAL LETTER C",
     "hand-written U+ lines whose first code point disagrees with its name", PERL_VIANAME_UPLUS),
]
for fname, enc, how, orc in DECOYS:
    op, rc, err = sh(orc, enc)
    assert rc != 0, fname
    json.dump({"codec": "charnames", "plain": None, "encoded": enc, "decoy": True, "expected": "none",
               "generator_cmd": f"printf %s '{enc}'   # {how}", "oracle_cmd": f"printf %s \"$encoded\" | {orc}",
               "oracle_plain": op, "oracle_note": f"oracle rc={rc}: {err.splitlines()[-1] if err else ''}"},
              open(D / f"{fname}.json", "w"), indent=1, ensure_ascii=False)
print("ok")
