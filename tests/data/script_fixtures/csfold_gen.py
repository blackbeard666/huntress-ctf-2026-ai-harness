"""Generator for the csfold_* fixtures (target csharp-literal-fold), stdlib only.
Reads a D19 .csx specimen, takes its `descriptor_<id> = "..."` literal and re-assembles it in one .NET runtime form per
output file (marker comment line dropped, so only the folded expression carries the plan).
usage: python3 -I csfold_gen.py <specimen.csx> <form> <out>   (forms: see FORMS)"""
import base64
import random
import re
import sys


def u(s):
    """C# literal body with every non-[A-Za-z0-9+/=] char as \\uXXXX."""
    return "".join(c if re.match(r"[A-Za-z0-9+/=]", c) else "\\u%04x" % ord(c) for c in s)


def chunks(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]


def form(name, ident, d):
    v = f"descriptor_{ident}"
    tail = (f'IReadOnlyDictionary<string,string> BuildPlan_{ident}() => new Dictionary<string,string> '
            f'{{ ["descriptor"] = {v} }};\n')
    head = "#nullable enable\nusing System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Text;\n"
    if name == "cs_concat":          # string.Concat over \u-escaped, verbatim, raw, (char) hex/dec, char literal pieces
        a, b, c, rest = d[:6], d[6:20], d[20:40], d[43:]
        body = (f'string {v} = string.Concat("{u(a)}", @"{b}", """{c}""", (char)0x{ord(d[40]):x}, (char){ord(d[41])}, '
                f"'{d[42]}', \"{rest}\");\n")
    elif name == "cs_bytes_b64":      # Encoding.UTF8.GetString(new byte[] {..}) + ASCII.GetString(FromBase64String(..))
        a, rest = d[:48], d[48:]
        body = (f"const string tail_{ident} = \"{base64.b64encode(rest.encode()).decode()}\";\n"
                f"string {v} = Encoding.UTF8.GetString(new byte[] {{ {', '.join(str(b) for b in a.encode())} }}) + "
                f"Encoding.ASCII.GetString(Convert.FromBase64String(tail_{ident}));\n")
    elif name == "cs_sb_interp":      # const locals, StringBuilder().Append chains, $"{a}{b}"
        p = chunks(d, (len(d) + 3) // 4)
        body = "".join(f'const string p{i}_{ident} = "{x}";\n' for i, x in enumerate(p))
        body += (f"var sb_{ident} = new StringBuilder();\nsb_{ident}.Append(p0_{ident}).Append(p1_{ident});\n"
                 f'sb_{ident}.Append($"{{p2_{ident}}}{{p3_{ident}}}");\nstring {v} = sb_{ident}.ToString();\n')
    elif name == "cs_xor_reverse":    # ToCharArray + `^ 0x5A` for-loop + Array.Reverse
        x = "".join(chr(ord(c) ^ 0x5A) for c in d[::-1])
        body = (f'char[] buf_{ident} = "{u(x)}".ToCharArray();\n'
                f"for (int i = 0; i < buf_{ident}.Length; i++) {{ buf_{ident}[i] = (char)(buf_{ident}[i] ^ 0x5A); }}\n"
                f"Array.Reverse(buf_{ident});\nstring {v} = new string(buf_{ident});\n")
    elif name == "cs_hex_bitconv":    # BitConverter.ToString(..).Replace("-", "") + FromHexString + LINQ Reverse + Join
        n = len(d) // 3 // 2 * 2
        a, b, c = d[:n], d[n:2 * n], d[2 * n:]
        body = (f'string {v} = string.Join("", new[] {{ BitConverter.ToString(Convert.FromBase64String('
                f'"{base64.b64encode(bytes.fromhex(a)).decode()}")).Replace("-", "").ToLowerInvariant(), '
                f'Encoding.UTF8.GetString(Convert.FromHexString("{b.encode().hex().upper()}")), '
                f'new string("{c[::-1]}".Reverse().ToArray()) }});\n')
    elif name == "cs_select_xor":     # LINQ .Select(c => (char)(c ^ 0x21)) + new string(new char[] {..})
        x = "".join(chr(ord(c) ^ 0x21) for c in d[8:])
        body = (f"string {v} = new string(new char[] {{ {', '.join(repr(c) for c in d[:8])} }}) + "
                f'new string("{u(x)}".Select(c => (char)(c ^ 0x21)).ToArray());\n')
    elif name == "cs_decoy":          # same assembly forms, benign config text: no v=3 plan
        cfg = "theme=dark|font=Consolas|hotkey=ctrl+alt+t|window=Notepad|autosave=on|interval=300"
        b = base64.b64encode(cfg.encode()).decode()
        body = (f'string {v} = string.Concat(Encoding.UTF8.GetString(new byte[] {{ {", ".join(str(c) for c in b[:10].encode())} }}), '
                f'(char)0x{ord(b[10]):x}, "{b[11:]}");\n')
    elif name == "vb_chrw":           # VB.NET: ChrW(n) & .. & StrReverse(..) with `& _` line continuations
        body = None
        a, b, rest = d[:6], d[6:len(d) // 2], d[len(d) // 2:]
        vb = ("Imports System\nImports Microsoft.VisualBasic\nModule M\n    Sub Main()\n"
              f"        Dim {v} As String = " + " & ".join(f"ChrW({ord(c)})" for c in a) + " & _\n"
              f'            StrReverse("{b[::-1]}") & _\n            "{rest}"\n'
              f"        Console.Write({v})\n    End Sub\nEnd Module\n")
        return vb
    elif name == "fs_concat":         # F#: String.concat "" [..] with char/string pieces
        a, b, rest = d[:5], d[5:30], d[30:]
        return (f"let {v} =\n    String.concat \"\" [ " + "; ".join(f"string (char {ord(c)})" for c in a) +
                f'; "{b}"; "{rest}" ]\nprintf "%s" {v}\n')
    else:
        raise SystemExit(f"unknown form {name}")
    return head + body + tail


FORMS = ("cs_concat", "cs_bytes_b64", "cs_sb_interp", "cs_xor_reverse", "cs_hex_bitconv", "cs_select_xor", "cs_decoy",
         "vb_chrw", "fs_concat")

if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8").read()
    m = re.search(r'string descriptor_(\w+) = "([^"]+)";', src)
    random.seed(19)
    open(sys.argv[3], "w", encoding="utf-8", newline="\n").write(form(sys.argv[2], m.group(1), m.group(2)))
