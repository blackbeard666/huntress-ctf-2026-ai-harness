"""Bash "behavior graph" fixtures (Day 6 "Shell We Begin"). Never executed: everything is read statically.

Each .sh file holds `readonly Material_<id>='...'` (the plan bytes in some representation) and
`readonly Codec_<id>='rep|transform|key'`, plus Load_<id> (representation -> byte list), Decode_<id> (undo the byte
transform), Recover_<id> (bytes -> text, the Decode call wrapped in some control construct), Inspect_/Plan_ wrappers.
The recovered text is `v=1|steps=a,b,c|adapter=..|stage_count=N|campaign_id=..|<indicator>=..`.

Two independent decoders: `codec_decode` (driven by the Codec_ const) and `code_decode` (representation and
transform inferred from the Load_/Decode_ function bodies, so a variant without the Codec_ const or with a new codec
name still decodes). A plan is accepted only if it parses as k=v|... text; when both decode, they must agree."""
import base64
import re

ASSIGN = r"(?:^|[\s;])(?:readonly\s+|declare\s+-[a-zA-Z]+\s+|local\s+(?:-[a-zA-Z]+\s+)?|typeset\s+-[a-zA-Z]+\s+|export\s+)?"


def bash_word(s, i):
    """Parse one shell word starting at s[i] (concatenated '..', "..", $'..' and bare parts) -> (value, end)."""
    out = []
    n = len(s)
    while i < n and not s[i].isspace() and s[i] not in ";&|)":
        c = s[i]
        if c == "'":
            j = s.index("'", i + 1)
            out.append(s[i + 1:j])
            i = j + 1
        elif c == "$" and i + 1 < n and s[i + 1] == "'":
            j = i + 2
            buf = []
            while s[j] != "'":
                if s[j] == "\\":
                    buf.append(s[j:j + 2])
                    j += 2
                else:
                    buf.append(s[j])
                    j += 1
            out.append(_ansi_c("".join(buf)))
            i = j + 1
        elif c == '"':
            j = i + 1
            buf = []
            while s[j] != '"':
                if s[j] == "\\" and s[j + 1] in '"\\$`\n':
                    buf.append(s[j + 1])
                    j += 2
                else:
                    buf.append(s[j])
                    j += 1
            out.append("".join(buf))
            i = j + 1
        elif c == "\\":
            out.append(s[i + 1:i + 2])
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out), i


def _ansi_c(s):
    return re.sub(r"\\(x[0-9a-fA-F]{1,2}|[0-7]{1,3}|.)", lambda m: chr(int(m.group(1)[1:], 16)) if m.group(1)[0] == "x"
                  else chr(int(m.group(1), 8)) if m.group(1)[0] in "01234567"
                  else {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", "'": "'", '"': '"'}.get(m.group(1), m.group(1)), s)


def assignment(text, prefix):
    """{suffix_id: value} for `<prefix><id>=<word>` assignments, incl. `<prefix><id>=( w1 w2 ... )` arrays (joined
    with a space) and later `+=` appends."""
    out = {}
    for m in re.finditer(ASSIGN + r"(%s([A-Za-z0-9_]+))(\+?)=" % re.escape(prefix), text, re.M):
        fid, plus, i = m.group(2), m.group(3), m.end()
        if i < len(text) and text[i] == "(":
            i += 1
            parts = []
            while True:
                while i < len(text) and text[i].isspace():
                    i += 1
                if i >= len(text) or text[i] == ")":
                    break
                w, i = bash_word(text, i)
                parts.append(w)
            val = " ".join(parts)
        else:
            val, _ = bash_word(text, i)
        out[fid] = out.get(fid, "") + val if plus else val
    return out


def func_body(text, name):
    """Body of the bash function `name` (`name() {` or `function name {`), brace matched outside quotes."""
    m = re.search(r"(?:^|[\s;])(?:function\s+)?%s\s*(?:\(\s*\))?\s*\{" % re.escape(name), text, re.M)
    if not m:
        return ""
    i, depth, q = m.end(), 1, None
    j = i
    while j < len(text):
        c = text[j]
        if q:
            if c == "\\" and q == '"':
                j += 1
            elif c == q:
                q = None
        elif c in "'\"" and text[j - 1] != "\\":
            q = c
        elif c == "{" and text[j - 1] != "$":
            depth += 1
        elif c == "}" and not _param_close(text, j):
            depth -= 1
            if depth == 0:
                return text[i:j]
        j += 1
    return text[i:]


def _param_close(text, j):
    """True when the '}' at j closes a ${...} parameter expansion on the same line."""
    line_start = text.rfind("\n", 0, j) + 1
    seg = text[line_start:j]
    return seg.count("${") > seg.count("}")


# ---------------------------------------------------------------- representation -> bytes
def material_bytes(material, rep):
    rep = (rep or "").lower()
    s = material.strip()
    if "base64" in rep or "b64" in rep:
        s2 = re.sub(r"\s", "", s)
        s2 += "=" * (-len(s2) % 4)
        data = base64.urlsafe_b64decode(s2) if ("urlsafe" in rep or "url" in rep) else base64.b64decode(s2)
    elif "base32" in rep:
        s2 = re.sub(r"\s", "", s).upper()
        data = base64.b32decode(s2 + "=" * (-len(s2) % 8))
    elif "octal" in rep:
        data = bytes(int(x, 8) for x in re.findall(r"[0-7]+", s))
    elif "hex" in rep:
        toks = re.findall(r"(?:0x|\\x)?([0-9a-fA-F]+)", s.replace("%", " "))
        if "compact" in rep or (len(toks) == 1 and len(toks[0]) > 2):
            data = bytes.fromhex("".join(toks))
        else:
            data = bytes(int(t, 16) for t in toks)
    else:
        data = bytes(int(x) for x in re.findall(r"\d+", s))
    if rep.startswith("reversed") or rep.endswith("reversed"):
        data = data[::-1]
    return data


def untransform(data, transform, key):
    """Undo the ENCODE-side transform named in the Codec (add_modulo_256 encoded by adding -> decode subtracts)."""
    t = (transform or "").lower()
    kb = key_bytes(key)
    k = kb[0] if kb else 0
    if t in ("identity", "none", "plain", ""):
        return data
    if t == "reverse_bytes":
        return data[::-1]
    if t == "reverse_then_xor":
        return bytes(b ^ k for b in data[::-1])
    if t == "xor_then_reverse":
        return bytes(b ^ k for b in data)[::-1]
    if t == "single_byte_xor":
        return bytes(b ^ k for b in data)
    if t == "repeating_key_xor":
        return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))
    if t == "rolling_xor":  # VBS generator: plain = c ^ prev, prev = the cipher byte, seeded with the key
        out, prev = [], k
        for b in data:
            out.append(b ^ prev)
            prev = b
        return bytes(out)
    if t == "subtract_modulo_256":
        return bytes((b + k) % 256 for b in data)
    if t == "add_modulo_256":
        return bytes((b - k) % 256 for b in data)
    raise ValueError("unknown transform " + t)


def key_bytes(key):
    key = (key or "").strip()
    if not key:
        return b""
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", key):
        return bytes.fromhex(key)
    toks = re.split(r"[^0-9a-fA-Fx]+", key)
    if all(re.fullmatch(r"(?:0x)?[0-9a-fA-F]{1,2}", t) for t in toks if t):
        return bytes(int(t, 16) for t in toks if t)
    return key.encode()


def codec_decode(material, codec):
    rep, transform, key = (codec.split("|") + ["", "", ""])[:3]
    return untransform(material_bytes(material, rep), transform, key)


# ---------------------------------------------------------------- inference from the function bodies
def infer_representation(load):
    if re.search(r"\bbase64\s+(?:--decode|-d|-D)\b", load):
        rep = "base64"
    elif re.search(r"\bbase32\s+(?:--decode|-d)\b", load):
        rep = "base32"
    elif "16#" in load or re.search(r"\bxxd\s+-r", load):
        rep = "hex"
    elif "8#" in load:
        rep = "octal"
    else:
        rep = "decimal"
    if re.search(r"for\s*\(\(\s*\w+\s*=\s*\$\{#\w+\[@\]\}\s*-\s*1\s*;[^)]*--", load) or re.search(r"\btac\b|\brev\b", load):
        rep = "reversed_" + rep
    return rep


def _int(tok):
    tok = tok.strip()
    if tok.lower().startswith("0x"):
        return int(tok, 16)
    if "#" in tok:
        b, v = tok.split("#", 1)
        return int(v, int(b))
    return int(tok)


NUM = r"(?:0[xX][0-9a-fA-F]+|\d+#[0-9a-zA-Z]+|\d+)"


def infer_transform(dec):
    """(transform, key_hex) from the arithmetic in Decode_<id>()."""
    reverse = bool(re.search(r"\[\s*\$\{#\w+\[@\]\}\s*-\s*1\s*-\s*\w+\s*\]", dec))
    reverse = reverse or bool(re.search(r"for\s*\(\(\s*\w+\s*=\s*\$\{#\w+\[@\]\}\s*-\s*1\s*;[^)]*--", dec))
    m_chain = re.search(r"\^\s*\$?\{?(\w+)\}?\s*\)\)", dec)
    if m_chain and re.search(r"\b%s=\$?\{?\w+\[" % m_chain.group(1), dec):  # c ^ prev; prev = cipher byte
        seed = re.search(r"\b%s=(%s)\b" % (m_chain.group(1), NUM), dec)
        return "rolling_xor", "%02x" % _int(seed.group(1)) if seed else None
    m_xor = re.search(r"\^\s*(%s)\b" % NUM, dec)
    m_xor_arr = re.search(r"\^\s*\$?\{?\w+\[\s*\$?\w+\s*%\s*", dec)
    m_sub = re.search(r"-\s*(%s)\s*\+\s*256\s*\)\s*%%\s*256" % NUM, dec)
    m_add = re.search(r"\+\s*(%s)\s*\)\s*%%\s*256" % NUM, dec)
    m_roll = re.search(r"\^\s*\(\s*\(?\s*(%s)\s*\+\s*\w+\s*\)?\s*%%\s*256" % NUM, dec)
    if m_roll:
        return "rolling_xor", "%02x" % _int(m_roll.group(1))
    if m_xor_arr:
        return "repeating_key_xor", None
    if m_xor:
        return ("reverse_then_xor" if reverse else "single_byte_xor"), "%02x" % _int(m_xor.group(1))
    if m_sub:  # decode subtracts -> encode added
        return "add_modulo_256", "%02x" % _int(m_sub.group(1))
    if m_add:
        return "subtract_modulo_256", "%02x" % _int(m_add.group(1))
    return ("reverse_bytes" if reverse else "identity"), ""


def code_decode(text, fid, material):
    load = func_body(text, "Load_" + fid)
    dec = func_body(text, "Decode_" + fid)
    if not (load and dec):
        return None, None
    rep = infer_representation(load)
    transform, key = infer_transform(dec)
    if transform == "repeating_key_xor":  # key = an array literal in Decode_ or a sibling const
        km = re.search(r"\w+=\(\s*((?:%s\s*)+)\)" % NUM, dec)
        if not km:
            return None, (rep, transform, key)
        key = "".join("%02x" % _int(x) for x in km.group(1).split())
    data = untransform(material_bytes(material, rep), transform, key)
    return data, (rep, transform, key)


# ---------------------------------------------------------------- restricted Decode_ interpreter
class Unsupported(Exception):
    pass


class Arr(dict):
    """A bash indexed array: sparse, unset elements read as 0, ${#a[@]} = number of set elements."""
    def __missing__(self, k):
        return 0


class Scope(dict):
    def __missing__(self, k):
        if k.startswith("__"):
            raise KeyError(k)  # falls through to the eval globals (__len__ only)
        return 0  # unset bash variables are 0 in arithmetic


def split_statements(body):
    """Split a function body into simple statements on newlines/';' outside quotes and (( )) / ( ) / ${ }."""
    out, cur, depth, q, i = [], [], 0, None, 0
    while i < len(body):
        c = body[i]
        if q:
            cur.append(c)
            if c == "\\" and q == '"':
                cur.append(body[i + 1])
                i += 1
            elif c == q:
                q = None
        elif c in "'\"":
            q = c
            cur.append(c)
        elif c in "({":
            depth += 1
            cur.append(c)
        elif c in ")}":
            depth -= 1
            cur.append(c)
        elif c == "#" and depth == 0 and (not cur or cur[-1].isspace()):
            while i < len(body) and body[i] != "\n":
                i += 1
            continue
        elif c in "\n;" and depth == 0:
            if body[i:i + 2] == ";;":
                raise Unsupported("case")
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    out.append("".join(cur).strip())
    stmts = []
    for st in out:
        # `do X` / `then X` / `else X` share a line with their first statement
        m = re.match(r"^(do|then|else)\s+(.+)$", st, re.S)
        if m:
            stmts += [m.group(1), m.group(2).strip()]
        elif st:
            stmts.append(st)
    return stmts


ARITH_TOKEN = re.compile(r"\s*(?:(\d+#[0-9A-Za-z@_]+)|(0[xX][0-9a-fA-F]+)|(\d+)|([A-Za-z_]\w*)|"
                         r"(<<|>>|<=|>=|==|!=|&&|\|\||[-+*/%^&|~!<>()\[\]?:,]))")


def arith_py(expr):
    """Bash arithmetic -> a Python expression over Scope names. Raises Unsupported for anything outside the subset."""
    expr = re.sub(r"\$\{#(\w+)\[[@*]\]\}", r" __len__(\1) ", expr)
    expr = re.sub(r"\$\{(\w+)(\[[^\]]*\])?\}", r" \1\2 ", expr)
    expr = re.sub(r"\$(\w+)", r" \1 ", expr)
    out, i = [], 0
    while i < len(expr):
        if expr[i:].strip() == "":
            break
        m = ARITH_TOKEN.match(expr, i)
        if not m:
            raise Unsupported("arith token at %r" % expr[i:])
        i = m.end()
        based, hexa, dec, name, op = m.groups()
        if based:
            b, v = based.split("#", 1)
            out.append(str(int(v, int(b))))
        elif hexa:
            out.append(str(int(hexa, 16)))
        elif dec:
            out.append(str(int(dec, 8)) if len(dec) > 1 and dec.startswith("0") else dec)
        elif name:
            if name.startswith("_"):
                if name != "__len__":
                    raise Unsupported("name " + name)
            out.append(name)
        else:
            if op == "*" and out and out[-1] == "*":
                raise Unsupported("exponent")  # unbounded cost; leave it to the Codec decoder
            out.append({"/": "//", "&&": " and ", "||": " or ", "!": " not "}.get(op, op))
            if op in "?:":
                raise Unsupported("ternary")
    return " ".join(out)


class Interp:
    def __init__(self, scope):
        self.v = scope
        self.steps = 0

    def ev(self, expr):
        py = arith_py(expr)
        r = eval(py, {"__builtins__": {}, "__len__": lambda a: len(a) if isinstance(a, dict) else len(str(a))}, self.v)  # noqa: S307
        return int(r)

    def arith_stmt(self, expr):
        """((expr)) / $((expr)) with assignment operators."""
        expr = expr.strip()
        for part in re.split(r",(?![^\[]*\])", expr):
            part = part.strip()
            m = re.fullmatch(r"(\+\+|--)?\s*(\w+)\s*(\[[^\]]*\])?\s*(\+\+|--)?", part)
            if m and (m.group(1) or m.group(4)):
                self.assign(m.group(2), m.group(3), self.get(m.group(2), m.group(3)) + (1 if "+" in (m.group(1) or m.group(4)) else -1))
                continue
            m = re.fullmatch(r"(\w+)\s*(\[[^\]]*\])?\s*([-+*/%^&|]|<<|>>)?=(?!=)\s*(.+)", part, re.S)
            if m:
                val = self.ev(m.group(4))
                if m.group(3):
                    cur = self.get(m.group(1), m.group(2))
                    op = {"/": "//"}.get(m.group(3), m.group(3))
                    val = int(eval("%d %s %d" % (cur, op, val), {"__builtins__": {}}))  # noqa: S307
                self.assign(m.group(1), m.group(2), val)
                continue
            last = self.ev(part)
        return 0

    def get(self, name, idx):
        cur = self.v.get(name, 0)
        if idx:
            return cur[self.ev(idx[1:-1])] if isinstance(cur, dict) else (cur if self.ev(idx[1:-1]) == 0 else 0)
        return cur[0] if isinstance(cur, dict) else cur

    def assign(self, name, idx, val):
        if name.startswith("_"):
            raise Unsupported(name)
        if idx:
            arr = self.v.get(name)
            if not isinstance(arr, dict):
                arr = self.v[name] = Arr()
            arr[self.ev(idx[1:-1])] = val
        else:
            self.v[name] = val

    def word_value(self, w):
        """Value of an assignment RHS: $((..)), ${a[i]}, $x, integer literal, or a quoted form of those."""
        w = w.strip()
        if len(w) >= 2 and w[0] == w[-1] and w[0] in "\"'":
            w = w[1:-1]
        m = re.fullmatch(r"\$\(\((.*)\)\)", w, re.S)
        if m:
            return self.ev(m.group(1))
        if re.fullmatch(r"\$\{?\w+(\[[^\]]*\])?\}?|-?\d+|0[xX][0-9a-fA-F]+|\d+#\w+", w):
            return self.ev(w)
        raise Unsupported("rhs " + w)

    def array_literal(self, inner):
        arr = Arr()
        words = re.findall(r'"[^"]*"|\'[^\']*\'|\S+', inner)
        for i, w in enumerate(words):
            arr[i] = self.word_value(w)
        return arr

    def run(self, stmts):
        i = 0
        while i < len(stmts):
            i = self.stmt(stmts, i)

    def block(self, stmts, i, ends):
        """Collect statements from i up to the matching end keyword; returns (body, end_keyword_index)."""
        depth, j, body = 0, i, []
        while j < len(stmts):
            st = stmts[j]
            first = st.split()[0] if st.split() else ""
            if first in ("for", "while", "until", "if") and not st.startswith("(("):
                depth += 1
            if depth == 0 and first in ends:
                return body, j
            if first in ("done", "fi") and depth > 0:
                depth -= 1
            body.append(st)
            j += 1
        raise Unsupported("unterminated block")

    def stmt(self, stmts, i):
        st = stmts[i]
        self.steps += 1
        if self.steps > 2_000_000:
            raise Unsupported("step limit")
        m = re.fullmatch(r"for\s*\(\((.*?);(.*?);(.*?)\)\)", st, re.S)
        if m:
            assert stmts[i + 1] == "do"
            body, j = self.block(stmts, i + 2, ("done",))
            init, cond, step = m.groups()
            if init.strip():
                self.arith_stmt(init)
            n = 0
            while (self.ev(cond) if cond.strip() else 1):
                self.run(body)
                if step.strip():
                    self.arith_stmt(step)
                n += 1
                if n > 1_000_000:
                    raise Unsupported("loop limit")
            return j + 1
        m = re.fullmatch(r"for\s+(\w+)\s+in\s+(.+)", st, re.S)
        if m:
            assert stmts[i + 1] == "do"
            body, j = self.block(stmts, i + 2, ("done",))
            src = m.group(2).strip().strip('"')
            mi = re.fullmatch(r"\$\{(!?)(\w+)\[[@*]\]\}", src)
            if mi:
                arr = self.v.get(mi.group(2), Arr())
                arr = arr if isinstance(arr, dict) else Arr({0: arr})
                items = sorted(arr) if mi.group(1) else [arr[k] for k in sorted(arr)]
            elif re.fullmatch(r"[-\d\s]+", src):
                items = [int(x) for x in src.split()]
            else:
                raise Unsupported("for-in " + src)
            for it in items:
                self.v[m.group(1)] = it
                self.run(body)
            return j + 1
        m = re.fullmatch(r"(while|until)\s*\(\((.*)\)\)", st, re.S)
        if m:
            assert stmts[i + 1] == "do"
            body, j = self.block(stmts, i + 2, ("done",))
            n = 0
            while bool(self.ev(m.group(2))) == (m.group(1) == "while"):
                self.run(body)
                n += 1
                if n > 1_000_000:
                    raise Unsupported("loop limit")
            return j + 1
        m = re.fullmatch(r"if\s*\(\((.*)\)\)", st, re.S)
        if m:
            assert stmts[i + 1] == "then"
            body, j = self.block(stmts, i + 2, ("else", "fi"))
            other = []
            if stmts[j] == "else":
                other, j = self.block(stmts, j + 1, ("fi",))
            self.run(body if self.ev(m.group(1)) else other)
            return j + 1
        m = re.fullmatch(r"\(\((.*)\)\)", st, re.S)
        if m:
            self.arith_stmt(m.group(1))
            return i + 1
        m = re.fullmatch(r"(?:local|declare|typeset)((?:\s+-[a-zA-Z]+)*)\s+(.*)", st, re.S)
        if m:
            for decl in re.findall(r"\w+(?:=\([^)]*\)|=(?:\"[^\"]*\"|'[^']*'|\S+))?", m.group(2)):
                name, _, rhs = decl.partition("=")
                if rhs:
                    self.simple_assign(name, None, rhs)
                elif "a" in (m.group(1) or ""):
                    self.v[name] = Arr()
                elif name not in self.v:
                    self.v[name] = 0
            return i + 1
        m = _lhs(st)
        if m:
            name, idx, op, rhs = m
            if op == "+=":
                if not rhs.startswith("("):
                    raise Unsupported("string append")
                arr = self.v.get(name)
                if not isinstance(arr, dict):
                    arr = self.v[name] = Arr()
                lit = self.array_literal(rhs.strip()[1:-1])
                base = max(arr) + 1 if arr else 0
                for k in sorted(lit):
                    arr[base + k] = lit[k]
            else:
                self.simple_assign(name, idx, rhs)
            return i + 1
        if st in (":", "true") or re.fullmatch(r"return\s+0|return", st):
            return len(stmts) if st.startswith("return") else i + 1
        raise Unsupported("stmt " + st[:60])

    def simple_assign(self, name, idx, rhs):
        rhs = rhs.strip()
        if rhs.startswith("(") and rhs.endswith(")"):
            self.v[name] = self.array_literal(rhs[1:-1])
        else:
            self.assign(name, idx, self.word_value(rhs))


def _lhs(st):
    """`name[idx]+=rhs` / `name=rhs` with a bracket-matched (nested) index -> (name, idx|None, op, rhs) or None."""
    m = re.match(r"(\w+)", st)
    if not m:
        return None
    i, idx = m.end(), None
    if i < len(st) and st[i] == "[":
        depth = 0
        for j in range(i, len(st)):
            depth += {"[": 1, "]": -1}.get(st[j], 0)
            if depth == 0:
                idx, i = st[m.end():j + 1], j + 1
                break
        else:
            return None
    op = re.match(r"\+?=", st[i:])
    if not op:
        return None
    return m.group(1), idx, op.group(0), st[i + op.end():]


def array_names(load, dec):
    """(input array filled by Load_, output array filled by Decode_)."""
    m_out = re.search(r"^\s*(\w+)=\(\)", dec, re.M) or re.search(r"^\s*(\w+)(?:\[.*\]=|\+=\()", dec, re.M)
    a_out = m_out.group(1) if m_out else None
    filled = re.findall(r"read\s+(?:-\w+\s+)*-a\s+(\w+)|(?:^|[\s;])(\w+)(?:\+=\(|=\()", load, re.M)
    filled = [a or b for a, b in filled]
    used = re.findall(r"\$\{#(\w+)\[[@*]\]\}|\b(\w+)\[", dec)
    used = [a or b for a, b in used if (a or b) != a_out]
    a_in = next((u for u in used if u in filled), None) or next((f for f in filled if f in used), None) \
        or (filled[0] if filled else None)
    return a_in, a_out


def interp_decode(text, fid, stored):
    """Run Decode_<id>() over `stored` (the Load_ output bytes) in the restricted interpreter."""
    load = func_body(text, "Load_" + fid)
    dec = func_body(text, "Decode_" + fid)
    a_in, a_out = array_names(load, dec)
    if not (dec and a_in and a_out):
        raise Unsupported("arrays")
    scope = Scope({a_in: Arr(enumerate(stored))})
    for cm in re.finditer(r"^(?:readonly|declare\s+-r|declare)?\s*(\w+)=(%s)\s*$" % NUM, text, re.M):  # top-level int consts
        scope.setdefault(cm.group(1), _int(cm.group(2)))
    it = Interp(scope)
    it.run(split_statements(dec))
    out = scope.get(a_out)
    if not isinstance(out, dict):
        raise Unsupported("no output")
    return bytes(out[k] & 0xFF for k in sorted(out))


# ---------------------------------------------------------------- plan
def parse_plan(text):
    out = {}
    for item in text.strip().split("|"):
        if "=" in item:
            k, v = item.split("=", 1)
            out[k.strip()] = v
    return out


def _plain(raw):
    if not raw:
        return None
    try:
        cand = raw.decode("ascii")
    except UnicodeDecodeError:
        return None
    return cand if ("=" in cand and "|" in cand and cand.isprintable()) else None


def material_of(text, fid, mats):
    """Material text: the Material_ variables Load_<id> references, concatenated in reference order."""
    load = func_body(text, "Load_" + fid)
    refs = [n for n in re.findall(r"\$\{?(Material_\w+?)\}?(?=[\"'\s}:]|$)", load) if n[len("Material_"):] in mats]
    if refs:
        return "".join(mats[n[len("Material_"):]] for n in dict.fromkeys(refs))
    return mats.get(fid) or "".join(v for k, v in mats.items() if k.startswith(fid))


REPS = ("base64", "hex", "decimal", "reversed_decimal", "reversed_hex", "octal", "base64_urlsafe")
TRANSFORMS = ("identity", "reverse_bytes", "single_byte_xor", "reverse_then_xor", "xor_then_reverse",
              "repeating_key_xor", "rolling_xor", "add_modulo_256", "subtract_modulo_256")


def analyse(data):
    text = data.decode("utf-8", "ignore").lstrip("﻿").replace("\r\n", "\n")
    mats = assignment(text, "Material_")
    cods = assignment(text, "Codec_")
    fids = re.findall(r"(?:^|\s)(?:function\s+)?Decode_(\w+)\s*(?:\(\s*\))?\s*\{", text, re.M)
    fid = fids[0] if fids else next(iter(mats), "")
    material = material_of(text, fid, mats)
    codec = cods.get(fid) or next(iter(cods.values()), None)
    c_rep, c_tr, c_key = ((codec or "").split("|") + ["", "", ""])[:3]
    errs, plains = [], {}
    inferred = None
    try:
        inferred = (infer_representation(func_body(text, "Load_" + fid)),) + infer_transform(func_body(text, "Decode_" + fid))
    except Exception as e:  # noqa: BLE001
        errs.append("infer: %r" % e)
    reps = [r for r in dict.fromkeys([inferred[0] if inferred else None, c_rep or None]) if r]
    for rep in reps:  # 1) the file's own Decode_ loop over the Load_ bytes
        try:
            plains["interp:" + rep] = _plain(interp_decode(text, fid, material_bytes(material, rep)))
        except Exception as e:  # noqa: BLE001
            errs.append("interp(%s): %r" % (rep, e))
    if codec:  # 2) the Codec_ description
        try:
            plains["codec"] = _plain(codec_decode(material, codec))
        except Exception as e:  # noqa: BLE001
            errs.append("codec: %r" % e)
    try:  # 3) representation/transform inferred from the function bodies
        raw, _ = code_decode(text, fid, material)
        plains["code"] = _plain(raw)
    except Exception as e:  # noqa: BLE001
        errs.append("code: %r" % e)
    good = {k: v for k, v in plains.items() if v and _is_plan(v)}
    if len(set(good.values())) > 1:
        errs.append("decoders disagree: %s" % sorted(good))
    plain = next((v for k, v in good.items() if k.startswith("interp")), None) or good.get("codec") or good.get("code")
    if not plain:  # 4) last resort: known representation x transform grid with the keys named in the file
        keys = [k for k in dict.fromkeys([c_key, inferred[2] if inferred else None] +
                ["%02x" % _int(x) for x in re.findall(NUM, func_body(text, "Decode_" + fid))]) if k is not None]
        for rep in dict.fromkeys(reps + list(REPS)):
            for tr in TRANSFORMS:
                for key in keys or [""]:
                    try:
                        cand = _plain(untransform(material_bytes(material, rep), tr, key))
                    except Exception:  # noqa: BLE001
                        continue
                    if cand and _is_plan(cand):
                        plain = cand
                        errs.append("grid decode: %s|%s|%s" % (rep, tr, key))
                        break
                if plain:
                    break
            if plain:
                break
    return {"id": fid, "codec": codec, "inferred": inferred, "plain": plain, "plan": parse_plan(plain or ""),
            "decoders": sorted(good), "agree": len(good) >= 2 and len(set(good.values())) == 1, "errors": errs}


def _is_plan(text):
    p = parse_plan(text)
    return "steps" in p and ("adapter" in p or "campaign_id" in p)
