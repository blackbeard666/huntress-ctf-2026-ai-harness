"""Windows Internet Shortcut (.url) fields (prebuilt, SPECULATIVE -- never GM-asked yet).

A .url is an INI text file: `[InternetShortcut]` with URL=, IconFile=, IconIndex=, WorkingDirectory=, HotKey=,
ShowCommand=, Modified= (hex FILETIME blob), optionally a leading `[DEFAULT]` BASEURL= and `[InternetShortcut.A/.W]`
variant sections (ignored). Phishing use: URL=file://\\\\host\\share\\x.exe / IconFile=\\\\host\\icon (NTLM leak).
Parsed line by line (no configparser: duplicate keys, '%' and missing sections must not raise). Section and key names
case-insensitive; the FIRST occurrence of a key in [InternetShortcut] wins (GetPrivateProfileString semantics).
Values verbatim, whitespace-trimmed (quotes / %ENV% kept). icon_index / hotkey / show_command: int when the stored
text is a decimal integer, else the text. Encoding: BOM (UTF-16LE/BE, UTF-8), else UTF-8, else cp1252.
No [InternetShortcut] section (a .desktop / .ini impostor, binary) -> "none"; key absent or empty -> "none".
Fmt spellings url / internet_shortcut."""
import re

FIELDS = {
    ("url", "url"): "url_value",
    ("url", "target_url"): "url_value",
    ("url", "internet_shortcut_url"): "url_value",
    ("url", "shortcut_url"): "url_value",
    ("url", "icon_file"): "url_value",
    ("url", "icon_file_name"): "url_value",
    ("url", "icon_location"): "url_value",
    ("url", "icon_path"): "url_value",
    ("url", "icon_index"): "url_value",
    ("url", "working_directory"): "url_value",
    ("url", "working_dir"): "url_value",
    ("url", "hotkey"): "url_value",
    ("url", "hot_key"): "url_value",
    ("url", "show_command"): "url_value",
    ("url", "base_url"): "url_value",
    ("url", "modified"): "url_value",
    ("url", "key_names"): "url_value",
    ("url", "section_names"): "url_value",
    # fmt alias internet_shortcut: the core fields only
    ("internet_shortcut", "url"): "url_value",
    ("internet_shortcut", "target_url"): "url_value",
    ("internet_shortcut", "icon_file"): "url_value",
    ("internet_shortcut", "icon_index"): "url_value",
    ("internet_shortcut", "working_directory"): "url_value",
    ("internet_shortcut", "hotkey"): "url_value",
    ("internet_shortcut", "hot_key"): "url_value",
    ("internet_shortcut", "show_command"): "url_value",
    ("internet_shortcut", "base_url"): "url_value",
}

_KEYS = {"url": "url", "target_url": "url", "internet_shortcut_url": "url", "shortcut_url": "url",
         "icon_file": "iconfile", "icon_file_name": "iconfile", "icon_location": "iconfile", "icon_path": "iconfile",
         "icon_index": "iconindex", "working_directory": "workingdirectory", "working_dir": "workingdirectory",
         "hotkey": "hotkey", "hot_key": "hotkey", "show_command": "showcommand", "modified": "modified"}
_INTS = ("iconindex", "hotkey", "showcommand")


def _decode(b):
    if b[:2] == b"\xff\xfe":
        return b[2:].decode("utf-16-le", "replace")
    if b[:2] == b"\xfe\xff":
        return b[2:].decode("utf-16-be", "replace")
    if b[:3] == b"\xef\xbb\xbf":
        return b[3:].decode("utf-8", "replace")
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


def _sections(text):
    """[(section name as stored, [(key as stored, value)])] in stored order."""
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line[0] in ";#":
            continue
        m = re.match(r"^\[([^\]]*)\]", line)
        if m:
            out.append((m.group(1).strip(), []))
        elif "=" in line and out:
            k, _, v = line.partition("=")
            out[-1][1].append((k.strip(), v.strip()))
    return out


def _first(pairs, key):
    for k, v in pairs:
        if k.lower() == key:
            return v
    return None


def url_value(data, ctx):
    """url.<field>: a value of an Internet Shortcut ("none" = absent / not a .url, None = cannot answer)."""
    try:
        if not data:
            return None if data is None else "none"
        field = ctx.get("field") or ""
        b = bytes(data[:1 << 20])
        if b"\x00" in b[:4096] and b[:2] not in (b"\xff\xfe", b"\xfe\xff"):
            return "none"   # binary impostor
        secs = _sections(_decode(b))
        if field == "section_names":
            return [s for s, _ in secs] if secs else "none"
        shortcut = [p for s, p in secs if s.lower() == "internetshortcut"]
        if not shortcut:
            return "none"
        pairs = [kv for p in shortcut for kv in p]
        if field == "key_names":
            return [k for k, _ in pairs]
        if field == "base_url":
            v = next((_first(p, "baseurl") for s, p in secs if s.lower() == "default" and _first(p, "baseurl")), None)
            return v or "none"
        key = _KEYS.get(field)
        if key is None:
            return None
        v = _first(pairs, key)
        if not v:
            return "none"
        if key in _INTS and re.fullmatch(r"-?\d+", v):
            return int(v)
        return v
    except Exception:  # noqa: BLE001 -- bytes in, value out; never raise past the extractor
        return None
