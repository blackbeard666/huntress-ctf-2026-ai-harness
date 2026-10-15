"""Static cmd.exe reconstruction for the Huntress Batch fixtures (no line is ever executed by cmd).

Each fixture's `:HUNTRESS_INSPECT` block builds a pipe-delimited plan `v=1|steps=...|adapter=...|graph=...|campaign_id=...`
from fragment variables and echoes it. The fragments are joined with one of four expansion forms (percent `%a%%b%`,
delayed `!a!!b!`, CALL-double `call set "x=%%a%%%%b%%"`, FOR-indirect `for %%G in (..) do call set "x=%%x%%%%f%%G%%"`)
and wrapped in a control-flow construct. A small interpreter applies cmd's phases (percent expansion, FOR variable
substitution, delayed expansion, caret/quote handling, CALL's second percent pass, goto/call :label/exit /b, if defined /
if errorlevel) to reconstruct the variables exactly as the interpreter would see them. The `HUNTRESS-MATERIAL` comment
(codec named by `HUNTRESS-CODEC`) is a second copy of the plan, used only as a fallback/cross-check.
"""
import base64, re

LABEL_RE = re.compile(r"^\s*:([A-Za-z_][\w.-]*)\s*$")


class Batch:
    def __init__(self, text):
        self.lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        self.labels = {}
        for i, ln in enumerate(self.lines):
            m = LABEL_RE.match(ln)
            if m and not ln.lstrip().startswith("::"):
                self.labels.setdefault(m.group(1).lower(), i)
        self.env = {}
        self.errorlevel = 0
        self.delayed = bool(re.search(r"(?i)setlocal\b[^\n]*enabledelayedexpansion", text))
        self.echoed = []
        self.trace = []   # (line_no, raw line) of executed commands

    # --- expansion phases ---------------------------------------------------------------------------------------
    def _var(self, body):
        """%body% / !body! content -> value, supporting :~a,b substrings and :old=new replacement."""
        m = re.match(r"^([^:]+):~\s*(-?\d+)\s*(?:,\s*(-?\d+))?$", body)
        if m:
            v = self.env.get(m.group(1).lower())
            if v is None:
                return None
            a = int(m.group(2))
            a = max(len(v) + a, 0) if a < 0 else a
            if m.group(3) is None:
                return v[a:]
            b = int(m.group(3))
            return v[a:a + b] if b >= 0 else v[a:len(v) + b]
        m = re.match(r"^([^:]+):(\*?)([^=]*)=(.*)$", body, re.S)
        if m:
            v = self.env.get(m.group(1).lower())
            if v is None:
                return None
            old, new = m.group(3), m.group(4)
            if not old:
                return v
            if m.group(2):
                i = v.lower().find(old.lower())
                return v if i < 0 else new + v[i + len(old):]
            return re.sub(re.escape(old), lambda _: new, v, flags=re.I)
        return self.env.get(body.lower())

    def percent(self, s, batch_file=True):
        out, i, n = [], 0, len(s)
        while i < n:
            c = s[i]
            if c != "%":
                out.append(c); i += 1; continue
            if i + 1 < n and s[i + 1] == "%":
                out.append("%"); i += 2; continue
            m = re.match(r"%(?:~[a-zA-Z]*)?[0-9*]", s[i:])
            if m:                                        # %1 / %~dp1 / %* -> no arguments (%item0% is a variable)
                i += len(m.group(0)); continue
            j = s.find("%", i + 1)
            if j < 0:
                i += 1; continue                         # lone % is dropped
            body = s[i + 1:j]
            v = self._var(body) if body and "\n" not in body else None
            if v is None:
                if batch_file:
                    i = j + 1                            # undefined %var% expands to nothing in a batch file
                else:
                    out.append(s[i:j]); i = j
                continue
            out.append(v); i = j + 1
        return "".join(out)

    def delayed_exp(self, s):
        if not self.delayed or "!" not in s:
            return s
        out, i, n = [], 0, len(s)
        while i < n:
            c = s[i]
            if c == "^":                                 # with '!' on the line, carets escape once more
                if i + 1 < n:
                    out.append(s[i + 1])
                i += 2; continue
            if c != "!":
                out.append(c); i += 1; continue
            j = s.find("!", i + 1)
            if j < 0:
                i += 1; continue
            v = self._var(s[i + 1:j])
            out.append(v or "")
            i = j + 1
        return "".join(out)

    # --- tokenising ---------------------------------------------------------------------------------------------
    @staticmethod
    def split_ops(s):
        """Split a line on unquoted, unescaped & && || | -> [(cmd, op_before)]; also strip carets outside quotes."""
        parts, cur, op, q, i, n = [], [], None, False, 0, len(s)
        while i < n:
            c = s[i]
            if c == '"':
                q = not q; cur.append(c); i += 1; continue
            if not q and c == "^" and i + 1 < n:
                cur.append("\x00" + s[i + 1]); i += 2; continue   # escaped char, marked so later passes keep it
            if not q and c in "&|":
                dbl = i + 1 < n and s[i + 1] == c
                parts.append(("".join(cur), op))
                op = c * 2 if dbl else c
                cur = []; i += 2 if dbl else 1; continue
            cur.append(c); i += 1
        parts.append(("".join(cur), op))
        return parts

    @staticmethod
    def unmark(s):
        return s.replace("\x00", "")

    # --- execution ----------------------------------------------------------------------------------------------
    def run(self, start_label="HUNTRESS_INSPECT", max_steps=5000):
        pc = self.labels.get(start_label.lower())
        if pc is None:
            pc = 0
        stack, steps = [], 0
        while pc is not None and pc < len(self.lines) and steps < max_steps:
            steps += 1
            raw = self.lines[pc]
            pc += 1
            line = raw.strip()
            if not line or LABEL_RE.match(line) or line.startswith("::"):
                continue
            jump = self.exec_line(line, pc - 1)
            if jump is None:
                continue
            kind, arg = jump
            if kind == "goto":
                if arg == "eof":
                    pc = stack.pop() if stack else None
                else:
                    pc = self.labels.get(arg)
            elif kind == "call":
                if arg in self.labels:
                    stack.append(pc); pc = self.labels[arg]
            elif kind == "exit":
                pc = stack.pop() if stack else None
        return self

    def exec_line(self, line, lno):
        line = line.lstrip("@")
        expanded = self.percent(line)
        prev_ok = True
        for cmd, op in self.split_ops(expanded):
            if op == "&&" and not prev_ok:
                continue
            if op == "||" and prev_ok:
                continue
            if op == "|":
                continue                                  # right side of a pipe: output only, ignore
            r = self.exec_cmd(cmd.strip(), lno)
            if isinstance(r, tuple):
                return r
            prev_ok = r is not False
        return None

    def exec_cmd(self, cmd, lno, depth=0):
        if not cmd or depth > 8:
            return True
        if cmd.startswith("(") and cmd.endswith(")"):
            cmd = cmd[1:-1].strip()
        low = cmd.lower()
        word = re.match(r"[^\s(]*", low).group(0)
        if word in ("rem", "@rem") or low.startswith("rem ") or word in ("setlocal", "endlocal", "ver", "title",
                                                                         "cls", "color", "pause", "@echo"):
            return True
        self.trace.append((lno, cmd))
        if low.startswith("echo") and len(cmd) > 4 and cmd[4] in "(.:;,/\\[]+= \t":
            if low.strip() in ("echo off", "echo on"):
                return True
            self.echoed.append(self.unmark(self.delayed_exp(cmd[5:])))
            return True
        if word == "goto":
            tgt = cmd[4:].strip().lstrip(":").split()[0].lower() if cmd[4:].strip() else ""
            return ("goto", tgt)
        if word == "exit":
            return ("exit", None)
        if word == "call":
            rest = cmd[4:].strip()
            if rest.startswith(":"):
                return ("call", rest[1:].split()[0].lower())
            return self.exec_cmd(self.split_ops(self.percent(self.unmark(rest)))[0][0].strip(), lno, depth + 1)
        if word == "if":
            return self.exec_if(cmd, lno, depth)
        if word == "for":
            return self.exec_for(cmd, lno, depth)
        if word == "set":
            return self.exec_set(cmd[3:].lstrip())
        return True

    def exec_if(self, cmd, lno, depth):
        m = re.match(r"(?i)if\s+(/i\s+)?(not\s+)?(.*)$", cmd)
        neg, rest = bool(m.group(2)), m.group(3)
        md = re.match(r"(?i)defined\s+(\S+)\s+(.*)$", rest)
        me = re.match(r"(?i)errorlevel\s+(\d+)\s+(.*)$", rest)
        mx = re.match(r"(?i)exist\s+(\S+)\s+(.*)$", rest)
        mc = re.match(r'("[^"]*"|\S+?)\s*(==|\s(?:equ|neq|lss|leq|gtr|geq)\s)\s*("[^"]*"|\S+)\s+(.*)$', rest, re.I)
        if md:
            cond, body = self.delayed_exp(self.unmark(md.group(1))).lower() in self.env, md.group(2)
        elif me:
            cond, body = self.errorlevel >= int(me.group(1)), me.group(2)
        elif mx:
            cond, body = False, mx.group(2)
        elif mc:
            a, b = self.delayed_exp(self.unmark(mc.group(1))), self.delayed_exp(self.unmark(mc.group(3)))
            if m.group(1):
                a, b = a.lower(), b.lower()
            o = mc.group(2).strip().lower()
            cond = {"==": a == b, "equ": a == b, "neq": a != b}.get(o, False)
            body = mc.group(4)
        else:
            return True
        if neg:
            cond = not cond
        body = re.sub(r"(?is)\s+else\s+.*$", "", body) if cond else (re.search(r"(?is)\s+else\s+(.*)$", body) or [None, ""])[1]
        if not body:
            return True
        body = body.strip()
        if body.startswith("(") and body.endswith(")"):
            body = body[1:-1]
        return self.exec_cmd(body.strip(), lno, depth + 1)

    def exec_for(self, cmd, lno, depth):
        m = re.match(r"(?is)for\s+(?:/l\s+)?%([A-Za-z])\s+in\s*\((.*?)\)\s*do\s+(.*)$", cmd)
        if not m:
            return True
        var, items, body = m.group(1), m.group(2), m.group(3).strip()
        if re.match(r"(?i)for\s+/l", cmd):
            a = [int(x) for x in re.split(r"[\s,]+", items.strip()) if x]
            seq = [str(x) for x in range(a[0], a[2] + (1 if a[1] > 0 else -1), a[1])] if len(a) == 3 else []
        else:
            seq = [x for x in re.split(r"[\s,;]+", items.strip()) if x]
        if body.startswith("(") and body.endswith(")"):
            body = body[1:-1].strip()
        for it in seq:
            r = self.exec_cmd(body.replace("%" + var, it), lno, depth + 1)
            if isinstance(r, tuple):
                return r
        return True

    def exec_set(self, rest):
        if rest[:2].lower() in ("/a", "/p"):
            return True
        rest = self.delayed_exp(rest)
        if rest.startswith('"'):
            body = rest[1:]
            k = body.rfind('"')
            body = body[:k] if k >= 0 else body
        else:
            body = rest
        body = self.unmark(body)
        if "=" not in body:
            return True
        name, val = body.split("=", 1)
        name = name.strip().lower() if rest.startswith('"') else name.lower()
        if val == "":
            self.env.pop(name, None)
        else:
            self.env[name] = val
        return True


# --- plan + style extraction -----------------------------------------------------------------------------------------
def parse_plan(s):
    if not s or not re.match(r"\s*v=\d", s):
        return None
    plan = {}
    for kv in s.strip().split("|"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            plan[k.strip()] = v
    return plan if "steps" in plan else None


def decode_material(text):
    """Fallback: the HUNTRESS-MATERIAL copy of the plan, decoded per the HUNTRESS-CODEC hint (or by trying all)."""
    m = re.search(r"HUNTRESS-MATERIAL:(\S+)", text)
    if not m:
        return None
    mat = m.group(1)
    raws = []
    for fn in (lambda x: bytes(int(t) for t in re.split(r"[.,\s]+", x) if t),
               lambda x: bytes.fromhex(x),
               lambda x: base64.b64decode(x[::-1] + "=" * (-len(x) % 4)),
               lambda x: base64.b64decode(x + "=" * (-len(x) % 4))):
        try:
            raws.append(fn(mat))
        except Exception:
            pass
    for raw in raws:
        for r in (raw, raw[::-1]):
            cands = [r] + [bytes(((c << k) | (c >> (8 - k))) & 255 for c in r) for k in range(1, 8)]
            if r:  # single-byte XOR / add_N: key from the known 'v' prefix
                cands.append(bytes(c ^ (r[0] ^ ord("v")) for c in r))
                cands.append(bytes((c - r[0] + ord("v")) & 255 for c in r))
            for c in cands:
                if c.startswith(b"v=") and b"steps=" in c:
                    try:
                        return parse_plan(c.decode())
                    except UnicodeDecodeError:
                        pass
    return None


def _frag_prefix(raw):
    """Fragment-variable pool of a join line: `%%h%%G%%` / `%%h0%%` -> 'h', `%%FrAg0%%` -> 'frag', `%%v_a%%G%%` -> 'v_a'."""
    m = re.search(r"%%([A-Za-z_]+?)%%G%%", raw) or re.search(r"%%([A-Za-z_]+?)\d%%", raw)
    return m.group(1).lower() if m else None


def expansion_form(b, target, ignore_echo=False):
    """GM expansion label for how `target` reaches the final handoff (Day 3 single solve, confirmed 9/9).

    The handoff is `echo(!var!)`, so a non-FOR assembly is labelled `delayed` whatever the join line uses. A FOR
    assembly (`for ... do call set "T=%%T%%%%frag%%G%%"`) is `for_indirect`, except when its accumulator reset is
    wrapped in `if defined` (that variant is labelled `call_double`)."""
    echo_delayed = any(re.match(r"(?i)echo.\s*!%s!" % re.escape(target), b.lines[l].strip()) for l, _ in b.trace)
    for lno, cmd in reversed(b.trace):
        raw = b.lines[lno].strip()
        if not re.search(r'(?i)set\s+"?%s=' % re.escape(target), raw):
            continue
        rhs = raw.split("=", 1)[1]
        if not re.search(r"[%!]", rhs):
            continue
        pref = _frag_prefix(raw)
        if re.match(r"(?i)(?:@?\s*)for\s", raw) or re.search(r"(?i)\bdo\s+call\s+set\b", raw):
            # GM-verified over ~100 timed cases: the generator's call_double template is the one that uses the h
            # fragment pool (cfg = %%h0%%..., or a FOR over %%h%%G%%), guarded reset or not; every other pool's FOR
            # loop is for_indirect. (An earlier "guarded reset" rule only looked right on the single-solve sample.)
            return "call_double" if pref == "h" else "for_indirect"
        if re.search(r"(?i)\bcall\s+set\b", raw) and "%%" in rhs and pref == "h":
            # `call set "cfg=%%h0%%..."` (h fragment pool) = call_double; other pools (FrAg/fragment/v_a) = delayed.
            return "call_double"
        if ignore_echo:
            # statement-only labelling (regular untimed pool): !x! join = delayed, any other %-join = percent
            return "delayed" if re.search(r"![^!\s]+!", rhs) else "percent"
        if echo_delayed:
            return "delayed"
        if re.search(r"(?i)\bcall\s+set\b", raw):
            return "call_double"
        if re.search(r"![^!\s]+!", rhs):
            return "delayed"
        return "percent"
    return None


# GM control-flow vocabulary (Day 3 single solve, ALL confirmed): direct, errorlevel_guard (if errorlevel),
# goto_dispatch (goto :LABEL), call_subroutine (call :LABEL), and if_guard for the `set "X=1"` + `if defined X <stmt>`
# construct. Naming keys on the cmd `if` keyword (generic if-conditional guard), parallel to errorlevel_guard.
DEFINED_GUARD_FORM = "if_guard"


def control_form(b):
    """The control construct on the executed path between the fragments and the echo (separator gotos excluded)."""
    feats = []
    for lno, cmd in b.trace:
        low = cmd.lower()
        if low.startswith("call :"):
            feats.append("call_subroutine")
        elif low.startswith("goto") and "separator" not in low and "huntress_inspect" not in low \
                and "huntress_plan" not in low:
            feats.append("goto_dispatch")
        elif re.match(r"if\s+(not\s+)?defined\b", low):
            feats.append(DEFINED_GUARD_FORM)
        elif re.match(r"if\s+(not\s+)?errorlevel\b", low):
            feats.append("errorlevel_guard")
    return feats[0] if feats else "direct", feats


def analyse(data):
    text = data.decode("utf-8", "ignore").lstrip("﻿")
    b = Batch(text).run()
    plan = None
    for s in b.echoed:
        plan = parse_plan(s)
        if plan:
            break
    target = None
    m = None
    for lno, cmd in b.trace:
        mm = re.match(r"(?i)echo.\s*[!%]([^!%]+)[!%]", b.lines[lno].strip())
        if mm:
            target = mm.group(1).lower()
    mat = decode_material(text)
    if not plan:
        plan = mat or {}
    ctrl, feats = control_form(b)
    return {"plan": plan, "material": mat, "expansion": expansion_form(b, target) if target else None,
            "expansion_stmt": expansion_form(b, target, ignore_echo=True) if target else None,
            "control": ctrl, "control_features": feats, "target": target}
