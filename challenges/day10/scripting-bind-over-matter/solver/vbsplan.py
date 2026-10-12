"""Static VBScript reconstruction for the Huntress WSH fixtures (nothing is run by a script host).

Each fixture stores a pipe-delimited plan `v=1|steps=...|adapter=...|campaign_id=...` as `Const Material_<id>`, loaded
into a byte array by `Load_<id>()` (decimal/hex text, some separator, maybe reversed) and un-transformed by
`Decode_<id>()` (xor / rolling xor / add-sub mod 256 / reverse). `Recover_<id>()` wraps the Decode call in a control-flow
construct (Select Case, Do..Exit Do, While..Wend, plain) and joins Chr() of the bytes.

Load and Decode are executed by a tiny VBScript-subset transpiler (assignments, Dim/ReDim, For..Next, single-line and
block If, Split/Mid/Len/UBound/CInt/Array/Chr/Asc...), so a variant with a different separator or transform still
decodes from its own code. The `Codec_<id>` const (`representation|transform|key`) names the representation and
transform; when it is absent the names are inferred from the code.
"""
import re

try:
    from lib.knowledge import VBS_CONTROL_FOR_ONCE, VBS_CONTROL_ON_ERROR
except ImportError:                 # standalone use without the project root on sys.path
    VBS_CONTROL_ON_ERROR, VBS_CONTROL_FOR_ONCE = "error_guard", "for_once"

# ---------------------------------------------------------------------------------------------------------------
# VBScript subset -> Python


class VArr(list):
    """VBScript array: a(i) reads (it is a call in the source), a[i] = v writes."""

    def __call__(self, i):
        return self[int(i)]


def _cint(x):
    if isinstance(x, str):
        s = x.strip()
        if s[:2].upper() == "&H":
            return int(s[2:], 16)
        if s[:2].upper() == "&O":
            return int(s[2:], 8)
        return int(round(float(s)))
    return int(round(x))


def _split(s, sep=" ", *_):
    return VArr(str(s).split(sep))


def _instr(*a):
    if len(a) >= 3 and isinstance(a[0], (int, float)):
        start, hay, needle = int(a[0]), str(a[1]), str(a[2])
    else:
        start, hay, needle = 1, str(a[0]), str(a[1])
    return hay.find(needle, start - 1) + 1


def _replace(s, find, repl, *_):
    return str(s).replace(str(find), str(repl)) if find != "" else str(s)


def _mid(s, start, length=None):
    s = str(s)
    a = int(start) - 1
    return s[a:] if length is None else s[a:a + int(length)]


BUILTINS = {
    "cint": _cint, "clng": _cint, "cbyte": _cint, "int": lambda x: int(x // 1), "fix": lambda x: int(x),
    "len": lambda s: len(str(s)), "ubound": lambda a, *_: len(a) - 1, "lbound": lambda a, *_: 0,
    "split": _split, "join": lambda a, sep=" ": sep.join(map(str, a)), "mid": _mid,
    "left": lambda s, n: str(s)[:int(n)], "right": lambda s, n: str(s)[len(str(s)) - int(n):] if int(n) else "",
    "chr": lambda n: chr(int(n)), "chrw": lambda n: chr(int(n)), "asc": lambda s: ord(str(s)[0]),
    "ascw": lambda s: ord(str(s)[0]), "array": lambda *a: VArr(a), "lcase": lambda s: str(s).lower(),
    "ucase": lambda s: str(s).upper(), "strreverse": lambda s: str(s)[::-1], "cstr": str,
    "hex": lambda n: "%X" % int(n), "abs": abs, "true": True, "false": False, "empty": "", "null": None,
    "vbnullstring": "", "instr": _instr, "replace": _replace, "trim": lambda s: str(s).strip(),
    "vbcr": "\r", "vblf": "\n", "vbcrlf": "\r\n", "vbtab": "\t", "vbnewline": "\r\n",
    "vbbinarycompare": 0, "vbtextcompare": 1,
}

_STR = re.compile(r'"(?:[^"]|"")*"')
_TOK = re.compile(r'"(?:[^"]|"")*"|&H[0-9A-Fa-f]+&?|&O[0-7]+&?|\d+(?:\.\d+)?|[A-Za-z_]\w*|<>|<=|>=|[-+*/\\^&=<>(),:]|\s+')
_KW = {"mod": "%", "xor": "^", "and": "&", "or": "|", "not": "~", "is": "is"}


def expr_py(src, cond=False):
    """Translate one VBScript expression to Python source. Raises ValueError on anything outside the subset."""
    out, pos = [], 0
    src = src.strip()
    while pos < len(src):
        m = _TOK.match(src, pos)
        if not m:
            raise ValueError("untranslatable: %r" % src[pos:pos + 20])
        t = m.group(0)
        pos = m.end()
        lt = t.lower()
        if t.isspace():
            out.append(" ")
        elif t.startswith('"'):
            out.append(repr(t[1:-1].replace('""', '"')))
        elif lt.startswith("&h"):
            out.append(str(int(t[2:].rstrip("&"), 16)))
        elif lt.startswith("&o"):
            out.append(str(int(t[2:].rstrip("&"), 8)))
        elif t == "&":
            out.append(" + ")      # string concatenation (operands here are strings)
        elif t == "\\":
            out.append(" // ")
        elif t == "^":
            out.append(" ** ")
        elif t == "<>":
            out.append(" != ")
        elif t == "=":
            out.append(" == " if cond else "=")
        elif lt in _KW:
            out.append(" %s " % _KW[lt])
        elif re.match(r"[A-Za-z_]", t):
            if "__" in t:
                raise ValueError("bad identifier")
            out.append("v_" + lt)
        else:
            out.append(t)
    return "".join(out)


class VBS:
    """Holds the module text; runs the subset of Function bodies we need."""

    def __init__(self, text):
        self.text = text.replace("\r\n", "\n").replace("\r", "\n")
        self.text = re.sub(r"[ \t]+_\n[ \t]*", " ", self.text)       # line continuations
        self.consts = {}
        self.funcs = {}
        for m in re.finditer(r"(?ims)^\s*(?:Private\s+|Public\s+)?(Function|Sub)\s+(\w+)\s*(?:\(([^)]*)\))?\s*$(.*?)^\s*End\s+\1\b",
                             self.text):
            args = [re.sub(r"(?i)^\s*(ByRef|ByVal)\s+", "", a).strip().lower() for a in (m.group(3) or "").split(",") if a.strip()]
            self.funcs[m.group(2).lower()] = (args, m.group(4))

        for m in re.finditer(r"(?im)^\s*(?:Private\s+|Public\s+)?Const\s+(\w+)\s*=\s*(.+?)\s*$", self.text):
            try:
                self.consts[m.group(1).lower()] = self.eval(m.group(2), {})
            except Exception:
                pass
    def ns(self, local):
        env = {"v_" + k: v for k, v in BUILTINS.items()}
        env.update({"v_" + k: v for k, v in self.consts.items()})
        for name in self.funcs:
            env["v_" + name] = (lambda n: lambda *a: self.call(n, *a))(name)
        env.update(local)
        return env

    _code = {}

    def eval(self, src, local, cond=False):
        code = self._code.get((src, cond))
        if code is None:
            code = self._code[(src, cond)] = compile(expr_py(src, cond), "<vbs>", "eval")
        return eval(code, {"__builtins__": {}}, self.ns(local))  # subset-only source, no attribute access

    def call(self, name, *args, depth=0):
        argn, body = self.funcs[name.lower()]
        local = {"v_" + a: v for a, v in zip(argn, args)}
        lines = [ln.split("'")[0].strip() if "\"" not in ln else ln.strip() for ln in body.split("\n")]
        lines = [ln for ln in lines if ln and not ln.startswith("'")]
        self._run(lines, local, 0)
        return local.get("v_" + name.lower())

    def _assign(self, lhs, rhs, local):
        val = self.eval(rhs, local)
        m = re.match(r"^(\w+)\s*\((.+)\)$", lhs)
        if m:
            local["v_" + m.group(1).lower()][int(self.eval(m.group(2), local))] = val
        else:
            local["v_" + lhs.lower()] = val

    def _block_end(self, lines, i, open_re, close_re):
        depth = 0
        for j in range(i, len(lines)):
            if re.match(open_re, lines[j], re.I):
                depth += 1
            elif re.match(close_re, lines[j], re.I):
                depth -= 1
                if depth == 0:
                    return j
        raise ValueError("unterminated block")

    def _run(self, lines, local, guard):
        i = 0
        while i < len(lines):
            ln = lines[i]
            low = ln.lower()
            if re.match(r"^(dim|option|on error|call\s)", low) or low in ("exit function", "exit sub"):
                if low.startswith(("exit function", "exit sub")):
                    return "exit"
                i += 1
                continue
            if re.match(r"(?i)^Err\.Raise\b", ln):
                raise ValueError("script raised: %r" % ln)
            m = re.match(r"(?i)^ReDim\s+(Preserve\s+)?(\w+)\s*\((.+)\)$", ln)
            if m:
                n = int(self.eval(m.group(3), local)) + 1
                old = list(local.get("v_" + m.group(2).lower()) or []) if m.group(1) else []
                local["v_" + m.group(2).lower()] = VArr((old + [0] * n)[:n])
                i += 1
                continue
            m = re.match(r"(?i)^For\s+(\w+)\s*=\s*(.+?)\s+To\s+(.+?)(?:\s+Step\s+(.+))?$", ln)
            if m:
                end = self._block_end(lines, i, r"^For\s", r"^Next\b")
                a, b = int(self.eval(m.group(2), local)), int(self.eval(m.group(3), local))
                step = int(self.eval(m.group(4), local)) if m.group(4) else 1
                v = a
                while (v <= b) if step > 0 else (v >= b):
                    local["v_" + m.group(1).lower()] = v
                    if self._run(lines[i + 1:end], local, guard) == "exit":
                        return "exit"
                    v += step
                i = end + 1
                continue
            m = re.match(r"(?i)^If\s+(.+?)\s+Then\s+(.+?)(?:\s+Else\s+(.+))?$", ln)
            if m:      # single-line If
                br = m.group(2) if self.eval(m.group(1), local, cond=True) else m.group(3)
                if br and self._run([br], local, guard) == "exit":
                    return "exit"
                i += 1
                continue
            m = re.match(r"(?i)^If\s+(.+?)\s+Then$", ln)
            if m:
                end = self._block_end(lines, i, r"^If\s.+\sThen$", r"^End\s+If\b")
                body = lines[i + 1:end]
                # split on a top-level Else
                depth, cut = 0, None
                for k, b in enumerate(body):
                    if re.match(r"(?i)^If\s.+\sThen$", b):
                        depth += 1
                    elif re.match(r"(?i)^End\s+If\b", b):
                        depth -= 1
                    elif depth == 0 and re.match(r"(?i)^Else$", b):
                        cut = k
                yes, no = (body, []) if cut is None else (body[:cut], body[cut + 1:])
                if self._run(yes if self.eval(m.group(1), local, cond=True) else no, local, guard) == "exit":
                    return "exit"
                i = end + 1
                continue
            m = re.match(r"^([\w]+(?:\s*\(.+?\))?)\s*=\s*(.+)$", ln)
            if m:
                self._assign(m.group(1), m.group(2), local)
                i += 1
                continue
            raise ValueError("unsupported statement: %r" % ln)


# ---------------------------------------------------------------------------------------------------------------
# fixture analysis

SEP_NAMES = {"|": "pipe", "-": "dash", ",": "comma", ":": "colon", " ": "space", ";": "semicolon", ".": "dot", "/": "slash"}


def _fn(vbs, prefix):
    return next((n for n in vbs.funcs if n.startswith(prefix.lower())), None)


def infer_representation(load_src):
    if re.search(r"(?i)\bBase64_?\w*\s*\(", load_src):      # Material is Base64 text (maybe split into Mid() chunks)
        return "base64_chunks" if re.search(r"(?i)\bMid\s*\(", load_src) else "base64_literal"
    hexa = bool(re.search(r'"&H"', load_src, re.I))
    rev = bool(re.search(r"(?i)\(\s*UBound\s*\([^)]*\)\s*-\s*\w+\s*\)\s*=", load_src))
    m = re.search(r'(?i)Split\s*\(\s*\w+\s*,\s*"([^"]*)"', load_src)
    if m:
        sep = SEP_NAMES.get(m.group(1), "delimited")
        base = ("hex_" if hexa else "decimal_") + sep
    else:
        base = "hex_compact" if hexa else "decimal_compact"
    return ("reversed_" + base.split("_")[0]) if rev and base.endswith("comma") else (("reversed_" + base) if rev else base)


def infer_transform(dec_src):
    s = dec_src
    rev = re.search(r"(?i)\(\s*UBound\s*\([^)]*\)\s*-\s*\w+\s*\)\s*=", s)
    if rev and re.search(r"(?i)\bXor\b", s):
        return "reverse_then_xor"
    if re.search(r"(?i)\bXor\s+previous\b", s) or re.search(r"(?i)previous\s*=", s) and re.search(r"(?i)\bXor\b", s):
        return "rolling_xor"
    if re.search(r"(?i)\bXor\s+\w+\s*\(\s*\w+\s+Mod\s+\d+", s):
        return "repeating_key_xor"
    if re.search(r"(?i)\bXor\s+(\d+|&H[0-9a-f]+)", s):
        return "single_byte_xor"
    if re.search(r"(?i)\+\s*\d+\s*\)\s*Mod\s+256", s):
        return "subtract_modulo_256"     # the material was produced by subtracting the key; decoding adds it back
    if re.search(r"(?i)-\s*\d+(\s*\+\s*256)?\s*\)\s*Mod\s+256", s):
        return "add_modulo_256"
    if rev:
        return "reverse_bytes"
    if re.search(r"(?i)^\s*(\w+)\s*\(\s*(\w+)\s*\)\s*=\s*\w+\s*\(\s*\2\s*\)\s*$", s, re.M):
        return "identity"            # result(i) = s(i)
    return None


def control_form(recover_src, decode_name=None):
    """Construct wrapping the Decode call inside Recover_<id>, GM vocabulary (lib.knowledge.VBS_CONTROL_VOCAB):
    direct / select_case / do_once (Do .. Exit Do .. Loop) / while_once (While p < 1 .. Wend). An outer
    `If True Then .. End If` block and single-line opaque `If (2 > 1) Then .. Else ..` junk are noise (GM-confirmed).
    Also `On Error Resume Next` .. `On Error GoTo 0` (GM: NOT direct, NOT on_error_resume; VBS_CONTROL_ON_ERROR) and a run-once
    `For p = 0 To 0` .. `Next` (VBS_CONTROL_FOR_ONCE)."""
    lines = [ln.strip() for ln in recover_src.split("\n")]
    call = next((i for i, ln in enumerate(lines) if decode_name and re.search(r"(?i)\b%s\s*\(" % re.escape(decode_name), ln)),
                None)
    if call is None:
        call = next((i for i, ln in enumerate(lines) if re.search(r"(?i)\bDecode_\w*\s*\(", ln)), None)
    if call is None:
        return "direct"
    # innermost open block around the call
    stack, on_error = [], None
    for ln in lines[:call]:
        low = ln.lower()
        if re.match(r"select\s+case\b", low):
            stack.append("select_case")
        elif re.match(r"end\s+select\b", low):
            stack and stack.pop()
        elif re.match(r"do\b", low):
            stack.append("do_once")
        elif re.match(r"loop\b", low):
            stack and stack.pop()
        elif re.match(r"while\b", low):
            stack.append("while_once")
        elif re.match(r"wend\b", low):
            stack and stack.pop()
        elif re.match(r"on\s+error\s+resume\s+next\b", low):
            on_error = len(stack)              # a mode, not a block: remember the depth it was switched on at
        elif re.match(r"on\s+error\s+goto\s+0\b", low):
            on_error = None
        elif re.match(r"for\b", low):
            m = re.match(r"for\s+\w+\s*=\s*(-?\d+)\s+to\s+(-?\d+)\s*$", low)
            stack.append(VBS_CONTROL_FOR_ONCE if m and m.group(1) == m.group(2) else "for")
        elif re.match(r"next\b", low):
            stack and stack.pop()
        elif re.match(r"if\b.*\bthen$", low):
            stack.append("if")
        elif re.match(r"end\s+if\b", low):
            stack and stack.pop()
    forms = [(i, f) for i, f in enumerate(stack) if f in ("select_case", "do_once", "while_once", VBS_CONTROL_FOR_ONCE)]
    if on_error is not None and (not forms or on_error > forms[-1][0]):
        return VBS_CONTROL_ON_ERROR
    return forms[-1][1] if forms else "direct"


SEP_CHARS = {v: k for k, v in SEP_NAMES.items()}


def codec_decode(material, rep, trans, key):
    """Decode straight from the `Codec_` description (fallback/cross-check for the interpreter)."""
    try:
        r = rep.lower()
        kind, _, sep = r.partition("_")
        if kind == "base64":            # base64_literal / base64_chunks (chunks are re-joined in order)
            import base64
            vals = list(base64.b64decode(re.sub(r"\s+", "", material)))
        elif kind == "reversed":
            vals = [int(x) for x in re.split(r"[^0-9]+", material) if x][::-1]
        elif kind == "hex":
            vals = [int(material[i:i + 2], 16) for i in range(0, len(material), 2)] if sep == "compact" else \
                [int(x, 16) for x in material.split(SEP_CHARS.get(sep, sep)) if x]
        else:
            vals = [int(x) for x in material.split(SEP_CHARS.get(sep, sep)) if x]
        keys = [int(k, 16) for k in (key or "").split(",") if k.strip()]
        t = trans.lower()
        if t == "subtract_modulo_256":
            vals = [(v + keys[0]) % 256 for v in vals]
        elif t == "add_modulo_256":
            vals = [(v - keys[0]) % 256 for v in vals]
        elif t in ("single_byte_xor", "repeating_key_xor", "xor"):
            vals = [v ^ keys[i % len(keys)] for i, v in enumerate(vals)]
        elif t == "reverse_then_xor":    # decode: result(UBound - i) = s(i) Xor key
            vals = [v ^ keys[i % len(keys)] for i, v in enumerate(vals)][::-1]
        elif t == "identity":
            pass
        elif t == "rolling_xor":
            prev, out = keys[0], []
            for v in vals:
                out.append(v ^ prev)
                prev = v
            vals = out
        elif t == "reverse_bytes":
            vals = vals[::-1]
        else:
            return None
        return "".join(map(chr, vals))
    except Exception:
        return None


def analyse(data, plain_hint=None):
    """plain_hint: the declared codec already decoded by the caller (lib.codec). A `v=` plan there skips the
    interpreter, which costs ~40 ms/file and agreed with lib.codec on every codec-bearing case (117/117)."""
    text = data.decode("utf-8", "ignore").lstrip("﻿")
    vbs = VBS(text)
    load, dec, rec = _fn(vbs, "load_"), _fn(vbs, "decode_"), _fn(vbs, "recover_")
    codec = next((v for k, v in vbs.consts.items() if k.startswith("codec") and isinstance(v, str)), None)
    rep = trans = key = None
    if codec and codec.count("|") >= 1:
        rep, trans, key = (codec.split("|") + [""])[:3]
    load_src = vbs.funcs[load][1] if load else ""
    dec_src = vbs.funcs[dec][1] if dec else ""
    plain = plain_hint if plain_hint and plain_hint.startswith("v=") else ""
    if load and dec and not plain:
        try:
            out = vbs.call(dec, vbs.call(load))
            plain = "".join(chr(int(b) & 0xFFFF) for b in out)
        except Exception as e:      # statement outside the subset: fall back to the Codec description
            import sys
            print("vbsplan: interpreter failed (%r); using Codec_ fallback" % (e,), file=sys.stderr)
    if not plain.startswith("v=") and rep and trans:
        material = next((v for k, v in vbs.consts.items() if k.startswith("material") and isinstance(v, str)), None)
        alt = codec_decode(material, rep, trans, key) if material else None
        if alt and (alt.startswith("v=") or not plain):
            plain = alt
    plan = {}
    for part in plain.split("|"):
        k, eq, v = part.partition("=")
        if eq:
            plan.setdefault(k.strip(), v)
    return {"plain": plain, "plan": plan,
            "representation": rep or infer_representation(load_src),
            "transform": trans or infer_transform(dec_src),
            "inferred": {"representation": infer_representation(load_src), "transform": infer_transform(dec_src)},
            "key": key, "control": control_form(vbs.funcs[rec][1] if rec else "", dec)}


if __name__ == "__main__":
    import json, sys
    for p in sys.argv[1:]:
        r = analyse(open(p, "rb").read())
        print(p, json.dumps(r))
