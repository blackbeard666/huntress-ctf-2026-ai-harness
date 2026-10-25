"""Offline generator for the code-point-notation knob fixtures (codepoints_any). Each `encoded` comes from an
independent writer (perl sprintf / node / python format / xxd) and each `oracle_plain` from an independent reader
(perl string eval, node eval, perl oct, python chr) -- never lib.warmups_codecs. Run: python3 <this file>."""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: {}"


def sh(cmd, **env):
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, env={**os.environ, **env})


CASES = [
    ("codepoints-perl-xbrace-amber", S.format("amber-falcon-42"),
     """printf %s "$plain" | perl -CSD -0777 -ne 'print join(" ", map { sprintf("\\\\x{%x}", ord) } split //)'""",
     """perl -CSD -e 'my $e = $ENV{encoded} =~ s/ //gr; print eval(qq{"$e"})'"""),
    ("codepoints-perl-Nuplus-adjacent-astral-cobalt", S.format("cobalt-otter-17") + " \U0001F600",
     """printf %s "$plain" | perl -CSD -0777 -ne 'print join("", map { sprintf("\\\\N{U+%04X}", ord) } split //)'""",
     """perl -CSD -e 'print eval(qq{"$ENV{encoded}"})'"""),
    ("codepoints-node-ubrace-adjacent-jade", S.format("jade-heron-73") + " \U0001F600",
     """node -e 'process.stdout.write([...process.env.plain].map(c => "\\\\u{" + c.codePointAt(0).toString(16).toUpperCase() + "}").join(""))'""",
     """node -e 'process.stdout.write(eval("\\"" + process.env.encoded + "\\""))'"""),
    ("codepoints-perl-short-uplus-mixedcase-maple", S.format("maple-badger-90"),
     """printf %s "$plain" | perl -CSD -0777 -ne 'my $i = 0; print join(" ", map { $i++ % 2 ? sprintf("u+%x", ord) : sprintf("U+%X", ord) } split //)'""",
     """python3 -I -c 'import os, re; print("".join(chr(int(h, 16)) for h in re.findall(r"[Uu]\\+([0-9A-Fa-f]+)", os.environ["encoded"])), end="")'"""),
    ("codepoints-python-0o-adjacent-clover", S.format("clover-lynx-05"),
     """python3 -I -c 'import os; print("".join(format(ord(c), "#o") for c in os.environ["plain"]), end="")'""",
     """perl -CSD -e 'print map { chr oct } $ENV{encoded} =~ /(0o[0-7]+?)(?=0o|$)/g'"""),
    ("codepoints-perl-0d-0b-semicolon-amber", S.format("amber-wolf-31"),
     """printf %s "$plain" | perl -CSD -0777 -ne 'my $i = 0; print join(";", map { $i++ % 2 ? sprintf("0b%b", ord) : sprintf("0d%d", ord) } split //)'""",
     """python3 -I -c 'import os; print("".join(chr(int(x[2:], 10 if x[1] == "d" else 2)) for x in os.environ["encoded"].split(";")), end="")'"""),
]
DECOYS = [
    ("codepoints-decoy-xxd-c-array-utf8-bytes", S.format("café-moth-11"),
     """printf %s "$plain" | xxd -i   # C array of UTF-8 BYTES (0xc3, 0xa9): hex/char-code decoders own it""",
     """printf %s "$encoded" | grep -o '0x[0-9a-f]*' | xxd -r -p   # reads back as UTF-8 bytes, not code points"""),
    ("codepoints-decoy-xxd-plain-hex", S.format("jade-crane-64"),
     """printf %s "$plain" | xxd -p -c0   # bare hex, no code-point prefix""",
     """printf %s "$encoded" | xxd -r -p"""),
]

for name, plain, gen, orc in CASES + DECOYS:
    decoy = (name, plain, gen, orc) in DECOYS
    r = sh(gen.split("   #")[0], plain=plain)
    assert r.returncode == 0, (name, r.stderr)
    enc = r.stdout.strip("\n") if decoy else r.stdout
    o = sh(orc.split("   #")[0], encoded=enc)
    assert o.returncode == 0 and o.stdout == plain, (name, o.stdout, o.stderr)
    fx = {"codec": "codepoints-any", "plain": None if decoy else plain, "encoded": enc,
          "generator_cmd": gen, "oracle_cmd": orc, "oracle_plain": o.stdout}
    if decoy:
        fx.update(decoy=True, expected="none", source_plain=plain)
    else:
        fx["expected"] = "match"
    (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1, ensure_ascii=False) + "\n")
    print(name, enc[:70])
