"""Mobile app SQLite stores (prebuilt, SPECULATIVE): iOS sms.db / chat.db, iOS KnowledgeC.db, Android mmssms.db,
Android contacts2.db, WhatsApp msgstore.db. Same fields under fmt sqlite and the aliases ios / android / whatsapp.

Rows come from sqlite.py's stdlib b-tree walker via sqlite_browser._rows (rowid = stored order, columns named from the
CREATE TABLE sql, lowercased); the store is recognised by its tables/columns, not by the file name:
  iOS sms.db/chat.db  `message`(ROWID, text, date, is_from_me, service, handle_id) + `handle`(ROWID, id, service)
                      date = Apple Cocoa epoch (2001-01-01 UTC): NANOseconds when > 1e12 (iOS 11+), else seconds
  KnowledgeC.db       `ZOBJECT`(ZSTREAMNAME, ZVALUESTRING, ZSTARTDATE, ZENDDATE) -- `/app/inFocus` rows carry the
                      bundle id in ZVALUESTRING; dates = Cocoa seconds (float)
  Android mmssms.db   `sms`(address, date, type, body) -- date = unix ms; type 1 inbox (received) / 2 sent
  Android contacts2   `raw_contacts`(display_name, deleted) (+ `data`/`mimetypes` name rows as a fallback)
  WhatsApp msgstore   legacy `messages`(key_remote_jid, key_from_me, timestamp, data) -- timestamp = unix ms; the
                      placeholder row key_remote_jid '-1' is not a message. New schema: `message`(chat_row_id,
                      from_me, timestamp, text_data) + `chat`(jid_row_id) + `jid`(raw_string)
Generic message_count / first_message_utc / last_message_utc follow whichever store the file is (iMessage, WhatsApp,
then Android sms). Lists (*_ids / *_names / *_addresses / *_jids / services): de-duplicated and SORTED unless the
question asks for stored order ("order" in the question), then rowid order. Timestamps: ISO-8601 `YYYY-MM-DDTHH:MM:SSZ`
(second precision, truncated). Not "SQLite format 3\\0" (decoy / renamed impostor) or no such table -> "none";
unreadable -> None."""
import datetime
import re

from .sqlite import _MAGIC, _header, _schema
from .sqlite_browser import _list, _rows

FIELDS = {
    ("sqlite", "message_count"): "mobile_db_value",
    ("sqlite", "sent_message_count"): "mobile_db_value",
    ("sqlite", "received_message_count"): "mobile_db_value",
    ("sqlite", "from_me_count"): "mobile_db_value",
    ("sqlite", "first_message_utc"): "mobile_db_value",
    ("sqlite", "last_message_utc"): "mobile_db_value",
    ("sqlite", "earliest_message_utc"): "mobile_db_value",
    ("sqlite", "latest_message_utc"): "mobile_db_value",
    ("sqlite", "handle_ids"): "mobile_db_value",
    ("sqlite", "handle_count"): "mobile_db_value",
    ("sqlite", "services"): "mobile_db_value",
    ("sqlite", "message_services"): "mobile_db_value",
    ("sqlite", "chat_identifiers"): "mobile_db_value",
    ("sqlite", "app_bundle_ids"): "mobile_db_value",
    ("sqlite", "bundle_ids"): "mobile_db_value",
    ("sqlite", "app_usage_count"): "mobile_db_value",
    ("sqlite", "app_in_focus_count"): "mobile_db_value",
    ("sqlite", "first_app_usage_utc"): "mobile_db_value",
    ("sqlite", "last_app_usage_utc"): "mobile_db_value",
    ("sqlite", "stream_names"): "mobile_db_value",
    ("sqlite", "sms_count"): "mobile_db_value",
    ("sqlite", "sms_addresses"): "mobile_db_value",
    ("sqlite", "sms_sent_count"): "mobile_db_value",
    ("sqlite", "sms_inbox_count"): "mobile_db_value",
    ("sqlite", "sms_received_count"): "mobile_db_value",
    ("sqlite", "first_sms_utc"): "mobile_db_value",
    ("sqlite", "last_sms_utc"): "mobile_db_value",
    ("sqlite", "contact_display_names"): "mobile_db_value",
    ("sqlite", "display_names"): "mobile_db_value",
    ("sqlite", "contact_count"): "mobile_db_value",
    ("sqlite", "chat_jids"): "mobile_db_value",
    ("sqlite", "remote_jids"): "mobile_db_value",
    ("sqlite", "key_remote_jids"): "mobile_db_value",
    ("sqlite", "chat_count"): "mobile_db_value",
    ("ios", "message_count"): "mobile_db_value",
    ("ios", "sent_message_count"): "mobile_db_value",
    ("ios", "received_message_count"): "mobile_db_value",
    ("ios", "from_me_count"): "mobile_db_value",
    ("ios", "first_message_utc"): "mobile_db_value",
    ("ios", "last_message_utc"): "mobile_db_value",
    ("ios", "earliest_message_utc"): "mobile_db_value",
    ("ios", "latest_message_utc"): "mobile_db_value",
    ("ios", "handle_ids"): "mobile_db_value",
    ("ios", "handle_count"): "mobile_db_value",
    ("ios", "services"): "mobile_db_value",
    ("ios", "message_services"): "mobile_db_value",
    ("ios", "chat_identifiers"): "mobile_db_value",
    ("ios", "app_bundle_ids"): "mobile_db_value",
    ("ios", "bundle_ids"): "mobile_db_value",
    ("ios", "app_usage_count"): "mobile_db_value",
    ("ios", "app_in_focus_count"): "mobile_db_value",
    ("ios", "first_app_usage_utc"): "mobile_db_value",
    ("ios", "last_app_usage_utc"): "mobile_db_value",
    ("ios", "stream_names"): "mobile_db_value",
    ("android", "message_count"): "mobile_db_value",
    ("android", "sms_count"): "mobile_db_value",
    ("android", "sms_addresses"): "mobile_db_value",
    ("android", "sms_sent_count"): "mobile_db_value",
    ("android", "sms_inbox_count"): "mobile_db_value",
    ("android", "sms_received_count"): "mobile_db_value",
    ("android", "first_sms_utc"): "mobile_db_value",
    ("android", "last_sms_utc"): "mobile_db_value",
    ("android", "first_message_utc"): "mobile_db_value",
    ("android", "last_message_utc"): "mobile_db_value",
    ("android", "contact_display_names"): "mobile_db_value",
    ("android", "display_names"): "mobile_db_value",
    ("android", "contact_count"): "mobile_db_value",
    ("android", "chat_jids"): "mobile_db_value",
    ("whatsapp", "message_count"): "mobile_db_value",
    ("whatsapp", "sent_message_count"): "mobile_db_value",
    ("whatsapp", "received_message_count"): "mobile_db_value",
    ("whatsapp", "from_me_count"): "mobile_db_value",
    ("whatsapp", "first_message_utc"): "mobile_db_value",
    ("whatsapp", "last_message_utc"): "mobile_db_value",
    ("whatsapp", "earliest_message_utc"): "mobile_db_value",
    ("whatsapp", "latest_message_utc"): "mobile_db_value",
    ("whatsapp", "chat_jids"): "mobile_db_value",
    ("whatsapp", "remote_jids"): "mobile_db_value",
    ("whatsapp", "key_remote_jids"): "mobile_db_value",
    ("whatsapp", "chat_count"): "mobile_db_value",
}

_UNIX = datetime.datetime(1970, 1, 1)
_COCOA = datetime.datetime(2001, 1, 1)


def _iso(epoch, seconds):
    if not isinstance(seconds, (int, float)) or isinstance(seconds, bool) or seconds <= 0:
        return None
    try:
        return (epoch + datetime.timedelta(seconds=int(seconds))).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, ValueError):
        return None


def _imsg_secs(v):
    """iMessage message.date -> seconds since 2001: ns when > 1e12 (iOS 11+), else already seconds."""
    if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
        return None
    return v / 1e9 if v > 1e12 else v


def _ms_secs(v):
    if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
        return None
    return v / 1000.0


def _span(vals, epoch, latest):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "none"
    return _iso(epoch, max(vals) if latest else min(vals)) or "none"


def _cols(tables, name):
    r = tables.get(name)
    return set(re.findall(r"[\w$]+", (r[4] or "").lower())) if r else set()


def _kind(tables):
    """Message store of this file: 'imessage' / 'whatsapp' / 'whatsapp_new' / 'sms', or None."""
    mc = _cols(tables, "message")
    if "message" in tables and ("handle" in tables or "is_from_me" in mc):
        return "imessage"
    if "messages" in tables and "key_remote_jid" in _cols(tables, "messages"):
        return "whatsapp"
    if "message" in tables and "chat_row_id" in mc:
        return "whatsapp_new"
    if "sms" in tables:
        return "sms"
    return None


def _messages(b, h, tables, kind):
    """[(epoch, seconds_or_None, from_me_or_None)] of the store's real messages."""
    if kind == "imessage":
        return [(_COCOA, _imsg_secs(d.get("date")), d.get("is_from_me")) for d in _rows(b, h, tables, "message")]
    if kind == "whatsapp":
        return [(_UNIX, _ms_secs(d.get("timestamp")), d.get("key_from_me"))
                for d in _rows(b, h, tables, "messages") if d.get("key_remote_jid") not in (None, "-1")]
    if kind == "whatsapp_new":
        return [(_UNIX, _ms_secs(d.get("timestamp")), d.get("from_me"))
                for d in _rows(b, h, tables, "message") if d.get("chat_row_id") not in (None, -1)]
    if kind == "sms":
        return [(_UNIX, _ms_secs(d.get("date")), 1 if d.get("type") == 2 else 0 if d.get("type") == 1 else None)
                for d in _rows(b, h, tables, "sms")]
    return None


def _message_field(b, h, tables, f):
    kind = _kind(tables)
    msgs = _messages(b, h, tables, kind) if kind else None
    if msgs is None:
        return "none"
    if f == "message_count":
        return len(msgs)
    if f in ("sent_message_count", "from_me_count"):
        return sum(1 for m in msgs if m[2] == 1)
    if f == "received_message_count":
        return sum(1 for m in msgs if m[2] == 0)
    latest = f.startswith(("last_", "latest_"))
    return _span([m[1] for m in msgs], msgs[0][0] if msgs else _UNIX, latest)


def _imessage(b, h, tables, f, ordered):
    if f == "handle_count":
        return len(_rows(b, h, tables, "handle")) if "handle" in tables else "none"
    if f == "handle_ids":
        if "handle" not in tables:
            return "none"
        return _list([d.get("id") for d in _rows(b, h, tables, "handle")], ordered)
    if f == "chat_identifiers":
        if "chat" not in tables:
            return "none"
        return _list([d.get("chat_identifier") for d in _rows(b, h, tables, "chat")], ordered)
    # services: message.service values (iMessage / SMS), handle.service when the message table lacks the column
    if "message" in tables and "service" in _cols(tables, "message"):
        return _list([d.get("service") for d in _rows(b, h, tables, "message")], ordered)
    if "handle" in tables:
        return _list([d.get("service") for d in _rows(b, h, tables, "handle")], ordered)
    return "none"


def _knowledgec(b, h, tables, f, ordered):
    if "zobject" not in tables:
        return "none"
    recs = _rows(b, h, tables, "zobject")
    if f == "stream_names":
        return _list([d.get("zstreamname") for d in recs], ordered)
    focus = [d for d in recs if d.get("zstreamname") == "/app/inFocus"]
    if f in ("app_bundle_ids", "bundle_ids"):
        return _list([d.get("zvaluestring") for d in focus], ordered)
    if f in ("app_usage_count", "app_in_focus_count"):
        return len(focus)
    return _span([d.get("zstartdate") for d in focus], _COCOA, f.startswith("last_"))


def _sms(b, h, tables, f, ordered):
    if "sms" not in tables:
        return "none"
    recs = _rows(b, h, tables, "sms")
    if f == "sms_count":
        return len(recs)
    if f == "sms_addresses":
        return _list([d.get("address") for d in recs], ordered)
    if f == "sms_sent_count":
        return sum(1 for d in recs if d.get("type") == 2)
    if f in ("sms_inbox_count", "sms_received_count"):
        return sum(1 for d in recs if d.get("type") == 1)
    return _span([_ms_secs(d.get("date")) for d in recs], _UNIX, f.startswith("last_"))


def _contacts(b, h, tables, f, ordered):
    if "raw_contacts" not in tables:
        return "none"
    recs = [d for d in _rows(b, h, tables, "raw_contacts") if d.get("deleted") != 1]
    if f == "contact_count":
        return len(recs)
    names = [d.get("display_name") for d in recs]
    if not any(names) and "data" in tables and "mimetypes" in tables:
        mt = {d.get("_id"): d.get("mimetype") for d in _rows(b, h, tables, "mimetypes")}
        names = [d.get("data1") for d in _rows(b, h, tables, "data")
                 if mt.get(d.get("mimetype_id")) == "vnd.android.cursor.item/name"]
    return _list(names, ordered)


def _whatsapp(b, h, tables, f, ordered):
    if "messages" in tables and "key_remote_jid" in _cols(tables, "messages"):
        jids = [d.get("key_remote_jid") for d in _rows(b, h, tables, "messages")]
    elif "chat" in tables and "jid" in tables:
        raw = {d.get("_rowid"): d.get("raw_string") for d in _rows(b, h, tables, "jid")}
        jids = [raw.get(d.get("jid_row_id")) for d in _rows(b, h, tables, "chat")]
    else:
        return "none"
    jids = [j for j in jids if j not in (None, "", "-1")]
    vals = _list(jids, ordered)
    return len(vals) if f == "chat_count" else vals


def mobile_db_value(data, ctx):
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
        if f in ("message_count", "sent_message_count", "received_message_count", "from_me_count",
                 "first_message_utc", "last_message_utc", "earliest_message_utc", "latest_message_utc"):
            return _message_field(data, h, tables, f)
        if f in ("handle_ids", "handle_count", "services", "message_services", "chat_identifiers"):
            return _imessage(data, h, tables, f, ordered)
        if f in ("app_bundle_ids", "bundle_ids", "app_usage_count", "app_in_focus_count", "first_app_usage_utc",
                 "last_app_usage_utc", "stream_names"):
            return _knowledgec(data, h, tables, f, ordered)
        if f.startswith("sms_") or f in ("first_sms_utc", "last_sms_utc"):
            return _sms(data, h, tables, f, ordered)
        if f in ("contact_display_names", "display_names", "contact_count"):
            return _contacts(data, h, tables, f, ordered)
        if f in ("chat_jids", "remote_jids", "key_remote_jids", "chat_count"):
            return _whatsapp(data, h, tables, f, ordered)
        return None
    except Exception:  # noqa: BLE001
        return None
