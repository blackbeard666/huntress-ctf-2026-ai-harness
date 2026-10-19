"""Mark-of-the-Web: NTFS `Zone.Identifier` alternate data stream fields (prebuilt, SPECULATIVE -- never GM-asked yet).

The ADS (`x.exe:Zone.Identifier`; copied off NTFS it becomes `x.exe_Zone.Identifier` / `x.exe.Zone.Identifier`) is an
INI text written by URLMon / browsers / the Attachment Manager:
    [ZoneTransfer]
    ZoneId=3
    ReferrerUrl=https://...        HostUrl=https://...        (Chromium / Edge / Firefox add these)
    LastWriterPackageFamilyName=Microsoft.MicrosoftEdge_8wekyb3d8bbwe   AppZoneId=4   (UWP writers)
Encoding: UTF-8 (BOM optional) is normal; UTF-16LE/BE with BOM also occurs; else cp1252. Parsed line by line (no
configparser: '%', duplicate keys, missing newline must not raise); section/key names case-insensitive; FIRST
occurrence in [ZoneTransfer] wins (GetPrivateProfileString). Values verbatim, whitespace-trimmed.
zone_id / app_zone_id: int when the stored text is a decimal integer, else the text. zone_name: the URLZONE number
-> 0 Local, 1 Intranet, 2 Trusted, 3 Internet, 4 Restricted (contract accepted_values remap the casing / spelling).
No [ZoneTransfer] section (a .url / .ini impostor, binary) -> "none"; key absent or empty -> "none".
Fmt spellings zone_identifier / motw / ads. NOTE: lib.meta's question grammar takes [a-z0-9] fmt tokens, so a
`zone_identifier.<field>` id resolves through the registered `-zone_identifier-<field>` id suffix."""

FIELDS = {
    ("zone_identifier", "zone_id"): "zone_value",
    ("zone_identifier", "zoneid"): "zone_value",
    ("zone_identifier", "zone_transfer_zone_id"): "zone_value",
    ("zone_identifier", "zonetransfer_zone_id"): "zone_value",
    ("zone_identifier", "zone_identifier_zone_id"): "zone_value",
    ("zone_identifier", "security_zone"): "zone_value",
    ("zone_identifier", "zone"): "zone_value",
    ("zone_identifier", "zone_name"): "zone_value",
    ("zone_identifier", "zone_id_name"): "zone_value",
    ("zone_identifier", "security_zone_name"): "zone_value",
    ("zone_identifier", "zone_label"): "zone_value",
    ("zone_identifier", "referrer_url"): "zone_value",
    ("zone_identifier", "referrerurl"): "zone_value",
    ("zone_identifier", "referer_url"): "zone_value",
    ("zone_identifier", "referrer"): "zone_value",
    ("zone_identifier", "host_url"): "zone_value",
    ("zone_identifier", "hosturl"): "zone_value",
    ("zone_identifier", "download_url"): "zone_value",
    ("zone_identifier", "source_url"): "zone_value",
    ("zone_identifier", "host"): "zone_value",
    ("zone_identifier", "last_writer_package_family_name"): "zone_value",
    ("zone_identifier", "lastwriterpackagefamilyname"): "zone_value",
    ("zone_identifier", "last_writer_package"): "zone_value",
    ("zone_identifier", "package_family_name"): "zone_value",
    ("zone_identifier", "app_zone_id"): "zone_value",
    ("zone_identifier", "appzoneid"): "zone_value",
    ("zone_identifier", "key_names"): "zone_value",
    ("zone_identifier", "keys"): "zone_value",
    ("zone_identifier", "zone_transfer_keys"): "zone_value",
    ("zone_identifier", "section_names"): "zone_value",
    ("zone_identifier", "sections"): "zone_value",
    ("motw", "zone_id"): "zone_value",
    ("motw", "zoneid"): "zone_value",
    ("motw", "zone_transfer_zone_id"): "zone_value",
    ("motw", "zonetransfer_zone_id"): "zone_value",
    ("motw", "zone_identifier_zone_id"): "zone_value",
    ("motw", "security_zone"): "zone_value",
    ("motw", "zone"): "zone_value",
    ("motw", "zone_name"): "zone_value",
    ("motw", "zone_id_name"): "zone_value",
    ("motw", "security_zone_name"): "zone_value",
    ("motw", "zone_label"): "zone_value",
    ("motw", "referrer_url"): "zone_value",
    ("motw", "referrerurl"): "zone_value",
    ("motw", "referer_url"): "zone_value",
    ("motw", "referrer"): "zone_value",
    ("motw", "host_url"): "zone_value",
    ("motw", "hosturl"): "zone_value",
    ("motw", "download_url"): "zone_value",
    ("motw", "source_url"): "zone_value",
    ("motw", "host"): "zone_value",
    ("motw", "last_writer_package_family_name"): "zone_value",
    ("motw", "lastwriterpackagefamilyname"): "zone_value",
    ("motw", "last_writer_package"): "zone_value",
    ("motw", "package_family_name"): "zone_value",
    ("motw", "app_zone_id"): "zone_value",
    ("motw", "appzoneid"): "zone_value",
    ("motw", "key_names"): "zone_value",
    ("motw", "keys"): "zone_value",
    ("motw", "zone_transfer_keys"): "zone_value",
    ("motw", "section_names"): "zone_value",
    ("motw", "sections"): "zone_value",
    ("ads", "zone_id"): "zone_value",
    ("ads", "zoneid"): "zone_value",
    ("ads", "zone_transfer_zone_id"): "zone_value",
    ("ads", "zonetransfer_zone_id"): "zone_value",
    ("ads", "zone_identifier_zone_id"): "zone_value",
    ("ads", "security_zone"): "zone_value",
    ("ads", "zone"): "zone_value",
    ("ads", "zone_name"): "zone_value",
    ("ads", "zone_id_name"): "zone_value",
    ("ads", "security_zone_name"): "zone_value",
    ("ads", "zone_label"): "zone_value",
    ("ads", "referrer_url"): "zone_value",
    ("ads", "referrerurl"): "zone_value",
    ("ads", "referer_url"): "zone_value",
    ("ads", "referrer"): "zone_value",
    ("ads", "host_url"): "zone_value",
    ("ads", "hosturl"): "zone_value",
    ("ads", "download_url"): "zone_value",
    ("ads", "source_url"): "zone_value",
    ("ads", "host"): "zone_value",
    ("ads", "last_writer_package_family_name"): "zone_value",
    ("ads", "lastwriterpackagefamilyname"): "zone_value",
    ("ads", "last_writer_package"): "zone_value",
    ("ads", "package_family_name"): "zone_value",
    ("ads", "app_zone_id"): "zone_value",
    ("ads", "appzoneid"): "zone_value",
    ("ads", "key_names"): "zone_value",
    ("ads", "keys"): "zone_value",
    ("ads", "zone_transfer_keys"): "zone_value",
    ("ads", "section_names"): "zone_value",
    ("ads", "sections"): "zone_value",
}

_KEYS = {"zone_id": "zoneid", "zoneid": "zoneid", "zone_transfer_zone_id": "zoneid", "zonetransfer_zone_id": "zoneid",
         "zone_identifier_zone_id": "zoneid", "security_zone": "zoneid", "zone": "zoneid",
         "referrer_url": "referrerurl", "referrerurl": "referrerurl", "referer_url": "referrerurl",
         "referrer": "referrerurl", "host_url": "hosturl", "hosturl": "hosturl", "download_url": "hosturl",
         "source_url": "hosturl", "host": "hosturl",
         "last_writer_package_family_name": "lastwriterpackagefamilyname",
         "lastwriterpackagefamilyname": "lastwriterpackagefamilyname",
         "last_writer_package": "lastwriterpackagefamilyname", "package_family_name": "lastwriterpackagefamilyname",
         "app_zone_id": "appzoneid", "appzoneid": "appzoneid"}
_NAMES = ("zone_name", "zone_id_name", "security_zone_name", "zone_label")
_ZONES = {0: "Local", 1: "Intranet", 2: "Trusted", 3: "Internet", 4: "Restricted"}


def _decode(b):
    if b[:2] == b"\xff\xfe":
        return b[2:].decode("utf-16-le", "replace")
    if b[:2] == b"\xfe\xff":
        return b[2:].decode("utf-16-be", "replace")
    if b[:3] == b"\xef\xbb\xbf":
        return b[3:].decode("utf-8", "replace")
    if len(b) > 3 and b[1:2] == b"\0" and b[3:4] == b"\0":
        return b.decode("utf-16-le", "replace")      # BOM-less UTF-16LE
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


def zone_transfer(b):
    """([(key_lower, KeyAsStored, value)], [section names]) of the [ZoneTransfer] section, or None if absent."""
    if not isinstance(b, (bytes, bytearray)) or b"\0\0\0\0" in bytes(b[:64]):
        return None
    text = _decode(bytes(b)).replace("\x00", "")
    sec, secs, out, seen = None, [], [], False
    for line in text.splitlines():
        s = line.strip()
        if not s or s[0] in ";#":
            continue
        if s.startswith("[") and "]" in s:
            sec = s[1:s.index("]")].strip()
            secs.append(sec)
            seen = seen or sec.lower() == "zonetransfer"
            continue
        if sec is not None and sec.lower() == "zonetransfer" and "=" in s:
            k, _, v = s.partition("=")
            out.append((k.strip().lower(), k.strip(), v.strip()))
    return (out, secs) if seen else None


def _num(v):
    t = v.strip()
    return int(t) if t.lstrip("-").isdigit() else t


def _value(data, field):
    zt = zone_transfer(data)
    if zt is None:
        return "none"
    kv, secs = zt
    if field in ("section_names", "sections"):
        return secs
    if field in ("key_names", "keys", "zone_transfer_keys"):
        return [k for _, k, _ in kv]
    want = "zoneid" if field in _NAMES else _KEYS.get(field)
    if want is None:
        return None
    v = next((v for k, _, v in kv if k == want), "")
    if not v:
        return "none"
    if field in _NAMES:
        n = _num(v)
        return _ZONES.get(n, "none") if isinstance(n, int) else "none"
    return _num(v) if want in ("zoneid", "appzoneid") else v


def zone_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(data, ctx.get("field") or "")
    except Exception:  # noqa: BLE001
        return None
