"""macOS `com.apple.quarantine` xattr fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Value (LaunchServices, xattr -p): `flags;hex_unix_time;agent;event_uuid` -- flags = 4 hex digits (u16, 0x0001 =
downloaded, 0x0040 = user approved ...), time = seconds since 1970-01-01 UTC as 8 hex digits, agent = the
downloading app ("Safari", "Google Chrome", "TextEdit"), uuid = the event row in QuarantineEventsV2 (may be empty).
Accepted members: the raw value (a bare text file, or `xattr -l` style `com.apple.quarantine: <value>`), or an
AppleDouble `._` file whose ATTR block holds com.apple.quarantine (exiftool: MacOS:XAttrQuarantine). A real macOS
`._` was seen storing `q/0081;6a35c123;TextEdit;` so the value is located by its `XXXX;XXXXXXXX;` shape, not offset 0.
quarantine_flags_hex: Hex(flags, 4) -> "0x0081" (the *_hex law; the stored text "0081" is the alternate);
quarantine_flags = the stored text verbatim. quarantine_time_utc: the hex unix time as ISO-8601 "YYYY-MM-DDTHH:MM:SSZ"
(the stored epoch IS unix, so no conversion choice); quarantine_time_unix: the int. Agent / UUID verbatim (an empty
field -> "none"). No quarantine value -> "none"."""
import datetime
import re

from ..spell import Hex
from .appledouble import entries, xattr

FIELDS = {
    ("quarantine", "quarantine_flags_hex"): "q_value",
    ("quarantine", "quarantine_flags_u16_hex"): "q_value",
    ("quarantine", "quarantine_flags"): "q_value",
    ("quarantine", "flags_hex"): "q_value",
    ("quarantine", "flags_u16_hex"): "q_value",
    ("quarantine", "flags"): "q_value",
    ("quarantine", "quarantine_time_utc"): "q_value",
    ("quarantine", "quarantine_timestamp_utc"): "q_value",
    ("quarantine", "quarantine_date_utc"): "q_value",
    ("quarantine", "time_utc"): "q_value",
    ("quarantine", "timestamp_utc"): "q_value",
    ("quarantine", "quarantine_time_unix"): "q_value",
    ("quarantine", "quarantine_timestamp_unix"): "q_value",
    ("quarantine", "quarantine_timestamp"): "q_value",
    ("quarantine", "timestamp"): "q_value",
    ("quarantine", "quarantine_time_hex"): "q_value",
    ("quarantine", "quarantine_timestamp_hex"): "q_value",
    ("quarantine", "time_hex"): "q_value",
    ("quarantine", "quarantine_agent"): "q_value",
    ("quarantine", "quarantine_agent_name"): "q_value",
    ("quarantine", "agent"): "q_value",
    ("quarantine", "agent_name"): "q_value",
    ("quarantine", "quarantine_event_uuid"): "q_value",
    ("quarantine", "quarantine_event_id"): "q_value",
    ("quarantine", "quarantine_uuid"): "q_value",
    ("quarantine", "event_uuid"): "q_value",
    ("quarantine", "event_id"): "q_value",
    ("quarantine", "uuid"): "q_value",
    ("quarantine", "quarantine_value"): "q_value",
    ("quarantine", "value"): "q_value",
    # the same values asked against the AppleDouble that carries them
    ("appledouble", "quarantine_flags_hex"): "q_value",
    ("appledouble", "quarantine_flags"): "q_value",
    ("appledouble", "quarantine_time_utc"): "q_value",
    ("appledouble", "quarantine_timestamp_utc"): "q_value",
    ("appledouble", "quarantine_time_unix"): "q_value",
    ("appledouble", "quarantine_agent"): "q_value",
    ("appledouble", "quarantine_agent_name"): "q_value",
    ("appledouble", "quarantine_event_uuid"): "q_value",
    ("appledouble", "quarantine_event_id"): "q_value",
    ("appledouble", "quarantine_uuid"): "q_value",
}

_QV = re.compile(rb"([0-9A-Fa-f]{4});([0-9A-Fa-f]{8});([^;\r\n\x00]*)(?:;([^;\r\n\x00]*))?")


def quarantine(b):
    """(flags_text, time_hex_text, agent, uuid) of the first quarantine value in b, or None."""
    if not isinstance(b, (bytes, bytearray)):
        return None
    src = bytes(b)
    if entries(src) is not None:
        src = xattr(src, "com.apple.quarantine")
        if src is None:
            return None
    elif src[:2] in (b"\xff\xfe", b"\xfe\xff"):
        src = src[2:].decode("utf-16-le" if src[:2] == b"\xff\xfe" else "utf-16-be", "replace").encode()
    m = _QV.search(src)
    if not m:
        return None
    return tuple((g or b"").decode("utf-8", "replace").strip() for g in m.groups())


def _utc(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _value(data, f):
    q = quarantine(data)
    if q is None:
        return "none"
    flags, th, agent, uid = q
    f = f[len("quarantine_"):] if f.startswith("quarantine_") else f
    if f in ("flags_hex", "flags_u16_hex"):
        return Hex(int(flags, 16), 4)
    if f == "flags":
        return flags
    if f in ("time_utc", "timestamp_utc", "date_utc"):
        return _utc(int(th, 16))
    if f in ("time_unix", "timestamp_unix", "timestamp"):
        return int(th, 16)
    if f in ("time_hex", "timestamp_hex"):
        return Hex(int(th, 16), 8)
    if f in ("agent", "agent_name"):
        return agent or "none"
    if f in ("event_uuid", "event_id", "uuid"):
        return uid or "none"
    if f == "value":
        return ";".join(x for x in q)
    return None


def q_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, ctx.get("field") or "")
    except Exception:  # noqa: BLE001
        return None
