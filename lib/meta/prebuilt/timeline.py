"""Windows Timeline ActivitiesCache.db fields (prebuilt, SPECULATIVE -- never asked by the GM yet).

ActivitiesCache.db (%LOCALAPPDATA%\\ConnectedDevicesPlatform\\<id>\\) is SQLite; the `Activity` table (Id GUID, AppId
TEXT, ActivityType INT, StartTime/EndTime/LastModifiedTime/ExpirationTime DATETIME, Payload BLOB, ...) is read with the
stdlib b-tree walker of prebuilt/sqlite.py (rows in rowid = stored order, columns named from the CREATE TABLE sql;
`ActivityOperation` is the pending-sync twin and is NOT counted).
AppId = a JSON list [{"application": ..., "platform": ...}]; the application name is the entry of the first platform
in windows_win32 / x_exe_path / windows_universal / packageId order (else the first entry) -- the order
WindowsTimeline parsers (KAPE/ WxTCmd) use. Payload = JSON with "displayText" / "appDisplayName" (type 5 opens).
Times: the table stores UNIX epoch seconds (ints) -> ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' (UTC); 0 / NULL skipped.
Lists keep first-seen stored order, de-duplicated (application_names, display_texts); *_counts is a JSON object keyed
by the ActivityType as a string, sorted numerically. Not SQLite / no Activity table (decoy) -> "none"."""
import datetime
import json

from .sqlite import _MAGIC, _columns, _header, _schema, _table_rows

FIELDS = {
    ("timeline", "activity_count"): "timeline_value",
    ("timeline", "record_count"): "timeline_value",
    ("timeline", "row_count"): "timeline_value",
    ("timeline", "entry_count"): "timeline_value",
    ("timeline", "application_names"): "timeline_value",
    ("timeline", "app_names"): "timeline_value",
    ("timeline", "applications"): "timeline_value",
    ("timeline", "app_ids"): "timeline_value",
    ("timeline", "first_application_name"): "timeline_value",
    ("timeline", "activity_type_counts"): "timeline_value",
    ("timeline", "activity_types"): "timeline_value",
    ("timeline", "start_times_utc"): "timeline_value",
    ("timeline", "end_times_utc"): "timeline_value",
    ("timeline", "earliest_start_time_utc"): "timeline_value",
    ("timeline", "first_start_time_utc"): "timeline_value",
    ("timeline", "latest_end_time_utc"): "timeline_value",
    ("timeline", "last_end_time_utc"): "timeline_value",
    ("timeline", "latest_start_time_utc"): "timeline_value",
    ("timeline", "display_texts"): "timeline_value",
    ("timeline", "payload_display_texts"): "timeline_value",
    ("timeline", "first_display_text"): "timeline_value",
    ("activitiescache", "activity_count"): "timeline_value",
    ("activitiescache", "record_count"): "timeline_value",
    ("activitiescache", "row_count"): "timeline_value",
    ("activitiescache", "entry_count"): "timeline_value",
    ("activitiescache", "application_names"): "timeline_value",
    ("activitiescache", "app_names"): "timeline_value",
    ("activitiescache", "applications"): "timeline_value",
    ("activitiescache", "app_ids"): "timeline_value",
    ("activitiescache", "first_application_name"): "timeline_value",
    ("activitiescache", "activity_type_counts"): "timeline_value",
    ("activitiescache", "activity_types"): "timeline_value",
    ("activitiescache", "start_times_utc"): "timeline_value",
    ("activitiescache", "end_times_utc"): "timeline_value",
    ("activitiescache", "earliest_start_time_utc"): "timeline_value",
    ("activitiescache", "first_start_time_utc"): "timeline_value",
    ("activitiescache", "latest_end_time_utc"): "timeline_value",
    ("activitiescache", "last_end_time_utc"): "timeline_value",
    ("activitiescache", "latest_start_time_utc"): "timeline_value",
    ("activitiescache", "display_texts"): "timeline_value",
    ("activitiescache", "payload_display_texts"): "timeline_value",
    ("activitiescache", "first_display_text"): "timeline_value",
}

_PLATFORMS = ("windows_win32", "x_exe_path", "windows_universal", "packageId")


def _activity_rows(b):
    """[dict(column -> value)] of the Activity table in stored order, None if not SQLite / no Activity table."""
    if not b or bytes(b[:16]) != _MAGIC:
        return None
    h = _header(b)
    if h is None:
        return None
    sch = _schema(b, h) or []
    for typ, name, _tbl, root, sql in sch:
        if typ == "table" and str(name).lower() == "activity" and isinstance(root, int):
            cols = _columns(sql)
            out = []
            for _rowid, vals in _table_rows(b, h, root):
                vals = list(vals) + [None] * (len(cols) - len(vals))
                out.append(dict(zip(cols, vals)))
            return out
    return None


def _app_name(appid):
    try:
        ents = json.loads(appid) if isinstance(appid, str) else None
    except ValueError:
        ents = None
    if not isinstance(ents, list):
        return appid if isinstance(appid, str) and appid else None
    ents = [e for e in ents if isinstance(e, dict) and e.get("application")]
    for p in _PLATFORMS:
        for e in ents:
            if e.get("platform") == p:
                return e["application"]
    return ents[0]["application"] if ents else None


def _iso(v):
    if not isinstance(v, int) or v <= 0:
        return None
    try:
        return datetime.datetime.fromtimestamp(v, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, OSError, ValueError):
        return None


def _display(payload):
    if isinstance(payload, (bytes, bytearray)):
        payload = bytes(payload).decode("utf-8", "replace")
    try:
        d = json.loads(payload) if isinstance(payload, str) else None
    except ValueError:
        return None
    if isinstance(d, dict):
        return d.get("displayText") or None
    return None


def _uniq(xs):
    seen, out = set(), []
    for x in xs:
        if x is not None and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def timeline_value(data, ctx):
    try:
        rows = _activity_rows(data)
    except Exception:  # noqa: BLE001
        return None
    if rows is None:
        return "none"
    f = ctx.get("field") or ""
    if f in ("activity_count", "record_count", "row_count", "entry_count"):
        return len(rows)
    if f in ("application_names", "app_names", "applications", "app_ids", "first_application_name"):
        names = _uniq(_app_name(r.get("appid")) for r in rows)
        if f == "first_application_name":
            return names[0] if names else "none"
        return names
    if f in ("activity_type_counts", "activity_types"):
        cnt = {}
        for r in rows:
            t = r.get("activitytype")
            if isinstance(t, int):
                cnt[t] = cnt.get(t, 0) + 1
        if f == "activity_types":
            return sorted(cnt)
        return {str(k): cnt[k] for k in sorted(cnt)}
    if "time" in f:
        col = "starttime" if "start" in f else "endtime"
        ts = [r.get(col) for r in rows if _iso(r.get(col))]
        if f.endswith("times_utc"):
            return [_iso(t) for t in ts]
        if not ts:
            return "none"
        return _iso(min(ts) if f.startswith(("earliest", "first")) else max(ts))
    if "display_text" in f:
        txt = _uniq(_display(r.get("payload")) for r in rows)
        if f == "first_display_text":
            return txt[0] if txt else "none"
        return txt
    return None
