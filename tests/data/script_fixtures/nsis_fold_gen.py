"""Generator for the nsis_fold_* fixtures: re-wrap the D22 polyglot-nsis members' StrCpy literal in NSIS string
semantics (stdlib only). Usage: python3 nsis_fold_gen.py <d22 evidence dir> <out dir>"""
import re
import sys
from pathlib import Path

ev, out = Path(sys.argv[1]), Path(sys.argv[2])


def lit(name):
    return re.search(r'StrCpy \$0 "([^"]+)"', (ev / name).read_text()).group(1)


def chunks(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]


# 1. launcher (plain hex): !define pieces (one !undef/redefined), ${X} appends, `\` continuation, /* */ split marker
h = lit("polyglot-nsis-launcher.nsi")
p = chunks(h, 96)
L = ["/* HUNTRESS_ANALYSIS_V1:", "   HEX- (see $0) */", "Unicode True", "!define /date STAMP \"%Y%m%d\"",
     "!define /math PARTS 2 * 4", "!define P0 \"deadbeef\"", "!undef P0", "!define P0 \"%s\"" % p[0],
     "!define Q \"${P0}\"", 'Name "Setup ${STAMP}"', 'OutFile "setup.exe"', "Section", '  StrCpy $0 "${Q}"']
for i, c in enumerate(p[1:], 1):
    a, b = c[:len(c) // 2], c[len(c) // 2:]
    L += ["!define P%d \"%s\\" % (i, a), "%s\"" % b, '  StrCpy $0 "$0${P%d}"  ; part %d' % (i, i)]
L += ["SectionEnd"]
(out / "nsis_fold_define_append.nsi").write_text("\n".join(L) + "\n")

# 2. staged-chain (base64): !macro + Push/Pop stack, Var /GLOBAL, LangString, '..' / `..` quotes, $1 slicing
b = lit("polyglot-nsis-staged-chain.nsi")
q = chunks(b, 120)
L = ["# HUNTRESS_ANALYSIS_V1:B64- ; assembled at runtime", "Unicode True", 'OutFile "setup.exe"',
     "Var /GLOBAL blob", "!macro PUSHPART part", "  Push `${part}`", "!macroend",
     'LangString TAIL ${LANG_ENGLISH} "%s"' % q[-1], "Section"]
for c in reversed(q[:-1]):
    L.append("  !insertmacro PUSHPART '%s'" % c)
L.append("  StrCpy $blob ''")
for _ in q[:-1]:
    L += ["  Pop $R1", '  StrCpy $blob "$blob$R1"']
L += ['  StrCpy $1 "XX$\\"$blob$(TAIL)$$9" -2 3 ; drop the 3-char pad and the trailing $$9', "SectionEnd"]
(out / "nsis_fold_macro_stack.nsi").write_text("\n".join(L) + "\n")

# 3. decoy: same shapes, but the assembled base64 is a benign banner (no plan)
import base64
d = base64.b64encode(b"Thank you for installing Huntress Notepad 1.2 -- see readme.txt").decode()
L = ["; installer banner", "!define A \"%s\"" % d[:40], "!define B \"%s\"" % d[40:], 'OutFile "np.exe"', "Section",
     '  StrCpy $0 "${A}"', '  StrCpy $0 "$0${B}"', "  MessageBox MB_OK $0", "SectionEnd"]
(out / "nsis_fold_decoy_banner.nsi").write_text("\n".join(L) + "\n")
