"""RFC 5322 e-mail AUTHENTICATION / sender-alignment fields for `email` / `eml` (prebuilt, SPECULATIVE).
Parsing is eml.py's (_parse: stdlib email, raw_items() unfolded + trimmed; not an e-mail -> "none").

Authentication-Results (RFC 8601): the TOPMOST header (= the last receiving MTA's verdict; lower ones are older hops
and can be forged by the sender). RFC 5322 comments "(...)" are stripped first (they hold ';' and '=' text), the value
is split on ';': part 0 = authserv-id (an optional trailing authres-version number dropped), the rest are resinfo
"method=result prop.name=value ...". <method>_result = the FIRST resinfo of that method in the topmost header that
has one, lowercased (RFC 8601 result keywords are lowercase); with no Authentication-Results at all the topmost
ARC-Authentication-Results (its "i=N;" prefix dropped) is used. spf_result falls back to Received-SPF.
received_spf_result = first word of the topmost Received-SPF, lowercased ("Pass (mailfrom) ..." -> "pass");
received_spf_client_ip / _envelope_from / _helo = its key=value pairs.
DKIM-Signature (RFC 6376 tag=value list, FWS removed): the FIRST signature. dkim_signed_headers = h= split on ':'
(stored case and order kept, list); dkim_algorithm a=, dkim_canonicalization c=, dkim_body_hash bh=, dkim_identity i=,
dkim_version v=, dkim_timestamp t= (int). (d= / s= are eml.py's dkim_domain / dkim_selector.)
ARC (RFC 8617): arc_seal_count / arc_message_signature_count / arc_authentication_results_count = number of those
headers; arc_instance_count = highest i= seen; arc_chain_validation = cv= of the highest-i ARC-Seal.
Domains: the addr-spec of Return-Path / From / Reply-To / Sender, part after the last '@', lowercased, '>' and
trailing '.' trimmed; "<>" (null sender) -> "none". *_mismatch = exact (case-insensitive) domain inequality, NOT
DMARC relaxed alignment; when the second header is absent the answer is false (nothing to mismatch)."""
import re

FIELDS = {
    ("email", "spf_result"): "auth_value",
    ("email", "spf"): "auth_value",
    ("email", "dkim_result"): "auth_value",
    ("email", "dkim"): "auth_value",
    ("email", "dmarc_result"): "auth_value",
    ("email", "dmarc"): "auth_value",
    ("email", "arc_result"): "auth_value",
    ("email", "compauth_result"): "auth_value",
    ("email", "authentication_results_spf"): "auth_value",
    ("email", "authentication_results_dkim"): "auth_value",
    ("email", "authentication_results_dmarc"): "auth_value",
    ("email", "auth_results_spf"): "auth_value",
    ("email", "auth_results_dkim"): "auth_value",
    ("email", "auth_results_dmarc"): "auth_value",
    ("email", "dkim_results"): "auth_value",
    ("email", "authserv_id"): "auth_value",
    ("email", "authentication_results_authserv_id"): "auth_value",
    ("email", "auth_results_authserv_id"): "auth_value",
    ("email", "authentication_results_count"): "auth_value",
    ("email", "spf_smtp_mailfrom"): "auth_value",
    ("email", "smtp_mailfrom"): "auth_value",
    ("email", "spf_mailfrom"): "auth_value",
    ("email", "dkim_header_d"): "auth_value",
    ("email", "dkim_header_i"): "auth_value",
    ("email", "dmarc_header_from"): "auth_value",
    ("email", "auth_results_header_from"): "auth_value",
    ("email", "received_spf_result"): "auth_value",
    ("email", "received_spf"): "auth_value",
    ("email", "received_spf_client_ip"): "auth_value",
    ("email", "received_spf_envelope_from"): "auth_value",
    ("email", "received_spf_helo"): "auth_value",
    ("email", "dkim_signed_headers"): "auth_value",
    ("email", "dkim_h"): "auth_value",
    ("email", "dkim_h_tag"): "auth_value",
    ("email", "dkim_signature_h"): "auth_value",
    ("email", "dkim_signature_signed_headers"): "auth_value",
    ("email", "dkim_signed_header_names"): "auth_value",
    ("email", "dkim_headers"): "auth_value",
    ("email", "dkim_signed_header_count"): "auth_value",
    ("email", "dkim_signature_count"): "auth_value",
    ("email", "dkim_algorithm"): "auth_value",
    ("email", "dkim_signature_algorithm"): "auth_value",
    ("email", "dkim_a"): "auth_value",
    ("email", "dkim_canonicalization"): "auth_value",
    ("email", "dkim_c"): "auth_value",
    ("email", "dkim_body_hash"): "auth_value",
    ("email", "dkim_bh"): "auth_value",
    ("email", "dkim_identity"): "auth_value",
    ("email", "dkim_i"): "auth_value",
    ("email", "dkim_version"): "auth_value",
    ("email", "dkim_v"): "auth_value",
    ("email", "dkim_timestamp"): "auth_value",
    ("email", "dkim_t"): "auth_value",
    ("email", "arc_seal_count"): "auth_value",
    ("email", "arc_seals"): "auth_value",
    ("email", "arc_message_signature_count"): "auth_value",
    ("email", "arc_authentication_results_count"): "auth_value",
    ("email", "arc_instance_count"): "auth_value",
    ("email", "arc_chain_length"): "auth_value",
    ("email", "arc_max_instance"): "auth_value",
    ("email", "arc_chain_validation"): "auth_value",
    ("email", "arc_cv"): "auth_value",
    ("email", "arc_seal_cv"): "auth_value",
    ("email", "return_path_domain"): "auth_value",
    ("email", "from_domain"): "auth_value",
    ("email", "from_address_domain"): "auth_value",
    ("email", "header_from_domain"): "auth_value",
    ("email", "reply_to_domain"): "auth_value",
    ("email", "sender_domain"): "auth_value",
    ("email", "envelope_from_domain"): "auth_value",
    ("email", "mail_from_domain"): "auth_value",
    ("email", "from_return_path_mismatch"): "auth_value",
    ("email", "return_path_mismatch"): "auth_value",
    ("email", "return_path_from_mismatch"): "auth_value",
    ("email", "from_return_path_domain_mismatch"): "auth_value",
    ("email", "envelope_from_mismatch"): "auth_value",
    ("email", "reply_to_mismatch"): "auth_value",
    ("email", "from_reply_to_mismatch"): "auth_value",
    ("email", "reply_to_from_mismatch"): "auth_value",
    ("email", "reply_to_domain_mismatch"): "auth_value",
    ("eml", "spf_result"): "auth_value",
    ("eml", "spf"): "auth_value",
    ("eml", "dkim_result"): "auth_value",
    ("eml", "dkim"): "auth_value",
    ("eml", "dmarc_result"): "auth_value",
    ("eml", "dmarc"): "auth_value",
    ("eml", "arc_result"): "auth_value",
    ("eml", "compauth_result"): "auth_value",
    ("eml", "authentication_results_spf"): "auth_value",
    ("eml", "authentication_results_dkim"): "auth_value",
    ("eml", "authentication_results_dmarc"): "auth_value",
    ("eml", "auth_results_spf"): "auth_value",
    ("eml", "auth_results_dkim"): "auth_value",
    ("eml", "auth_results_dmarc"): "auth_value",
    ("eml", "dkim_results"): "auth_value",
    ("eml", "authserv_id"): "auth_value",
    ("eml", "authentication_results_authserv_id"): "auth_value",
    ("eml", "auth_results_authserv_id"): "auth_value",
    ("eml", "authentication_results_count"): "auth_value",
    ("eml", "spf_smtp_mailfrom"): "auth_value",
    ("eml", "smtp_mailfrom"): "auth_value",
    ("eml", "spf_mailfrom"): "auth_value",
    ("eml", "dkim_header_d"): "auth_value",
    ("eml", "dkim_header_i"): "auth_value",
    ("eml", "dmarc_header_from"): "auth_value",
    ("eml", "auth_results_header_from"): "auth_value",
    ("eml", "received_spf_result"): "auth_value",
    ("eml", "received_spf"): "auth_value",
    ("eml", "received_spf_client_ip"): "auth_value",
    ("eml", "received_spf_envelope_from"): "auth_value",
    ("eml", "received_spf_helo"): "auth_value",
    ("eml", "dkim_signed_headers"): "auth_value",
    ("eml", "dkim_h"): "auth_value",
    ("eml", "dkim_h_tag"): "auth_value",
    ("eml", "dkim_signature_h"): "auth_value",
    ("eml", "dkim_signature_signed_headers"): "auth_value",
    ("eml", "dkim_signed_header_names"): "auth_value",
    ("eml", "dkim_headers"): "auth_value",
    ("eml", "dkim_signed_header_count"): "auth_value",
    ("eml", "dkim_signature_count"): "auth_value",
    ("eml", "dkim_algorithm"): "auth_value",
    ("eml", "dkim_signature_algorithm"): "auth_value",
    ("eml", "dkim_a"): "auth_value",
    ("eml", "dkim_canonicalization"): "auth_value",
    ("eml", "dkim_c"): "auth_value",
    ("eml", "dkim_body_hash"): "auth_value",
    ("eml", "dkim_bh"): "auth_value",
    ("eml", "dkim_identity"): "auth_value",
    ("eml", "dkim_i"): "auth_value",
    ("eml", "dkim_version"): "auth_value",
    ("eml", "dkim_v"): "auth_value",
    ("eml", "dkim_timestamp"): "auth_value",
    ("eml", "dkim_t"): "auth_value",
    ("eml", "arc_seal_count"): "auth_value",
    ("eml", "arc_seals"): "auth_value",
    ("eml", "arc_message_signature_count"): "auth_value",
    ("eml", "arc_authentication_results_count"): "auth_value",
    ("eml", "arc_instance_count"): "auth_value",
    ("eml", "arc_chain_length"): "auth_value",
    ("eml", "arc_max_instance"): "auth_value",
    ("eml", "arc_chain_validation"): "auth_value",
    ("eml", "arc_cv"): "auth_value",
    ("eml", "arc_seal_cv"): "auth_value",
    ("eml", "return_path_domain"): "auth_value",
    ("eml", "from_domain"): "auth_value",
    ("eml", "from_address_domain"): "auth_value",
    ("eml", "header_from_domain"): "auth_value",
    ("eml", "reply_to_domain"): "auth_value",
    ("eml", "sender_domain"): "auth_value",
    ("eml", "envelope_from_domain"): "auth_value",
    ("eml", "mail_from_domain"): "auth_value",
    ("eml", "from_return_path_mismatch"): "auth_value",
    ("eml", "return_path_mismatch"): "auth_value",
    ("eml", "return_path_from_mismatch"): "auth_value",
    ("eml", "from_return_path_domain_mismatch"): "auth_value",
    ("eml", "envelope_from_mismatch"): "auth_value",
    ("eml", "reply_to_mismatch"): "auth_value",
    ("eml", "from_reply_to_mismatch"): "auth_value",
    ("eml", "reply_to_from_mismatch"): "auth_value",
    ("eml", "reply_to_domain_mismatch"): "auth_value",
}

_AR_METHOD = {"spf": "spf", "dkim": "dkim", "dmarc": "dmarc", "arc_result": "arc", "compauth_result": "compauth",
              "spf_result": "spf", "dkim_result": "dkim", "dmarc_result": "dmarc"}
_DKIM_TAG = {"dkim_algorithm": "a", "dkim_signature_algorithm": "a", "dkim_a": "a", "dkim_canonicalization": "c",
             "dkim_c": "c", "dkim_body_hash": "bh", "dkim_bh": "bh", "dkim_identity": "i", "dkim_i": "i",
             "dkim_version": "v", "dkim_v": "v", "dkim_timestamp": "t", "dkim_t": "t"}
_DOMAIN_HDR = {"return_path_domain": ("return-path",), "envelope_from_domain": ("return-path",),
               "mail_from_domain": ("return-path",), "from_domain": ("from",), "from_address_domain": ("from",),
               "header_from_domain": ("from",), "reply_to_domain": ("reply-to",), "sender_domain": ("sender",)}


def _hdrs(raw, name):
    return [v for k, v in raw if k == name]


def _uncomment(s):
    """s with RFC 5322 comments (nested parens, backslash escapes) removed; quoted strings kept."""
    out, depth, q, esc = [], 0, False, False
    for ch in s:
        if esc:
            esc = False
            if depth == 0:
                out.append(ch)
            continue
        if ch == "\\":
            esc = True
            if depth == 0:
                out.append(ch)
            continue
        if q:
            out.append(ch)
            q = ch != '"'
            continue
        if ch == '"' and depth == 0:
            q = True
            out.append(ch)
        elif ch == "(":
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
            if depth == 0:
                out.append(" ")
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _ar_parse(v, arc=False):
    """(authserv_id, [(method, result, {prop: value})]) of one (ARC-)Authentication-Results value."""
    parts = [p.strip() for p in _uncomment(v).split(";")]
    if arc and parts and re.fullmatch(r"i\s*=\s*\d+", parts[0]):
        parts = parts[1:]
    if not parts:
        return None, []
    sid = parts[0].split()
    sid = sid[0] if sid else None
    res = []
    for p in parts[1:]:
        m = re.match(r"([A-Za-z0-9_-]+)\s*(?:/\s*\d+\s*)?=\s*([A-Za-z0-9_-]+)(.*)$", p, re.S)
        if not m:
            continue
        props = {}
        for pm in re.finditer(r"([A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)+)\s*=\s*(\"[^\"]*\"|[^\s;]+)", m.group(3)):
            props.setdefault(pm.group(1).lower(), pm.group(2).strip('"'))
        res.append((m.group(1).lower(), m.group(2).lower(), props))
    if sid and "=" in sid:   # "none" authserv-less form is not legal; a resinfo in slot 0 means no id
        sid = None
    return sid, res


def _ar_all(raw):
    ars = [_ar_parse(v) for v in _hdrs(raw, "authentication-results")]
    if not ars:
        ars = [_ar_parse(v, arc=True) for v in _hdrs(raw, "arc-authentication-results")]
    return ars


def _ar_first(raw, method):
    for _sid, res in _ar_all(raw):
        for m, r, props in res:
            if m == method:
                return r, props
    return None, None


def _dkim_tags(v):
    tags = {}
    for part in v.split(";"):
        if "=" in part:
            k, val = part.split("=", 1)
            tags.setdefault(k.strip().lower(), re.sub(r"\s+", "", val))
    return tags


def _received_spf(raw):
    v = (_hdrs(raw, "received-spf") or [None])[0]
    if v is None:
        return None, {}
    m = re.match(r"\s*([A-Za-z]+)", v)
    kv = {k.lower(): val.strip('"') for k, val in
          re.findall(r"([A-Za-z-]+)\s*=\s*(\"[^\"]*\"|[^\s;]+)", _uncomment(v))}
    return (m.group(1).lower() if m else None), kv


def _domain(raw, name):
    from .eml import _addr
    v = (_hdrs(raw, name) or [None])[0]
    if v is None:
        return None
    a = _addr(v)
    if not a or "@" not in a:
        return None
    d = a.rsplit("@", 1)[1].strip().strip("<>").rstrip(".").lower()
    return d or None


def _mismatch(raw, other):
    f = _domain(raw, "from")
    if f is None:
        return None
    o = _domain(raw, other)
    return False if o is None else o != f


def _value(b, f):
    from .eml import _parse
    p = _parse(b)
    if p is None:
        return None
    _msg, raw = p
    for pre in ("authentication_results_", "auth_results_"):
        if f.startswith(pre) and f[len(pre):] in ("spf", "dkim", "dmarc"):
            f = f[len(pre):]
    if f in _AR_METHOD:
        meth = _AR_METHOD[f]
        r, _ = _ar_first(raw, meth)
        if r is None and meth == "spf":
            r = _received_spf(raw)[0]
        return r
    if f == "dkim_results":
        return [r for _sid, res in _ar_all(raw)[:1] for m, r, _p in res if m == "dkim"] or None
    if f.endswith("authserv_id"):
        for sid, _res in _ar_all(raw):
            if sid:
                return sid
        return None
    if f == "authentication_results_count":
        return len(_hdrs(raw, "authentication-results"))
    if f in ("spf_smtp_mailfrom", "smtp_mailfrom", "spf_mailfrom"):
        return (_ar_first(raw, "spf")[1] or {}).get("smtp.mailfrom")
    if f in ("dkim_header_d", "dkim_header_i"):
        return (_ar_first(raw, "dkim")[1] or {}).get("header." + f[-1])
    if f in ("dmarc_header_from", "auth_results_header_from"):
        return (_ar_first(raw, "dmarc")[1] or {}).get("header.from")
    if f.startswith("received_spf"):
        r, kv = _received_spf(raw)
        if f in ("received_spf_result", "received_spf"):
            return r
        return kv.get(f[len("received_spf_"):].replace("_", "-"))
    sigs = _hdrs(raw, "dkim-signature")
    if f == "dkim_signature_count":
        return len(sigs)
    if f.startswith("dkim_"):
        if not sigs:
            return None
        tags = _dkim_tags(sigs[0])
        if f in _DKIM_TAG:
            v = tags.get(_DKIM_TAG[f])
            if v and _DKIM_TAG[f] == "t":
                return int(v) if v.isdigit() else v
            return v
        h = [x.strip() for x in (tags.get("h") or "").split(":") if x.strip()]
        if f == "dkim_signed_header_count":
            return len(h)
        return h or None
    if f.startswith("arc_"):
        seals = _hdrs(raw, "arc-seal")
        if f in ("arc_seal_count", "arc_seals"):
            return len(seals)
        if f == "arc_message_signature_count":
            return len(_hdrs(raw, "arc-message-signature"))
        if f == "arc_authentication_results_count":
            return len(_hdrs(raw, "arc-authentication-results"))
        inst = []
        for n in ("arc-seal", "arc-message-signature", "arc-authentication-results"):
            for v in _hdrs(raw, n):
                m = re.search(r"(?:^|;)\s*i\s*=\s*(\d+)", v)
                if m:
                    inst.append(int(m.group(1)))
        if f in ("arc_instance_count", "arc_chain_length", "arc_max_instance"):
            return max(inst) if inst else 0
        best = None
        for v in seals:
            t = _dkim_tags(v)
            i = int(t["i"]) if (t.get("i") or "").isdigit() else 0
            if t.get("cv") and (best is None or i > best[0]):
                best = (i, t["cv"].lower())
        return best[1] if best else None
    if f in _DOMAIN_HDR:
        return _domain(raw, _DOMAIN_HDR[f][0])
    if f.startswith("reply_to") or f.endswith("reply_to_mismatch"):
        return _mismatch(raw, "reply-to")
    if "mismatch" in f:
        return _mismatch(raw, "return-path")
    return None


def auth_value(data, ctx):
    if data is None:
        return None
    try:
        v = _value(data, (ctx or {}).get("field") or "")
    except Exception:  # noqa: BLE001 -- a malformed message never raises past the extractor
        return None
    return "none" if v is None or v == "" or v == [] else v
