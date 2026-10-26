"""Offline generator for the toy instruction-listing fixtures (lib.warmups_codecs vm_dec): every `encoded` comes from
a perl writer and every `oracle_plain` from a REAL interpreter of that dialect, never lib/: GNU dc 1.07.1 and gforth
0.7.3 (Ubuntu debs unpacked under tools/vmlangs), Ghostscript (print / txtwrite of show), keystone + unicorn for the
8086 listings (vmlisting_x86_oracle.py), and node for the generic stack / register VMs (vmlisting_oracle.mjs).
Run from the repo root: python3 tests/data/warmups_fixtures/vmlisting_mkfixtures.py"""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
S = "Nice work decoding this warmup! To solve, submit this exact answer to the Game Master: "
G = "tools/vmlangs/usr"
DC = f"{G}/bin/dc"
FORTH = (f"LD_LIBRARY_PATH={G}/lib/x86_64-linux-gnu {G}/bin/gforth-0.7.3 -i "
         f"{G}/lib/x86_64-linux-gnu/gforth/0.7.3/gforth.fi -p {G}/share/gforth/0.7.3 /dev/stdin -e bye")
GS_PRINT = "gs -q -dNODISPLAY -dNOPAUSE -dBATCH -dSAFER -"
GS_SHOW = "gs -q -dNOPAUSE -dBATCH -dSAFER -sDEVICE=txtwrite -sOutputFile=- - | sed 's/^ *//; s/\\r$//' | tr -d '\\n'"
X86 = ".venv/bin/python tests/data/warmups_fixtures/vmlisting_x86_oracle.py"
NODE = "tools/node/bin/node tests/data/warmups_fixtures/vmlisting_oracle.mjs"
PE = "perl -e '@c = unpack \"U*\", $ARGV[0]; "

CASES = [   # (name, codec, slug, generator, oracle, decoy)
    ("vm-dc-nP-amber", "vm-dc", "amber-falcon-42", PE + "print map { \"${_}P\" } @c' \"$plain\"", DC, False),
    ("vm-dc-hex-ibase-cobalt", "vm-dc", "cobalt-heron-17",
     PE + "print \"16i \", join(\" \", map { sprintf \"%XP\", $_ } @c), \"\\n\"' \"$plain\"", DC, False),
    ("vm-forth-emit-jade", "vm-forth", "jade-lynx-72", PE + "print join(\" \", map { \"$_ emit\" } @c)' \"$plain\"",
     FORTH, False),
    ("vm-forth-hex-char-maple", "vm-forth", "maple-otter-35",
     PE + "print join(\"\\n\", map { chr($_) =~ /[a-z]/ ? \"char \".chr($_).\" emit\" : sprintf(\"\\$%02X emit\", $_) }"
     " @c), \"\\n\"' \"$plain\"", FORTH, False),
    ("vm-ps-print-clover", "vm-ps", "clover-badger-88",
     "perl -e '($s = $ARGV[0]) =~ s/([\\\\()])/\\\\$1/g; print \"%!PS\\n($s) print\\n\"' \"$plain\"", GS_PRINT, False),
    ("vm-ps-show-ivory", "vm-ps", "ivory-moose-51",
     "perl -e '($s = $ARGV[0]) =~ s/([\\\\()])/\\\\$1/g; print \"%!PS\\n/Courier findfont 5 scalefont setfont\\n"
     "10 700 moveto\\n($s) show\\nshowpage\\n\"' \"$plain\"", GS_SHOW, False),
    ("vm-x86-bios-amber", "vm-x86", "amber-viper-23",
     PE + "print \"mov ah, 0x0e\\n\", map { sprintf \"mov al, 0x%02x\\nint 0x10\\n\", $_ } @c' \"$plain\"", X86, False),
    ("vm-x86-dos-cobalt", "vm-x86", "cobalt-lynx-64",
     PE + "print \"mov ah, 2\\n\", map { \"mov dl, $_    ; char\\nint 21h\\n\" } @c' \"$plain\"", X86, False),
    ("vm-stack-push-out-jade", "vm-stack", "jade-falcon-19",
     PE + "print map { \"PUSH $_\\nOUT\\n\" } @c; print \"HALT\\n\"' \"$plain\"", NODE, False),
    ("vm-stack-delta-maple", "vm-stack", "maple-heron-56",
     PE + "for (@c) { $d = int($_ / 2); print \"PUSH $d\\nPUSH \", $_ - $d, \"\\nADD\\nOUT\\n\" } print \"HALT\\n\"' "
     "\"$plain\"", NODE, False),
    ("vm-reg-mov-print-clover", "vm-reg", "clover-otter-31",
     PE + "$v = 0; print \"MOV R1, 0\\n\"; for (@c) { print $_ >= $v ? \"ADD R1, \" . ($_ - $v) : \"SUB R1, \" . "
     "($v - $_), \"\\nPRINT R1\\n\"; $v = $_ } print \"HALT\\n\"' \"$plain\"", NODE, False),
    ("vm-decoy-decimal-codes", "vm-*", "amber-moose-12", PE + "print join(\" \", @c)' \"$plain\"",
     f"{NODE}   # -> exits 1: a D5 decimal char-code list is not an instruction listing", True),
    ("vm-decoy-prose-mnemonics", "vm-*", None,
     "printf %s 'Push the button, then print the page and halt the press before you add more ink.'",
     f"{NODE}   # -> exits 1: English words that start with mnemonics are not instructions", True),
    ("vm-decoy-forth-no-emit", "vm-*", "ivory-falcon-77",
     PE + "print join(\" \", @c), \" dup drop\"' \"$plain\"",
     f"{FORTH}   # -> prints nothing: numbers pushed, never emitted", True),
]


def sh(cmd, env, stdin=None):
    r = subprocess.run(["bash", "-c", cmd], env=env, input=stdin, capture_output=True, text=True, timeout=60,
                       cwd=ROOT)
    return r.stdout, r.returncode


def main():
    for name, codec, slug, gen, oracle, decoy in CASES:
        plain = S + slug if slug else None
        env = dict(os.environ, plain=plain or "")
        enc, rc = sh(gen, env)
        assert rc == 0 and enc, name
        got, orc = sh(oracle.split("   #")[0], env, enc)
        fx = {"codec": codec, "plain": plain, "encoded": enc, "generator_cmd": gen, "oracle_cmd": oracle}
        if decoy:
            assert orc != 0 or (got or "").strip() == "" or got != plain, (name, got)
            fx.update(oracle_plain=got if orc == 0 else None, decoy=True, expected="none")
        else:
            assert orc == 0 and got == plain, (name, orc, got[:120])
            fx.update(oracle_plain=got, expected="match")
        (HERE / f"{name}.json").write_text(json.dumps(fx, indent=1, ensure_ascii=False) + "\n")
        print("wrote", name)


if __name__ == "__main__":
    main()
