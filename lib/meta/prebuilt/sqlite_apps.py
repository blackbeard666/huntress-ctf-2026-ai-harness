"""SQLite database -> parent application attribution (prebuilt, SPECULATIVE -- never GM-asked yet).

Coverage-atlas row "sqlite-app-attribution" (D23 flavor: "connect databases to parent applications"). Header facts
reuse sqlite.py (_header: application id = BE u32 @68, user version @60) and its stdlib sqlite_master walker (_schema,
_table_rows, _columns); application_id_u32_hex / user_version stay in sqlite.py.
  application_id_ascii      = the 4 header bytes @68 as text when all 4 are printable ASCII (D23 `HTRT`), else "none"
                              (also for id 0 = "not set").
  application_id_known_name = the description sqlite's own magic.txt (and `file`'s magic) gives a registered id:
                              Fossil checkout / global configuration / repository, Bentley BeSQLite, OGC GeoPackage,
                              Esri, MBTiles -- spelled exactly as `file` prints it in "SQLite 3.x database (<name>)".
                              Unregistered / zero id -> "none".
  parent_application        = first schema fingerprint (set of user table names, compared case-insensitively) that the
                              database contains, in _APPS order (most specific first); none matched -> "unknown".
                              iOS sms.db and macOS chat.db share one schema -> both "iMessage chat.db".
  meta_version / meta_last_compatible_version = Chrome's `meta` table (key, value) row, value as stored; no meta table
                              or no such key -> "none".
  table_fingerprint         = user table names (sqlite_* excluded), SORTED (case-sensitive codepoint order), JSON list.
synthesis.databases_by_application: over a kit zip / the question's Files list, {parent_application: [sorted member
names]} with keys sorted; non-SQLite members skipped, unmatched databases under "unknown".
Not "SQLite format 3\\0" (decoy / renamed impostor) -> "none"; valid header with an unreadable schema -> None."""
from .sqlite import _MAGIC, _columns, _header, _schema, _table_rows

FIELDS = {
    ("sqlite", "application_id_ascii"): "sqlite_app_value",
    ("sqlite", "application_id_text"): "sqlite_app_value",
    ("sqlite", "application_id_fourcc"): "sqlite_app_value",
    ("sqlite", "application_id_chars"): "sqlite_app_value",
    ("sqlite", "application_id_known_name"): "sqlite_app_value",
    ("sqlite", "application_id_name"): "sqlite_app_value",
    ("sqlite", "application_id_description"): "sqlite_app_value",
    ("sqlite", "application_id_registered_name"): "sqlite_app_value",
    ("sqlite", "known_application_id_name"): "sqlite_app_value",
    ("sqlite", "parent_application"): "sqlite_app_value",
    ("sqlite", "parent_app"): "sqlite_app_value",
    ("sqlite", "parent_application_name"): "sqlite_app_value",
    ("sqlite", "source_application"): "sqlite_app_value",
    ("sqlite", "owning_application"): "sqlite_app_value",
    ("sqlite", "application_name"): "sqlite_app_value",
    ("sqlite", "schema_application"): "sqlite_app_value",
    ("sqlite", "meta_version"): "sqlite_app_value",
    ("sqlite", "chrome_meta_version"): "sqlite_app_value",
    ("sqlite", "meta_last_compatible_version"): "sqlite_app_value",
    ("sqlite", "chrome_meta_last_compatible_version"): "sqlite_app_value",
    ("sqlite", "table_fingerprint"): "sqlite_app_value",
    ("sqlite", "schema_fingerprint"): "sqlite_app_value",
    ("sqlite", "table_names_sorted"): "sqlite_app_value",
    ("sqlite", "sorted_table_names"): "sqlite_app_value",
    ("synthesis", "databases_by_application"): "sqlite_apps_synthesis_value",
    ("synthesis", "databases_by_parent_application"): "sqlite_apps_synthesis_value",
    ("synthesis", "parent_application_groups"): "sqlite_apps_synthesis_value",
    ("synthesis", "application_groups"): "sqlite_apps_synthesis_value",
    ("synthesis", "files_by_application"): "sqlite_apps_synthesis_value",
    ("synthesis", "database_application_groups"): "sqlite_apps_synthesis_value",
}

# sqlite.org magic.txt (= `file` magic) registered application ids
_KNOWN = {0x0F055111: "Fossil repository", 0x0F055112: "Fossil checkout", 0x0F055113: "Fossil global configuration",
          0x42654462: "Bentley Systems BeSQLite Database", 0x42654C6E: "Bentley Systems Localization File",
          0x47504B47: "OGC GeoPackage file", 0x47503130: "OGC GeoPackage version 1.0 file",
          0x45737269: "Esri Spatially-Enabled Database", 0x4D504258: "MBTiles tileset"}

# (name, required table set) -- most specific first; any listed set matching wins
_APPS = [
    ("Chrome History", [{"urls", "visits"}]),
    ("Chrome Cookies", [{"cookies", "meta"}]),
    ("Chrome Login Data", [{"logins"}]),
    ("Chrome Web Data", [{"autofill"}]),
    ("Firefox places", [{"moz_places", "moz_historyvisits"}, {"moz_places"}]),
    ("Firefox cookies", [{"moz_cookies"}]),
    ("Firefox formhistory", [{"moz_formhistory"}]),
    ("Safari History.db", [{"history_items", "history_visits"}]),
    ("WhatsApp msgstore.db", [{"messages", "jid"}, {"message", "jid"}, {"jid", "chat_list"}]),
    ("iMessage chat.db", [{"message", "handle", "chat"}]),
    ("Android mmssms.db", [{"sms", "pdu"}]),
    ("contacts2.db", [{"raw_contacts"}]),
    ("Windows ActivitiesCache.db", [{"activity", "activityoperation"}]),
    ("Windows wpndatabase.db", [{"notification", "notificationhandler"}]),
    ("Skype main.db", [{"messages", "conversations"}]),
]


def _user_tables(sch):
    return [r[1] for r in sch if r[0] == "table" and isinstance(r[1], str) and not r[1].lower().startswith("sqlite_")]


def _parent(sch):
    have = {t.lower() for t in _user_tables(sch)}
    for name, sigs in _APPS:
        if any(s <= have for s in sigs):
            return name
    return "unknown"


def _meta(b, h, sch, key):
    row = next((r for r in sch if r[0] == "table" and str(r[1]).lower() == "meta"), None)
    if row is None or not isinstance(row[3], int):
        return "none"
    cols = _columns(row[4])
    ki = cols.index("key") if "key" in cols else 0
    vi = cols.index("value") if "value" in cols else 1
    try:
        rows = _table_rows(b, h, row[3])
    except Exception:  # noqa: BLE001
        return None
    for _, vals in rows:
        if ki < len(vals) and str(vals[ki]) == key:
            v = vals[vi] if vi < len(vals) else None
            if v is None:
                return "none"
            return v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
    return "none"


def app_value_of(b, field):
    if not b or bytes(b[:16]) != _MAGIC:
        return "none"
    h = _header(b)
    if h is None:
        return None
    f = field or ""
    if f.startswith("application_id") or f == "known_application_id_name":
        if f.endswith(("_ascii", "_text", "_fourcc", "_chars")):
            raw = bytes(b[68:72])
            return raw.decode("ascii") if h["app_id"] and all(0x20 <= c < 0x7F for c in raw) else "none"
        return _KNOWN.get(h["app_id"], "none")
    sch = _schema(b, h)
    if sch is None:
        return None
    if "fingerprint" in f or "sorted" in f:
        return sorted(_user_tables(sch))
    if "meta_" in f:
        return _meta(b, h, sch, "last_compatible_version" if "last_compatible" in f else "version")
    return _parent(sch)


def sqlite_app_value(data, ctx):
    """sqlite.<attribution field> (see the module docstring)."""
    try:
        return app_value_of(data, ctx.get("field"))
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None


def sqlite_apps_synthesis_value(data, ctx):
    """synthesis.databases_by_application: {parent_application: sorted member names}."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        g = {}
        for n in names:
            b = read(n)
            if b is None:
                return None
            if bytes(b[:16]) != _MAGIC:
                continue
            app = app_value_of(b, "parent_application")
            if app is None:
                return None
            g.setdefault(app, []).append(n)
        if not g:
            return "none" if from_zip else None
        return {k: sorted(g[k]) for k in sorted(g)}
    except Exception:  # noqa: BLE001
        return None
