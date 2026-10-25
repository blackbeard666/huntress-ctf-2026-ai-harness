"""EVTX per-event content via a stdlib BinXML reader (prebuilt, SPECULATIVE; no python-evtx needed).

Walk: ElfFile header -> every physical 64 KiB ElfChnk -> records "**\\0\\0" (size u32 @4, EventRecordID u64 @8,
written FILETIME @16, BinXML @24). BinXML (libevtx "Binary XML"): 0x0F fragment header (3 bytes), 0x0C template
instance (u8, template id u32, template definition offset u32 -- chunk-relative; when it equals the current position
the definition follows inline: next u32, GUID 16, data size u32, data), then the instance's substitution array
(count u32, count x {size u16, type u8, pad u8}, then the values). Elements 0x01/0x41 (dependency id u16, data size
u32, name offset u32 -> chunk string {next u32, hash u16, nchars u16, UTF-16LE, NUL}, inline when the offset is the
current position; 0x41 adds an attribute-list size u32), 0x02 close-start, 0x03 close-empty, 0x04 end, 0x05/0x45
value text, 0x06/0x46 attribute, 0x07 CDATA, 0x08 char ref, 0x09 entity ref, 0x0D/0x0E normal/optional substitution
(index u16, type u8). Templates are parsed once per (chunk, offset). Value types: 0x01 UTF-16 string, 0x04/0x06/0x08/
0x0A u8/u16/u32/u64, 0x11 FILETIME, 0x13 SID, 0x14/0x15 hex32/hex64, 0x0E binary, 0x0F GUID, 0x21 nested BinXML.

Fields (System = Event/System, data = Event/EventData/Data[@Name] (+ UserData leaf elements by tag name)):
distinct_event_ids sorted ints; event_id_counts = {"<id>": n} keys in NUMERIC order (json.dumps(sort_keys=True) of a
Counter of int ids gives the same); most_common_event_id = collections.Counter.most_common(1) (tie -> first seen in
record order); computer_names sorted distinct; logon_types = 4624 LogonType sorted distinct ints; target_user_names =
4624/4625 TargetUserName sorted distinct; new_process_names (4688 NewProcessName), service_names / service_image_paths
(7045 ServiceName / ImagePath) sorted distinct; script_block_text_first = ScriptBlockText of the first 4104 record;
log_cleared = 1102 or 104 present (bool). EventID = the EventID element text (Qualifiers not folded in).
Not ElfFile -> "none"; no records / no matching event -> "none"; BinXML parse failure or deadline -> None."""
import struct
import time

FIELDS = {
    ("evtx", "distinct_event_ids"): "binxml_value",
    ("evtx", "unique_event_ids"): "binxml_value",
    ("evtx", "event_ids_sorted"): "binxml_value",
    ("evtx", "event_id_set"): "binxml_value",
    ("evtx", "event_id_counts"): "binxml_value",
    ("evtx", "event_id_count_map"): "binxml_value",
    ("evtx", "event_counts_by_id"): "binxml_value",
    ("evtx", "most_common_event_id"): "binxml_value",
    ("evtx", "most_frequent_event_id"): "binxml_value",
    ("evtx", "computer_names"): "binxml_value",
    ("evtx", "distinct_computer_names"): "binxml_value",
    ("evtx", "unique_computer_names"): "binxml_value",
    ("evtx", "computers"): "binxml_value",
    ("evtx", "channels"): "binxml_value",
    ("evtx", "channel_names"): "binxml_value",
    ("evtx", "provider_names_sorted"): "binxml_value",
    ("evtx", "logon_types"): "binxml_value",
    ("evtx", "distinct_logon_types"): "binxml_value",
    ("evtx", "logon_type_list"): "binxml_value",
    ("evtx", "target_user_names"): "binxml_value",
    ("evtx", "target_usernames"): "binxml_value",
    ("evtx", "distinct_target_user_names"): "binxml_value",
    ("evtx", "logon_target_user_names"): "binxml_value",
    ("evtx", "new_process_names"): "binxml_value",
    ("evtx", "process_names"): "binxml_value",
    ("evtx", "process_creation_names"): "binxml_value",
    ("evtx", "service_names"): "binxml_value",
    ("evtx", "installed_service_names"): "binxml_value",
    ("evtx", "service_image_paths"): "binxml_value",
    ("evtx", "service_file_names"): "binxml_value",
    ("evtx", "script_block_text_first"): "binxml_value",
    ("evtx", "first_script_block_text"): "binxml_value",
    ("evtx", "script_block_text"): "binxml_value",
    ("evtx", "log_cleared"): "binxml_value",
    ("evtx", "is_log_cleared"): "binxml_value",
    ("evtx", "log_was_cleared"): "binxml_value",
    ("evtx", "audit_log_cleared"): "binxml_value",
}

_EPOCH = 11644473600
_VALUE_TOKENS = (0x05, 0x07, 0x08, 0x09, 0x0D, 0x0E)


class _Err(Exception):
    pass


def _ft_iso(ft):
    # FILETIME (100 ns since 1601) -> 'YYYY-MM-DDTHH:MM:SSZ', sub-second dropped (house spelling, see evtx.py)
    s = ft // 10000000 - _EPOCH
    if s < 0 or s > 253402300799:
        return str(ft)
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(s))


def _sid(v):
    if len(v) < 8:
        return ""
    n = v[1]
    auth = int.from_bytes(v[2:8], "big")
    subs = struct.unpack_from("<%dI" % n, v, 8) if len(v) >= 8 + 4 * n else ()
    return "S-%d-%d" % (v[0], auth) + "".join("-%d" % x for x in subs)


def _guid(v):
    if len(v) < 16:
        return ""
    a, b, c = struct.unpack_from("<IHH", v, 0)
    d = v[8:16].hex().upper()
    return "{%08X-%04X-%04X-%s-%s}" % (a, b, c, d[:4], d[4:])


class _Chunk:
    """BinXML reader over one chunk's bytes (offsets are chunk-relative)."""

    def __init__(self, c):
        self.c = c
        self.names = {}
        self.templates = {}

    def name(self, off):
        n = self.names.get(off)
        if n is None:
            if off + 8 > len(self.c):
                raise _Err("name")
            ln, = struct.unpack_from("<H", self.c, off + 6)
            n = self.c[off + 8:off + 8 + 2 * ln].decode("utf-16-le", "replace")
            self.names[off] = n
        return n

    def name_ref(self, p):
        """(name, position after the reference and any inline string)."""
        off, = struct.unpack_from("<I", self.c, p)
        p += 4
        nm = self.name(off)
        if off == p:
            p += 8 + 2 * len(nm) + 2
        return nm, p

    # ---- token stream -> nodes: ("E", name, [(attr, valnodes)], children) | ("T", text) | ("S", idx, type, opt)
    def parse(self, p, end, depth=0):
        """Parse a fragment/element sequence from p; returns (nodes, p, template_instance_or_None)."""
        if depth > 32:
            raise _Err("depth")
        c, out = self.c, []
        while p < end:
            t = c[p]
            tok = t & 0x0F
            if t == 0x00:
                return out, p + 1, None
            if t == 0x0F:
                p += 4
            elif t == 0x0C:
                return out, p, self.template_instance(p, depth)
            elif tok == 0x01:
                el, p = self.element(p, end, depth)
                out.append(el)
            elif tok == 0x04:
                return out, p + 1, None
            else:
                v, p = self.value_token(p)
                out.append(v)
        return out, p, None

    def element(self, p, end, depth):
        c = self.c
        has_attr = c[p] & 0x40
        p += 1
        # dependency id u16 (present in Windows-written records; a few writers omit it inside nested BinXML)
        sz, = struct.unpack_from("<I", c, p + 2)
        if p + 6 + sz > len(c):
            p -= 2
        p += 2
        p += 4
        nm, p = self.name_ref(p)
        attrs, children = [], []
        if has_attr:
            p += 4
            while c[p] & 0x0F == 0x06:
                an, p = self.name_ref(p + 1)
                val = []
                while c[p] & 0x0F in _VALUE_TOKENS:
                    v, p = self.value_token(p)
                    val.append(v)
                attrs.append((an, val))
        t = c[p]
        if t == 0x03:
            return ("E", nm, attrs, children), p + 1
        if t != 0x02:
            raise _Err("close-start %#x" % t)
        p += 1
        while True:
            if p >= end:
                raise _Err("eof in element")
            t = c[p]
            tok = t & 0x0F
            if t == 0x04:
                return ("E", nm, attrs, children), p + 1
            if tok == 0x01:
                el, p = self.element(p, end, depth + 1)
                children.append(el)
            elif tok in _VALUE_TOKENS:
                v, p = self.value_token(p)
                children.append(v)
            elif tok in (0x0A, 0x0B):
                p = self.pi(p)
            else:
                raise _Err("token %#x" % t)

    def pi(self, p):
        if self.c[p] & 0x0F == 0x0A:
            _, p = self.name_ref(p + 1)
            return p
        ln, = struct.unpack_from("<H", self.c, p + 1)
        return p + 3 + 2 * ln

    def value_token(self, p):
        c = self.c
        tok = c[p] & 0x0F
        if tok == 0x05:
            typ = c[p + 1]
            if typ != 0x01:
                raise _Err("value type %#x" % typ)
            ln, = struct.unpack_from("<H", c, p + 2)
            return ("T", c[p + 4:p + 4 + 2 * ln].decode("utf-16-le", "replace")), p + 4 + 2 * ln
        if tok == 0x07:
            ln, = struct.unpack_from("<H", c, p + 1)
            return ("T", c[p + 3:p + 3 + 2 * ln].decode("utf-16-le", "replace")), p + 3 + 2 * ln
        if tok == 0x08:
            ch, = struct.unpack_from("<H", c, p + 1)
            return ("T", chr(ch)), p + 3
        if tok == 0x09:
            nm, p = self.name_ref(p + 1)
            return ("T", {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}.get(nm, "")), p
        if tok in (0x0D, 0x0E):
            idx, typ = struct.unpack_from("<HB", c, p + 1)
            return ("S", idx, typ, tok == 0x0E), p + 4
        raise _Err("value token %#x" % c[p])

    def template_instance(self, p, depth):
        """(template nodes, substitution values) for the 0x0C token at p; also returns the end position."""
        c = self.c
        doff, = struct.unpack_from("<I", c, p + 6)
        p += 10
        tmpl = self.templates.get(doff)
        if tmpl is None:
            if doff + 24 > len(c):
                raise _Err("template offset")
            dsize, = struct.unpack_from("<I", c, doff + 20)
            nodes, _, _ = self.parse(doff + 24, min(doff + 24 + dsize, len(c)), depth + 1)
            tmpl = self.templates.setdefault(doff, nodes)
        if doff == p:
            dsize, = struct.unpack_from("<I", c, doff + 20)
            p = doff + 24 + dsize
        n, = struct.unpack_from("<I", c, p)
        if n > 4096:
            raise _Err("substitution count")
        p += 4
        descs = [struct.unpack_from("<HB", c, p + 4 * i) for i in range(n)]
        p += 4 * n
        vals = []
        for size, typ in descs:
            if typ == 0x21:
                # nested BinXML: its name/template offsets stay chunk-relative -> parse it in place
                vals.append(("X", render_fragment(self, p, p + size, depth + 1)) if size else None)
            else:
                vals.append(self.typed(c[p:p + size], typ))
            p += size
        return tmpl, vals, p

    def typed(self, v, typ):
        if typ == 0x00 or not v and typ != 0x01:
            return None
        if typ == 0x01:
            return v.decode("utf-16-le", "replace").rstrip("\x00")
        if typ == 0x02:
            return v.decode("latin-1").rstrip("\x00")
        if typ & 0x80:
            if typ & 0x7F == 0x01:
                return ", ".join(s for s in v.decode("utf-16-le", "replace").split("\x00") if s)
            return v.hex().upper()
        fmt = {0x03: "b", 0x04: "B", 0x05: "h", 0x06: "H", 0x07: "i", 0x08: "I", 0x09: "q", 0x0A: "Q", 0x0B: "f",
               0x0C: "d", 0x0D: "I", 0x10: "Q", 0x11: "Q", 0x14: "I", 0x15: "Q"}.get(typ)
        if fmt:
            if len(v) < struct.calcsize(fmt):
                return None
            x, = struct.unpack_from("<" + fmt, v, 0)
            if typ == 0x0D:
                return "true" if x else "false"
            if typ == 0x11:
                return _ft_iso(x)
            if typ in (0x10, 0x14):
                return "0x%x" % x if typ == 0x10 else "0x%08x" % x
            if typ == 0x15:
                return "0x%016x" % x
            return str(x)
        if typ == 0x0E:
            return v.hex().upper()
        if typ == 0x0F:
            return _guid(v)
        if typ == 0x13:
            return _sid(v)
        if typ == 0x12 and len(v) >= 16:
            y, mo, _, d, h, mi, s, _ = struct.unpack_from("<8H", v, 0)
            return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (y, mo, d, h, mi, s)
        return v.hex().upper()


def _instantiate(nodes, vals):
    """Template nodes + substitution values -> ("E", name, {attr: text}, children) trees with plain text."""
    out = []
    for n in nodes:
        k = n[0]
        if k == "T":
            out.append(n[1])
        elif k == "S":
            v = vals[n[1]] if n[1] < len(vals) else None
            if isinstance(v, tuple) and v[0] == "X":
                out.extend(v[1])
            elif v is not None:
                out.append(v)
        elif k == "E":
            attrs = {}
            for an, av in n[2]:
                parts = _instantiate(av, vals)
                if any(isinstance(x, tuple) for x in parts):
                    continue
                attrs[an] = "".join(parts)
            out.append(("E", n[1], attrs, _instantiate(n[3], vals)))
    return out


def render_fragment(ch, p, end, depth=0):
    nodes, p, inst = ch.parse(p, end, depth)
    if inst is not None:
        tmpl, vals, _ = inst
        return _instantiate(nodes + tmpl, vals)
    return _instantiate(nodes, [])


def _text(e):
    return "".join(x if isinstance(x, str) else _text(x) for x in e[3])


def _event(tree):
    """{event_id, provider, channel, computer, time, data: {name: text}} from a rendered record."""
    ev = next((e for e in tree if isinstance(e, tuple) and e[1] == "Event"), None)
    if ev is None:
        raise _Err("no Event")
    out = {"event_id": None, "provider": None, "channel": None, "computer": None, "time": None, "data": {}}
    for sec in ev[3]:
        if not isinstance(sec, tuple):
            continue
        if sec[1] == "System":
            for e in sec[3]:
                if not isinstance(e, tuple):
                    continue
                if e[1] == "EventID":
                    t = _text(e).strip()
                    out["event_id"] = int(t) if t.isdigit() else None
                elif e[1] == "Provider":
                    out["provider"] = e[2].get("Name")
                elif e[1] in ("Channel", "Computer"):
                    out[e[1].lower()] = _text(e).strip()
                elif e[1] == "TimeCreated":
                    out["time"] = e[2].get("SystemTime")
        elif sec[1] == "EventData":
            for e in sec[3]:
                if isinstance(e, tuple) and e[1] == "Data" and "Name" in e[2]:
                    out["data"].setdefault(e[2]["Name"], _text(e))
        elif sec[1] == "UserData":
            stack = [x for x in sec[3] if isinstance(x, tuple)]
            while stack:
                e = stack.pop(0)
                kids = [x for x in e[3] if isinstance(x, tuple)]
                if kids:
                    stack[:0] = kids
                else:
                    out["data"].setdefault(e[1], _text(e))
    return out


def events(b, deadline=0.8):
    """[event dict] for every record of every physical chunk, in file order. Raises on a parse failure/timeout."""
    from .evtx import _records
    t0 = time.monotonic()
    chunks, out = {}, []
    for coff, roff in _records(b):
        if time.monotonic() - t0 > deadline:
            raise TimeoutError
        ch = chunks.get(coff)
        if ch is None:
            ch = chunks[coff] = _Chunk(b[coff:coff + 0x10000])
        size, = struct.unpack_from("<I", b, roff + 4)
        p = roff - coff
        out.append(_event(render_fragment(ch, p + 24, p + size - 4)))
    return out


def _distinct_sorted(vals):
    vals = [v for v in vals if v not in (None, "")]
    return sorted(set(vals)) or "none"


def _data(evs, ids, key):
    return [e["data"].get(key) for e in evs if e["event_id"] in ids]


def binxml_value(data, ctx):
    if data is None:
        return None
    f = ctx.get("field") or ""
    try:
        from .evtx import file_header
        b = bytes(data)
        if file_header(b) is None:
            return "none"
        evs = events(b)
    except Exception:
        return None
    if not evs:
        return "none"
    ids = [e["event_id"] for e in evs if e["event_id"] is not None]
    if f in ("log_cleared", "is_log_cleared", "log_was_cleared", "audit_log_cleared"):
        return 1102 in ids or 104 in ids
    if f in ("distinct_event_ids", "unique_event_ids", "event_ids_sorted", "event_id_set"):
        return sorted(set(ids)) or "none"
    if f in ("event_id_counts", "event_id_count_map", "event_counts_by_id"):
        cnt = {}
        for i in ids:
            cnt[i] = cnt.get(i, 0) + 1
        return {str(k): cnt[k] for k in sorted(cnt)} or "none"
    if f in ("most_common_event_id", "most_frequent_event_id"):
        if not ids:
            return "none"
        cnt = {}
        for i in ids:
            cnt[i] = cnt.get(i, 0) + 1
        return max(cnt, key=lambda k: cnt[k])   # dict keeps first-seen order: ties -> first seen (Counter rule)
    if "computer" in f:
        return _distinct_sorted([e["computer"] for e in evs])
    if "channel" in f:
        return _distinct_sorted([e["channel"] for e in evs])
    if f == "provider_names_sorted":
        return _distinct_sorted([e["provider"] for e in evs])
    if "logon_type" in f:
        vals = [v.strip() for v in _data(evs, {4624}, "LogonType") if v]
        return sorted(set(int(v) if v.isdigit() else v for v in vals),
                      key=lambda x: (isinstance(x, str), x)) or "none"
    if "target_user" in f:
        return _distinct_sorted(_data(evs, {4624, 4625}, "TargetUserName"))
    if "process" in f:
        return _distinct_sorted(_data(evs, {4688}, "NewProcessName"))
    if f in ("service_names", "installed_service_names"):
        return _distinct_sorted(_data(evs, {7045}, "ServiceName"))
    if f in ("service_image_paths", "service_file_names"):
        return _distinct_sorted(_data(evs, {7045}, "ImagePath"))
    if "script_block" in f:
        v = next((x for x in _data(evs, {4104}, "ScriptBlockText") if x is not None), None)
        return "none" if v is None or v == "" else v
    return None
