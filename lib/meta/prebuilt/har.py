"""HAR 1.2 HTTP archives (browser DevTools / Playwright / Fiddler "save as HAR") (prebuilt, SPECULATIVE -- never
GM-asked yet). Pure json + urllib.parse; a gzip-wrapped .har is unwrapped first.

Shape (W3C HAR 1.2 draft): {"log": {"version", "creator": {name, version}, "browser": {name, version}?, "pages": [
{startedDateTime, id, title, ...}]?, "entries": [{pageref?, startedDateTime, time, request: {method, url, httpVersion,
cookies: [{name, value}], headers, queryString, postData?}, response: {status, statusText, cookies, headers,
content: {size, mimeType, text?}, redirectURL, bodySize}, serverIPAddress?, connection?}]}}.
Accepted only when the JSON root is an object whose "log" is an object with an "entries" list; anything else (other
JSON, text, binary, truncated JSON) -> "none".

Conventions chosen here (no GM ruling yet):
  * counts are len(entries) / len(pages) (pages absent -> 0).
  * the *set* lists (request_urls, request_methods, response_status_codes, server_ip_addresses, hosts, mime types,
    cookie names) are SORTED UNIQUE (the coverage goal's wording); the *_in_order / entry_* lists keep entry order.
    Status codes are ints, everything else verbatim strings; empty strings / missing values are skipped.
  * hosts = URL netloc minus userinfo (port kept, as in the Host header); hostnames = lowercase hostname, no port.
  * first/last_request_url: entries ordered by parsed startedDateTime (ISO-8601, offset honoured, stable for ties);
    entries whose time does not parse sort after the rest. *_started_date_time = that entry's stored text verbatim;
    *_utc = the same instant as 'YYYY-MM-DDTHH:MM:SS[.mmm|.uuuuuu]Z'.
  * total_response_body_size = sum of response.bodySize over entries with bodySize >= 0 (-1 = unknown, skipped);
    total_response_content_size = sum of response.content.size >= 0."""
import datetime
import gzip
import json
from urllib.parse import urlsplit

FIELDS = {
    ("har", "entry_count"): "har_value",
    ("har", "entries_count"): "har_value",
    ("har", "number_of_entries"): "har_value",
    ("har", "num_entries"): "har_value",
    ("har", "request_count"): "har_value",
    ("har", "requests_count"): "har_value",
    ("har", "number_of_requests"): "har_value",
    ("har", "log_entry_count"): "har_value",
    ("har", "page_count"): "har_value",
    ("har", "pages_count"): "har_value",
    ("har", "number_of_pages"): "har_value",
    ("har", "log_page_count"): "har_value",
    ("har", "version"): "har_value",
    ("har", "har_version"): "har_value",
    ("har", "log_version"): "har_value",
    ("har", "creator_name"): "har_value",
    ("har", "log_creator_name"): "har_value",
    ("har", "creator_version"): "har_value",
    ("har", "log_creator_version"): "har_value",
    ("har", "creator"): "har_value",
    ("har", "browser_name"): "har_value",
    ("har", "log_browser_name"): "har_value",
    ("har", "browser_version"): "har_value",
    ("har", "log_browser_version"): "har_value",
    ("har", "request_urls"): "har_value",
    ("har", "urls"): "har_value",
    ("har", "unique_request_urls"): "har_value",
    ("har", "distinct_request_urls"): "har_value",
    ("har", "entry_request_urls"): "har_value",
    ("har", "request_urls_in_order"): "har_value",
    ("har", "entry_urls"): "har_value",
    ("har", "request_methods"): "har_value",
    ("har", "methods"): "har_value",
    ("har", "http_methods"): "har_value",
    ("har", "unique_request_methods"): "har_value",
    ("har", "response_status_codes"): "har_value",
    ("har", "status_codes"): "har_value",
    ("har", "http_status_codes"): "har_value",
    ("har", "unique_status_codes"): "har_value",
    ("har", "server_ip_addresses"): "har_value",
    ("har", "server_ips"): "har_value",
    ("har", "server_ip_address_list"): "har_value",
    ("har", "unique_server_ip_addresses"): "har_value",
    ("har", "hosts"): "har_value",
    ("har", "request_hosts"): "har_value",
    ("har", "host_names_netloc"): "har_value",
    ("har", "unique_hosts"): "har_value",
    ("har", "netlocs"): "har_value",
    ("har", "request_netlocs"): "har_value",
    ("har", "hostnames"): "har_value",
    ("har", "request_hostnames"): "har_value",
    ("har", "domains"): "har_value",
    ("har", "request_domains"): "har_value",
    ("har", "response_mime_types"): "har_value",
    ("har", "mime_types"): "har_value",
    ("har", "content_mime_types"): "har_value",
    ("har", "response_content_mime_types"): "har_value",
    ("har", "total_response_body_size"): "har_value",
    ("har", "response_body_size_total"): "har_value",
    ("har", "total_body_size"): "har_value",
    ("har", "response_body_size_sum"): "har_value",
    ("har", "total_response_body_size_bytes"): "har_value",
    ("har", "total_response_content_size"): "har_value",
    ("har", "response_content_size_total"): "har_value",
    ("har", "cookie_names"): "har_value",
    ("har", "request_cookie_names"): "har_value",
    ("har", "response_cookie_names"): "har_value",
    ("har", "unique_cookie_names"): "har_value",
    ("har", "first_request_url"): "har_value",
    ("har", "first_entry_url"): "har_value",
    ("har", "earliest_request_url"): "har_value",
    ("har", "last_request_url"): "har_value",
    ("har", "latest_request_url"): "har_value",
    ("har", "first_request_method"): "har_value",
    ("har", "first_started_date_time"): "har_value",
    ("har", "first_request_started_date_time"): "har_value",
    ("har", "first_started_date_time_utc"): "har_value",
    ("har", "first_request_time_utc"): "har_value",
    ("har", "earliest_started_date_time"): "har_value",
    ("har", "last_started_date_time"): "har_value",
    ("har", "last_started_date_time_utc"): "har_value",
    ("har", "last_request_time_utc"): "har_value",
    ("har", "latest_started_date_time"): "har_value",
    ("har", "page_titles"): "har_value",
    ("har", "page_ids"): "har_value",
    ("har", "first_page_title"): "har_value",
    ("har", "http_versions"): "har_value",
    ("har", "request_http_versions"): "har_value",
}


def _log(b):
    """The HAR `log` object, or None when `b` is not a HAR."""
    if not b:
        return None
    b = bytes(b)
    if b[:2] == b"\x1f\x8b":
        try:
            b = gzip.decompress(b)
        except Exception:
            return None
    head = b[:4096].lstrip(b"\xef\xbb\xbf \t\r\n")
    if not head.startswith(b"{"):
        return None
    try:
        root = json.loads(b.decode("utf-8-sig"))
    except Exception:
        return None
    lg = root.get("log") if isinstance(root, dict) else None
    if not isinstance(lg, dict) or not isinstance(lg.get("entries"), list):
        return None
    return lg


def _d(x):
    return x if isinstance(x, dict) else {}


def _l(x):
    return x if isinstance(x, list) else []


def _s(x):
    return x.strip() if isinstance(x, str) and x.strip() else None


def _when(s):
    """startedDateTime -> aware datetime (UTC assumed when no offset), or None."""
    if not isinstance(s, str) or not s.strip():
        return None
    t = s.strip().replace("z", "Z")
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    if "." in t:   # fromisoformat on older Pythons wants exactly 3 or 6 fraction digits
        head, rest = t.split(".", 1)
        i = 0
        while i < len(rest) and rest[i].isdigit():
            i += 1
        t = head + "." + (rest[:i] + "000000")[:6] + rest[i:]
    try:
        dt = datetime.datetime.fromisoformat(t)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=datetime.timezone.utc)


def _utc(dt):
    dt = dt.astimezone(datetime.timezone.utc)
    s = dt.strftime("%Y-%m-%dT%H:%M:%S")
    if dt.microsecond:
        s += (".%03d" % (dt.microsecond // 1000)) if dt.microsecond % 1000 == 0 else ".%06d" % dt.microsecond
    return s + "Z"


def _uniq_sorted(vals):
    return sorted(set(v for v in vals if v is not None))


def _netloc(url):
    try:
        p = urlsplit(url)
    except ValueError:
        return None, None
    nl = p.netloc.rsplit("@", 1)[-1] or None
    try:
        hn = p.hostname
    except ValueError:
        hn = None
    return nl, hn


def _chrono(entries):
    """Entries ordered by startedDateTime (stable; unparseable times last)."""
    keyed = [(0, _when(e.get("startedDateTime")), i, e) for i, e in enumerate(entries)]
    keyed = [((0, w, i) if w else (1, None, i), e) for _, w, i, e in keyed]
    keyed.sort(key=lambda k: (k[0][0], k[0][1] or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc),
                              k[0][2]))
    return [e for _, e in keyed]


def har_value(data, ctx):
    try:
        return _value(data, (ctx or {}).get("field") or "")
    except Exception:
        return None


def _value(data, f):
    if data is None:
        return None
    lg = _log(data)
    if lg is None:
        return "none"
    entries = [e for e in lg["entries"] if isinstance(e, dict)]
    pages = [p for p in _l(lg.get("pages")) if isinstance(p, dict)]
    reqs = [_d(e.get("request")) for e in entries]
    resps = [_d(e.get("response")) for e in entries]
    urls = [_s(r.get("url")) for r in reqs]

    if f in ("entry_count", "entries_count", "number_of_entries", "num_entries", "request_count", "requests_count",
             "number_of_requests", "log_entry_count"):
        return len(entries)
    if f in ("page_count", "pages_count", "number_of_pages", "log_page_count"):
        return len(pages)
    if f in ("version", "har_version", "log_version"):
        return _s(lg.get("version")) or "none"
    if f in ("creator_name", "log_creator_name", "creator"):
        return _s(_d(lg.get("creator")).get("name")) or "none"
    if f in ("creator_version", "log_creator_version"):
        return _s(_d(lg.get("creator")).get("version")) or "none"
    if f in ("browser_name", "log_browser_name"):
        return _s(_d(lg.get("browser")).get("name")) or "none"
    if f in ("browser_version", "log_browser_version"):
        return _s(_d(lg.get("browser")).get("version")) or "none"
    if f in ("request_urls", "urls", "unique_request_urls", "distinct_request_urls"):
        return _uniq_sorted(urls)
    if f in ("entry_request_urls", "request_urls_in_order", "entry_urls"):
        return [u for u in urls if u is not None]
    if f in ("request_methods", "methods", "http_methods", "unique_request_methods"):
        return _uniq_sorted(_s(r.get("method")) for r in reqs)
    if f in ("http_versions", "request_http_versions"):
        return _uniq_sorted(_s(r.get("httpVersion")) for r in reqs)
    if f in ("response_status_codes", "status_codes", "http_status_codes", "unique_status_codes"):
        codes = []
        for r in resps:
            st = r.get("status")
            if isinstance(st, bool):
                continue
            if isinstance(st, str) and st.strip().isdigit():
                st = int(st)
            if isinstance(st, int):
                codes.append(st)
        return _uniq_sorted(codes)
    if f in ("server_ip_addresses", "server_ips", "server_ip_address_list", "unique_server_ip_addresses"):
        return _uniq_sorted(_s(e.get("serverIPAddress")) for e in entries)
    if f in ("hosts", "request_hosts", "host_names_netloc", "unique_hosts", "netlocs", "request_netlocs"):
        return _uniq_sorted(_netloc(u)[0] for u in urls if u)
    if f in ("hostnames", "request_hostnames", "domains", "request_domains"):
        return _uniq_sorted(_netloc(u)[1] for u in urls if u)
    if f in ("response_mime_types", "mime_types", "content_mime_types", "response_content_mime_types"):
        return _uniq_sorted(_s(_d(r.get("content")).get("mimeType")) for r in resps)
    if f in ("total_response_body_size", "response_body_size_total", "total_body_size", "response_body_size_sum",
             "total_response_body_size_bytes"):
        return sum(r["bodySize"] for r in resps
                   if isinstance(r.get("bodySize"), int) and not isinstance(r.get("bodySize"), bool)
                   and r["bodySize"] >= 0)
    if f in ("total_response_content_size", "response_content_size_total"):
        sz = [_d(r.get("content")).get("size") for r in resps]
        return sum(s for s in sz if isinstance(s, int) and not isinstance(s, bool) and s >= 0)
    if f in ("cookie_names", "request_cookie_names", "response_cookie_names", "unique_cookie_names"):
        src = reqs if f == "request_cookie_names" else resps if f == "response_cookie_names" else reqs + resps
        return _uniq_sorted(_s(_d(c).get("name")) for r in src for c in _l(r.get("cookies")))
    if f in ("page_titles", "page_ids"):
        k = "title" if f == "page_titles" else "id"
        return [_s(p.get(k)) for p in pages if _s(p.get(k)) is not None]
    if f == "first_page_title":
        return (_s(pages[0].get("title")) if pages else None) or "none"
    if f.startswith(("first_", "earliest_", "last_", "latest_")):
        if not entries:
            return "none"
        order = _chrono(entries)
        e = order[-1] if f.startswith(("last_", "latest_")) else order[0]
        if f.endswith("_url"):
            return _s(_d(e.get("request")).get("url")) or "none"
        if f.endswith("_method"):
            return _s(_d(e.get("request")).get("method")) or "none"
        if f.endswith("_utc"):
            w = _when(e.get("startedDateTime"))
            return _utc(w) if w else "none"
        return _s(e.get("startedDateTime")) or "none"
    return None
