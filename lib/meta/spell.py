"""Suffix-driven GM spelling for metadata-forensics fields (the naming LAWS of lib/knowledge.py, in one place).

An extractor returns a TYPED raw value; `spell(fmt, field, raw, q)` renders it the way the GM confirmed for that kind of
field, keyed on the field name's SUFFIX (never on the day):

  *_uNN_hex        0x + lowercase hex zero-padded to NN/4 digits        (D9  pe.coff_machine_u16_hex "0x014c")
  *_rva_hex        0x + 8 digits (u32 struct width)                    (D10 "0x00065bd0"; "0x65bd0" REJECTED)
  *_hex            0x + the struct width the extractor gives via Hex(value, width)
  *_guid           Guid(kind, raw): kind "text" = the stored string VERBATIM (D13 MSI "{DD1A...}"), "bytes_le" =
                   a binary GUID as .NET Guid.ToString() = str(uuid.UUID(bytes_le=raw)) (D12 MVID, lowercase, no braces)
  *_dimensions_pixels  (w, h) -> "WxH"                                  (D4/D5)
  *_present / has_* / is_*   bool -> "true" / "false"                  (D3)
  *_names / json kind        list -> compact JSON, separators (",", ":"), non-ASCII kept   (D8)
  *_version        (major, minor) -> "x.y"; a string passes through    (D6)
  counts           int -> base-10                                      (D7)
  enums            mapped case-insensitively onto answer_format.accepted_values when the contract lists them
A plain str is already spelled (verbatim artifact text, or the literal "none" for an absent field).

`alternates(aid, value)` = other plausible spellings of the same value (hex widths/case/prefix, GUID braces/case/
byte order, dimension separators, booleans), most plausible first, minus every GM-REJECTED spelling in lib.knowledge.
"""
import json
import re
import uuid
from collections import namedtuple

Hex = namedtuple("Hex", "value width")          # width = hex DIGITS of the struct field (u16 -> 4, u32 -> 8, u64 -> 16)
Guid = namedtuple("Guid", "kind raw")           # kind: "text" (stored string) | "bytes_le" | "bytes_be" (16 raw bytes)
Dims = namedtuple("Dims", "width height")

_UNN = re.compile(r"_u(8|16|32|64)_hex$")


def hex_width(field, raw=None):
    """Digits for a *_hex field: the uNN suffix wins, then *_rva_hex (u32), then the extractor's Hex.width."""
    m = _UNN.search(field or "")
    if m:
        return int(m.group(1)) // 4
    if (field or "").endswith("_rva_hex"):
        return 8
    if isinstance(raw, Hex) and raw.width:
        return raw.width
    return 0


def _accepted(q):
    fmt = (q or {}).get("answer_format") or {}
    vals = fmt.get("accepted_values") or fmt.get("values") or []
    return [str(v) for v in vals] if isinstance(vals, (list, tuple)) else []


def _enum(v, q):
    acc = _accepted(q)
    if not acc:
        return v
    for a in acc:
        if a == v:
            return a
    low = {a.lower(): a for a in acc}
    return low.get(v.lower(), low.get(re.sub(r"[\s-]+", "_", v.lower()), v))


def spell(fmt, field, raw, q=None):
    """The GM spelling of `raw` for <fmt>.<field> (None stays None)."""
    field = field or ""
    if raw is None:
        return None
    if isinstance(raw, bool):
        return _enum("true" if raw else "false", q)
    if isinstance(raw, Guid):
        if raw.kind == "text":
            return str(raw.raw).strip()
        b = bytes(raw.raw)
        return str(uuid.UUID(bytes_le=b) if raw.kind == "bytes_le" else uuid.UUID(bytes=b))
    if isinstance(raw, Hex) or (isinstance(raw, int) and field.endswith("_hex")):
        val = raw.value if isinstance(raw, Hex) else raw
        w = hex_width(field, raw)
        return "0x%0*x" % (w, val) if w else "0x%x" % val
    if isinstance(raw, Dims) or (isinstance(raw, tuple) and len(raw) == 2 and field.endswith("_dimensions_pixels")):
        return f"{raw[0]}x{raw[1]}"
    if isinstance(raw, tuple) and field.endswith("_version") and all(isinstance(x, int) for x in raw):
        return ".".join(str(x) for x in raw)
    if isinstance(raw, (list, dict)):
        return json.dumps(raw, separators=(",", ":"), ensure_ascii=False)
    if isinstance(raw, (bytes, bytearray)):
        return bytes(raw).hex()
    if isinstance(raw, int):
        return str(raw)
    if field.endswith("_windows") and isinstance(raw, str):
        return _enum(raw.replace("/", "\\"), q)   # a Windows path: backslashes, otherwise verbatim (D14 lnk)
    return _enum(str(raw), q)


def rejected():
    """Every GM-REJECTED spelling recorded in lib.knowledge (`*_REJECTED` lists/tuples of strings)."""
    try:
        from lib import knowledge
    except ImportError:  # pragma: no cover
        return set()
    out = set()
    for k, v in vars(knowledge).items():
        if k.endswith("_REJECTED"):
            vals = v.values() if isinstance(v, dict) else v
            for x in vals:
                if isinstance(x, str):
                    out.add(x)
                elif isinstance(x, (list, tuple)):
                    out.update(y for y in x if isinstance(y, str))
    return out


_GUID_RE = re.compile(r"^\{?([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\}?$")


def alternates(aid, value, q=None):
    """Other spellings of `value` worth one probe each after a single-field `incorrect`, most plausible first.
    Excludes `value` itself and every knowledge *_REJECTED spelling."""
    v = str(value).strip()
    tail = (aid or "").split(".")[-1].lower()
    out = []
    m = _GUID_RE.match(v)
    if m:
        g = m.group(1)
        braced = v.startswith("{")
        for s in ((g if braced else "{%s}" % g), g.upper(), g.lower(), "{%s}" % g.upper(), "{%s}" % g.lower()):
            out.append(s)
        try:  # the other byte order (a binary GUID read big- vs little-endian)
            sw = str(uuid.UUID(bytes=uuid.UUID(g).bytes_le))
            out += [sw, sw.upper(), "{%s}" % sw.upper()]
        except ValueError:
            pass
    elif re.fullmatch(r"0[xX][0-9a-fA-F]+", v):
        n = int(v, 16)
        digits = len(v) - 2
        widths = [w for w in (4, 8, 16, 2) if w != digits and n < (1 << (4 * w))]
        out += ["0x%x" % n] + ["0x%0*x" % (w, n) for w in widths]
        out += [v[:2] + v[2:].upper(), v[2:], "0X" + v[2:].upper(), str(n)]
    elif re.fullmatch(r"\d+x\d+", v):
        w, h = v.split("x")
        out += [f"{w} x {h}", f"{w}X{h}", f"{w}×{h}", f"{w},{h}", f"{w}x{h}px"]
    elif v.lower() in ("true", "false"):
        t = v.lower() == "true"
        out += ["True" if t else "False", "yes" if t else "no", "1" if t else "0", "TRUE" if t else "FALSE"]
    elif v.startswith("[") and v.endswith("]"):
        try:
            arr = json.loads(v)
            out += [json.dumps(arr), json.dumps(arr, separators=(",", ":"), ensure_ascii=True), ",".join(map(str, arr))]
        except ValueError:
            pass
    else:
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            out.append(v[1:-1])
        if tail.endswith("-hex") or tail.endswith("-md5") or tail.endswith("-sha1") or tail.endswith("-sha256"):
            out.append(v.lower())
    bad = rejected() | {v}
    seen, res = set(), []
    for s in out:
        if s not in bad and s not in seen:
            seen.add(s)
            res.append(s)
    return res
