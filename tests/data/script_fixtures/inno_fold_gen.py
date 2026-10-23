"""Generator for the inno_fold_* fixtures: take the D22 GM-verified polyglot-nsis plans, relabel them as Inno Setup
(language=inno_setup, campaign INNO_SETUP-..), re-encode them (stdlib binascii/base64) and wrap the literal in Inno
Setup .iss semantics. Usage: python3 inno_fold_gen.py <d22 evidence dir> <out dir>"""
import base64
import binascii
import re
import sys
from pathlib import Path

ev, out = Path(sys.argv[1]), Path(sys.argv[2])


def plan(name):
    lit = re.search(r'StrCpy \$0 "([^"]+)"', (ev / name).read_text()).group(1)
    if name.endswith("staged-chain.nsi"):
        p = base64.b64decode(lit).decode()
    elif name.endswith("benign-utility.nsi"):
        p = base64.b64decode(binascii.unhexlify(lit)).decode()
    else:
        p = binascii.unhexlify(lit.replace(".", "")).decode()
    return p.replace("language=nsis", "language=inno_setup").replace("NSIS-", "INNO_SETUP-").replace(
        "nsis-", "inno-setup-").replace("huntress-nsis", "huntress-inno")


def chunks(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]


def pas(s):                      # Pascal literal with '' doubling
    return "'" + s.replace("'", "''") + "'"


# 1. launcher (HEX): `{ }` marker in [Code], var Descriptor, `'..' + #$37#55 + '..'` char literals, `X := X + '..'`
h = binascii.hexlify(plan("polyglot-nsis-launcher.nsi").encode()).decode()
p = chunks(h, 80)
first = p[0]
L = ["; Huntress analysis installer", "[Setup]", "AppName=Huntress Analysis 95e72522", "AppVersion=1.0",
     "DefaultDirName={autopf}\\Huntress", "OutputBaseFilename=huntress-95e72522", "", "[Code]",
     "{ HUNTRESS_ANALYSIS_V1:HEX- descriptor assembled in InitializeWizard }", "var", "  Descriptor: String;",
     "  ResultCode: Integer;", "", "procedure InitializeWizard();", "begin",
     "  Descriptor := %s#$%02x#%d + %s +" % (pas(first[:6]), ord(first[6]), ord(first[7]), pas(first[8:40])),
     "    %s;" % pas(first[40:])]
for c in p[1:]:
    L.append("  Descriptor := Descriptor + %s;  // piece" % pas(c))
L += ["  Log('Don''t panic: ' + Descriptor);",
      "  Exec(ExpandConstant('{sys}\\cmd.exe'), '/c echo ' + Descriptor, '', SW_HIDE, ewWaitUntilTerminated, "
      "ResultCode);", "end;"]
(out / "inno_fold_pascal_concat.iss").write_text("\r\n".join(L) + "\r\n")

# 2. staged-chain (B64): ISPP #define pieces + `Part1 + Part2` expression, {#Descriptor} into [Setup] AppComments and
#    a Pascal const; marker in a (* *) comment split over lines
b = base64.b64encode(plan("polyglot-nsis-staged-chain.nsi").encode()).decode()
q = chunks(b, len(b) // 3 + 1)
L = ['#define AppVer "1.0"', '#define Part1 "%s"' % q[0], '#define Part2 "%s"' % q[1], '#define Part3 "%s"' % q[2],
     "#define Descriptor Part1 + Part2 + Part3", "", "[Setup]", "AppName=Huntress Staged {#AppVer}",
     "AppComments={#Descriptor}", "DefaultDirName={tmp}\\stage", "", "[Code]", "(* HUNTRESS_ANALYSIS_V1:",
     "   B64- see AppComments *)", "const", "  Stage = '{#Descriptor}';", "", "function InitializeSetup(): Boolean;",
     "begin", "  Result := Length(Stage) > 0;", "end;"]
(out / "inno_fold_ispp_define.iss").write_text("\n".join(L) + "\n")

# 3. downloader (FRAG): `const descriptor_<8hex> = '..' + '..';` with a `//` marker, and [Run] Parameters with
#    {cm:..} custom messages ("" doubling)
f = ".".join(chunks(binascii.hexlify(plan("polyglot-nsis-downloader.nsi").encode()).decode(), 24))
r = chunks(f, len(f) // 2 + 1)
L = ["[Setup]", "AppName=Huntress Downloader 469977fb", "DefaultDirName={autopf}\\HD", "", "[CustomMessages]",
     "english.D1=%s" % r[0], "english.D2=%s" % r[1], "", "[Run]",
     'Filename: "{cmd}"; Parameters: "/c echo ""{cm:D1}{cm:D2}"""; Flags: runhidden', "", "[Code]",
     "// HUNTRESS_ANALYSIS_V1:FRAG- (fragments joined by .)", "const",
     "  descriptor_469977fb = %s +" % pas(r[0]), "    %s;" % pas(r[1])]
(out / "inno_fold_const_run.iss").write_text("\n".join(L) + "\n")

# 4. benign utility (HB64): [Run] Parameters only, `;` marker in a section comment
hb = binascii.hexlify(base64.b64encode(plan("polyglot-nsis-benign-utility.nsi").encode())).decode()
L = ["; HUNTRESS_ANALYSIS_V1:HB64- see [Run]", "[Setup]", "AppName=Huntress Utility 2ed0a0c1",
     "DefaultDirName={autopf}\\HU", "[Run]",
     'Filename: "{sys}\\cmd.exe"; Parameters: "/c set D=%s"; Flags: runhidden waituntilterminated' % hb]
(out / "inno_fold_run_params.iss").write_text("\n".join(L) + "\n")

# 5. decoy: same shapes, the assembled base64 is a benign banner (no plan, no marker)
d = base64.b64encode(b"Thank you for installing Huntress Notepad 1.2 -- see readme.txt").decode()
L = ["[Setup]", "AppName=Huntress Notepad", "DefaultDirName={autopf}\\NP", "[Code]", "{ banner }", "var",
     "  Banner: String;", "procedure InitializeWizard();", "begin",
     "  Banner := %s + %s;" % (pas(d[:40]), pas(d[40:])), "  MsgBox(Banner, mbInformation, MB_OK);", "end;"]
(out / "inno_fold_decoy_banner.iss").write_text("\n".join(L) + "\n")
