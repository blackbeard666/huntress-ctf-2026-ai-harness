"""Language-agnostic material/codec harvesting by the generator's naming convention.

Every scripted fixture since Day 3 names its payload `Material_<id>` / `MATERIAL_<id>` / `HUNTRESS-MATERIAL:` and its
codec `Codec_<id>` / `CODEC_<id>` / `HUNTRESS-CODEC:`, whatever the language syntax (readonly/Const/declare -r/plain
assignment/rem comment). We never parse the language: an assignment's right-hand side is scanned as a token stream of
string literals and integers until the statement ends (newline at bracket depth 0, no trailing operator / continuation),
so '..''..' (bash), "a" & _ "b" (VBS), ("a" "b") (Python), += appends and Material_<id>_a/_b splits all re-join.
Files without the convention (JScript, PowerShell) fall back to every long literal in the file.
"""
import re

ASSIGN = re.compile(r"(?im)(?:^|[\s;(,{])(?:(?:readonly|declare\s+-\w+|typeset\s+-\w+|local(?:\s+-\w+)?|export|const|var|"
                    r"let|dim|private|public|set)\s+)*\$?((?:material|codec)\w*)\s*(\+?=)")
COMMENT_TAG = re.compile(r"(?im)HUNTRESS-(MATERIAL|CODEC)\s*:\s*(\S+)")
CONT_TAIL = re.compile(r"(?:[&+,(\[{\\]|\s_)\s*$")


def _string(text, i):
    """Literal starting at text[i] (a quote) -> (body, end_index). Handles '', "", ``, VBS "" doubling, backslashes,
    bash $'..' (caller strips the $)."""
    q = text[i]
    j, out = i + 1, []
    n = len(text)
    while j < n:
        c = text[j]
        if c == "\\" and q != "'" and j + 1 < n:
            out.append(text[j:j + 2]); j += 2; continue
        if c == q:
            if q == '"' and j + 1 < n and text[j + 1] == '"' and not (out and out[-1].endswith("\\")):
                # VBS "" -> " only when not followed by another literal start; treat as escape inside VBS strings
                out.append('"'); j += 2; continue
            return "".join(out), j + 1
        out.append(c); j += 1
    return "".join(out), n


def rhs_tokens(text, start):
    """Scan an assignment's right-hand side from `start`: -> (list of string bodies, list of ints, end)."""
    strs, ints = [], []
    depth, i, n = 0, start, len(text)
    line_start = start
    while i < n:
        c = text[i]
        if c in "'\"`":
            body, i = _string(text, i)
            strs.append(body)
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth < 0:
                break
        elif c == "\n":
            seg = text[line_start:i]
            if depth <= 0 and not CONT_TAIL.search(seg):
                break
            line_start = i + 1
        elif c in ";" and depth <= 0:
            break
        elif c == "#" and depth <= 0 and (i == start or text[i - 1].isspace()):
            # comment to end of line (bash/python); stop scanning this statement
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        elif c.isdigit() and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] in "_#")):
            m = re.match(r"0x[0-9a-fA-F]+|\d+", text[i:])
            tok = m.group(0)
            ints.append(int(tok, 16) if tok.lower().startswith("0x") else int(tok))
            i += len(tok)
            continue
        i += 1
    return strs, ints, i


def _group(name):
    """Material_5eb0068b_a / MATERIAL_5c9e7818 / Material -> group key (the id)."""
    m = re.match(r"(?i)(?:material|codec)_?([0-9a-f]{6,})", name)
    return m.group(1).lower() if m else ""


def harvest(text):
    """-> {id: {'material': str|list|None, 'codec': str|None}} from the naming convention."""
    groups = {}
    for m in COMMENT_TAG.finditer(text):
        g = groups.setdefault("", {"material": None, "codec": None, "_parts": []})
        if m.group(1).upper() == "CODEC":
            g["codec"] = m.group(2)
        else:
            g["_parts"].append(m.group(2))
    for m in ASSIGN.finditer(text):
        name, op = m.group(1), m.group(2)
        strs, ints, _ = rhs_tokens(text, m.end())
        g = groups.setdefault(_group(name), {"material": None, "codec": None, "_parts": []})
        if name.lower().startswith("codec"):
            if strs and "|" in strs[0]:
                g["codec"] = strs[0]
            continue
        if strs:
            g["_parts"].append("".join(s[1:] if s.startswith("$") else s for s in strs))
        elif len(ints) >= 8:
            g["_parts"].append(ints)
    out = {}
    for k, g in groups.items():
        parts = g.pop("_parts")
        if not parts and not g["codec"]:
            continue
        if parts and all(isinstance(p, list) for p in parts):
            g["material"] = [x for p in parts for x in p]
        elif parts:
            g["material"] = "".join(p for p in parts if isinstance(p, str))
        out[k] = g
    return out


STRLIT = re.compile(r"\"((?:[^\"\\\n]|\\.)*)\"|'((?:[^'\\\n]|\\.)*)'")
INTARR = re.compile(r"[\[(]\s*((?:(?:0x[0-9a-fA-F]+|\d+)\s*,\s*){15,}(?:0x[0-9a-fA-F]+|\d+))\s*,?\s*[\])]")


def loose_literals(text, minlen=16):
    """Fallback for files without the naming convention: every long string literal, every per-line concatenation of
    literals, and every int-array literal (>= 16 items)."""
    out = []
    for line in text.split("\n"):
        lits = [a or b for a, b in STRLIT.findall(line)]
        longs = [s for s in lits if len(s) >= minlen]
        out += longs
        joined = "".join(s for s in lits if len(s) >= 4)
        if len(lits) > 1 and len(joined) >= minlen and joined not in out:
            out.append(joined)
    arrays = []
    for m in INTARR.finditer(text):
        vals = [int(t, 16) if t.lower().startswith("0x") else int(t) for t in re.split(r"\s*,\s*", m.group(1).strip())]
        if all(0 <= v < 256 for v in vals):
            arrays.append(vals)
    out += arrays
    if len(arrays) > 1:                       # material split over several arrays (firstPart + secondPart)
        out.append([v for a in arrays for v in a])
    longs = [s for s in out if isinstance(s, str) and len(s) >= minlen]
    if len(longs) > 1:                        # material split over several string literals
        out.append("".join(longs))
    out.sort(key=lambda x: -len(x))
    return out
