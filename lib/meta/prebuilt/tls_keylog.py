"""TLS material inside captures + SSLKEYLOGFILE (prebuilt, SPECULATIVE -- never GM-verified).
Complements pcap_app.py (ClientHello SNI/ALPN/JA3 + leaf sha256/CNs) with the SERVER side and the key log.

sslkeylog (NSS key log text, also the TLSK payload of a pcapng DSB): lines `<LABEL> <client_random hex> <secret hex>`
  (`# ...` comments / blank / malformed lines skipped -- Wireshark's own reader skips them too).
  line_count = key lines; client_randoms = 2nd field (all labels but RSA), lowercase, sorted unique JSON list;
  labels = sorted unique label set; label_counts = {label: n} JSON. Given a pcapng, its TLSK DSBs are read instead.
pcapng DSB = block type 0x0000000A: u32 secrets type (0x544c534b 'TLSK'), u32 length, payload (per-section byte
  order). dsb_count / dsb_present / dsb_secrets_type_u32_hex; keylog_* = the sslkeylog fields of the embedded log.
ServerHello (per TCP direction, reassembled in seq order, handshake records joined until ChangeCipherSpec):
  JA3S = md5('legacy_version,cipher,ext types') decimal, extensions '-'-joined in wire order, GREASE dropped --
  tshark tls.handshake.ja3s. cipher = Hex(cipher, 4) ('0x%04x', tshark tls.handshake.ciphersuite). negotiated
  version = supported_versions (43) else legacy version, spelled 'TLSv1.2'. Singular names: the value when every
  session agrees, else the sorted distinct list; plural names: always the sorted list.
Server certificate = the Certificate message (TLS <= 1.2; 1.3 certs are encrypted) in the SAME direction as the
  ServerHello (a client cert in mutual TLS is not the server's); leaf = first DER; serial / not_after / not_before /
  sha256 rendered by prebuilt/x509.py (serial lowercase hex, even length; ISO-8601 'YYYY-MM-DDTHH:MM:SSZ' UTC from
  the cert's UTCTime/GeneralizedTime). server_cert_fingerprints = sorted unique sha256 of each session's LEAF.
Not a capture / no TLS / no key lines -> "none" (counts -> 0, booleans -> false)."""
import collections
import hashlib
import re
import struct

from ..spell import Hex

FIELDS = {
    ("sslkeylog", "line_count"): "keylog_value",
    ("sslkeylog", "entry_count"): "keylog_value",
    ("sslkeylog", "secret_count"): "keylog_value",
    ("sslkeylog", "key_line_count"): "keylog_value",
    ("sslkeylog", "number_of_lines"): "keylog_value",
    ("sslkeylog", "record_count"): "keylog_value",
    ("sslkeylog", "client_randoms"): "keylog_value",
    ("sslkeylog", "client_random_list"): "keylog_value",
    ("sslkeylog", "unique_client_randoms"): "keylog_value",
    ("sslkeylog", "client_random_count"): "keylog_value",
    ("sslkeylog", "unique_client_random_count"): "keylog_value",
    ("sslkeylog", "session_count"): "keylog_value",
    ("sslkeylog", "first_client_random"): "keylog_value",
    ("sslkeylog", "labels"): "keylog_value",
    ("sslkeylog", "label_set"): "keylog_value",
    ("sslkeylog", "secret_labels"): "keylog_value",
    ("sslkeylog", "label_names"): "keylog_value",
    ("sslkeylog", "unique_labels"): "keylog_value",
    ("sslkeylog", "secret_types"): "keylog_value",
    ("sslkeylog", "label_count"): "keylog_value",
    ("sslkeylog", "unique_label_count"): "keylog_value",
    ("sslkeylog", "label_counts"): "keylog_value",
    ("sslkeylog", "client_random_line_count"): "keylog_value",
    ("sslkeylog", "tls13_secrets_present"): "keylog_value",
    ("sslkeylog", "has_tls13_secrets"): "keylog_value",
    ("keylog", "line_count"): "keylog_value",
    ("keylog", "entry_count"): "keylog_value",
    ("keylog", "secret_count"): "keylog_value",
    ("keylog", "key_line_count"): "keylog_value",
    ("keylog", "number_of_lines"): "keylog_value",
    ("keylog", "record_count"): "keylog_value",
    ("keylog", "client_randoms"): "keylog_value",
    ("keylog", "client_random_list"): "keylog_value",
    ("keylog", "unique_client_randoms"): "keylog_value",
    ("keylog", "client_random_count"): "keylog_value",
    ("keylog", "unique_client_random_count"): "keylog_value",
    ("keylog", "session_count"): "keylog_value",
    ("keylog", "first_client_random"): "keylog_value",
    ("keylog", "labels"): "keylog_value",
    ("keylog", "label_set"): "keylog_value",
    ("keylog", "secret_labels"): "keylog_value",
    ("keylog", "label_names"): "keylog_value",
    ("keylog", "unique_labels"): "keylog_value",
    ("keylog", "secret_types"): "keylog_value",
    ("keylog", "label_count"): "keylog_value",
    ("keylog", "unique_label_count"): "keylog_value",
    ("keylog", "label_counts"): "keylog_value",
    ("keylog", "client_random_line_count"): "keylog_value",
    ("keylog", "tls13_secrets_present"): "keylog_value",
    ("keylog", "has_tls13_secrets"): "keylog_value",
    ("pcapng", "dsb_count"): "dsb_value",
    ("pcapng", "decryption_secrets_block_count"): "dsb_value",
    ("pcapng", "dsb_block_count"): "dsb_value",
    ("pcapng", "dsb_present"): "dsb_value",
    ("pcapng", "has_decryption_secrets"): "dsb_value",
    ("pcapng", "has_dsb"): "dsb_value",
    ("pcapng", "decryption_secrets_present"): "dsb_value",
    ("pcapng", "dsb_secrets_type_u32_hex"): "dsb_value",
    ("pcapng", "decryption_secrets_type_u32_hex"): "dsb_value",
    ("pcapng", "dsb_secrets_length"): "dsb_value",
    ("pcapng", "dsb_secrets_length_bytes"): "dsb_value",
    ("pcapng", "dsb_keylog_line_count"): "dsb_value",
    ("pcapng", "keylog_line_count"): "dsb_value",
    ("pcapng", "embedded_keylog_line_count"): "dsb_value",
    ("pcapng", "tls_keylog_line_count"): "dsb_value",
    ("pcapng", "dsb_client_randoms"): "dsb_value",
    ("pcapng", "keylog_client_randoms"): "dsb_value",
    ("pcapng", "embedded_keylog_client_randoms"): "dsb_value",
    ("pcapng", "dsb_client_random_count"): "dsb_value",
    ("pcapng", "keylog_client_random_count"): "dsb_value",
    ("pcapng", "dsb_labels"): "dsb_value",
    ("pcapng", "keylog_labels"): "dsb_value",
    ("pcapng", "embedded_keylog_labels"): "dsb_value",
    ("pcapng", "dsb_secret_labels"): "dsb_value",
    ("pcapng", "tls_ja3s_md5"): "server_value",
    ("pcapng", "ja3s_md5"): "server_value",
    ("pcapng", "tls_ja3s"): "server_value",
    ("pcapng", "ja3s_hash"): "server_value",
    ("pcapng", "tls_ja3s_hash"): "server_value",
    ("pcapng", "tls_ja3s_md5s"): "server_value",
    ("pcapng", "ja3s_hashes"): "server_value",
    ("pcapng", "tls_ja3s_hashes"): "server_value",
    ("pcapng", "ja3s_md5s"): "server_value",
    ("pcapng", "tls_ja3s_first"): "server_value",
    ("pcapng", "first_ja3s"): "server_value",
    ("pcapng", "tls_ja3s_md5_first"): "server_value",
    ("pcapng", "tls_ja3s_string"): "server_value",
    ("pcapng", "tls_ja3s_full"): "server_value",
    ("pcapng", "ja3s_full"): "server_value",
    ("pcapng", "tls_ja3s_strings"): "server_value",
    ("pcapng", "tls_cipher_suite"): "server_value",
    ("pcapng", "tls_server_cipher_suite"): "server_value",
    ("pcapng", "server_cipher_suite"): "server_value",
    ("pcapng", "tls_cipher_suite_u16_hex"): "server_value",
    ("pcapng", "server_cipher_suite_u16_hex"): "server_value",
    ("pcapng", "tls_server_cipher_suite_u16_hex"): "server_value",
    ("pcapng", "tls_ciphersuite"): "server_value",
    ("pcapng", "selected_cipher_suite"): "server_value",
    ("pcapng", "tls_selected_cipher_suite"): "server_value",
    ("pcapng", "negotiated_cipher_suite"): "server_value",
    ("pcapng", "tls_negotiated_cipher_suite"): "server_value",
    ("pcapng", "server_hello_cipher_suite"): "server_value",
    ("pcapng", "server_hello_cipher_suite_u16_hex"): "server_value",
    ("pcapng", "tls_cipher_suites"): "server_value",
    ("pcapng", "server_cipher_suites"): "server_value",
    ("pcapng", "tls_server_cipher_suites"): "server_value",
    ("pcapng", "negotiated_cipher_suites"): "server_value",
    ("pcapng", "tls_negotiated_cipher_suites"): "server_value",
    ("pcapng", "tls_server_hello_count"): "server_value",
    ("pcapng", "server_hello_count"): "server_value",
    ("pcapng", "tls_serverhello_count"): "server_value",
    ("pcapng", "tls_negotiated_version"): "server_value",
    ("pcapng", "tls_server_version"): "server_value",
    ("pcapng", "negotiated_tls_version"): "server_value",
    ("pcapng", "tls_negotiated_versions"): "server_value",
    ("pcapng", "tls_server_versions"): "server_value",
    ("pcapng", "tls_cert_serial_hex"): "server_value",
    ("pcapng", "tls_cert_serial_number_hex"): "server_value",
    ("pcapng", "tls_certificate_serial_hex"): "server_value",
    ("pcapng", "tls_certificate_serial_number_hex"): "server_value",
    ("pcapng", "server_cert_serial_hex"): "server_value",
    ("pcapng", "tls_leaf_cert_serial_hex"): "server_value",
    ("pcapng", "tls_cert_not_after_utc"): "server_value",
    ("pcapng", "tls_certificate_not_after_utc"): "server_value",
    ("pcapng", "server_cert_not_after_utc"): "server_value",
    ("pcapng", "tls_cert_not_after"): "server_value",
    ("pcapng", "tls_leaf_cert_not_after_utc"): "server_value",
    ("pcapng", "tls_cert_expiry_utc"): "server_value",
    ("pcapng", "tls_cert_not_before_utc"): "server_value",
    ("pcapng", "tls_certificate_not_before_utc"): "server_value",
    ("pcapng", "server_cert_not_before_utc"): "server_value",
    ("pcapng", "tls_cert_not_before"): "server_value",
    ("pcapng", "tls_leaf_cert_not_before_utc"): "server_value",
    ("pcapng", "server_cert_fingerprints"): "server_value",
    ("pcapng", "tls_server_cert_fingerprints"): "server_value",
    ("pcapng", "server_cert_sha256_fingerprints"): "server_value",
    ("pcapng", "server_cert_sha256s"): "server_value",
    ("pcapng", "tls_server_cert_sha256s"): "server_value",
    ("pcapng", "server_certificate_fingerprints"): "server_value",
    ("pcap", "dsb_count"): "dsb_value",
    ("pcap", "decryption_secrets_block_count"): "dsb_value",
    ("pcap", "dsb_block_count"): "dsb_value",
    ("pcap", "dsb_present"): "dsb_value",
    ("pcap", "has_decryption_secrets"): "dsb_value",
    ("pcap", "has_dsb"): "dsb_value",
    ("pcap", "decryption_secrets_present"): "dsb_value",
    ("pcap", "dsb_secrets_type_u32_hex"): "dsb_value",
    ("pcap", "decryption_secrets_type_u32_hex"): "dsb_value",
    ("pcap", "dsb_secrets_length"): "dsb_value",
    ("pcap", "dsb_secrets_length_bytes"): "dsb_value",
    ("pcap", "dsb_keylog_line_count"): "dsb_value",
    ("pcap", "keylog_line_count"): "dsb_value",
    ("pcap", "embedded_keylog_line_count"): "dsb_value",
    ("pcap", "tls_keylog_line_count"): "dsb_value",
    ("pcap", "dsb_client_randoms"): "dsb_value",
    ("pcap", "keylog_client_randoms"): "dsb_value",
    ("pcap", "embedded_keylog_client_randoms"): "dsb_value",
    ("pcap", "dsb_client_random_count"): "dsb_value",
    ("pcap", "keylog_client_random_count"): "dsb_value",
    ("pcap", "dsb_labels"): "dsb_value",
    ("pcap", "keylog_labels"): "dsb_value",
    ("pcap", "embedded_keylog_labels"): "dsb_value",
    ("pcap", "dsb_secret_labels"): "dsb_value",
    ("pcap", "tls_ja3s_md5"): "server_value",
    ("pcap", "ja3s_md5"): "server_value",
    ("pcap", "tls_ja3s"): "server_value",
    ("pcap", "ja3s_hash"): "server_value",
    ("pcap", "tls_ja3s_hash"): "server_value",
    ("pcap", "tls_ja3s_md5s"): "server_value",
    ("pcap", "ja3s_hashes"): "server_value",
    ("pcap", "tls_ja3s_hashes"): "server_value",
    ("pcap", "ja3s_md5s"): "server_value",
    ("pcap", "tls_ja3s_first"): "server_value",
    ("pcap", "first_ja3s"): "server_value",
    ("pcap", "tls_ja3s_md5_first"): "server_value",
    ("pcap", "tls_ja3s_string"): "server_value",
    ("pcap", "tls_ja3s_full"): "server_value",
    ("pcap", "ja3s_full"): "server_value",
    ("pcap", "tls_ja3s_strings"): "server_value",
    ("pcap", "tls_cipher_suite"): "server_value",
    ("pcap", "tls_server_cipher_suite"): "server_value",
    ("pcap", "server_cipher_suite"): "server_value",
    ("pcap", "tls_cipher_suite_u16_hex"): "server_value",
    ("pcap", "server_cipher_suite_u16_hex"): "server_value",
    ("pcap", "tls_server_cipher_suite_u16_hex"): "server_value",
    ("pcap", "tls_ciphersuite"): "server_value",
    ("pcap", "selected_cipher_suite"): "server_value",
    ("pcap", "tls_selected_cipher_suite"): "server_value",
    ("pcap", "negotiated_cipher_suite"): "server_value",
    ("pcap", "tls_negotiated_cipher_suite"): "server_value",
    ("pcap", "server_hello_cipher_suite"): "server_value",
    ("pcap", "server_hello_cipher_suite_u16_hex"): "server_value",
    ("pcap", "tls_cipher_suites"): "server_value",
    ("pcap", "server_cipher_suites"): "server_value",
    ("pcap", "tls_server_cipher_suites"): "server_value",
    ("pcap", "negotiated_cipher_suites"): "server_value",
    ("pcap", "tls_negotiated_cipher_suites"): "server_value",
    ("pcap", "tls_server_hello_count"): "server_value",
    ("pcap", "server_hello_count"): "server_value",
    ("pcap", "tls_serverhello_count"): "server_value",
    ("pcap", "tls_negotiated_version"): "server_value",
    ("pcap", "tls_server_version"): "server_value",
    ("pcap", "negotiated_tls_version"): "server_value",
    ("pcap", "tls_negotiated_versions"): "server_value",
    ("pcap", "tls_server_versions"): "server_value",
    ("pcap", "tls_cert_serial_hex"): "server_value",
    ("pcap", "tls_cert_serial_number_hex"): "server_value",
    ("pcap", "tls_certificate_serial_hex"): "server_value",
    ("pcap", "tls_certificate_serial_number_hex"): "server_value",
    ("pcap", "server_cert_serial_hex"): "server_value",
    ("pcap", "tls_leaf_cert_serial_hex"): "server_value",
    ("pcap", "tls_cert_not_after_utc"): "server_value",
    ("pcap", "tls_certificate_not_after_utc"): "server_value",
    ("pcap", "server_cert_not_after_utc"): "server_value",
    ("pcap", "tls_cert_not_after"): "server_value",
    ("pcap", "tls_leaf_cert_not_after_utc"): "server_value",
    ("pcap", "tls_cert_expiry_utc"): "server_value",
    ("pcap", "tls_cert_not_before_utc"): "server_value",
    ("pcap", "tls_certificate_not_before_utc"): "server_value",
    ("pcap", "server_cert_not_before_utc"): "server_value",
    ("pcap", "tls_cert_not_before"): "server_value",
    ("pcap", "tls_leaf_cert_not_before_utc"): "server_value",
    ("pcap", "server_cert_fingerprints"): "server_value",
    ("pcap", "tls_server_cert_fingerprints"): "server_value",
    ("pcap", "server_cert_sha256_fingerprints"): "server_value",
    ("pcap", "server_cert_sha256s"): "server_value",
    ("pcap", "tls_server_cert_sha256s"): "server_value",
    ("pcap", "server_certificate_fingerprints"): "server_value",
}

_GREASE = frozenset(0x0A0A + 0x1010 * i for i in range(16))
_TV = {0x0300: "SSLv3", 0x0301: "TLSv1.0", 0x0302: "TLSv1.1", 0x0303: "TLSv1.2", 0x0304: "TLSv1.3"}
_LINE = re.compile(r"^([A-Z][A-Z0-9_]*) ([0-9A-Fa-f]{16,}) ([0-9A-Fa-f]{16,})$")
_TLS13 = ("CLIENT_HANDSHAKE_TRAFFIC_SECRET", "SERVER_HANDSHAKE_TRAFFIC_SECRET", "CLIENT_TRAFFIC_SECRET_0",
          "SERVER_TRAFFIC_SECRET_0", "EXPORTER_SECRET", "EARLY_EXPORTER_SECRET", "CLIENT_EARLY_TRAFFIC_SECRET")


# ---------------------------------------------------------------- keylog text / pcapng DSB

def _dsbs(data):
    """[(secrets_type, payload)] of every pcapng Decryption Secrets Block (type 0x0000000A), or None (not pcapng)."""
    if len(data) < 28 or data[:4] != b"\x0a\x0d\x0d\x0a":
        return None
    out, o, e = [], 0, "<"
    while o + 12 <= len(data):
        bt = data[o:o + 4]
        if bt == b"\x0a\x0d\x0d\x0a":
            bom = data[o + 8:o + 12]
            e = "<" if bom == b"\x4d\x3c\x2b\x1a" else ">" if bom == b"\x1a\x2b\x3c\x4d" else None
            if e is None:
                break
        t, ln = struct.unpack_from(e + "II", data, o)
        if ln < 12 or ln % 4 or o + ln > len(data):
            break
        if t == 0x0000000A and ln >= 20:
            st, sl = struct.unpack_from(e + "II", data, o + 8)
            out.append((st, bytes(data[o + 16:o + 16 + min(sl, ln - 20)])))
        o += ln
    return out


def _keylog_lines(data):
    """[(label, client_random_lower, secret)] of an NSS key log; a pcapng contributes its TLSK DSB payloads."""
    if not data:
        return []
    d = _dsbs(data)
    if d is not None:
        data = b"\n".join(p for t, p in d if t == 0x544C534B)
    if b"\x00" in data[:4096]:
        return []
    out = []
    for raw in data.decode("latin-1").splitlines():
        m = _LINE.match(raw.strip())
        if m:
            out.append((m.group(1), m.group(2).lower(), m.group(3).lower()))
    return out


def _sorted_or_none(vals):
    v = sorted(set(vals))
    return v if v else "none"


_KEYLOG = {
    "line_count": lambda ls: len(ls),
    "client_randoms": lambda ls: _sorted_or_none(r for lb, r, _s in ls if lb != "RSA"),
    "client_random_count": lambda ls: len({r for lb, r, _s in ls if lb != "RSA"}),
    "first_client_random": lambda ls: next((r for lb, r, _s in ls if lb != "RSA"), "none"),
    "labels": lambda ls: _sorted_or_none(lb for lb, _r, _s in ls),
    "label_count": lambda ls: len({lb for lb, _r, _s in ls}),
    "label_counts": lambda ls: dict(sorted(collections.Counter(lb for lb, _r, _s in ls).items())) or "none",
    "client_random_line_count": lambda ls: sum(1 for lb, _r, _s in ls if lb == "CLIENT_RANDOM"),
    "tls13_secrets_present": lambda ls: any(lb in _TLS13 for lb, _r, _s in ls),
}
_KL_ALIAS = {
    "line_count": "line_count", "entry_count": "line_count", "secret_count": "line_count",
    "key_line_count": "line_count", "number_of_lines": "line_count", "record_count": "line_count",
    "client_randoms": "client_randoms", "client_random_list": "client_randoms",
    "unique_client_randoms": "client_randoms",
    "client_random_count": "client_random_count", "unique_client_random_count": "client_random_count",
    "session_count": "client_random_count",
    "first_client_random": "first_client_random",
    "labels": "labels", "label_set": "labels", "secret_labels": "labels", "label_names": "labels",
    "unique_labels": "labels", "secret_types": "labels",
    "label_count": "label_count", "unique_label_count": "label_count",
    "label_counts": "label_counts",
    "client_random_line_count": "client_random_line_count",
    "tls13_secrets_present": "tls13_secrets_present", "has_tls13_secrets": "tls13_secrets_present",
}


def keylog_value(data, ctx):
    """sslkeylog.<field>: NSS key log lines `<LABEL> <client_random hex> <secret hex>` (comments/blank skipped)."""
    if data is None:
        return None
    kind = _KL_ALIAS.get((ctx or {}).get("field") or "")
    if kind is None:
        return None
    ls = _keylog_lines(data)
    if not ls:
        return False if kind == "tls13_secrets_present" else "none"
    return _KEYLOG[kind](ls)


_DSB_ALIAS = {
    "dsb_keylog_line_count": "line_count", "keylog_line_count": "line_count",
    "embedded_keylog_line_count": "line_count", "tls_keylog_line_count": "line_count",
    "dsb_client_randoms": "client_randoms", "keylog_client_randoms": "client_randoms",
    "embedded_keylog_client_randoms": "client_randoms",
    "dsb_client_random_count": "client_random_count", "keylog_client_random_count": "client_random_count",
    "dsb_labels": "labels", "keylog_labels": "labels", "embedded_keylog_labels": "labels",
    "dsb_secret_labels": "labels",
}


def dsb_value(data, ctx):
    """pcapng.<dsb field>: Decryption Secrets Blocks (block type 0x0000000A) and the TLS key log they embed."""
    if data is None:
        return None
    field = (ctx or {}).get("field") or ""
    d = _dsbs(data) or []
    if field in ("dsb_count", "decryption_secrets_block_count", "dsb_block_count"):
        return len(d)
    if field in ("dsb_present", "has_decryption_secrets", "has_dsb", "decryption_secrets_present"):
        return bool(d)
    if field in ("dsb_secrets_type_u32_hex", "decryption_secrets_type_u32_hex"):
        return Hex(d[0][0], 8) if d else "none"
    if field in ("dsb_secrets_length", "dsb_secrets_length_bytes"):
        return len(d[0][1]) if d else "none"
    kind = _DSB_ALIAS.get(field)
    if kind is None:
        return None
    ls = _keylog_lines(data) if d else []
    if not ls:
        return 0 if kind.endswith("_count") else "none"
    return _KEYLOG[kind](ls)


# ---------------------------------------------------------------- ServerHello / server Certificate

def _server_hello(b):
    """(legacy_version, negotiated_version, cipher, [ext types]) of a ServerHello body, or None."""
    if len(b) < 38:
        return None
    ver, = struct.unpack_from("!H", b, 0)
    o = 34
    o += 1 + b[o]
    if o + 3 > len(b):
        return None
    cs, = struct.unpack_from("!H", b, o)
    o += 3                                              # cipher + compression method
    exts, neg = [], ver
    if o + 2 <= len(b):
        el, = struct.unpack_from("!H", b, o)
        p, end = o + 2, min(len(b), o + 2 + el)
        while p + 4 <= end:
            t, ln = struct.unpack_from("!HH", b, p)
            if t == 43 and ln == 2:
                neg, = struct.unpack_from("!H", b, p + 4)
            exts.append(t)
            p += 4 + ln
    return ver, neg, cs, exts


def _chain(b):
    if len(b) < 3:
        return []
    total = int.from_bytes(b[0:3], "big")
    o, end, chain = 3, min(len(b), 3 + total), []
    while o + 3 <= end:
        ln = int.from_bytes(b[o:o + 3], "big")
        if o + 3 + ln > end:
            break
        chain.append(bytes(b[o + 3:o + 3 + ln]))
        o += 3 + ln
    return chain


def _sessions(data):
    """[(ts, server_hello tuple, server chain)] ordered by the ServerHello's first segment time, or None."""
    from .pcap_app import _parse, _reassemble
    from .pcap_flows import _ip, _l3
    recs = _parse(data)
    if recs is None:
        return None
    streams = collections.OrderedDict()
    for i, (lt, sec, frac, res, _incl, _orig, d) in enumerate(recs):
        try:
            l3 = _l3(lt, d)
            ip = _ip(d, l3[1], l3[0]) if l3 and l3[0] in (0x0800, 0x86DD) else None
            if ip is None or ip[3] is None or ip[2] != 6:
                continue
            src, dst, _proto, l4 = ip
            if l3[0] == 0x0800:
                tot, = struct.unpack_from("!H", d, l3[1] + 2)
                end = min(len(d), l3[1] + tot) if tot >= 20 else len(d)
            else:
                pl, = struct.unpack_from("!H", d, l3[1] + 4)
                end = min(len(d), l3[1] + 40 + pl) if pl else len(d)
            if l4 + 20 > end:
                continue
            sp, dp, seq = struct.unpack_from("!HHI", d, l4)
            p = bytes(d[l4 + (d[l4 + 12] >> 4) * 4:end])
            if p:
                streams.setdefault((src, sp, dst, dp), [i, []])[1].append((seq, p))
        except (struct.error, IndexError, ValueError, TypeError):
            continue
    out = []
    for _key, (ts, segs) in streams.items():
        try:
            s = _reassemble(segs)
            if len(s) < 6 or s[0] != 22 or s[1] != 3:
                continue
            o, hs = 0, bytearray()
            while o + 5 <= len(s):
                ct, ln = s[o], struct.unpack_from("!H", s, o + 3)[0]
                if ct not in (20, 21, 22, 23) or s[o + 1] != 3 or ct == 20:
                    break
                if ct == 22:
                    hs += s[o + 5:o + 5 + ln]
                o += 5 + ln
            p, sh, chain = 0, None, []
            while p + 4 <= len(hs):
                t, ln = hs[p], int.from_bytes(hs[p + 1:p + 4], "big")
                body = bytes(hs[p + 4:p + 4 + ln])
                if t == 2 and sh is None:
                    sh = _server_hello(body)
                elif t == 11 and sh is not None and not chain:
                    chain = _chain(body)
                elif t not in (12, 13, 14, 16, 4, 8, 2, 11):
                    break
                p += 4 + ln
            if sh is not None:
                out.append((ts, sh, chain))
        except (struct.error, IndexError, ValueError):
            continue
    out.sort(key=lambda x: x[0])
    return out


def _ja3s(sh):
    ver, _neg, cs, exts = sh
    return "%d,%d,%s" % (ver, cs, "-".join(str(t) for t in exts if t not in _GREASE))


def _one_or_list(vals):
    """Singular field: the value when every session agrees, else the sorted distinct list."""
    v = sorted(set(vals))
    return "none" if not v else v[0] if len(v) == 1 else v


def _leaf(sess, fn):
    for _ts, _sh, chain in sess:
        if chain:
            v = fn(chain[0], {})
            if v not in (None, "none"):
                return v
    return "none"


_SRV_ALIAS = {}
for _k, _names in {
    "ja3s": ("tls_ja3s_md5", "ja3s_md5", "tls_ja3s", "ja3s", "ja3s_hash", "tls_ja3s_hash"),
    "ja3s_list": ("tls_ja3s_md5s", "ja3s_hashes", "tls_ja3s_hashes", "ja3s_md5s"),
    "ja3s_first": ("tls_ja3s_first", "ja3s_first", "first_ja3s", "tls_ja3s_md5_first"),
    "ja3s_string": ("tls_ja3s_string", "ja3s_string", "tls_ja3s_full", "ja3s_full"),
    "ja3s_strings": ("tls_ja3s_strings", "ja3s_strings"),
    "cipher": ("tls_cipher_suite", "tls_server_cipher_suite", "server_cipher_suite", "tls_cipher_suite_u16_hex",
               "server_cipher_suite_u16_hex", "tls_server_cipher_suite_u16_hex", "tls_ciphersuite",
               "selected_cipher_suite", "tls_selected_cipher_suite", "negotiated_cipher_suite",
               "tls_negotiated_cipher_suite", "server_hello_cipher_suite", "server_hello_cipher_suite_u16_hex"),
    "ciphers": ("tls_cipher_suites", "server_cipher_suites", "tls_server_cipher_suites",
                "negotiated_cipher_suites", "tls_negotiated_cipher_suites"),
    "sh_count": ("tls_server_hello_count", "server_hello_count", "tls_serverhello_count"),
    "neg_version": ("tls_negotiated_version", "tls_server_version", "negotiated_tls_version"),
    "neg_versions": ("tls_negotiated_versions", "tls_server_versions"),
    "serial": ("tls_cert_serial_hex", "tls_cert_serial_number_hex", "tls_certificate_serial_hex",
               "tls_certificate_serial_number_hex", "server_cert_serial_hex", "tls_leaf_cert_serial_hex"),
    "not_after": ("tls_cert_not_after_utc", "tls_certificate_not_after_utc", "server_cert_not_after_utc",
                  "tls_cert_not_after", "tls_leaf_cert_not_after_utc", "tls_cert_expiry_utc"),
    "not_before": ("tls_cert_not_before_utc", "tls_certificate_not_before_utc", "server_cert_not_before_utc",
                   "tls_cert_not_before", "tls_leaf_cert_not_before_utc"),
    "fingerprints": ("server_cert_fingerprints", "tls_server_cert_fingerprints", "server_cert_sha256_fingerprints",
                     "server_cert_sha256s", "tls_server_cert_sha256s", "server_certificate_fingerprints"),
}.items():
    for _n in _names:
        _SRV_ALIAS[_n] = _k


def server_value(data, ctx):
    """pcap.<field> / pcapng.<field>: ServerHello JA3S / cipher / version and the server leaf certificate."""
    if data is None:
        return None
    kind = _SRV_ALIAS.get((ctx or {}).get("field") or "")
    if kind is None:
        return None
    sess = _sessions(data)
    if sess is None:
        return "none"
    shs = [sh for _t, sh, _c in sess]
    from .x509 import not_after_utc, not_before_utc, serial_hex, sha256_fingerprint
    md5 = lambda sh: hashlib.md5(_ja3s(sh).encode()).hexdigest()  # noqa: E731
    if kind == "sh_count":
        return len(shs)
    if not shs:
        return "none"
    if kind == "ja3s":
        return _one_or_list(md5(sh) for sh in shs)
    if kind == "ja3s_list":
        return _sorted_or_none(md5(sh) for sh in shs)
    if kind == "ja3s_first":
        return md5(shs[0])
    if kind == "ja3s_string":
        return _one_or_list(_ja3s(sh) for sh in shs)
    if kind == "ja3s_strings":
        return _sorted_or_none(_ja3s(sh) for sh in shs)
    if kind == "cipher":
        v = sorted({sh[2] for sh in shs})
        return Hex(v[0], 4) if len(v) == 1 else ["0x%04x" % c for c in v]
    if kind == "ciphers":
        return ["0x%04x" % c for c in sorted({sh[2] for sh in shs})]
    if kind == "neg_version":
        return _one_or_list(_TV.get(sh[1], "0x%04x" % sh[1]) for sh in shs)
    if kind == "neg_versions":
        return _sorted_or_none(_TV.get(sh[1], "0x%04x" % sh[1]) for sh in shs)
    if kind == "serial":
        return _leaf(sess, serial_hex)
    if kind == "not_after":
        return _leaf(sess, not_after_utc)
    if kind == "not_before":
        return _leaf(sess, not_before_utc)
    if kind == "fingerprints":
        return _sorted_or_none(v for _t, _sh, ch in sess if ch for v in [sha256_fingerprint(ch[0], {})]
                               if v not in (None, "none"))
    return None
