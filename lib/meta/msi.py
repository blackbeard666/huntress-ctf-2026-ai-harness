"""MSI (Windows Installer) fields. COPIED from the GM-verified D13 solver
(challenges/day13/metadata-product-placement/solver/solve.py): CFB streams -> !_StringPool/!_StringData -> !Property.
msi.product_code_guid = Property['ProductCode'] VERBATIM (uppercase, WITH braces; the bare form was REJECTED).
Decoys in the same MSI: UpgradeCode, Component.ComponentId, SummaryInformation RevisionNumber (= PackageCode).
The other Property fields (upgrade code, version, name, manufacturer, language) were in the D13 solver but never asked:
speculative tier."""
import re
import struct

from .cfb import cfb_streams
from .spell import Guid

_GUID = re.compile(rb"\{?([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\}?")


def string_pool(st):
    """The MSI string table as a list (index 0 = None), or None."""
    pool, sdata = st.get("!_StringPool"), st.get("!_StringData")
    if pool is None or sdata is None or len(pool) < 4:
        return None
    cp, = struct.unpack_from("<I", pool, 0)
    enc = {1252: "cp1252", 65001: "utf-8"}.get(cp & 0xFFFF, "cp1252")
    ents = struct.unpack("<%dH" % (len(pool) // 2 - 2), pool[4:4 + (len(pool) // 4 - 1) * 4])
    strs, off, i = [None], 0, 0
    while i + 1 < len(ents):
        ln, refs = ents[i], ents[i + 1]
        if ln == 0 and refs and i + 3 < len(ents):
            ln = ents[i + 2] + (refs << 16)
            i += 4
        else:
            i += 2
        strs.append(sdata[off:off + ln].decode(enc, "replace"))
        off += ln
    return strs, (3 if cp & 0x80000000 else 2)


def properties(b):
    """{Property: Value} of an MSI's Property table, or None."""
    st = cfb_streams(b)
    if not st:
        return None
    sp = string_pool(st)
    tbl = st.get("!Property")
    if sp is None or tbl is None:
        return None
    strs, w = sp
    rows = len(tbl) // (2 * w)
    rd = lambda o: int.from_bytes(tbl[o:o + w], "little")  # noqa: E731
    out = {}
    for r in range(rows):
        k, v = rd(r * w), rd((rows + r) * w)
        if 0 < k < len(strs) and 0 < v < len(strs):
            out.setdefault(strs[k], strs[v])
    return out


def msi_property(b, prop):
    return (properties(b) or {}).get(prop)


_PROPS = {"product_code": "ProductCode", "upgrade_code": "UpgradeCode", "product_version": "ProductVersion",
          "product_name": "ProductName", "manufacturer": "Manufacturer", "product_language": "ProductLanguage"}


def _prop_name(field):
    base = re.sub(r"_guid$", "", field or "")
    return _PROPS.get(base) or "".join(p.capitalize() for p in base.split("_"))


def property_value(data, ctx):
    """msi.<property>[_guid]: the Property table value; *_guid fields keep the stored string verbatim."""
    if data is None:
        return None
    field = ctx.get("field") or ""
    v = msi_property(data, _prop_name(field))
    if v is None and field == "product_code_guid":
        m = re.search(rb"ProductCode(\{[0-9A-Fa-f-]{36}\})", data)   # D13 fallback: a damaged string pool
        v = m.group(1).decode() if m else None
    if v is None:
        return None
    if field.endswith("_guid"):
        m = _GUID.search(v.encode())
        return Guid("text", v.strip()) if m else None
    return v
