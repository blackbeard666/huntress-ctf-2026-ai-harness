"""TNEF (winmail.dat, application/ms-tnef) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

MS-OXTNEF 2.1, all little-endian: TNEFSignature u32 = 0x223e9f78, LegacyKey u16 (attachment key), then a run of
attributes: level u8 (1 = message, 2 = attachment), id u32 (low word = attribute id, high word = attribute type --
e.g. attAttachTitle 0x00018010, attMessageClass 0x00078008), len u32, data[len], checksum u16 (sum of data bytes mod
65536). Each attachment starts at an attAttachRendData (0x00069002); attAttachTitle is the stored (often 8.3) title,
attAttachData (0x0006800f) the raw bytes, attAttachment (0x00069005) a MAPI property list whose
PR_ATTACH_LONG_FILENAME (0x3707) is the long name (tnefparse long_filename()).
message_class = attMessageClass verbatim (NUL-stripped), falling back to PR_MESSAGE_CLASS (0x001a) of attMsgProps.
Not TNEF / truncated before the first attribute -> "none"; a truncated attribute run keeps what was walked."""
import struct

from ..spell import Hex

FIELDS = {
    ("tnef", "signature_u32_hex"): "header_value",
    ("tnef", "tnef_signature_u32_hex"): "header_value",
    ("tnef", "magic_u32_hex"): "header_value",
    ("tnef", "key_u16_hex"): "header_value",
    ("tnef", "legacy_key_u16_hex"): "header_value",
    ("tnef", "attach_key_u16_hex"): "header_value",
    ("tnef", "key"): "header_value",
    ("tnef", "key_u16"): "header_value",
    ("tnef", "legacy_key"): "header_value",
    ("tnef", "tnef_version_u32_hex"): "header_value",
    ("tnef", "version_u32_hex"): "header_value",
    ("tnef", "oem_codepage"): "header_value",
    ("tnef", "code_page"): "header_value",
    ("tnef", "codepage"): "header_value",
    ("tnef", "message_class"): "message_class",
    ("tnef", "msg_class"): "message_class",
    ("tnef", "att_message_class"): "message_class",
    ("tnef", "attachment_names"): "attachment_list",
    ("tnef", "attachment_titles"): "attachment_list",
    ("tnef", "attach_titles"): "attachment_list",
    ("tnef", "att_attach_title_names"): "attachment_list",
    ("tnef", "attachment_file_names"): "attachment_list",
    ("tnef", "attachment_filenames"): "attachment_list",
    ("tnef", "attachment_long_filenames"): "attachment_list",
    ("tnef", "attachment_long_file_names"): "attachment_list",
    ("tnef", "attachment_count"): "attachment_list",
    ("tnef", "attachments_count"): "attachment_list",
    ("tnef", "number_of_attachments"): "attachment_list",
    ("tnef", "attachment_sizes_bytes"): "attachment_list",
    ("tnef", "attachment_sizes"): "attachment_list",
    ("tnef", "attribute_count"): "attachment_list",
    ("tnef", "attribute_ids_u32_hex"): "attachment_list",
    ("winmail", "signature_u32_hex"): "header_value",
    ("winmail", "tnef_signature_u32_hex"): "header_value",
    ("winmail", "magic_u32_hex"): "header_value",
    ("winmail", "key_u16_hex"): "header_value",
    ("winmail", "legacy_key_u16_hex"): "header_value",
    ("winmail", "attach_key_u16_hex"): "header_value",
    ("winmail", "key"): "header_value",
    ("winmail", "key_u16"): "header_value",
    ("winmail", "legacy_key"): "header_value",
    ("winmail", "tnef_version_u32_hex"): "header_value",
    ("winmail", "version_u32_hex"): "header_value",
    ("winmail", "oem_codepage"): "header_value",
    ("winmail", "code_page"): "header_value",
    ("winmail", "codepage"): "header_value",
    ("winmail", "message_class"): "message_class",
    ("winmail", "msg_class"): "message_class",
    ("winmail", "att_message_class"): "message_class",
    ("winmail", "attachment_names"): "attachment_list",
    ("winmail", "attachment_titles"): "attachment_list",
    ("winmail", "attach_titles"): "attachment_list",
    ("winmail", "att_attach_title_names"): "attachment_list",
    ("winmail", "attachment_file_names"): "attachment_list",
    ("winmail", "attachment_filenames"): "attachment_list",
    ("winmail", "attachment_long_filenames"): "attachment_list",
    ("winmail", "attachment_long_file_names"): "attachment_list",
    ("winmail", "attachment_count"): "attachment_list",
    ("winmail", "attachments_count"): "attachment_list",
    ("winmail", "number_of_attachments"): "attachment_list",
    ("winmail", "attachment_sizes_bytes"): "attachment_list",
    ("winmail", "attachment_sizes"): "attachment_list",
    ("winmail", "attribute_count"): "attachment_list",
    ("winmail", "attribute_ids_u32_hex"): "attachment_list",
}

SIG = 0x223E9F78
ATT_MESSAGE_CLASS = 0x00078008
ATT_TNEF_VERSION = 0x00089006
ATT_OEM_CODEPAGE = 0x00069007
ATT_MSG_PROPS = 0x00069003
ATT_ATTACH_RENDDATA = 0x00069002
ATT_ATTACH_TITLE = 0x00018010
ATT_ATTACH_DATA = 0x0006800F
ATT_ATTACHMENT = 0x00069005

# MAPI property value sizes (MS-OXTNEF 2.1.3.4): fixed types padded to 4; variable types carry a count + lengths
_FIXED = {0x0001: 0, 0x0002: 4, 0x0003: 4, 0x0004: 4, 0x000A: 4, 0x000B: 4, 0x0005: 8, 0x0006: 8, 0x0007: 8,
          0x0014: 8, 0x0040: 8, 0x0048: 16}
_VAR = (0x001E, 0x001F, 0x0102, 0x000D)


def walk(b):
    """(key, [(level, attr_id, data)]) of a TNEF stream, or None (not TNEF / truncated header)."""
    if not b or len(b) < 6:
        return None
    sig, key = struct.unpack_from("<IH", b, 0)
    if sig != SIG:
        return None
    attrs, off, n = [], 6, len(b)
    while off + 9 <= n:
        lvl, aid, ln = struct.unpack_from("<BII", b, off)
        if lvl not in (1, 2) or off + 9 + ln + 2 > n:
            break
        attrs.append((lvl, aid, bytes(b[off + 9:off + 9 + ln])))
        off += 9 + ln + 2
    return key, attrs


def mapi_props(d, want):
    """{propid: raw value bytes (first value)} for the propids in `want` of a MAPI property list (best effort)."""
    out = {}
    try:
        cnt, = struct.unpack_from("<I", d, 0)
        off = 4
        for _ in range(min(cnt, 4096)):
            typ, pid = struct.unpack_from("<HH", d, off)
            off += 4
            if pid >= 0x8000:                       # named property: GUID + kind + id/name
                kind, = struct.unpack_from("<I", d, off + 16)
                off += 20
                if kind == 0:
                    off += 4
                else:
                    nl, = struct.unpack_from("<I", d, off)
                    off += 4 + ((nl + 3) & ~3)
            base, multi = typ & 0x0FFF, bool(typ & 0x1000)
            vals = []
            if base in _VAR or multi:
                nv, = struct.unpack_from("<I", d, off)
                off += 4
            else:
                nv = 1
            for _ in range(min(nv, 65536)):
                if base in _VAR:
                    vl, = struct.unpack_from("<I", d, off)
                    off += 4
                    vals.append(d[off + (16 if base == 0x000D else 0):off + vl])
                    off += (vl + 3) & ~3
                elif base in _FIXED:
                    vals.append(d[off:off + _FIXED[base]])
                    off += _FIXED[base]
                else:
                    return out
            if pid in want and vals and off <= len(d):
                out[pid] = (base, vals[0])
    except struct.error:
        pass
    return out


def _mapi_str(v):
    if not v:
        return None
    base, raw = v
    s = raw.decode("utf-16-le", "replace") if base == 0x001F else raw.decode("cp1252", "replace")
    return s.rstrip("\x00").strip() or None


def _text(d):
    return d.split(b"\x00", 1)[0].decode("cp1252", "replace").strip()


def attachments(attrs):
    """[{'title', 'long', 'size'}] -- one per attAttachRendData (a title/data before any RendData opens one)."""
    out = []
    for lvl, aid, d in attrs:
        if lvl != 2:
            continue
        if aid == ATT_ATTACH_RENDDATA or not out:
            out.append({"title": None, "long": None, "size": None})
            if aid == ATT_ATTACH_RENDDATA:
                continue
        cur = out[-1]
        if aid == ATT_ATTACH_TITLE:
            cur["title"] = _text(d)
        elif aid == ATT_ATTACH_DATA:
            cur["size"] = len(d)
        elif aid == ATT_ATTACHMENT:
            p = mapi_props(d, {0x3707, 0x3704, 0x3001})
            cur["long"] = _mapi_str(p.get(0x3707)) or _mapi_str(p.get(0x3704))
            cur["title"] = cur["title"] or _mapi_str(p.get(0x3001))
    return out


def header_value(data, ctx):
    if data is None:
        return None
    try:
        w = walk(data)
        if w is None:
            return "none"
        key, attrs = w
        f = ctx.get("field") or ""
        if f in ("signature_u32_hex", "tnef_signature_u32_hex", "magic_u32_hex"):
            return Hex(SIG, 8)
        if f.endswith("_u16_hex"):
            return Hex(key, 4)
        if f in ("key", "key_u16", "legacy_key"):
            return key
        want = ATT_TNEF_VERSION if "version" in f else ATT_OEM_CODEPAGE
        d = next((d for lvl, aid, d in attrs if lvl == 1 and aid == want and len(d) >= 4), None)
        if d is None:
            return "none"
        v, = struct.unpack_from("<I", d, 0)
        return Hex(v, 8) if f.endswith("_hex") else v
    except Exception:
        return None


def message_class(data, ctx):
    if data is None:
        return None
    try:
        w = walk(data)
        if w is None:
            return "none"
        attrs = w[1]
        d = next((d for lvl, aid, d in attrs if lvl == 1 and aid == ATT_MESSAGE_CLASS), None)
        if d is not None and _text(d):
            return _text(d)
        d = next((d for lvl, aid, d in attrs if lvl == 1 and aid == ATT_MSG_PROPS), None)
        return (_mapi_str(mapi_props(d, {0x001A}).get(0x001A)) if d else None) or "none"
    except Exception:
        return None


def attachment_list(data, ctx):
    if data is None:
        return None
    try:
        w = walk(data)
        if w is None:
            return "none"
        attrs = w[1]
        f = ctx.get("field") or ""
        if f == "attribute_count":
            return len(attrs)
        if f == "attribute_ids_u32_hex":
            return ["0x%08x" % aid for _, aid, _ in attrs]
        atts = attachments(attrs)
        if "count" in f or f == "number_of_attachments":
            return len(atts)
        if "size" in f:
            return [a["size"] or 0 for a in atts]
        if "long" in f:   # PR_ATTACH_LONG_FILENAME, falling back to the stored title
            return [a["long"] or a["title"] or "" for a in atts]
        # attAttachTitle (the goal's attachment_names); an attachment with no title falls back to its long name
        return [a["title"] or a["long"] or "" for a in atts]
    except Exception:
        return None
