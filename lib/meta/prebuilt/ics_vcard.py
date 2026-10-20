"""iCalendar (RFC 5545) / vCard (RFC 6350 / 2426) property fields (prebuilt, SPECULATIVE -- never GM-asked yet).

Pure text parse, no zoneinfo/dateutil: decode (UTF-8, BOM stripped; latin-1 fallback), unfold (CRLF/LF followed by
one space or tab is removed), split each content line `NAME;PARAM=..;P="a:b":value` on the FIRST colon outside a
double-quoted parameter value; NAME = text before the first ';', uppercased; group prefixes (`item1.EMAIL`) dropped.
Text values (SUMMARY, LOCATION, FN, N, ORG, UID) are unescaped (`\\,` `\\;` `\\n`/`\\N` `\\\\`); URI-ish values
(ORGANIZER, ATTENDEE, EMAIL, TEL) and DTSTART/DTEND stay verbatim (`mailto:` kept).
ics: the file must open with BEGIN:VCALENDAR; event fields come from the FIRST VEVENT; method / prodid from the
VCALENDAR level; event_count = number of VEVENT components; attendees = the first VEVENT's ATTENDEE values (JSON list,
stored order). dtstart / dtend = the stored value verbatim (e.g. 20261020T140000Z, 20261020T090000, 20261020);
*_utc / *_iso8601 = ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' ONLY when the stored value ends in Z (a TZID/floating time would need tz
data -> None = cannot answer).
vcard (vcf): the file must open with BEGIN:VCARD; fields from the FIRST card; email = first EMAIL, emails = all
EMAIL values (stored order), tel = first TEL, org = ORG unescaped (components keep their ';' separators, trailing
empty components dropped), n = N unescaped as stored. Wrong format / property absent -> "none"."""
import re

FIELDS = {
    ("ics", "uid"): "ics_value",
    ("ics", "event_uid"): "ics_value",
    ("ics", "vevent_uid"): "ics_value",
    ("ics", "organizer"): "ics_value",
    ("ics", "event_organizer"): "ics_value",
    ("ics", "attendees"): "ics_value",
    ("ics", "attendee_list"): "ics_value",
    ("ics", "event_attendees"): "ics_value",
    ("ics", "dtstart"): "ics_value",
    ("ics", "event_dtstart"): "ics_value",
    ("ics", "dtend"): "ics_value",
    ("ics", "event_dtend"): "ics_value",
    ("ics", "dtstart_utc"): "ics_value",
    ("ics", "dtend_utc"): "ics_value",
    ("ics", "event_dtstart_utc"): "ics_value",
    ("ics", "event_dtend_utc"): "ics_value",
    ("ics", "summary"): "ics_value",
    ("ics", "event_summary"): "ics_value",
    ("ics", "location"): "ics_value",
    ("ics", "event_location"): "ics_value",
    ("ics", "method"): "ics_value",
    ("ics", "calendar_method"): "ics_value",
    ("ics", "prodid"): "ics_value",
    ("ics", "calendar_prodid"): "ics_value",
    ("ics", "product_id"): "ics_value",
    ("ics", "event_count"): "ics_value",
    ("ics", "vevent_count"): "ics_value",
    ("ics", "events_count"): "ics_value",
    ("ics", "number_of_events"): "ics_value",
    ("ics", "attendee_count"): "ics_value",
    ("ical", "uid"): "ics_value",
    ("ical", "event_uid"): "ics_value",
    ("ical", "vevent_uid"): "ics_value",
    ("ical", "organizer"): "ics_value",
    ("ical", "event_organizer"): "ics_value",
    ("ical", "attendees"): "ics_value",
    ("ical", "attendee_list"): "ics_value",
    ("ical", "event_attendees"): "ics_value",
    ("ical", "dtstart"): "ics_value",
    ("ical", "event_dtstart"): "ics_value",
    ("ical", "dtend"): "ics_value",
    ("ical", "event_dtend"): "ics_value",
    ("ical", "dtstart_utc"): "ics_value",
    ("ical", "dtend_utc"): "ics_value",
    ("ical", "event_dtstart_utc"): "ics_value",
    ("ical", "event_dtend_utc"): "ics_value",
    ("ical", "summary"): "ics_value",
    ("ical", "event_summary"): "ics_value",
    ("ical", "location"): "ics_value",
    ("ical", "event_location"): "ics_value",
    ("ical", "method"): "ics_value",
    ("ical", "calendar_method"): "ics_value",
    ("ical", "prodid"): "ics_value",
    ("ical", "calendar_prodid"): "ics_value",
    ("ical", "product_id"): "ics_value",
    ("ical", "event_count"): "ics_value",
    ("ical", "vevent_count"): "ics_value",
    ("ical", "events_count"): "ics_value",
    ("ical", "number_of_events"): "ics_value",
    ("ical", "attendee_count"): "ics_value",
    ("icalendar", "uid"): "ics_value",
    ("icalendar", "event_uid"): "ics_value",
    ("icalendar", "vevent_uid"): "ics_value",
    ("icalendar", "organizer"): "ics_value",
    ("icalendar", "event_organizer"): "ics_value",
    ("icalendar", "attendees"): "ics_value",
    ("icalendar", "attendee_list"): "ics_value",
    ("icalendar", "event_attendees"): "ics_value",
    ("icalendar", "dtstart"): "ics_value",
    ("icalendar", "event_dtstart"): "ics_value",
    ("icalendar", "dtend"): "ics_value",
    ("icalendar", "event_dtend"): "ics_value",
    ("icalendar", "dtstart_utc"): "ics_value",
    ("icalendar", "dtend_utc"): "ics_value",
    ("icalendar", "event_dtstart_utc"): "ics_value",
    ("icalendar", "event_dtend_utc"): "ics_value",
    ("icalendar", "summary"): "ics_value",
    ("icalendar", "event_summary"): "ics_value",
    ("icalendar", "location"): "ics_value",
    ("icalendar", "event_location"): "ics_value",
    ("icalendar", "method"): "ics_value",
    ("icalendar", "calendar_method"): "ics_value",
    ("icalendar", "prodid"): "ics_value",
    ("icalendar", "calendar_prodid"): "ics_value",
    ("icalendar", "product_id"): "ics_value",
    ("icalendar", "event_count"): "ics_value",
    ("icalendar", "vevent_count"): "ics_value",
    ("icalendar", "events_count"): "ics_value",
    ("icalendar", "number_of_events"): "ics_value",
    ("icalendar", "attendee_count"): "ics_value",
    ("calendar", "uid"): "ics_value",
    ("calendar", "event_uid"): "ics_value",
    ("calendar", "vevent_uid"): "ics_value",
    ("calendar", "organizer"): "ics_value",
    ("calendar", "event_organizer"): "ics_value",
    ("calendar", "attendees"): "ics_value",
    ("calendar", "attendee_list"): "ics_value",
    ("calendar", "event_attendees"): "ics_value",
    ("calendar", "dtstart"): "ics_value",
    ("calendar", "event_dtstart"): "ics_value",
    ("calendar", "dtend"): "ics_value",
    ("calendar", "event_dtend"): "ics_value",
    ("calendar", "dtstart_utc"): "ics_value",
    ("calendar", "dtend_utc"): "ics_value",
    ("calendar", "event_dtstart_utc"): "ics_value",
    ("calendar", "event_dtend_utc"): "ics_value",
    ("calendar", "summary"): "ics_value",
    ("calendar", "event_summary"): "ics_value",
    ("calendar", "location"): "ics_value",
    ("calendar", "event_location"): "ics_value",
    ("calendar", "method"): "ics_value",
    ("calendar", "calendar_method"): "ics_value",
    ("calendar", "prodid"): "ics_value",
    ("calendar", "calendar_prodid"): "ics_value",
    ("calendar", "product_id"): "ics_value",
    ("calendar", "event_count"): "ics_value",
    ("calendar", "vevent_count"): "ics_value",
    ("calendar", "events_count"): "ics_value",
    ("calendar", "number_of_events"): "ics_value",
    ("calendar", "attendee_count"): "ics_value",
    ("ics", "dtstart_iso8601"): "ics_value",
    ("ics", "dtend_iso8601"): "ics_value",
    ("ical", "dtstart_iso8601"): "ics_value",
    ("ical", "dtend_iso8601"): "ics_value",
    ("icalendar", "dtstart_iso8601"): "ics_value",
    ("icalendar", "dtend_iso8601"): "ics_value",
    ("calendar", "dtstart_iso8601"): "ics_value",
    ("calendar", "dtend_iso8601"): "ics_value",
    ("vcard", "fn"): "vcard_value",
    ("vcard", "full_name"): "vcard_value",
    ("vcard", "formatted_name"): "vcard_value",
    ("vcard", "n"): "vcard_value",
    ("vcard", "structured_name"): "vcard_value",
    ("vcard", "name"): "vcard_value",
    ("vcard", "email"): "vcard_value",
    ("vcard", "first_email"): "vcard_value",
    ("vcard", "email_address"): "vcard_value",
    ("vcard", "emails"): "vcard_value",
    ("vcard", "email_addresses"): "vcard_value",
    ("vcard", "email_list"): "vcard_value",
    ("vcard", "tel"): "vcard_value",
    ("vcard", "telephone"): "vcard_value",
    ("vcard", "phone"): "vcard_value",
    ("vcard", "phone_number"): "vcard_value",
    ("vcard", "org"): "vcard_value",
    ("vcard", "organization"): "vcard_value",
    ("vcard", "organisation"): "vcard_value",
    ("vcard", "uid"): "vcard_value",
    ("vcard", "version"): "vcard_value",
    ("vcard", "vcard_version"): "vcard_value",
    ("vcard", "email_count"): "vcard_value",
    ("vcf", "fn"): "vcard_value",
    ("vcf", "full_name"): "vcard_value",
    ("vcf", "formatted_name"): "vcard_value",
    ("vcf", "n"): "vcard_value",
    ("vcf", "structured_name"): "vcard_value",
    ("vcf", "name"): "vcard_value",
    ("vcf", "email"): "vcard_value",
    ("vcf", "first_email"): "vcard_value",
    ("vcf", "email_address"): "vcard_value",
    ("vcf", "emails"): "vcard_value",
    ("vcf", "email_addresses"): "vcard_value",
    ("vcf", "email_list"): "vcard_value",
    ("vcf", "tel"): "vcard_value",
    ("vcf", "telephone"): "vcard_value",
    ("vcf", "phone"): "vcard_value",
    ("vcf", "phone_number"): "vcard_value",
    ("vcf", "org"): "vcard_value",
    ("vcf", "organization"): "vcard_value",
    ("vcf", "organisation"): "vcard_value",
    ("vcf", "uid"): "vcard_value",
    ("vcf", "version"): "vcard_value",
    ("vcf", "vcard_version"): "vcard_value",
    ("vcf", "email_count"): "vcard_value",
}

_FOLD = re.compile(r"\r?\n[ \t]")
_ESC = re.compile(r"\\(.)", re.S)


def _text(b):
    if not b:
        return None
    b = bytes(b)
    if b.startswith(b"\xef\xbb\xbf"):
        b = b[3:]
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("latin-1")


def _split(line):
    """(NAME, params-text, value) of one unfolded content line, or None."""
    q = False
    for i, c in enumerate(line):
        if c == '"':
            q = not q
        elif c == ":" and not q:
            head, val = line[:i], line[i + 1:]
            name, _, params = head.partition(";")
            name = name.strip().upper()
            if "." in name:
                name = name.rsplit(".", 1)[1]
            return (name, params, val) if name else None
    return None


def _unescape(v):
    return _ESC.sub(lambda m: "\n" if m.group(1) in "nN" else m.group(1), v)


def parse(data, root):
    """[(component path tuple, NAME, value)] for a text whose first content line is BEGIN:<root>, or None."""
    t = _text(data)
    if t is None:
        return None
    t = _FOLD.sub("", t)
    out, stack = [], []
    for raw in re.split(r"\r?\n|\r", t):
        if not raw.strip():
            continue
        p = _split(raw)
        if p is None:
            if not stack:
                return None
            continue
        name, _, val = p
        if not stack and not (name == "BEGIN" and val.strip().upper() == root):
            return None
        if name == "BEGIN":
            stack.append(val.strip().upper())
            out.append((tuple(stack), "BEGIN", val))
        elif name == "END":
            if stack:
                stack.pop()
            if not stack:
                break
        else:
            out.append((tuple(stack), name, val))
    return out if out else None


def _iso_utc(v):
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z", v.strip())
    return "%s-%s-%sT%s:%s:%sZ" % m.groups() if m else None


def ics_value(data, ctx):
    try:
        return _ics(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- defensive: a hostile member never raises past the extractor
        return None


def _ics(data, f):
    if data is None:
        return None
    props = parse(data, "VCALENDAR")
    if props is None:
        return "none"
    f = re.sub(r"^(event|vevent|calendar)_", "", f)
    if f in ("method", "prodid", "product_id"):
        key = "PRODID" if f != "method" else "METHOD"
        for path, n, v in props:
            if path == ("VCALENDAR",) and n == key:
                return v.strip()
        return "none"
    events = [i for i, (path, n, v) in enumerate(props) if n == "BEGIN" and path == ("VCALENDAR", "VEVENT")]
    if f in ("count", "events_count", "number_of_events") or f.endswith("event_count"):
        return len(events)
    ev = []
    if events:
        start = events[0]
        for path, n, v in props[start + 1:]:
            if n == "BEGIN" and path == ("VCALENDAR", "VEVENT"):
                break
            if path == ("VCALENDAR", "VEVENT"):
                ev.append((n, v))
    if f in ("attendees", "attendee_list", "attendee_count"):
        lst = [v.strip() for n, v in ev if n == "ATTENDEE"]
        return len(lst) if f == "attendee_count" else (lst if lst else "none")
    key = {"uid": "UID", "organizer": "ORGANIZER", "summary": "SUMMARY", "location": "LOCATION",
           "dtstart": "DTSTART", "dtend": "DTEND", "dtstart_utc": "DTSTART", "dtend_utc": "DTEND",
           "dtstart_iso8601": "DTSTART", "dtend_iso8601": "DTEND"}.get(f)
    if key is None:
        return None
    val = next((v for n, v in ev if n == key), None)
    if val is None:
        return "none"
    if f.endswith(("_utc", "_iso8601")):
        return _iso_utc(val)
    if key in ("SUMMARY", "LOCATION", "UID"):
        return _unescape(val).strip()
    return val.strip()


def vcard_value(data, ctx):
    try:
        return _vcard(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001
        return None


def _vcard(data, f):
    if data is None:
        return None
    props = parse(data, "VCARD")
    if props is None:
        return "none"
    card = [(n, v) for path, n, v in props if path == ("VCARD",)]
    if f in ("emails", "email_addresses", "email_list", "email_count"):
        lst = [v.strip() for n, v in card if n == "EMAIL"]
        return len(lst) if f == "email_count" else (lst if lst else "none")
    key = {"fn": "FN", "full_name": "FN", "formatted_name": "FN", "n": "N", "structured_name": "N", "name": "N",
           "email": "EMAIL", "first_email": "EMAIL", "email_address": "EMAIL", "tel": "TEL", "telephone": "TEL",
           "phone": "TEL", "phone_number": "TEL", "org": "ORG", "organization": "ORG", "organisation": "ORG",
           "uid": "UID", "version": "VERSION", "vcard_version": "VERSION"}.get(f)
    if key is None:
        return None
    val = next((v for n, v in card if n == key), None)
    if val is None:
        return "none"
    if key == "ORG":
        return _unescape(val.strip().rstrip(";")) or "none"
    if key in ("FN", "N", "UID"):
        return _unescape(val).strip()
    return val.strip()
