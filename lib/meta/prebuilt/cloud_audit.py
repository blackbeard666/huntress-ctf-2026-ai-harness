"""Cloud / identity audit exports (prebuilt, SPECULATIVE -- no field here was ever GM-verified; coverage-atlas target
"cloud-identity-audit-logs": on-brand for Huntress ITDR, a plausible host/identity-narrative member). stdlib only
(json + a manual RFC 4180 CSV split honouring quotes; no csv module).

Formats (GM fmt token -> parser):
  ual / m365_audit / unified_audit_log
                Microsoft 365 Unified Audit Log CSV export: classic `CreationDate,UserIds,Operations,AuditData` or the
                Purview layout `RecordId,CreationDate,RecordType,Operation,UserId,AuditData,...` (header names matched
                case-insensitively); AuditData is a JSON string (""-escaped). Also a JSON array / JSON lines of bare
                AuditData objects (Search-UnifiedAuditLog | expand AuditData: Operation + CreationTime + Workload).
  entra_signin  Entra ID (Azure AD) sign-in logs: Graph JSON (array, {"value": [...]}, or JSON lines; keys
                createdDateTime, userPrincipalName, ipAddress, appDisplayName, status.errorCode, location.*) or the
                portal CSV export ("Date (UTC)", "Username", "IP address", "Application", "Status",
                "Sign-in error code", "Location").
  cloudtrail    AWS CloudTrail: {"Records": [...]} (optionally gzip, as S3 delivers it), a bare array, or JSON lines;
                a record needs eventName + eventSource.
  okta          Okta System Log (API /api/v1/logs): array or JSON lines; an event needs eventType + published.

Value conventions (match netlogs.py): sets are JSON lists = Python sorted() of the distinct TEXT values (error codes /
record types as sorted ints); counts are base-10 ints; *_counts objects have sorted keys; inbox-rule names keep record
order (deduplicated). Bare first_*/last_* = the STORED timestamp text of the earliest / latest record (ordered by the
parsed instant, not by text); the *_utc spelling normalizes it to ISO-8601 "YYYY-MM-DDTHH:MM:SSZ" (fractional seconds
dropped, offsets applied; UAL "M/D/YYYY h:mm:ss AM" and naive times are read as UTC -- the export's own convention).
client IPs: AuditData ClientIP / ClientIPAddress / ActorIpAddress with a trailing :port and [] stripped when the rest is
an IP (UAL ClientIP is often "1.2.3.4:5678"); anything else kept verbatim. CloudTrail source_ips = distinct
sourceIPAddress values verbatim (service principals like "ec2.amazonaws.com" included); source_ip_addresses_only
keeps just the IPs. Empty set / no such record -> "none"; counts stay 0. Not that format -> "none"."""
import collections
import datetime
import gzip
import ipaddress
import json
import re

# ----------------------------------------------------------------------------------------------- shared helpers


def _text(data):
    if not isinstance(data, (bytes, bytearray)) or not data:
        return None
    b = bytes(data)
    if b[:2] == b"\x1f\x8b":
        try:
            b = gzip.decompress(b)
        except (OSError, EOFError, ValueError):
            return None
    if b[:3] == b"\xef\xbb\xbf":
        b = b[3:]
    elif b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        try:
            return b.decode("utf-16").lstrip("﻿")
        except UnicodeDecodeError:
            return None
    if b"\x00" in b[:4096]:
        return None
    return b.decode("utf-8", "replace")


def _json_objs(txt):
    """A JSON document or JSON lines -> list of top-level values (dicts expected), or None."""
    s = txt.strip()
    if not s or s[0] not in "[{":
        return None
    try:
        o = json.loads(s)
        return [o]
    except ValueError:
        pass
    out = []
    for ln in s.splitlines():
        ln = ln.strip().rstrip(",")
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except ValueError:
            return None
    return out


def _records(txt, wrapper_keys=("Records", "value", "records", "events", "data")):
    """Flatten JSON doc(s) into a list of dicts (arrays, {"Records": [...]}/{"value": [...]} wrappers, lines)."""
    objs = _json_objs(txt)
    if objs is None:
        return None
    out = []
    for o in objs:
        if isinstance(o, list):
            out += [x for x in o if isinstance(x, dict)]
        elif isinstance(o, dict):
            for k in wrapper_keys:
                if isinstance(o.get(k), list):
                    out += [x for x in o[k] if isinstance(x, dict)]
                    break
            else:
                out.append(o)
    return out


def _csv_rows(txt):
    """RFC 4180 split: quoted fields may hold commas, newlines and "" escapes. -> list of rows (lists of str)."""
    rows, row, cur, q, i, n = [], [], [], False, 0, len(txt)
    while i < n:
        ch = txt[i]
        if q:
            if ch == '"':
                if i + 1 < n and txt[i + 1] == '"':
                    cur.append('"')
                    i += 1
                else:
                    q = False
            else:
                cur.append(ch)
        elif ch == '"':
            q = True
        elif ch == ",":
            row.append("".join(cur))
            cur = []
        elif ch in "\r\n":
            if ch == "\r" and i + 1 < n and txt[i + 1] == "\n":
                i += 1
            row.append("".join(cur))
            cur = []
            if any(c.strip() for c in row):
                rows.append(row)
            row = []
        else:
            cur.append(ch)
        i += 1
    if cur or row:
        row.append("".join(cur))
        if any(c.strip() for c in row):
            rows.append(row)
    return rows


def _csv_dicts(txt):
    """Header row -> [{lowercased header: cell}], or None when it does not look like CSV."""
    if not txt or txt.lstrip()[:1] in "[{":
        return None
    rows = _csv_rows(txt)
    if len(rows) < 1 or len(rows[0]) < 2:
        return None
    hdr = [h.strip().lower() for h in rows[0]]
    return hdr, [{hdr[j]: (r[j] if j < len(r) else "") for j in range(len(hdr))} for r in rows[1:]]


def _col(row, *names):
    for nm in names:
        v = row.get(nm)
        if v not in (None, ""):
            return v
    return None


def _g(o, *path):
    for p in path:
        if not isinstance(o, dict):
            return None
        o = o.get(p)
    return o


def _sset(vals):
    out = set()
    for v in vals:
        if v is None or isinstance(v, (dict, list)):
            continue
        s = str(v).strip()
        if s and s not in ("-", "null"):
            out.add(s)
    return sorted(out) or "none"


def _iset(vals):
    out = set()
    for v in vals:
        try:
            out.add(int(str(v).strip()))
        except (TypeError, ValueError):
            pass
    return sorted(out) or "none"


def _counts(vals):
    c = collections.Counter(str(v) for v in vals if v not in (None, "", "-"))
    return {k: c[k] for k in sorted(c)} if c else "none"


def _top(vals):
    c = collections.Counter(str(v) for v in vals if v not in (None, "", "-"))
    if not c:
        return "none"
    best = max(c.values())
    return sorted(k for k, n in c.items() if n == best)[0]


def _ordered_unique(vals):
    seen, out = set(), []
    for v in vals:
        if v not in (None, "") and v not in seen:
            seen.add(v)
            out.append(v)
    return out or "none"


def _ip_ok(s):
    try:
        ipaddress.ip_address(str(s).strip())
        return True
    except ValueError:
        return False


def _client_ip(v):
    """'1.2.3.4:5678' / '[2001:db8::1]:443' / '::ffff:1.2.3.4' -> the IP text; else verbatim."""
    if v in (None, ""):
        return None
    s = str(v).strip()
    if _ip_ok(s):
        return s
    m = re.match(r"^\[([0-9A-Fa-f:.]+)\](?::\d+)?$", s) or re.match(r"^([0-9.]+):\d+$", s)
    if m and _ip_ok(m.group(1)):
        return m.group(1)
    return s


_US_DT = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*([AaPp][Mm]))?$")


def _parse_dt(s):
    """Stored timestamp text -> aware UTC datetime, or None."""
    if s in (None, ""):
        return None
    t = str(s).strip()
    m = _US_DT.match(t)
    if m:
        mo, d, y, hh, mi, ss, ap = m.groups()
        hh = int(hh)
        if ap:
            hh = hh % 12 + (12 if ap.lower() == "pm" else 0)
        try:
            return datetime.datetime(int(y), int(mo), int(d), hh, int(mi), int(ss or 0), tzinfo=datetime.timezone.utc)
        except ValueError:
            return None
    t = t.replace(" ", "T", 1) if re.match(r"^\d{4}-\d{2}-\d{2} \d", t) else t
    t = re.sub(r"[Zz]$", "+00:00", t)
    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?)(\.\d+)?([+-]\d{2}:?\d{2})?$", t)
    if not m:
        return None
    base, _frac, off = m.groups()
    try:
        dt = datetime.datetime.fromisoformat(base)
    except ValueError:
        return None
    if off:
        sign = 1 if off[0] == "+" else -1
        hh, mm = int(off[1:3]), int(off[-2:])
        dt = dt.replace(tzinfo=datetime.timezone(sign * datetime.timedelta(hours=hh, minutes=mm)))
    else:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _edge(stamps, last, utc):
    """stamps: stored texts. Earliest/latest by instant -> stored text, or ISO-8601 Z when utc."""
    pairs = [(d, s) for s in stamps for d in [_parse_dt(s)] if d is not None]
    if not pairs:
        return "none"
    d, s = (max if last else min)(pairs, key=lambda p: p[0])
    return d.strftime("%Y-%m-%dT%H:%M:%SZ") if utc else str(s).strip()


def _canon(field, table):
    f = (field or "").lower()
    for canon, names in table.items():
        if f in names:
            return canon
    return None


def _time_field(c, stamps):
    """first / last / first_utc / last_utc canon names -> value."""
    last = c.startswith("last")
    return _edge(stamps, last, c.endswith("_utc"))


# ------------------------------------------------------------------------------------------- M365 UAL


def parse_ual(data):
    """-> list of {date, user, op, ad (AuditData dict)} or None when not a UAL export."""
    txt = _text(data)
    if txt is None:
        return None
    cd = _csv_dicts(txt)
    if cd is not None:
        hdr, rows = cd
        if "auditdata" not in hdr or not ({"operations", "operation"} & set(hdr)):
            return None
        out = []
        for r in rows:
            try:
                ad = json.loads(r.get("auditdata") or "")
            except ValueError:
                ad = None
            ad = ad if isinstance(ad, dict) else {}
            out.append({"date": _col(r, "creationdate", "creationtime") or ad.get("CreationTime"),
                        "user": _col(r, "userids", "userid") or ad.get("UserId"),
                        "op": _col(r, "operations", "operation") or ad.get("Operation"), "ad": ad})
        return out
    recs = _records(txt)
    if not recs:
        return None
    recs = [o for o in recs if "Operation" in o and "CreationTime" in o and ("Workload" in o or "RecordType" in o)]
    if not recs:
        return None
    return [{"date": o.get("CreationTime"), "user": o.get("UserId"), "op": o.get("Operation"), "ad": o} for o in recs]


def _ual_ip(ad):
    for k in ("ClientIP", "ClientIPAddress", "ActorIpAddress", "ClientIp"):
        if ad.get(k) not in (None, ""):
            return _client_ip(ad[k])
    return None


def _rule_name(ad):
    for p in ad.get("Parameters") or []:
        if isinstance(p, dict) and str(p.get("Name", "")).lower() == "name":
            return p.get("Value")
    for p in ad.get("OperationProperties") or []:           # UpdateInboxRules (client-side Outlook rule)
        if isinstance(p, dict) and p.get("Name") == "RuleName":
            return p.get("Value")
    return ad.get("ObjectId") if ad.get("Operation") in ("New-InboxRule", "Set-InboxRule") else None


_RULE_OPS = ("New-InboxRule", "Set-InboxRule", "UpdateInboxRules")
_UAL = {
    "record_count": ("record_count", "records_count", "row_count", "entry_count", "event_count", "number_of_records",
                     "total_records", "num_records", "audit_record_count"),
    "operations": ("operations", "operation_names", "unique_operations", "distinct_operations", "operation_set",
                   "operation_list"),
    "operation_count": ("operation_count", "unique_operation_count", "distinct_operation_count"),
    "operation_counts": ("operation_counts", "operations_counts", "counts_by_operation", "operation_histogram"),
    "top_operation": ("top_operation", "most_common_operation", "most_frequent_operation"),
    "user_ids": ("user_ids", "userids", "users", "user_names", "unique_user_ids", "distinct_user_ids", "user_set",
                 "unique_users"),
    "user_count": ("user_count", "user_id_count", "unique_user_count", "distinct_user_count"),
    "client_ips": ("client_ips", "client_ip_addresses", "ip_addresses", "source_ips", "ips", "unique_ips",
                   "unique_client_ips", "distinct_client_ips", "actor_ip_addresses", "client_ip_set"),
    "client_ip_count": ("client_ip_count", "unique_client_ip_count", "ip_count", "unique_ip_count"),
    "first": ("first_creation_date", "earliest_creation_date", "first_event_time", "first_record_time",
              "earliest_event_time", "first_timestamp", "earliest_timestamp", "first_creation_time"),
    "last": ("last_creation_date", "latest_creation_date", "last_event_time", "last_record_time",
             "latest_event_time", "last_timestamp", "latest_timestamp", "last_creation_time"),
    "first_utc": ("first_creation_date_utc", "earliest_creation_date_utc", "first_event_time_utc",
                  "first_record_time_utc", "earliest_event_time_utc", "first_timestamp_utc",
                  "first_creation_time_utc"),
    "last_utc": ("last_creation_date_utc", "latest_creation_date_utc", "last_event_time_utc", "last_record_time_utc",
                 "latest_event_time_utc", "last_timestamp_utc", "last_creation_time_utc"),
    "mail_items_accessed_count": ("mail_items_accessed_count", "mailitemsaccessed_count",
                                  "mail_items_accessed_record_count", "mail_items_accessed_events"),
    "mail_items_accessed_users": ("mail_items_accessed_users", "mail_items_accessed_user_ids"),
    "inbox_rule_names": ("inbox_rule_names", "inbox_rules", "rule_names", "mailbox_rule_names"),
    "new_inbox_rule_names": ("new_inbox_rule_names", "new_inboxrule_names", "new_inbox_rules"),
    "inbox_rule_count": ("inbox_rule_count", "new_inbox_rule_count", "inbox_rule_operation_count"),
    "failed_login_count": ("failed_login_count", "user_login_failed_count", "failed_logon_count",
                           "login_failure_count", "failed_signin_count", "failed_sign_in_count"),
    "workloads": ("workloads", "workload_names", "unique_workloads"),
    "record_types": ("record_types", "record_type_ids", "unique_record_types"),
    "result_statuses": ("result_statuses", "result_status_values"),
    "user_agents": ("user_agents", "unique_user_agents"),
}


def _ual_ua(ad):
    if ad.get("UserAgent"):
        return ad["UserAgent"]
    for p in ad.get("ExtendedProperties") or []:
        if isinstance(p, dict) and p.get("Name") == "UserAgent":
            return p.get("Value")
    return None


def ual_value(data, ctx):
    if data is None:
        return None
    recs = parse_ual(data)
    if recs is None:
        return "none"
    c = _canon(ctx.get("field"), _UAL)
    ops = [r["op"] for r in recs]
    if c == "record_count":
        return len(recs)
    if c == "operations":
        return _sset(ops)
    if c == "operation_count":
        s = _sset(ops)
        return 0 if s == "none" else len(s)
    if c == "operation_counts":
        return _counts(ops)
    if c == "top_operation":
        return _top(ops)
    if c == "user_ids":
        return _sset(r["user"] for r in recs)
    if c == "user_count":
        s = _sset(r["user"] for r in recs)
        return 0 if s == "none" else len(s)
    if c == "client_ips":
        return _sset(_ual_ip(r["ad"]) for r in recs)
    if c == "client_ip_count":
        s = _sset(_ual_ip(r["ad"]) for r in recs)
        return 0 if s == "none" else len(s)
    if c in ("first", "last", "first_utc", "last_utc"):
        return _time_field(c, [r["date"] for r in recs])
    if c == "mail_items_accessed_count":
        return sum(1 for o in ops if o == "MailItemsAccessed")
    if c == "mail_items_accessed_users":
        return _sset(r["user"] for r in recs if r["op"] == "MailItemsAccessed")
    if c == "inbox_rule_names":
        return _ordered_unique(_rule_name(r["ad"]) for r in recs if r["op"] in _RULE_OPS)
    if c == "new_inbox_rule_names":
        return _ordered_unique(_rule_name(r["ad"]) for r in recs if r["op"] == "New-InboxRule")
    if c == "inbox_rule_count":
        return sum(1 for o in ops if o == "New-InboxRule")
    if c == "failed_login_count":
        return sum(1 for o in ops if o == "UserLoginFailed")
    if c == "workloads":
        return _sset(r["ad"].get("Workload") for r in recs)
    if c == "record_types":
        return _iset(r["ad"].get("RecordType") for r in recs)
    if c == "result_statuses":
        return _sset(r["ad"].get("ResultStatus") for r in recs)
    if c == "user_agents":
        return _sset(_ual_ua(r["ad"]) for r in recs)
    return None


# ------------------------------------------------------------------------------------------- Entra sign-ins


def parse_entra(data):
    """-> list of {time, upn, ip, app, err (int|None), status, country, city, location} or None."""
    txt = _text(data)
    if txt is None:
        return None
    cd = _csv_dicts(txt)
    if cd is not None:
        hdr, rows = cd
        hs = set(hdr)
        if not ({"sign-in error code", "ip address", "ipaddress"} & hs) or not (
                {"username", "user", "userprincipalname", "user principal name"} & hs) or "auditdata" in hs:
            return None
        out = []
        for r in rows:
            loc = _col(r, "location")
            parts = [p.strip() for p in (loc or "").split(",") if p.strip()]
            err = _col(r, "sign-in error code", "error code", "errorcode", "status.errorcode")
            out.append({"time": _col(r, "date (utc)", "date", "createddatetime", "created date time"),
                        "upn": _col(r, "username", "userprincipalname", "user principal name", "user"),
                        "ip": _col(r, "ip address", "ipaddress", "ip"),
                        "app": _col(r, "application", "appdisplayname", "app display name"),
                        "err": _int(err), "status": _col(r, "status"), "location": loc,
                        "country": parts[-1] if parts else None, "city": parts[0] if len(parts) > 1 else None,
                        "client_app": _col(r, "client app", "clientappused"),
                        "ca_status": _col(r, "conditional access", "conditionalaccessstatus")})
        return out
    recs = _records(txt)
    if not recs:
        return None
    recs = [o for o in recs if "userPrincipalName" in o and ("createdDateTime" in o or "ipAddress" in o)]
    if not recs:
        return None
    out = []
    for o in recs:
        loc = o.get("location") if isinstance(o.get("location"), dict) else {}
        city, state, cc = loc.get("city"), loc.get("state"), loc.get("countryOrRegion")
        st = o.get("status") if isinstance(o.get("status"), dict) else {}
        out.append({"time": o.get("createdDateTime"), "upn": o.get("userPrincipalName"), "ip": o.get("ipAddress"),
                    "app": o.get("appDisplayName"), "err": _int(st.get("errorCode")), "status": None,
                    "location": ", ".join(str(x) for x in (city, state, cc) if x) or None, "country": cc,
                    "city": city, "client_app": o.get("clientAppUsed"),
                    "ca_status": o.get("conditionalAccessStatus")})
    return out


def _int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def _failed(r):
    if r["err"] is not None:
        return r["err"] != 0
    return str(r.get("status") or "").strip().lower() in ("failure", "failed", "interrupted")


_ENTRA = {
    "record_count": ("record_count", "records_count", "row_count", "entry_count", "event_count", "signin_count",
                     "sign_in_count", "number_of_records", "total_records", "total_signins", "total_sign_ins"),
    "failed": ("failed_signin_count", "failed_sign_in_count", "failure_count", "failed_count", "failed_login_count",
               "failed_logon_count", "failed_signins", "signin_failure_count", "sign_in_failure_count"),
    "success": ("successful_signin_count", "successful_sign_in_count", "success_count", "successful_login_count"),
    "ips": ("ip_addresses", "ip_set", "ips", "source_ips", "unique_ips", "unique_ip_addresses", "distinct_ips",
            "client_ips"),
    "ip_count": ("ip_count", "unique_ip_count", "distinct_ip_count", "ip_address_count"),
    "failed_ips": ("failed_signin_ips", "failed_sign_in_ips", "failed_ip_addresses", "failure_ips", "failed_ips"),
    "top_failed_ip": ("top_failed_ip", "most_failed_ip", "top_failure_ip"),
    "upns": ("user_principal_names", "userprincipalnames", "upns", "users", "user_names", "usernames",
             "unique_users", "user_ids"),
    "failed_upns": ("failed_user_principal_names", "failed_users", "failed_upns"),
    "apps": ("app_display_names", "applications", "application_names", "apps", "app_names"),
    "error_codes": ("error_codes", "status_error_codes", "signin_error_codes", "sign_in_error_codes",
                    "unique_error_codes"),
    "countries": ("countries", "country_codes", "countries_or_regions", "location_countries"),
    "cities": ("cities", "location_cities"),
    "locations": ("locations", "location_set", "unique_locations"),
    "client_apps": ("client_apps", "client_app_used", "client_apps_used"),
    "ca_statuses": ("conditional_access_statuses", "conditional_access_status"),
    "first": ("first_signin_time", "first_sign_in_time", "first_created_date_time", "earliest_created_date_time",
              "first_event_time", "earliest_event_time", "first_timestamp"),
    "last": ("last_signin_time", "last_sign_in_time", "last_created_date_time", "latest_created_date_time",
             "last_event_time", "latest_event_time", "last_timestamp"),
    "first_utc": ("first_signin_time_utc", "first_sign_in_time_utc", "first_created_date_time_utc",
                  "first_event_time_utc", "earliest_event_time_utc", "first_timestamp_utc"),
    "last_utc": ("last_signin_time_utc", "last_sign_in_time_utc", "last_created_date_time_utc",
                 "last_event_time_utc", "latest_event_time_utc", "last_timestamp_utc"),
}


def entra_value(data, ctx):
    if data is None:
        return None
    recs = parse_entra(data)
    if recs is None:
        return "none"
    c = _canon(ctx.get("field"), _ENTRA)
    fail = [r for r in recs if _failed(r)]
    if c == "record_count":
        return len(recs)
    if c == "failed":
        return len(fail)
    if c == "success":
        return len(recs) - len(fail)
    if c == "ips":
        return _sset(r["ip"] for r in recs)
    if c == "ip_count":
        s = _sset(r["ip"] for r in recs)
        return 0 if s == "none" else len(s)
    if c == "failed_ips":
        return _sset(r["ip"] for r in fail)
    if c == "top_failed_ip":
        return _top(r["ip"] for r in fail)
    if c == "upns":
        return _sset(r["upn"] for r in recs)
    if c == "failed_upns":
        return _sset(r["upn"] for r in fail)
    if c == "apps":
        return _sset(r["app"] for r in recs)
    if c == "error_codes":
        return _iset(r["err"] for r in recs if r["err"] is not None)
    if c == "countries":
        return _sset(r["country"] for r in recs)
    if c == "cities":
        return _sset(r["city"] for r in recs)
    if c == "locations":
        return _sset(r["location"] for r in recs)
    if c == "client_apps":
        return _sset(r["client_app"] for r in recs)
    if c == "ca_statuses":
        return _sset(r["ca_status"] for r in recs)
    if c in ("first", "last", "first_utc", "last_utc"):
        return _time_field(c, [r["time"] for r in recs])
    return None


# ------------------------------------------------------------------------------------------- AWS CloudTrail


def parse_cloudtrail(data):
    txt = _text(data)
    if txt is None:
        return None
    recs = _records(txt, ("Records", "records", "Events", "events"))
    if not recs:
        return None
    recs = [o for o in recs if "eventName" in o and "eventSource" in o]
    return recs or None


_CT = {
    "record_count": ("record_count", "records_count", "event_count", "events_count", "entry_count", "row_count",
                     "number_of_records", "total_records", "num_records"),
    "event_names": ("event_names", "unique_event_names", "distinct_event_names", "event_name_set", "api_calls",
                    "api_names"),
    "event_name_count": ("event_name_count", "unique_event_name_count", "distinct_event_name_count"),
    "event_name_counts": ("event_name_counts", "event_counts", "counts_by_event_name"),
    "top_event_name": ("top_event_name", "most_common_event_name", "most_frequent_event_name"),
    "event_sources": ("event_sources", "unique_event_sources", "services", "service_names"),
    "source_ips": ("source_ips", "source_ip_addresses", "source_ip_address_set", "unique_source_ips", "ip_addresses",
                   "ips", "distinct_source_ips", "src_ips"),
    "source_ips_only": ("source_ip_addresses_only", "source_ips_only", "public_source_ips"),
    "source_ip_count": ("source_ip_count", "unique_source_ip_count", "ip_count"),
    "regions": ("regions", "aws_regions", "unique_regions", "region_set"),
    "user_names": ("user_names", "usernames", "user_identity_user_names", "users", "iam_user_names"),
    "arns": ("user_arns", "arns", "user_identity_arns", "principal_arns"),
    "identity_types": ("identity_types", "user_identity_types", "principal_types"),
    "access_key_ids": ("access_key_ids", "user_identity_access_key_ids"),
    "account_ids": ("account_ids", "recipient_account_ids", "aws_account_ids"),
    "error_codes": ("error_codes", "unique_error_codes"),
    "error_count": ("error_count", "error_event_count", "failed_event_count", "failed_api_call_count",
                    "access_denied_count"),
    "failed_console_logins": ("failed_console_login_count", "console_login_failure_count", "failed_login_count",
                              "failed_console_logins"),
    "user_agents": ("user_agents", "unique_user_agents"),
    "event_versions": ("event_versions", "event_version_set"),
    "first": ("first_event_time", "earliest_event_time", "first_timestamp", "first_record_time"),
    "last": ("last_event_time", "latest_event_time", "last_timestamp", "last_record_time"),
    "first_utc": ("first_event_time_utc", "earliest_event_time_utc", "first_timestamp_utc", "first_record_time_utc"),
    "last_utc": ("last_event_time_utc", "latest_event_time_utc", "last_timestamp_utc", "last_record_time_utc"),
}


def cloudtrail_value(data, ctx):
    if data is None:
        return None
    recs = parse_cloudtrail(data)
    if recs is None:
        return "none"
    c = _canon(ctx.get("field"), _CT)
    names = [o.get("eventName") for o in recs]
    if c == "record_count":
        return len(recs)
    if c == "event_names":
        return _sset(names)
    if c == "event_name_count":
        s = _sset(names)
        return 0 if s == "none" else len(s)
    if c == "event_name_counts":
        return _counts(names)
    if c == "top_event_name":
        return _top(names)
    if c == "event_sources":
        return _sset(o.get("eventSource") for o in recs)
    if c == "source_ips":
        return _sset(o.get("sourceIPAddress") for o in recs)
    if c == "source_ips_only":
        return _sset(o.get("sourceIPAddress") for o in recs if _ip_ok(o.get("sourceIPAddress")))
    if c == "source_ip_count":
        s = _sset(o.get("sourceIPAddress") for o in recs)
        return 0 if s == "none" else len(s)
    if c == "regions":
        return _sset(o.get("awsRegion") for o in recs)
    if c == "user_names":
        return _sset(_g(o, "userIdentity", "userName") for o in recs)
    if c == "arns":
        return _sset(_g(o, "userIdentity", "arn") for o in recs)
    if c == "identity_types":
        return _sset(_g(o, "userIdentity", "type") for o in recs)
    if c == "access_key_ids":
        return _sset(_g(o, "userIdentity", "accessKeyId") for o in recs)
    if c == "account_ids":
        return _sset(o.get("recipientAccountId") or _g(o, "userIdentity", "accountId") for o in recs)
    if c == "error_codes":
        return _sset(o.get("errorCode") for o in recs)
    if c == "error_count":
        return sum(1 for o in recs if o.get("errorCode"))
    if c == "failed_console_logins":
        return sum(1 for o in recs if o.get("eventName") == "ConsoleLogin"
                   and (_g(o, "responseElements", "ConsoleLogin") == "Failure" or o.get("errorMessage")))
    if c == "user_agents":
        return _sset(o.get("userAgent") for o in recs)
    if c == "event_versions":
        return _sset(o.get("eventVersion") for o in recs)
    if c in ("first", "last", "first_utc", "last_utc"):
        return _time_field(c, [o.get("eventTime") for o in recs])
    return None


# ------------------------------------------------------------------------------------------- Okta System Log


def parse_okta(data):
    txt = _text(data)
    if txt is None:
        return None
    recs = _records(txt, ("events", "data", "value"))
    if not recs:
        return None
    recs = [o for o in recs if "eventType" in o and "published" in o]
    return recs or None


_OKTA = {
    "record_count": ("record_count", "records_count", "event_count", "events_count", "entry_count", "row_count",
                     "number_of_events", "total_events", "num_records"),
    "event_types": ("event_types", "unique_event_types", "distinct_event_types", "event_type_set"),
    "event_type_count": ("event_type_count", "unique_event_type_count"),
    "event_type_counts": ("event_type_counts", "counts_by_event_type"),
    "top_event_type": ("top_event_type", "most_common_event_type", "most_frequent_event_type"),
    "actors": ("actor_alternate_ids", "actor_ids", "actors", "users", "user_names", "usernames", "alternate_ids",
               "actor_alternateids", "unique_actors"),
    "actor_display_names": ("actor_display_names", "display_names"),
    "client_ips": ("client_ips", "client_ip_addresses", "ip_addresses", "ips", "source_ips", "unique_ips",
                   "distinct_ips"),
    "client_ip_count": ("client_ip_count", "ip_count", "unique_ip_count"),
    "outcome_results": ("outcome_results", "outcomes", "results", "unique_outcomes"),
    "outcome_reasons": ("outcome_reasons", "failure_reasons"),
    "failure_count": ("failure_count", "failed_event_count", "failed_count", "outcome_failure_count",
                      "failures_count"),
    "failed_logins": ("failed_login_count", "failed_signin_count", "failed_sign_in_count", "failed_logon_count",
                      "failed_authentication_count", "login_failure_count"),
    "success_count": ("success_count", "successful_event_count"),
    "failed_ips": ("failed_ips", "failure_ips", "failed_client_ips"),
    "failed_actors": ("failed_actors", "failed_users", "failed_actor_alternate_ids"),
    "countries": ("countries", "client_countries", "geo_countries"),
    "user_agents": ("user_agents", "raw_user_agents", "client_user_agents"),
    "target_ids": ("target_alternate_ids", "targets", "target_ids"),
    "display_messages": ("display_messages", "messages"),
    "severities": ("severities", "severity_levels"),
    "first": ("first_published", "earliest_published", "first_event_time", "earliest_event_time", "first_timestamp"),
    "last": ("last_published", "latest_published", "last_event_time", "latest_event_time", "last_timestamp"),
    "first_utc": ("first_published_utc", "earliest_published_utc", "first_event_time_utc", "first_timestamp_utc"),
    "last_utc": ("last_published_utc", "latest_published_utc", "last_event_time_utc", "last_timestamp_utc"),
}


def _okta_fail(o):
    return str(_g(o, "outcome", "result") or "").upper() in ("FAILURE", "DENY")


def okta_value(data, ctx):
    if data is None:
        return None
    recs = parse_okta(data)
    if recs is None:
        return "none"
    c = _canon(ctx.get("field"), _OKTA)
    types = [o.get("eventType") for o in recs]
    fail = [o for o in recs if _okta_fail(o)]
    if c == "record_count":
        return len(recs)
    if c == "event_types":
        return _sset(types)
    if c == "event_type_count":
        s = _sset(types)
        return 0 if s == "none" else len(s)
    if c == "event_type_counts":
        return _counts(types)
    if c == "top_event_type":
        return _top(types)
    if c == "actors":
        return _sset(_g(o, "actor", "alternateId") for o in recs)
    if c == "actor_display_names":
        return _sset(_g(o, "actor", "displayName") for o in recs)
    if c == "client_ips":
        return _sset(_g(o, "client", "ipAddress") for o in recs)
    if c == "client_ip_count":
        s = _sset(_g(o, "client", "ipAddress") for o in recs)
        return 0 if s == "none" else len(s)
    if c == "outcome_results":
        return _sset(_g(o, "outcome", "result") for o in recs)
    if c == "outcome_reasons":
        return _sset(_g(o, "outcome", "reason") for o in recs)
    if c == "failure_count":
        return len(fail)
    if c == "failed_logins":
        return sum(1 for o in fail if str(o.get("eventType", "")).startswith(("user.session.start",
                                                                               "user.authentication")))
    if c == "success_count":
        return sum(1 for o in recs if str(_g(o, "outcome", "result") or "").upper() == "SUCCESS")
    if c == "failed_ips":
        return _sset(_g(o, "client", "ipAddress") for o in fail)
    if c == "failed_actors":
        return _sset(_g(o, "actor", "alternateId") for o in fail)
    if c == "countries":
        return _sset(_g(o, "client", "geographicalContext", "country") for o in recs)
    if c == "user_agents":
        return _sset(_g(o, "client", "userAgent", "rawUserAgent") for o in recs)
    if c == "target_ids":
        return _sset(t.get("alternateId") for o in recs for t in (o.get("target") or []) if isinstance(t, dict))
    if c == "display_messages":
        return _sset(o.get("displayMessage") for o in recs)
    if c == "severities":
        return _sset(o.get("severity") for o in recs)
    if c in ("first", "last", "first_utc", "last_utc"):
        return _time_field(c, [o.get("published") for o in recs])
    return None


# FIELDS: generated from the alias tables above (literal, read with ast by lib.meta).
FIELDS = {
    # ual
    ("ual", "actor_ip_addresses"): "ual_value",
    ("ual", "audit_record_count"): "ual_value",
    ("ual", "client_ip_addresses"): "ual_value",
    ("ual", "client_ip_count"): "ual_value",
    ("ual", "client_ip_set"): "ual_value",
    ("ual", "client_ips"): "ual_value",
    ("ual", "counts_by_operation"): "ual_value",
    ("ual", "distinct_client_ips"): "ual_value",
    ("ual", "distinct_operation_count"): "ual_value",
    ("ual", "distinct_operations"): "ual_value",
    ("ual", "distinct_user_count"): "ual_value",
    ("ual", "distinct_user_ids"): "ual_value",
    ("ual", "earliest_creation_date"): "ual_value",
    ("ual", "earliest_creation_date_utc"): "ual_value",
    ("ual", "earliest_event_time"): "ual_value",
    ("ual", "earliest_event_time_utc"): "ual_value",
    ("ual", "earliest_timestamp"): "ual_value",
    ("ual", "entry_count"): "ual_value",
    ("ual", "event_count"): "ual_value",
    ("ual", "failed_login_count"): "ual_value",
    ("ual", "failed_logon_count"): "ual_value",
    ("ual", "failed_sign_in_count"): "ual_value",
    ("ual", "failed_signin_count"): "ual_value",
    ("ual", "first_creation_date"): "ual_value",
    ("ual", "first_creation_date_utc"): "ual_value",
    ("ual", "first_creation_time"): "ual_value",
    ("ual", "first_creation_time_utc"): "ual_value",
    ("ual", "first_event_time"): "ual_value",
    ("ual", "first_event_time_utc"): "ual_value",
    ("ual", "first_record_time"): "ual_value",
    ("ual", "first_record_time_utc"): "ual_value",
    ("ual", "first_timestamp"): "ual_value",
    ("ual", "first_timestamp_utc"): "ual_value",
    ("ual", "inbox_rule_count"): "ual_value",
    ("ual", "inbox_rule_names"): "ual_value",
    ("ual", "inbox_rule_operation_count"): "ual_value",
    ("ual", "inbox_rules"): "ual_value",
    ("ual", "ip_addresses"): "ual_value",
    ("ual", "ip_count"): "ual_value",
    ("ual", "ips"): "ual_value",
    ("ual", "last_creation_date"): "ual_value",
    ("ual", "last_creation_date_utc"): "ual_value",
    ("ual", "last_creation_time"): "ual_value",
    ("ual", "last_creation_time_utc"): "ual_value",
    ("ual", "last_event_time"): "ual_value",
    ("ual", "last_event_time_utc"): "ual_value",
    ("ual", "last_record_time"): "ual_value",
    ("ual", "last_record_time_utc"): "ual_value",
    ("ual", "last_timestamp"): "ual_value",
    ("ual", "last_timestamp_utc"): "ual_value",
    ("ual", "latest_creation_date"): "ual_value",
    ("ual", "latest_creation_date_utc"): "ual_value",
    ("ual", "latest_event_time"): "ual_value",
    ("ual", "latest_event_time_utc"): "ual_value",
    ("ual", "latest_timestamp"): "ual_value",
    ("ual", "login_failure_count"): "ual_value",
    ("ual", "mail_items_accessed_count"): "ual_value",
    ("ual", "mail_items_accessed_events"): "ual_value",
    ("ual", "mail_items_accessed_record_count"): "ual_value",
    ("ual", "mail_items_accessed_user_ids"): "ual_value",
    ("ual", "mail_items_accessed_users"): "ual_value",
    ("ual", "mailbox_rule_names"): "ual_value",
    ("ual", "mailitemsaccessed_count"): "ual_value",
    ("ual", "most_common_operation"): "ual_value",
    ("ual", "most_frequent_operation"): "ual_value",
    ("ual", "new_inbox_rule_count"): "ual_value",
    ("ual", "new_inbox_rule_names"): "ual_value",
    ("ual", "new_inbox_rules"): "ual_value",
    ("ual", "new_inboxrule_names"): "ual_value",
    ("ual", "num_records"): "ual_value",
    ("ual", "number_of_records"): "ual_value",
    ("ual", "operation_count"): "ual_value",
    ("ual", "operation_counts"): "ual_value",
    ("ual", "operation_histogram"): "ual_value",
    ("ual", "operation_list"): "ual_value",
    ("ual", "operation_names"): "ual_value",
    ("ual", "operation_set"): "ual_value",
    ("ual", "operations"): "ual_value",
    ("ual", "operations_counts"): "ual_value",
    ("ual", "record_count"): "ual_value",
    ("ual", "record_type_ids"): "ual_value",
    ("ual", "record_types"): "ual_value",
    ("ual", "records_count"): "ual_value",
    ("ual", "result_status_values"): "ual_value",
    ("ual", "result_statuses"): "ual_value",
    ("ual", "row_count"): "ual_value",
    ("ual", "rule_names"): "ual_value",
    ("ual", "source_ips"): "ual_value",
    ("ual", "top_operation"): "ual_value",
    ("ual", "total_records"): "ual_value",
    ("ual", "unique_client_ip_count"): "ual_value",
    ("ual", "unique_client_ips"): "ual_value",
    ("ual", "unique_ip_count"): "ual_value",
    ("ual", "unique_ips"): "ual_value",
    ("ual", "unique_operation_count"): "ual_value",
    ("ual", "unique_operations"): "ual_value",
    ("ual", "unique_record_types"): "ual_value",
    ("ual", "unique_user_agents"): "ual_value",
    ("ual", "unique_user_count"): "ual_value",
    ("ual", "unique_user_ids"): "ual_value",
    ("ual", "unique_users"): "ual_value",
    ("ual", "unique_workloads"): "ual_value",
    ("ual", "user_agents"): "ual_value",
    ("ual", "user_count"): "ual_value",
    ("ual", "user_id_count"): "ual_value",
    ("ual", "user_ids"): "ual_value",
    ("ual", "user_login_failed_count"): "ual_value",
    ("ual", "user_names"): "ual_value",
    ("ual", "user_set"): "ual_value",
    ("ual", "userids"): "ual_value",
    ("ual", "users"): "ual_value",
    ("ual", "workload_names"): "ual_value",
    ("ual", "workloads"): "ual_value",
    # m365_audit
    ("m365_audit", "actor_ip_addresses"): "ual_value",
    ("m365_audit", "audit_record_count"): "ual_value",
    ("m365_audit", "client_ip_addresses"): "ual_value",
    ("m365_audit", "client_ip_count"): "ual_value",
    ("m365_audit", "client_ip_set"): "ual_value",
    ("m365_audit", "client_ips"): "ual_value",
    ("m365_audit", "counts_by_operation"): "ual_value",
    ("m365_audit", "distinct_client_ips"): "ual_value",
    ("m365_audit", "distinct_operation_count"): "ual_value",
    ("m365_audit", "distinct_operations"): "ual_value",
    ("m365_audit", "distinct_user_count"): "ual_value",
    ("m365_audit", "distinct_user_ids"): "ual_value",
    ("m365_audit", "earliest_creation_date"): "ual_value",
    ("m365_audit", "earliest_creation_date_utc"): "ual_value",
    ("m365_audit", "earliest_event_time"): "ual_value",
    ("m365_audit", "earliest_event_time_utc"): "ual_value",
    ("m365_audit", "earliest_timestamp"): "ual_value",
    ("m365_audit", "entry_count"): "ual_value",
    ("m365_audit", "event_count"): "ual_value",
    ("m365_audit", "failed_login_count"): "ual_value",
    ("m365_audit", "failed_logon_count"): "ual_value",
    ("m365_audit", "failed_sign_in_count"): "ual_value",
    ("m365_audit", "failed_signin_count"): "ual_value",
    ("m365_audit", "first_creation_date"): "ual_value",
    ("m365_audit", "first_creation_date_utc"): "ual_value",
    ("m365_audit", "first_creation_time"): "ual_value",
    ("m365_audit", "first_creation_time_utc"): "ual_value",
    ("m365_audit", "first_event_time"): "ual_value",
    ("m365_audit", "first_event_time_utc"): "ual_value",
    ("m365_audit", "first_record_time"): "ual_value",
    ("m365_audit", "first_record_time_utc"): "ual_value",
    ("m365_audit", "first_timestamp"): "ual_value",
    ("m365_audit", "first_timestamp_utc"): "ual_value",
    ("m365_audit", "inbox_rule_count"): "ual_value",
    ("m365_audit", "inbox_rule_names"): "ual_value",
    ("m365_audit", "inbox_rule_operation_count"): "ual_value",
    ("m365_audit", "inbox_rules"): "ual_value",
    ("m365_audit", "ip_addresses"): "ual_value",
    ("m365_audit", "ip_count"): "ual_value",
    ("m365_audit", "ips"): "ual_value",
    ("m365_audit", "last_creation_date"): "ual_value",
    ("m365_audit", "last_creation_date_utc"): "ual_value",
    ("m365_audit", "last_creation_time"): "ual_value",
    ("m365_audit", "last_creation_time_utc"): "ual_value",
    ("m365_audit", "last_event_time"): "ual_value",
    ("m365_audit", "last_event_time_utc"): "ual_value",
    ("m365_audit", "last_record_time"): "ual_value",
    ("m365_audit", "last_record_time_utc"): "ual_value",
    ("m365_audit", "last_timestamp"): "ual_value",
    ("m365_audit", "last_timestamp_utc"): "ual_value",
    ("m365_audit", "latest_creation_date"): "ual_value",
    ("m365_audit", "latest_creation_date_utc"): "ual_value",
    ("m365_audit", "latest_event_time"): "ual_value",
    ("m365_audit", "latest_event_time_utc"): "ual_value",
    ("m365_audit", "latest_timestamp"): "ual_value",
    ("m365_audit", "login_failure_count"): "ual_value",
    ("m365_audit", "mail_items_accessed_count"): "ual_value",
    ("m365_audit", "mail_items_accessed_events"): "ual_value",
    ("m365_audit", "mail_items_accessed_record_count"): "ual_value",
    ("m365_audit", "mail_items_accessed_user_ids"): "ual_value",
    ("m365_audit", "mail_items_accessed_users"): "ual_value",
    ("m365_audit", "mailbox_rule_names"): "ual_value",
    ("m365_audit", "mailitemsaccessed_count"): "ual_value",
    ("m365_audit", "most_common_operation"): "ual_value",
    ("m365_audit", "most_frequent_operation"): "ual_value",
    ("m365_audit", "new_inbox_rule_count"): "ual_value",
    ("m365_audit", "new_inbox_rule_names"): "ual_value",
    ("m365_audit", "new_inbox_rules"): "ual_value",
    ("m365_audit", "new_inboxrule_names"): "ual_value",
    ("m365_audit", "num_records"): "ual_value",
    ("m365_audit", "number_of_records"): "ual_value",
    ("m365_audit", "operation_count"): "ual_value",
    ("m365_audit", "operation_counts"): "ual_value",
    ("m365_audit", "operation_histogram"): "ual_value",
    ("m365_audit", "operation_list"): "ual_value",
    ("m365_audit", "operation_names"): "ual_value",
    ("m365_audit", "operation_set"): "ual_value",
    ("m365_audit", "operations"): "ual_value",
    ("m365_audit", "operations_counts"): "ual_value",
    ("m365_audit", "record_count"): "ual_value",
    ("m365_audit", "record_type_ids"): "ual_value",
    ("m365_audit", "record_types"): "ual_value",
    ("m365_audit", "records_count"): "ual_value",
    ("m365_audit", "result_status_values"): "ual_value",
    ("m365_audit", "result_statuses"): "ual_value",
    ("m365_audit", "row_count"): "ual_value",
    ("m365_audit", "rule_names"): "ual_value",
    ("m365_audit", "source_ips"): "ual_value",
    ("m365_audit", "top_operation"): "ual_value",
    ("m365_audit", "total_records"): "ual_value",
    ("m365_audit", "unique_client_ip_count"): "ual_value",
    ("m365_audit", "unique_client_ips"): "ual_value",
    ("m365_audit", "unique_ip_count"): "ual_value",
    ("m365_audit", "unique_ips"): "ual_value",
    ("m365_audit", "unique_operation_count"): "ual_value",
    ("m365_audit", "unique_operations"): "ual_value",
    ("m365_audit", "unique_record_types"): "ual_value",
    ("m365_audit", "unique_user_agents"): "ual_value",
    ("m365_audit", "unique_user_count"): "ual_value",
    ("m365_audit", "unique_user_ids"): "ual_value",
    ("m365_audit", "unique_users"): "ual_value",
    ("m365_audit", "unique_workloads"): "ual_value",
    ("m365_audit", "user_agents"): "ual_value",
    ("m365_audit", "user_count"): "ual_value",
    ("m365_audit", "user_id_count"): "ual_value",
    ("m365_audit", "user_ids"): "ual_value",
    ("m365_audit", "user_login_failed_count"): "ual_value",
    ("m365_audit", "user_names"): "ual_value",
    ("m365_audit", "user_set"): "ual_value",
    ("m365_audit", "userids"): "ual_value",
    ("m365_audit", "users"): "ual_value",
    ("m365_audit", "workload_names"): "ual_value",
    ("m365_audit", "workloads"): "ual_value",
    # unified_audit_log
    ("unified_audit_log", "actor_ip_addresses"): "ual_value",
    ("unified_audit_log", "audit_record_count"): "ual_value",
    ("unified_audit_log", "client_ip_addresses"): "ual_value",
    ("unified_audit_log", "client_ip_count"): "ual_value",
    ("unified_audit_log", "client_ip_set"): "ual_value",
    ("unified_audit_log", "client_ips"): "ual_value",
    ("unified_audit_log", "counts_by_operation"): "ual_value",
    ("unified_audit_log", "distinct_client_ips"): "ual_value",
    ("unified_audit_log", "distinct_operation_count"): "ual_value",
    ("unified_audit_log", "distinct_operations"): "ual_value",
    ("unified_audit_log", "distinct_user_count"): "ual_value",
    ("unified_audit_log", "distinct_user_ids"): "ual_value",
    ("unified_audit_log", "earliest_creation_date"): "ual_value",
    ("unified_audit_log", "earliest_creation_date_utc"): "ual_value",
    ("unified_audit_log", "earliest_event_time"): "ual_value",
    ("unified_audit_log", "earliest_event_time_utc"): "ual_value",
    ("unified_audit_log", "earliest_timestamp"): "ual_value",
    ("unified_audit_log", "entry_count"): "ual_value",
    ("unified_audit_log", "event_count"): "ual_value",
    ("unified_audit_log", "failed_login_count"): "ual_value",
    ("unified_audit_log", "failed_logon_count"): "ual_value",
    ("unified_audit_log", "failed_sign_in_count"): "ual_value",
    ("unified_audit_log", "failed_signin_count"): "ual_value",
    ("unified_audit_log", "first_creation_date"): "ual_value",
    ("unified_audit_log", "first_creation_date_utc"): "ual_value",
    ("unified_audit_log", "first_creation_time"): "ual_value",
    ("unified_audit_log", "first_creation_time_utc"): "ual_value",
    ("unified_audit_log", "first_event_time"): "ual_value",
    ("unified_audit_log", "first_event_time_utc"): "ual_value",
    ("unified_audit_log", "first_record_time"): "ual_value",
    ("unified_audit_log", "first_record_time_utc"): "ual_value",
    ("unified_audit_log", "first_timestamp"): "ual_value",
    ("unified_audit_log", "first_timestamp_utc"): "ual_value",
    ("unified_audit_log", "inbox_rule_count"): "ual_value",
    ("unified_audit_log", "inbox_rule_names"): "ual_value",
    ("unified_audit_log", "inbox_rule_operation_count"): "ual_value",
    ("unified_audit_log", "inbox_rules"): "ual_value",
    ("unified_audit_log", "ip_addresses"): "ual_value",
    ("unified_audit_log", "ip_count"): "ual_value",
    ("unified_audit_log", "ips"): "ual_value",
    ("unified_audit_log", "last_creation_date"): "ual_value",
    ("unified_audit_log", "last_creation_date_utc"): "ual_value",
    ("unified_audit_log", "last_creation_time"): "ual_value",
    ("unified_audit_log", "last_creation_time_utc"): "ual_value",
    ("unified_audit_log", "last_event_time"): "ual_value",
    ("unified_audit_log", "last_event_time_utc"): "ual_value",
    ("unified_audit_log", "last_record_time"): "ual_value",
    ("unified_audit_log", "last_record_time_utc"): "ual_value",
    ("unified_audit_log", "last_timestamp"): "ual_value",
    ("unified_audit_log", "last_timestamp_utc"): "ual_value",
    ("unified_audit_log", "latest_creation_date"): "ual_value",
    ("unified_audit_log", "latest_creation_date_utc"): "ual_value",
    ("unified_audit_log", "latest_event_time"): "ual_value",
    ("unified_audit_log", "latest_event_time_utc"): "ual_value",
    ("unified_audit_log", "latest_timestamp"): "ual_value",
    ("unified_audit_log", "login_failure_count"): "ual_value",
    ("unified_audit_log", "mail_items_accessed_count"): "ual_value",
    ("unified_audit_log", "mail_items_accessed_events"): "ual_value",
    ("unified_audit_log", "mail_items_accessed_record_count"): "ual_value",
    ("unified_audit_log", "mail_items_accessed_user_ids"): "ual_value",
    ("unified_audit_log", "mail_items_accessed_users"): "ual_value",
    ("unified_audit_log", "mailbox_rule_names"): "ual_value",
    ("unified_audit_log", "mailitemsaccessed_count"): "ual_value",
    ("unified_audit_log", "most_common_operation"): "ual_value",
    ("unified_audit_log", "most_frequent_operation"): "ual_value",
    ("unified_audit_log", "new_inbox_rule_count"): "ual_value",
    ("unified_audit_log", "new_inbox_rule_names"): "ual_value",
    ("unified_audit_log", "new_inbox_rules"): "ual_value",
    ("unified_audit_log", "new_inboxrule_names"): "ual_value",
    ("unified_audit_log", "num_records"): "ual_value",
    ("unified_audit_log", "number_of_records"): "ual_value",
    ("unified_audit_log", "operation_count"): "ual_value",
    ("unified_audit_log", "operation_counts"): "ual_value",
    ("unified_audit_log", "operation_histogram"): "ual_value",
    ("unified_audit_log", "operation_list"): "ual_value",
    ("unified_audit_log", "operation_names"): "ual_value",
    ("unified_audit_log", "operation_set"): "ual_value",
    ("unified_audit_log", "operations"): "ual_value",
    ("unified_audit_log", "operations_counts"): "ual_value",
    ("unified_audit_log", "record_count"): "ual_value",
    ("unified_audit_log", "record_type_ids"): "ual_value",
    ("unified_audit_log", "record_types"): "ual_value",
    ("unified_audit_log", "records_count"): "ual_value",
    ("unified_audit_log", "result_status_values"): "ual_value",
    ("unified_audit_log", "result_statuses"): "ual_value",
    ("unified_audit_log", "row_count"): "ual_value",
    ("unified_audit_log", "rule_names"): "ual_value",
    ("unified_audit_log", "source_ips"): "ual_value",
    ("unified_audit_log", "top_operation"): "ual_value",
    ("unified_audit_log", "total_records"): "ual_value",
    ("unified_audit_log", "unique_client_ip_count"): "ual_value",
    ("unified_audit_log", "unique_client_ips"): "ual_value",
    ("unified_audit_log", "unique_ip_count"): "ual_value",
    ("unified_audit_log", "unique_ips"): "ual_value",
    ("unified_audit_log", "unique_operation_count"): "ual_value",
    ("unified_audit_log", "unique_operations"): "ual_value",
    ("unified_audit_log", "unique_record_types"): "ual_value",
    ("unified_audit_log", "unique_user_agents"): "ual_value",
    ("unified_audit_log", "unique_user_count"): "ual_value",
    ("unified_audit_log", "unique_user_ids"): "ual_value",
    ("unified_audit_log", "unique_users"): "ual_value",
    ("unified_audit_log", "unique_workloads"): "ual_value",
    ("unified_audit_log", "user_agents"): "ual_value",
    ("unified_audit_log", "user_count"): "ual_value",
    ("unified_audit_log", "user_id_count"): "ual_value",
    ("unified_audit_log", "user_ids"): "ual_value",
    ("unified_audit_log", "user_login_failed_count"): "ual_value",
    ("unified_audit_log", "user_names"): "ual_value",
    ("unified_audit_log", "user_set"): "ual_value",
    ("unified_audit_log", "userids"): "ual_value",
    ("unified_audit_log", "users"): "ual_value",
    ("unified_audit_log", "workload_names"): "ual_value",
    ("unified_audit_log", "workloads"): "ual_value",
    # entra_signin
    ("entra_signin", "app_display_names"): "entra_value",
    ("entra_signin", "app_names"): "entra_value",
    ("entra_signin", "application_names"): "entra_value",
    ("entra_signin", "applications"): "entra_value",
    ("entra_signin", "apps"): "entra_value",
    ("entra_signin", "cities"): "entra_value",
    ("entra_signin", "client_app_used"): "entra_value",
    ("entra_signin", "client_apps"): "entra_value",
    ("entra_signin", "client_apps_used"): "entra_value",
    ("entra_signin", "client_ips"): "entra_value",
    ("entra_signin", "conditional_access_status"): "entra_value",
    ("entra_signin", "conditional_access_statuses"): "entra_value",
    ("entra_signin", "countries"): "entra_value",
    ("entra_signin", "countries_or_regions"): "entra_value",
    ("entra_signin", "country_codes"): "entra_value",
    ("entra_signin", "distinct_ip_count"): "entra_value",
    ("entra_signin", "distinct_ips"): "entra_value",
    ("entra_signin", "earliest_created_date_time"): "entra_value",
    ("entra_signin", "earliest_event_time"): "entra_value",
    ("entra_signin", "earliest_event_time_utc"): "entra_value",
    ("entra_signin", "entry_count"): "entra_value",
    ("entra_signin", "error_codes"): "entra_value",
    ("entra_signin", "event_count"): "entra_value",
    ("entra_signin", "failed_count"): "entra_value",
    ("entra_signin", "failed_ip_addresses"): "entra_value",
    ("entra_signin", "failed_ips"): "entra_value",
    ("entra_signin", "failed_login_count"): "entra_value",
    ("entra_signin", "failed_logon_count"): "entra_value",
    ("entra_signin", "failed_sign_in_count"): "entra_value",
    ("entra_signin", "failed_sign_in_ips"): "entra_value",
    ("entra_signin", "failed_signin_count"): "entra_value",
    ("entra_signin", "failed_signin_ips"): "entra_value",
    ("entra_signin", "failed_signins"): "entra_value",
    ("entra_signin", "failed_upns"): "entra_value",
    ("entra_signin", "failed_user_principal_names"): "entra_value",
    ("entra_signin", "failed_users"): "entra_value",
    ("entra_signin", "failure_count"): "entra_value",
    ("entra_signin", "failure_ips"): "entra_value",
    ("entra_signin", "first_created_date_time"): "entra_value",
    ("entra_signin", "first_created_date_time_utc"): "entra_value",
    ("entra_signin", "first_event_time"): "entra_value",
    ("entra_signin", "first_event_time_utc"): "entra_value",
    ("entra_signin", "first_sign_in_time"): "entra_value",
    ("entra_signin", "first_sign_in_time_utc"): "entra_value",
    ("entra_signin", "first_signin_time"): "entra_value",
    ("entra_signin", "first_signin_time_utc"): "entra_value",
    ("entra_signin", "first_timestamp"): "entra_value",
    ("entra_signin", "first_timestamp_utc"): "entra_value",
    ("entra_signin", "ip_address_count"): "entra_value",
    ("entra_signin", "ip_addresses"): "entra_value",
    ("entra_signin", "ip_count"): "entra_value",
    ("entra_signin", "ip_set"): "entra_value",
    ("entra_signin", "ips"): "entra_value",
    ("entra_signin", "last_created_date_time"): "entra_value",
    ("entra_signin", "last_created_date_time_utc"): "entra_value",
    ("entra_signin", "last_event_time"): "entra_value",
    ("entra_signin", "last_event_time_utc"): "entra_value",
    ("entra_signin", "last_sign_in_time"): "entra_value",
    ("entra_signin", "last_sign_in_time_utc"): "entra_value",
    ("entra_signin", "last_signin_time"): "entra_value",
    ("entra_signin", "last_signin_time_utc"): "entra_value",
    ("entra_signin", "last_timestamp"): "entra_value",
    ("entra_signin", "last_timestamp_utc"): "entra_value",
    ("entra_signin", "latest_created_date_time"): "entra_value",
    ("entra_signin", "latest_event_time"): "entra_value",
    ("entra_signin", "latest_event_time_utc"): "entra_value",
    ("entra_signin", "location_cities"): "entra_value",
    ("entra_signin", "location_countries"): "entra_value",
    ("entra_signin", "location_set"): "entra_value",
    ("entra_signin", "locations"): "entra_value",
    ("entra_signin", "most_failed_ip"): "entra_value",
    ("entra_signin", "number_of_records"): "entra_value",
    ("entra_signin", "record_count"): "entra_value",
    ("entra_signin", "records_count"): "entra_value",
    ("entra_signin", "row_count"): "entra_value",
    ("entra_signin", "sign_in_count"): "entra_value",
    ("entra_signin", "sign_in_error_codes"): "entra_value",
    ("entra_signin", "sign_in_failure_count"): "entra_value",
    ("entra_signin", "signin_count"): "entra_value",
    ("entra_signin", "signin_error_codes"): "entra_value",
    ("entra_signin", "signin_failure_count"): "entra_value",
    ("entra_signin", "source_ips"): "entra_value",
    ("entra_signin", "status_error_codes"): "entra_value",
    ("entra_signin", "success_count"): "entra_value",
    ("entra_signin", "successful_login_count"): "entra_value",
    ("entra_signin", "successful_sign_in_count"): "entra_value",
    ("entra_signin", "successful_signin_count"): "entra_value",
    ("entra_signin", "top_failed_ip"): "entra_value",
    ("entra_signin", "top_failure_ip"): "entra_value",
    ("entra_signin", "total_records"): "entra_value",
    ("entra_signin", "total_sign_ins"): "entra_value",
    ("entra_signin", "total_signins"): "entra_value",
    ("entra_signin", "unique_error_codes"): "entra_value",
    ("entra_signin", "unique_ip_addresses"): "entra_value",
    ("entra_signin", "unique_ip_count"): "entra_value",
    ("entra_signin", "unique_ips"): "entra_value",
    ("entra_signin", "unique_locations"): "entra_value",
    ("entra_signin", "unique_users"): "entra_value",
    ("entra_signin", "upns"): "entra_value",
    ("entra_signin", "user_ids"): "entra_value",
    ("entra_signin", "user_names"): "entra_value",
    ("entra_signin", "user_principal_names"): "entra_value",
    ("entra_signin", "usernames"): "entra_value",
    ("entra_signin", "userprincipalnames"): "entra_value",
    ("entra_signin", "users"): "entra_value",
    # cloudtrail
    ("cloudtrail", "access_denied_count"): "cloudtrail_value",
    ("cloudtrail", "access_key_ids"): "cloudtrail_value",
    ("cloudtrail", "account_ids"): "cloudtrail_value",
    ("cloudtrail", "api_calls"): "cloudtrail_value",
    ("cloudtrail", "api_names"): "cloudtrail_value",
    ("cloudtrail", "arns"): "cloudtrail_value",
    ("cloudtrail", "aws_account_ids"): "cloudtrail_value",
    ("cloudtrail", "aws_regions"): "cloudtrail_value",
    ("cloudtrail", "console_login_failure_count"): "cloudtrail_value",
    ("cloudtrail", "counts_by_event_name"): "cloudtrail_value",
    ("cloudtrail", "distinct_event_name_count"): "cloudtrail_value",
    ("cloudtrail", "distinct_event_names"): "cloudtrail_value",
    ("cloudtrail", "distinct_source_ips"): "cloudtrail_value",
    ("cloudtrail", "earliest_event_time"): "cloudtrail_value",
    ("cloudtrail", "earliest_event_time_utc"): "cloudtrail_value",
    ("cloudtrail", "entry_count"): "cloudtrail_value",
    ("cloudtrail", "error_codes"): "cloudtrail_value",
    ("cloudtrail", "error_count"): "cloudtrail_value",
    ("cloudtrail", "error_event_count"): "cloudtrail_value",
    ("cloudtrail", "event_count"): "cloudtrail_value",
    ("cloudtrail", "event_counts"): "cloudtrail_value",
    ("cloudtrail", "event_name_count"): "cloudtrail_value",
    ("cloudtrail", "event_name_counts"): "cloudtrail_value",
    ("cloudtrail", "event_name_set"): "cloudtrail_value",
    ("cloudtrail", "event_names"): "cloudtrail_value",
    ("cloudtrail", "event_sources"): "cloudtrail_value",
    ("cloudtrail", "event_version_set"): "cloudtrail_value",
    ("cloudtrail", "event_versions"): "cloudtrail_value",
    ("cloudtrail", "events_count"): "cloudtrail_value",
    ("cloudtrail", "failed_api_call_count"): "cloudtrail_value",
    ("cloudtrail", "failed_console_login_count"): "cloudtrail_value",
    ("cloudtrail", "failed_console_logins"): "cloudtrail_value",
    ("cloudtrail", "failed_event_count"): "cloudtrail_value",
    ("cloudtrail", "failed_login_count"): "cloudtrail_value",
    ("cloudtrail", "first_event_time"): "cloudtrail_value",
    ("cloudtrail", "first_event_time_utc"): "cloudtrail_value",
    ("cloudtrail", "first_record_time"): "cloudtrail_value",
    ("cloudtrail", "first_record_time_utc"): "cloudtrail_value",
    ("cloudtrail", "first_timestamp"): "cloudtrail_value",
    ("cloudtrail", "first_timestamp_utc"): "cloudtrail_value",
    ("cloudtrail", "iam_user_names"): "cloudtrail_value",
    ("cloudtrail", "identity_types"): "cloudtrail_value",
    ("cloudtrail", "ip_addresses"): "cloudtrail_value",
    ("cloudtrail", "ip_count"): "cloudtrail_value",
    ("cloudtrail", "ips"): "cloudtrail_value",
    ("cloudtrail", "last_event_time"): "cloudtrail_value",
    ("cloudtrail", "last_event_time_utc"): "cloudtrail_value",
    ("cloudtrail", "last_record_time"): "cloudtrail_value",
    ("cloudtrail", "last_record_time_utc"): "cloudtrail_value",
    ("cloudtrail", "last_timestamp"): "cloudtrail_value",
    ("cloudtrail", "last_timestamp_utc"): "cloudtrail_value",
    ("cloudtrail", "latest_event_time"): "cloudtrail_value",
    ("cloudtrail", "latest_event_time_utc"): "cloudtrail_value",
    ("cloudtrail", "most_common_event_name"): "cloudtrail_value",
    ("cloudtrail", "most_frequent_event_name"): "cloudtrail_value",
    ("cloudtrail", "num_records"): "cloudtrail_value",
    ("cloudtrail", "number_of_records"): "cloudtrail_value",
    ("cloudtrail", "principal_arns"): "cloudtrail_value",
    ("cloudtrail", "principal_types"): "cloudtrail_value",
    ("cloudtrail", "public_source_ips"): "cloudtrail_value",
    ("cloudtrail", "recipient_account_ids"): "cloudtrail_value",
    ("cloudtrail", "record_count"): "cloudtrail_value",
    ("cloudtrail", "records_count"): "cloudtrail_value",
    ("cloudtrail", "region_set"): "cloudtrail_value",
    ("cloudtrail", "regions"): "cloudtrail_value",
    ("cloudtrail", "row_count"): "cloudtrail_value",
    ("cloudtrail", "service_names"): "cloudtrail_value",
    ("cloudtrail", "services"): "cloudtrail_value",
    ("cloudtrail", "source_ip_address_set"): "cloudtrail_value",
    ("cloudtrail", "source_ip_addresses"): "cloudtrail_value",
    ("cloudtrail", "source_ip_addresses_only"): "cloudtrail_value",
    ("cloudtrail", "source_ip_count"): "cloudtrail_value",
    ("cloudtrail", "source_ips"): "cloudtrail_value",
    ("cloudtrail", "source_ips_only"): "cloudtrail_value",
    ("cloudtrail", "src_ips"): "cloudtrail_value",
    ("cloudtrail", "top_event_name"): "cloudtrail_value",
    ("cloudtrail", "total_records"): "cloudtrail_value",
    ("cloudtrail", "unique_error_codes"): "cloudtrail_value",
    ("cloudtrail", "unique_event_name_count"): "cloudtrail_value",
    ("cloudtrail", "unique_event_names"): "cloudtrail_value",
    ("cloudtrail", "unique_event_sources"): "cloudtrail_value",
    ("cloudtrail", "unique_regions"): "cloudtrail_value",
    ("cloudtrail", "unique_source_ip_count"): "cloudtrail_value",
    ("cloudtrail", "unique_source_ips"): "cloudtrail_value",
    ("cloudtrail", "unique_user_agents"): "cloudtrail_value",
    ("cloudtrail", "user_agents"): "cloudtrail_value",
    ("cloudtrail", "user_arns"): "cloudtrail_value",
    ("cloudtrail", "user_identity_access_key_ids"): "cloudtrail_value",
    ("cloudtrail", "user_identity_arns"): "cloudtrail_value",
    ("cloudtrail", "user_identity_types"): "cloudtrail_value",
    ("cloudtrail", "user_identity_user_names"): "cloudtrail_value",
    ("cloudtrail", "user_names"): "cloudtrail_value",
    ("cloudtrail", "usernames"): "cloudtrail_value",
    ("cloudtrail", "users"): "cloudtrail_value",
    # okta
    ("okta", "actor_alternate_ids"): "okta_value",
    ("okta", "actor_alternateids"): "okta_value",
    ("okta", "actor_display_names"): "okta_value",
    ("okta", "actor_ids"): "okta_value",
    ("okta", "actors"): "okta_value",
    ("okta", "alternate_ids"): "okta_value",
    ("okta", "client_countries"): "okta_value",
    ("okta", "client_ip_addresses"): "okta_value",
    ("okta", "client_ip_count"): "okta_value",
    ("okta", "client_ips"): "okta_value",
    ("okta", "client_user_agents"): "okta_value",
    ("okta", "countries"): "okta_value",
    ("okta", "counts_by_event_type"): "okta_value",
    ("okta", "display_messages"): "okta_value",
    ("okta", "display_names"): "okta_value",
    ("okta", "distinct_event_types"): "okta_value",
    ("okta", "distinct_ips"): "okta_value",
    ("okta", "earliest_event_time"): "okta_value",
    ("okta", "earliest_published"): "okta_value",
    ("okta", "earliest_published_utc"): "okta_value",
    ("okta", "entry_count"): "okta_value",
    ("okta", "event_count"): "okta_value",
    ("okta", "event_type_count"): "okta_value",
    ("okta", "event_type_counts"): "okta_value",
    ("okta", "event_type_set"): "okta_value",
    ("okta", "event_types"): "okta_value",
    ("okta", "events_count"): "okta_value",
    ("okta", "failed_actor_alternate_ids"): "okta_value",
    ("okta", "failed_actors"): "okta_value",
    ("okta", "failed_authentication_count"): "okta_value",
    ("okta", "failed_client_ips"): "okta_value",
    ("okta", "failed_count"): "okta_value",
    ("okta", "failed_event_count"): "okta_value",
    ("okta", "failed_ips"): "okta_value",
    ("okta", "failed_login_count"): "okta_value",
    ("okta", "failed_logon_count"): "okta_value",
    ("okta", "failed_sign_in_count"): "okta_value",
    ("okta", "failed_signin_count"): "okta_value",
    ("okta", "failed_users"): "okta_value",
    ("okta", "failure_count"): "okta_value",
    ("okta", "failure_ips"): "okta_value",
    ("okta", "failure_reasons"): "okta_value",
    ("okta", "failures_count"): "okta_value",
    ("okta", "first_event_time"): "okta_value",
    ("okta", "first_event_time_utc"): "okta_value",
    ("okta", "first_published"): "okta_value",
    ("okta", "first_published_utc"): "okta_value",
    ("okta", "first_timestamp"): "okta_value",
    ("okta", "first_timestamp_utc"): "okta_value",
    ("okta", "geo_countries"): "okta_value",
    ("okta", "ip_addresses"): "okta_value",
    ("okta", "ip_count"): "okta_value",
    ("okta", "ips"): "okta_value",
    ("okta", "last_event_time"): "okta_value",
    ("okta", "last_event_time_utc"): "okta_value",
    ("okta", "last_published"): "okta_value",
    ("okta", "last_published_utc"): "okta_value",
    ("okta", "last_timestamp"): "okta_value",
    ("okta", "last_timestamp_utc"): "okta_value",
    ("okta", "latest_event_time"): "okta_value",
    ("okta", "latest_published"): "okta_value",
    ("okta", "latest_published_utc"): "okta_value",
    ("okta", "login_failure_count"): "okta_value",
    ("okta", "messages"): "okta_value",
    ("okta", "most_common_event_type"): "okta_value",
    ("okta", "most_frequent_event_type"): "okta_value",
    ("okta", "num_records"): "okta_value",
    ("okta", "number_of_events"): "okta_value",
    ("okta", "outcome_failure_count"): "okta_value",
    ("okta", "outcome_reasons"): "okta_value",
    ("okta", "outcome_results"): "okta_value",
    ("okta", "outcomes"): "okta_value",
    ("okta", "raw_user_agents"): "okta_value",
    ("okta", "record_count"): "okta_value",
    ("okta", "records_count"): "okta_value",
    ("okta", "results"): "okta_value",
    ("okta", "row_count"): "okta_value",
    ("okta", "severities"): "okta_value",
    ("okta", "severity_levels"): "okta_value",
    ("okta", "source_ips"): "okta_value",
    ("okta", "success_count"): "okta_value",
    ("okta", "successful_event_count"): "okta_value",
    ("okta", "target_alternate_ids"): "okta_value",
    ("okta", "target_ids"): "okta_value",
    ("okta", "targets"): "okta_value",
    ("okta", "top_event_type"): "okta_value",
    ("okta", "total_events"): "okta_value",
    ("okta", "unique_actors"): "okta_value",
    ("okta", "unique_event_type_count"): "okta_value",
    ("okta", "unique_event_types"): "okta_value",
    ("okta", "unique_ip_count"): "okta_value",
    ("okta", "unique_ips"): "okta_value",
    ("okta", "unique_outcomes"): "okta_value",
    ("okta", "user_agents"): "okta_value",
    ("okta", "user_names"): "okta_value",
    ("okta", "usernames"): "okta_value",
    ("okta", "users"): "okta_value",
}
