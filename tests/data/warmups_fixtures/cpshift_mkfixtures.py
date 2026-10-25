"""Offline generator for the cpshift-* fixtures (code point + K / XOR K). Writer = perl (-CSA, chr/ord), reader = a
stdlib python3 one-liner -- neither is lib.warmups_codecs. Run: python3 tests/data/warmups_fixtures/cpshift_mkfixtures.py"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "

# name, slug, perl per-char expr ($c = the char), keep spaces, wrap with U+E0001..U+E007F, token printf fmt, oracle py expr
CASES = [
    ("cpshift-cjk-amber", "amber-falcon-42", "chr(ord($c)+0x4DE0)", 0, 0, None, "chr(ord(c)-0x4DE0)"),
    ("cpshift-tags-cobalt", "cobalt-heron-17", "chr(ord($c)+0xE0000)", 0, 0, None, "chr(ord(c)-0xE0000)"),
    ("cpshift-tags-wrapped-jade", "jade-otter-88", "chr(ord($c)+0xE0000)", 0, 1, None, "chr(ord(c)-0xE0000)"),
    ("cpshift-negative-clover", "clover-lynx-63", "chr(ord($c)-0x10)", 0, 0, None, "chr(ord(c)+0x10)"),
    ("cpshift-pua-maple", "maple-wren-29", "chr(ord($c)+0xE000)", 0, 0, None, "chr(ord(c)-0xE000)"),
    ("cpshift-astral-ivory", "ivory-badger-51", "chr(ord($c)+0x100000)", 0, 0, None, "chr(ord(c)-0x100000)"),
    ("cpshift-fullwidth-all-amber", "amber-moose-34", "chr(ord($c)+0xFEE0)", 0, 0, None, "chr(ord(c)-0xFEE0)"),
    ("cpshift-keepspace-cobalt", "cobalt-finch-76", "chr(ord($c)+0x3000)", 1, 0, None, "chr(ord(c)-0x3000)"),
    ("cpshift-xor-cjk-jade", "jade-viper-12", "chr(ord($c)^0x4E00)", 0, 0, None, "chr(ord(c)^0x4E00)"),
    ("cpshift-xor-braille-clover", "clover-stoat-90", "chr(ord($c)^0x2800)", 0, 0, None, "chr(ord(c)^0x2800)"),
    ("cpshift-uplus-maple", "maple-gecko-45", "chr(ord($c)+0x4DE0)", 0, 0, "U+%04X ", "chr(ord(c)-0x4DE0)"),
]


def perl(plain, expr, keep, wrap, tokfmt):
    sub = f"$c eq q( ) ? $c : {expr}" if keep else expr
    code = f'my $o = join q(), map {{ my $c = $_; {sub} }} split //, $ARGV[0];'
    if wrap:
        code += ' $o = chr(0xE0001) . $o . chr(0xE007F);'
    code += f' $o = join q( ), map {{ sprintf q({tokfmt.strip()}), ord }} split //, $o;' if tokfmt else ""
    code += " print $o;"
    out = subprocess.run(["perl", "-CSA", "-e", code, plain], capture_output=True, check=True).stdout.decode()
    return out, "perl -CSA -e " + repr(code) + ' "$plain"'


for name, slug, expr, keep, wrap, tok, oexpr in CASES:
    plain = S + slug
    enc, gcmd = perl(plain, expr, keep, wrap, tok)
    pre = "import re;t=''.join(chr(int(h,16)) for h in re.findall(r'U\\+([0-9A-F]+)',t));" if tok else ""
    body = f"''.join(c if c==' ' else {oexpr} for c in t)" if keep else f"''.join({oexpr} for c in t)"
    code = f"import sys;t=sys.argv[1];{pre}t=t.strip('\\U000E0001\\U000E007F');print({body},end='')"
    got = subprocess.run(["python3", "-I", "-c", code, enc], capture_output=True, check=True).stdout.decode()
    assert got == plain, (name, got)
    (HERE / f"{name}.json").write_text(json.dumps({
        "codec": "cpshift", "plain": plain, "encoded": enc, "generator_cmd": gcmd,
        "oracle_cmd": "python3 -I -c " + repr(code) + ' "$encoded"', "oracle_plain": got, "expected": "match"},
        ensure_ascii=False, indent=1) + "\n")

# decoys: a shifted DIFFERENT sentence (no crib), genuine CJK prose, ROT8000 (CyberChef fixture) and ICU fullwidth
other = "The quick brown fox jumps over the lazy dog while the warmup waits for nobody at all today."
enc, gcmd = perl(other, "chr(ord($c)+0x4DE0)", 0, 0, None)
decoys = [
    ("cpshift-decoy-other-sentence", enc, gcmd, "not the warmups sentence: K from 'N' fails the crib"),
    ("cpshift-decoy-chinese", "你好世界，这是一个普通的中文句子，并没有经过任何旋转。", "hand-written genuine Chinese prose",
     "no constant K maps it onto the crib"),
    ("cpshift-decoy-rot8000", json.loads((HERE / "rot8000-amber.json").read_text())["encoded"],
     "rot8000-amber.json encoded (CyberChef ROT8000): spaces kept at ROT8000's offset -> must stay codec rot8000",
     "CyberChef ROT8000 decodes it (rot8000_cyberchef.mjs)"),
    ("cpshift-decoy-icu-fullwidth", json.loads((HERE / "fullwidth-amber.json").read_text())["encoded"],
     "fullwidth-amber.json encoded (uconv -x Halfwidth-Fullwidth, space -> U+3000): unistyle's, not a constant K",
     "NFKC folds it (unistyle)"),
]
for name, enc, gcmd, why in decoys:
    (HERE / f"{name}.json").write_text(json.dumps({
        "codec": "cpshift", "plain": None, "encoded": enc, "decoy": True, "expected": "none", "generator_cmd": gcmd,
        "oracle_cmd": "python3 -I -c \"import sys;t=sys.argv[1];k=ord(t[0])-ord('N');"
                      "print(''.join(chr(ord(c)-k) for c in t)[:20])\" \"$encoded\"  # " + why},
        ensure_ascii=False, indent=1) + "\n")
print("ok")
