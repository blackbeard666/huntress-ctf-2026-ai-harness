"""Browser profile SQLite stores beyond history (prebuilt, SPECULATIVE): cookies, saved logins, autofill / form
history, downloads, bookmarks. Same fields under fmt sqlite and the aliases chrome / firefox / browser.

Rows come from sqlite.py's stdlib b-tree walker (_schema / _table_rows, rowid = stored order, columns named from the
CREATE TABLE sql); the store is recognised by its table, not by the file name:
  Chrome Cookies     `cookies`(host_key, name, path, creation_utc, expires_utc, last_access_utc, is_secure,
                     is_httponly, samesite, encrypted_value)       -- times = WebKit/Chrome us since 1601-01-01 UTC
  Firefox cookies    `moz_cookies`(host, name, path, expiry, lastAccessed, creationTime, isSecure, isHttpOnly,
                     sameSite)  -- expiry = unix SECONDS (a value > 1e11 is read as ms, newer builds); others PRTime us
  Chrome Login Data  `logins`(origin_url, action_url, username_value, date_created)   -- WebKit us
  Chrome Web Data    `autofill`(name, value, count, date_created, date_last_used)    -- unix SECONDS
  Firefox formhistory `moz_formhistory`(fieldname, value, timesUsed, firstUsed, lastUsed) -- PRTime us
  Chrome History     `downloads`(target_path, tab_url, referrer, danger_type, total_bytes, start_time, end_time)
                     + `downloads_url_chains`(id, chain_index, url)  -- WebKit us
  Firefox places     `moz_bookmarks`(type, title, dateAdded, lastModified)            -- PRTime us
Lists (*_hosts / *_names / *_urls / *_paths / ...): de-duplicated and SORTED, unless the question asks for the stored
/ insertion / chronological order ("order" in the question), then rowid order. Counts: rows. Timestamps: ISO-8601
`YYYY-MM-DDTHH:MM:SSZ` (second precision, truncated) for `*_utc` fields; the same name with `_raw` = the stored int.
cookie_encryption_version: the encrypted_value prefix (`v10` / `v11` / `v20`), one value when all agree, else the
sorted list. Not "SQLite format 3\\0" (decoy / renamed impostor) or no such table -> "none"; unreadable -> None."""
import datetime
import re

from .sqlite import _MAGIC, _columns, _header, _schema, _table_rows

FIELDS = {
    ("sqlite", "cookie_count"): "browser_store_value",
    ("sqlite", "cookie_hosts"): "browser_store_value",
    ("sqlite", "cookie_host_keys"): "browser_store_value",
    ("sqlite", "cookie_domains"): "browser_store_value",
    ("sqlite", "cookie_names"): "browser_store_value",
    ("sqlite", "cookie_paths"): "browser_store_value",
    ("sqlite", "cookie_encryption_version"): "browser_store_value",
    ("sqlite", "cookie_encryption_versions"): "browser_store_value",
    ("sqlite", "encrypted_cookie_count"): "browser_store_value",
    ("sqlite", "secure_cookie_count"): "browser_store_value",
    ("sqlite", "httponly_cookie_count"): "browser_store_value",
    ("sqlite", "secure_cookie_names"): "browser_store_value",
    ("sqlite", "httponly_cookie_names"): "browser_store_value",
    ("sqlite", "cookie_samesite_values"): "browser_store_value",
    ("sqlite", "cookie_earliest_creation_utc"): "browser_store_value",
    ("sqlite", "cookie_latest_creation_utc"): "browser_store_value",
    ("sqlite", "cookie_latest_last_access_utc"): "browser_store_value",
    ("sqlite", "cookie_latest_expires_utc"): "browser_store_value",
    ("sqlite", "cookie_earliest_creation_raw"): "browser_store_value",
    ("sqlite", "cookie_latest_creation_raw"): "browser_store_value",
    ("sqlite", "cookie_latest_last_access_raw"): "browser_store_value",
    ("sqlite", "cookie_latest_expires_raw"): "browser_store_value",
    ("sqlite", "login_count"): "browser_store_value",
    ("sqlite", "login_origins"): "browser_store_value",
    ("sqlite", "login_origin_urls"): "browser_store_value",
    ("sqlite", "login_action_urls"): "browser_store_value",
    ("sqlite", "login_usernames"): "browser_store_value",
    ("sqlite", "login_username_values"): "browser_store_value",
    ("sqlite", "login_signon_realms"): "browser_store_value",
    ("sqlite", "login_latest_date_created_utc"): "browser_store_value",
    ("sqlite", "login_latest_date_created_raw"): "browser_store_value",
    ("sqlite", "autofill_count"): "browser_store_value",
    ("sqlite", "autofill_names"): "browser_store_value",
    ("sqlite", "autofill_field_names"): "browser_store_value",
    ("sqlite", "autofill_values"): "browser_store_value",
    ("sqlite", "autofill_most_used_value"): "browser_store_value",
    ("sqlite", "autofill_most_used_name"): "browser_store_value",
    ("sqlite", "autofill_latest_used_utc"): "browser_store_value",
    ("sqlite", "autofill_latest_used_raw"): "browser_store_value",
    ("sqlite", "formhistory_count"): "browser_store_value",
    ("sqlite", "formhistory_fieldnames"): "browser_store_value",
    ("sqlite", "formhistory_field_names"): "browser_store_value",
    ("sqlite", "formhistory_values"): "browser_store_value",
    ("sqlite", "form_history_count"): "browser_store_value",
    ("sqlite", "form_history_field_names"): "browser_store_value",
    ("sqlite", "form_history_values"): "browser_store_value",
    ("sqlite", "download_count"): "browser_store_value",
    ("sqlite", "download_target_paths"): "browser_store_value",
    ("sqlite", "download_urls"): "browser_store_value",
    ("sqlite", "download_url_chains"): "browser_store_value",
    ("sqlite", "download_tab_urls"): "browser_store_value",
    ("sqlite", "download_referrers"): "browser_store_value",
    ("sqlite", "download_danger_types"): "browser_store_value",
    ("sqlite", "download_total_bytes"): "browser_store_value",
    ("sqlite", "download_total_bytes_sum"): "browser_store_value",
    ("sqlite", "download_earliest_start_time_utc"): "browser_store_value",
    ("sqlite", "download_latest_start_time_utc"): "browser_store_value",
    ("sqlite", "download_earliest_start_time_raw"): "browser_store_value",
    ("sqlite", "download_latest_start_time_raw"): "browser_store_value",
    ("sqlite", "download_file_names"): "browser_store_value",
    ("sqlite", "bookmark_count"): "browser_store_value",
    ("sqlite", "bookmark_titles"): "browser_store_value",
    ("chrome", "cookie_count"): "browser_store_value",
    ("chrome", "cookie_hosts"): "browser_store_value",
    ("chrome", "cookie_host_keys"): "browser_store_value",
    ("chrome", "cookie_domains"): "browser_store_value",
    ("chrome", "cookie_names"): "browser_store_value",
    ("chrome", "cookie_paths"): "browser_store_value",
    ("chrome", "cookie_encryption_version"): "browser_store_value",
    ("chrome", "cookie_encryption_versions"): "browser_store_value",
    ("chrome", "encrypted_cookie_count"): "browser_store_value",
    ("chrome", "secure_cookie_count"): "browser_store_value",
    ("chrome", "httponly_cookie_count"): "browser_store_value",
    ("chrome", "secure_cookie_names"): "browser_store_value",
    ("chrome", "httponly_cookie_names"): "browser_store_value",
    ("chrome", "cookie_samesite_values"): "browser_store_value",
    ("chrome", "cookie_earliest_creation_utc"): "browser_store_value",
    ("chrome", "cookie_latest_creation_utc"): "browser_store_value",
    ("chrome", "cookie_latest_last_access_utc"): "browser_store_value",
    ("chrome", "cookie_latest_expires_utc"): "browser_store_value",
    ("chrome", "cookie_earliest_creation_raw"): "browser_store_value",
    ("chrome", "cookie_latest_creation_raw"): "browser_store_value",
    ("chrome", "cookie_latest_last_access_raw"): "browser_store_value",
    ("chrome", "cookie_latest_expires_raw"): "browser_store_value",
    ("chrome", "login_count"): "browser_store_value",
    ("chrome", "login_origins"): "browser_store_value",
    ("chrome", "login_origin_urls"): "browser_store_value",
    ("chrome", "login_action_urls"): "browser_store_value",
    ("chrome", "login_usernames"): "browser_store_value",
    ("chrome", "login_username_values"): "browser_store_value",
    ("chrome", "login_signon_realms"): "browser_store_value",
    ("chrome", "login_latest_date_created_utc"): "browser_store_value",
    ("chrome", "login_latest_date_created_raw"): "browser_store_value",
    ("chrome", "autofill_count"): "browser_store_value",
    ("chrome", "autofill_names"): "browser_store_value",
    ("chrome", "autofill_field_names"): "browser_store_value",
    ("chrome", "autofill_values"): "browser_store_value",
    ("chrome", "autofill_most_used_value"): "browser_store_value",
    ("chrome", "autofill_most_used_name"): "browser_store_value",
    ("chrome", "autofill_latest_used_utc"): "browser_store_value",
    ("chrome", "autofill_latest_used_raw"): "browser_store_value",
    ("chrome", "formhistory_count"): "browser_store_value",
    ("chrome", "formhistory_fieldnames"): "browser_store_value",
    ("chrome", "formhistory_field_names"): "browser_store_value",
    ("chrome", "formhistory_values"): "browser_store_value",
    ("chrome", "form_history_count"): "browser_store_value",
    ("chrome", "form_history_field_names"): "browser_store_value",
    ("chrome", "form_history_values"): "browser_store_value",
    ("chrome", "download_count"): "browser_store_value",
    ("chrome", "download_target_paths"): "browser_store_value",
    ("chrome", "download_urls"): "browser_store_value",
    ("chrome", "download_url_chains"): "browser_store_value",
    ("chrome", "download_tab_urls"): "browser_store_value",
    ("chrome", "download_referrers"): "browser_store_value",
    ("chrome", "download_danger_types"): "browser_store_value",
    ("chrome", "download_total_bytes"): "browser_store_value",
    ("chrome", "download_total_bytes_sum"): "browser_store_value",
    ("chrome", "download_earliest_start_time_utc"): "browser_store_value",
    ("chrome", "download_latest_start_time_utc"): "browser_store_value",
    ("chrome", "download_earliest_start_time_raw"): "browser_store_value",
    ("chrome", "download_latest_start_time_raw"): "browser_store_value",
    ("chrome", "download_file_names"): "browser_store_value",
    ("chrome", "bookmark_count"): "browser_store_value",
    ("chrome", "bookmark_titles"): "browser_store_value",
    ("firefox", "cookie_count"): "browser_store_value",
    ("firefox", "cookie_hosts"): "browser_store_value",
    ("firefox", "cookie_host_keys"): "browser_store_value",
    ("firefox", "cookie_domains"): "browser_store_value",
    ("firefox", "cookie_names"): "browser_store_value",
    ("firefox", "cookie_paths"): "browser_store_value",
    ("firefox", "cookie_encryption_version"): "browser_store_value",
    ("firefox", "cookie_encryption_versions"): "browser_store_value",
    ("firefox", "encrypted_cookie_count"): "browser_store_value",
    ("firefox", "secure_cookie_count"): "browser_store_value",
    ("firefox", "httponly_cookie_count"): "browser_store_value",
    ("firefox", "secure_cookie_names"): "browser_store_value",
    ("firefox", "httponly_cookie_names"): "browser_store_value",
    ("firefox", "cookie_samesite_values"): "browser_store_value",
    ("firefox", "cookie_earliest_creation_utc"): "browser_store_value",
    ("firefox", "cookie_latest_creation_utc"): "browser_store_value",
    ("firefox", "cookie_latest_last_access_utc"): "browser_store_value",
    ("firefox", "cookie_latest_expires_utc"): "browser_store_value",
    ("firefox", "cookie_earliest_creation_raw"): "browser_store_value",
    ("firefox", "cookie_latest_creation_raw"): "browser_store_value",
    ("firefox", "cookie_latest_last_access_raw"): "browser_store_value",
    ("firefox", "cookie_latest_expires_raw"): "browser_store_value",
    ("firefox", "login_count"): "browser_store_value",
    ("firefox", "login_origins"): "browser_store_value",
    ("firefox", "login_origin_urls"): "browser_store_value",
    ("firefox", "login_action_urls"): "browser_store_value",
    ("firefox", "login_usernames"): "browser_store_value",
    ("firefox", "login_username_values"): "browser_store_value",
    ("firefox", "login_signon_realms"): "browser_store_value",
    ("firefox", "login_latest_date_created_utc"): "browser_store_value",
    ("firefox", "login_latest_date_created_raw"): "browser_store_value",
    ("firefox", "autofill_count"): "browser_store_value",
    ("firefox", "autofill_names"): "browser_store_value",
    ("firefox", "autofill_field_names"): "browser_store_value",
    ("firefox", "autofill_values"): "browser_store_value",
    ("firefox", "autofill_most_used_value"): "browser_store_value",
    ("firefox", "autofill_most_used_name"): "browser_store_value",
    ("firefox", "autofill_latest_used_utc"): "browser_store_value",
    ("firefox", "autofill_latest_used_raw"): "browser_store_value",
    ("firefox", "formhistory_count"): "browser_store_value",
    ("firefox", "formhistory_fieldnames"): "browser_store_value",
    ("firefox", "formhistory_field_names"): "browser_store_value",
    ("firefox", "formhistory_values"): "browser_store_value",
    ("firefox", "form_history_count"): "browser_store_value",
    ("firefox", "form_history_field_names"): "browser_store_value",
    ("firefox", "form_history_values"): "browser_store_value",
    ("firefox", "download_count"): "browser_store_value",
    ("firefox", "download_target_paths"): "browser_store_value",
    ("firefox", "download_urls"): "browser_store_value",
    ("firefox", "download_url_chains"): "browser_store_value",
    ("firefox", "download_tab_urls"): "browser_store_value",
    ("firefox", "download_referrers"): "browser_store_value",
    ("firefox", "download_danger_types"): "browser_store_value",
    ("firefox", "download_total_bytes"): "browser_store_value",
    ("firefox", "download_total_bytes_sum"): "browser_store_value",
    ("firefox", "download_earliest_start_time_utc"): "browser_store_value",
    ("firefox", "download_latest_start_time_utc"): "browser_store_value",
    ("firefox", "download_earliest_start_time_raw"): "browser_store_value",
    ("firefox", "download_latest_start_time_raw"): "browser_store_value",
    ("firefox", "download_file_names"): "browser_store_value",
    ("firefox", "bookmark_count"): "browser_store_value",
    ("firefox", "bookmark_titles"): "browser_store_value",
    ("browser", "cookie_count"): "browser_store_value",
    ("browser", "cookie_hosts"): "browser_store_value",
    ("browser", "cookie_host_keys"): "browser_store_value",
    ("browser", "cookie_domains"): "browser_store_value",
    ("browser", "cookie_names"): "browser_store_value",
    ("browser", "cookie_paths"): "browser_store_value",
    ("browser", "cookie_encryption_version"): "browser_store_value",
    ("browser", "cookie_encryption_versions"): "browser_store_value",
    ("browser", "encrypted_cookie_count"): "browser_store_value",
    ("browser", "secure_cookie_count"): "browser_store_value",
    ("browser", "httponly_cookie_count"): "browser_store_value",
    ("browser", "secure_cookie_names"): "browser_store_value",
    ("browser", "httponly_cookie_names"): "browser_store_value",
    ("browser", "cookie_samesite_values"): "browser_store_value",
    ("browser", "cookie_earliest_creation_utc"): "browser_store_value",
    ("browser", "cookie_latest_creation_utc"): "browser_store_value",
    ("browser", "cookie_latest_last_access_utc"): "browser_store_value",
    ("browser", "cookie_latest_expires_utc"): "browser_store_value",
    ("browser", "cookie_earliest_creation_raw"): "browser_store_value",
    ("browser", "cookie_latest_creation_raw"): "browser_store_value",
    ("browser", "cookie_latest_last_access_raw"): "browser_store_value",
    ("browser", "cookie_latest_expires_raw"): "browser_store_value",
    ("browser", "login_count"): "browser_store_value",
    ("browser", "login_origins"): "browser_store_value",
    ("browser", "login_origin_urls"): "browser_store_value",
    ("browser", "login_action_urls"): "browser_store_value",
    ("browser", "login_usernames"): "browser_store_value",
    ("browser", "login_username_values"): "browser_store_value",
    ("browser", "login_signon_realms"): "browser_store_value",
    ("browser", "login_latest_date_created_utc"): "browser_store_value",
    ("browser", "login_latest_date_created_raw"): "browser_store_value",
    ("browser", "autofill_count"): "browser_store_value",
    ("browser", "autofill_names"): "browser_store_value",
    ("browser", "autofill_field_names"): "browser_store_value",
    ("browser", "autofill_values"): "browser_store_value",
    ("browser", "autofill_most_used_value"): "browser_store_value",
    ("browser", "autofill_most_used_name"): "browser_store_value",
    ("browser", "autofill_latest_used_utc"): "browser_store_value",
    ("browser", "autofill_latest_used_raw"): "browser_store_value",
    ("browser", "formhistory_count"): "browser_store_value",
    ("browser", "formhistory_fieldnames"): "browser_store_value",
    ("browser", "formhistory_field_names"): "browser_store_value",
    ("browser", "formhistory_values"): "browser_store_value",
    ("browser", "form_history_count"): "browser_store_value",
    ("browser", "form_history_field_names"): "browser_store_value",
    ("browser", "form_history_values"): "browser_store_value",
    ("browser", "download_count"): "browser_store_value",
    ("browser", "download_target_paths"): "browser_store_value",
    ("browser", "download_urls"): "browser_store_value",
    ("browser", "download_url_chains"): "browser_store_value",
    ("browser", "download_tab_urls"): "browser_store_value",
    ("browser", "download_referrers"): "browser_store_value",
    ("browser", "download_danger_types"): "browser_store_value",
    ("browser", "download_total_bytes"): "browser_store_value",
    ("browser", "download_total_bytes_sum"): "browser_store_value",
    ("browser", "download_earliest_start_time_utc"): "browser_store_value",
    ("browser", "download_latest_start_time_utc"): "browser_store_value",
    ("browser", "download_earliest_start_time_raw"): "browser_store_value",
    ("browser", "download_latest_start_time_raw"): "browser_store_value",
    ("browser", "download_file_names"): "browser_store_value",
    ("browser", "bookmark_count"): "browser_store_value",
    ("browser", "bookmark_titles"): "browser_store_value",
}

_WEBKIT = datetime.datetime(1601, 1, 1)
_UNIX = datetime.datetime(1970, 1, 1)


def _rows(b, h, tables, name):
    """[{col: value}] of table `name` in rowid order (INTEGER PRIMARY KEY alias filled from the rowid), or None."""
    r = tables.get(name)
    if r is None:
        return None
    cols = _columns(r[4])
    out = []
    for rowid, vals in _table_rows(b, h, r[3]):
        d = dict(zip(cols, vals))
        for k in ("id", "rowid"):
            if k in d and d[k] is None:
                d[k] = rowid
        d["_rowid"] = rowid
        out.append(d)
    return out


def _iso(epoch, us):
    if not isinstance(us, int) or isinstance(us, bool) or us <= 0:
        return None
    try:
        return (epoch + datetime.timedelta(microseconds=us)).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, ValueError):
        return None


def _list(vals, ordered):
    """Strings/ints, de-duplicated; sorted unless the question asks for stored order."""
    seen, out = set(), []
    for v in vals:
        if v is None or v == "" or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out if ordered else sorted(out, key=lambda x: (str(type(x)), x))


def _pick(recs, col, conv, latest, raw):
    """ISO text (or the raw int) of the min/max positive `col` over recs."""
    vals = [d.get(col) for d in recs if isinstance(d.get(col), int) and not isinstance(d.get(col), bool)
            and d.get(col) > 0]
    if not vals:
        return "none"
    v = max(vals) if latest else min(vals)
    return v if raw else (conv(v) or "none")


def _cookies(b, h, tables, f, ordered):
    if "cookies" in tables:
        recs = _rows(b, h, tables, "cookies")
        host, sec, http, ss = "host_key", "is_secure", "is_httponly", "samesite"
        tconv = {"creation": ("creation_utc", lambda v: _iso(_WEBKIT, v)),
                 "last_access": ("last_access_utc", lambda v: _iso(_WEBKIT, v)),
                 "expires": ("expires_utc", lambda v: _iso(_WEBKIT, v))}
    elif "moz_cookies" in tables:
        recs = _rows(b, h, tables, "moz_cookies")
        host, sec, http, ss = "host", "issecure", "ishttponly", "samesite"
        # expiry: unix seconds (ms once > 1e11); creationTime / lastAccessed: PRTime us
        tconv = {"creation": ("creationtime", lambda v: _iso(_UNIX, v)),
                 "last_access": ("lastaccessed", lambda v: _iso(_UNIX, v)),
                 "expires": ("expiry", lambda v: _iso(_UNIX, v * (1000 if v > 10 ** 11 else 1000000)))}
    else:
        return "none"
    if f == "cookie_count":
        return len(recs)
    if f in ("cookie_hosts", "cookie_host_keys", "cookie_domains"):
        return _list([d.get(host) for d in recs], ordered)
    if f == "cookie_names":
        return _list([d.get("name") for d in recs], ordered)
    if f == "cookie_paths":
        return _list([d.get("path") for d in recs], ordered)
    if f == "cookie_samesite_values":
        return _list([d.get(ss) for d in recs], ordered)
    if f in ("secure_cookie_count", "httponly_cookie_count", "secure_cookie_names", "httponly_cookie_names"):
        hit = [d for d in recs if d.get(sec if f.startswith("secure") else http) == 1]
        return len(hit) if f.endswith("_count") else _list([d.get("name") for d in hit], ordered)
    if f.startswith("cookie_encryption_version") or f == "encrypted_cookie_count":
        vers = []
        for d in recs:
            ev = d.get("encrypted_value")
            if isinstance(ev, (bytes, bytearray)) and len(ev) >= 3 and re.match(rb"v\d\d", bytes(ev[:3])):
                vers.append(bytes(ev[:3]).decode())
        if f == "encrypted_cookie_count":
            return len(vers)
        if not vers:
            return "none"
        u = _list(vers, ordered)
        return u if f.endswith("versions") or len(u) > 1 else u[0]
    m = re.match(r"cookie_(earliest|latest)_(creation|last_access|expires)_(utc|raw)$", f)
    if m:
        col, conv = tconv[m.group(2)]
        return _pick(recs, col, conv, m.group(1) == "latest", m.group(3) == "raw")
    return None


def _logins(b, h, tables, f, ordered):
    recs = _rows(b, h, tables, "logins")
    if recs is None:
        return "none"
    if f == "login_count":
        return len(recs)
    col = {"login_origins": "origin_url", "login_origin_urls": "origin_url", "login_action_urls": "action_url",
           "login_usernames": "username_value", "login_username_values": "username_value",
           "login_signon_realms": "signon_realm"}.get(f)
    if col:
        return _list([d.get(col) for d in recs], ordered)
    if f.startswith("login_latest_date_created"):
        return _pick(recs, "date_created", lambda v: _iso(_WEBKIT, v), True, f.endswith("_raw"))
    return None


def _forms(b, h, tables, f, ordered):
    if "autofill" in tables:
        recs, nm, cnt, last, conv = _rows(b, h, tables, "autofill"), "name", "count", "date_last_used", \
            lambda v: _iso(_UNIX, v * 1000000)      # Chrome Web Data autofill dates: unix seconds
    elif "moz_formhistory" in tables:
        recs, nm, cnt, last, conv = _rows(b, h, tables, "moz_formhistory"), "fieldname", "timesused", "lastused", \
            lambda v: _iso(_UNIX, v)                # Firefox formhistory: PRTime us
    else:
        return "none"
    if f.endswith("_count"):
        return len(recs)
    if f.endswith(("_names", "_fieldnames")):
        return _list([d.get(nm) for d in recs], ordered)
    if f.endswith("_values"):
        return _list([d.get("value") for d in recs], ordered)
    if f.startswith("autofill_most_used"):
        best = max(recs, key=lambda d: d.get(cnt) if isinstance(d.get(cnt), int) else 0, default=None)
        if not best:
            return "none"
        return best.get("value" if f.endswith("_value") else nm) or "none"
    if f.startswith("autofill_latest_used"):
        return _pick(recs, last, conv, True, f.endswith("_raw"))
    return None


def _downloads(b, h, tables, f, ordered):
    recs = _rows(b, h, tables, "downloads")
    if recs is None:
        return "none"
    if f == "download_count":
        return len(recs)
    if f in ("download_urls", "download_url_chains"):
        chain = _rows(b, h, tables, "downloads_url_chains")
        if chain:
            chain.sort(key=lambda d: (d.get("id") or 0, d.get("chain_index") or 0))
            return _list([d.get("url") for d in chain], ordered)
        return _list([d.get("url") or d.get("tab_url") for d in recs], ordered)
    if f == "download_file_names":
        return _list([re.split(r"[\\/]", d["target_path"])[-1] for d in recs
                      if isinstance(d.get("target_path"), str) and d["target_path"]], ordered)
    col = {"download_target_paths": "target_path", "download_tab_urls": "tab_url", "download_referrers": "referrer",
           "download_danger_types": "danger_type", "download_total_bytes": "total_bytes"}.get(f)
    if col:
        vals = [d.get(col) for d in recs]
        if col in ("danger_type", "total_bytes"):    # per-download ints: stored order, not de-duplicated
            return [v for v in vals if v is not None] if ordered or col == "total_bytes" else sorted(
                {v for v in vals if v is not None})
        return _list(vals, ordered)
    if f == "download_total_bytes_sum":
        return sum(d.get("total_bytes") for d in recs if isinstance(d.get("total_bytes"), int))
    m = re.match(r"download_(earliest|latest)_start_time_(utc|raw)$", f)
    if m:
        return _pick(recs, "start_time", lambda v: _iso(_WEBKIT, v), m.group(1) == "latest", m.group(2) == "raw")
    return None


def _bookmarks(b, h, tables, f, ordered):
    recs = _rows(b, h, tables, "moz_bookmarks")
    if recs is None:
        return "none"
    marks = [d for d in recs if d.get("type") in (1, None)]     # type 1 = URL bookmark (2 folder, 3 separator)
    if f == "bookmark_count":
        return len(marks)
    return _list([d.get("title") for d in marks], ordered)


def browser_store_value(data, ctx):
    try:
        if not data or bytes(data[:16]) != _MAGIC:
            return "none"
        h = _header(data)
        sch = _schema(data, h) if h else None
        if sch is None:
            return None
        tables = {r[1].lower(): r for r in sch if r[0] == "table" and isinstance(r[1], str)}
        f = ctx.get("field") or ""
        q = ctx.get("question") or ""
        if isinstance(q, dict):
            q = q.get("question") or ""
        ordered = bool(re.search(r"\border\b|\bordered\b|as stored|chronolog", str(q), re.I))
        if f.startswith(("cookie_", "secure_cookie", "httponly_cookie", "encrypted_cookie")):
            return _cookies(data, h, tables, f, ordered)
        if f.startswith("login_"):
            return _logins(data, h, tables, f, ordered)
        if f.startswith(("autofill_", "formhistory_", "form_history_")):
            return _forms(data, h, tables, f, ordered)
        if f.startswith("download_"):
            return _downloads(data, h, tables, f, ordered)
        if f.startswith("bookmark_"):
            return _bookmarks(data, h, tables, f, ordered)
        return None
    except Exception:  # noqa: BLE001
        return None
