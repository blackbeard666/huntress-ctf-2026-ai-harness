"""PCAP / PCAPNG malformed-capture detection (prebuilt, SPECULATIVE; D27 flavor "reject malformed captures"; the
spelling was never GM-verified). Pure struct; reuses prebuilt/pcap.py's _unwrap (gz/zstd/lz4/xz) and _opts.

Per file (fmt pcap or pcapng, either container answered from its bytes), one structural walk:
  classic pcap: 24-byte global header, records ts_sec/ts_frac/incl_len/orig_len (16 bytes; Kuznetzov 24) + incl_len.
  pcapng: blocks type/total_len/body/total_len; SHB (BOM 0x1a2b3c4d, major 1), IDB (linktype, snaplen), EPB 6
  (if_id, ts hi/lo, caplen, origlen), obsolete PB 2, SPB 3, ISB 5 (if_id, ts, options isb_ifrecv 4 / isb_ifdrop 5 /
  isb_osdrop 7, u64).
malformed_reason = the FIRST anomaly in file order, one of:
  bad_magic       header shaped like a capture (pcap version 2.x at @4, or a pcapng SHB type) but magic/BOM unknown
  bad_version     pcap major != 2 (libpcap's PCAP_VERSION_MAJOR; Wireshark itself accepts 3+) / pcapng SHB major != 1
  truncated_record        a record's header is complete but its incl_len data (or a pcapng block) runs past EOF
  trailing_bytes          bytes after the last complete record, too few for a record/block header
  incl_len_exceeds_snaplen  incl_len (EPB caplen) > the header/IDB snaplen (snaplen 0 = unlimited)
  incl_len_exceeds_orig_len incl_len > orig_len
  block_length_mismatch   pcapng trailing total length != leading one, length < 12 / not a multiple of 4, or an
                          EPB/PB whose caplen does not fit its block
  undefined_interface     EPB/PB/ISB interface id with no IDB in its section
is_malformed / is_valid = bool (a non-monotonic timestamp alone is NOT malformed). Counts (ints):
  complete_record_count (= packet_count of prebuilt/pcap.py: records walked until the first truncation),
  truncated_record_count (0/1: the walk stops at the cut record), trailing_bytes_count (file length - end of the
  last complete record/block, 0 when it ends cleanly; covers the partial record too), records_exceeding_snaplen_count,
  records_exceeding_orig_len_count, non_monotonic_timestamp_count (record time < the previous record's, per file
  order), max_incl_len (largest walked incl_len/caplen; "none" with no records).
ISB (pcapng): isb_ifrecv / isb_ifdrop / isb_osdrop = the LAST ISB's value per interface, summed over interfaces
("none" when no ISB carries it); isb_ifrecv_matches = isb_ifrecv == walked EPB/PB count of those interfaces;
isb_ifrecv_mismatch = its negation; isb_walked_packet_count = that walked count.
Not a capture at all (text, snoop, renamed impostor) -> "none".

synthesis (several members from the question's `Files: [...]` / the container zip, via synthesis_media._source):
  malformed_capture_names (+ aliases) = sorted JSON list of members whose walk is malformed; members that are not
  captures count as malformed (bad_magic) only when NAMED like a capture (.pcap/.pcapng/.cap/.ntar, optionally
  .gz/.zst/.lz4/.xz); other non-captures are ignored. valid_capture_names / *_count, malformed_capture_count."""
import re
import struct

FIELDS = {
    ("pcap", "is_malformed"): "integrity_value", ("pcapng", "is_malformed"): "integrity_value",
    ("pcap", "malformed"): "integrity_value", ("pcapng", "malformed"): "integrity_value",
    ("pcap", "is_corrupt"): "integrity_value", ("pcapng", "is_corrupt"): "integrity_value",
    ("pcap", "is_corrupted"): "integrity_value", ("pcapng", "is_corrupted"): "integrity_value",
    ("pcap", "is_valid"): "integrity_value", ("pcapng", "is_valid"): "integrity_value",
    ("pcap", "valid"): "integrity_value", ("pcapng", "valid"): "integrity_value",
    ("pcap", "is_well_formed"): "integrity_value", ("pcapng", "is_well_formed"): "integrity_value",
    ("pcap", "well_formed"): "integrity_value", ("pcapng", "well_formed"): "integrity_value",
    ("pcap", "malformed_reason"): "integrity_value", ("pcapng", "malformed_reason"): "integrity_value",
    ("pcap", "malformation_reason"): "integrity_value", ("pcapng", "malformation_reason"): "integrity_value",
    ("pcap", "malformation"): "integrity_value", ("pcapng", "malformation"): "integrity_value",
    ("pcap", "corruption_reason"): "integrity_value", ("pcapng", "corruption_reason"): "integrity_value",
    ("pcap", "rejection_reason"): "integrity_value", ("pcapng", "rejection_reason"): "integrity_value",
    ("pcap", "reject_reason"): "integrity_value", ("pcapng", "reject_reason"): "integrity_value",
    ("pcap", "error_reason"): "integrity_value", ("pcapng", "error_reason"): "integrity_value",
    ("pcap", "truncated_record_count"): "integrity_value", ("pcapng", "truncated_record_count"): "integrity_value",
    ("pcap", "truncated_packet_count"): "integrity_value", ("pcapng", "truncated_packet_count"): "integrity_value",
    ("pcap", "truncated_records"): "integrity_value", ("pcapng", "truncated_records"): "integrity_value",
    ("pcap", "is_truncated"): "integrity_value", ("pcapng", "is_truncated"): "integrity_value",
    ("pcap", "truncated"): "integrity_value", ("pcapng", "truncated"): "integrity_value",
    ("pcap", "trailing_bytes_count"): "integrity_value", ("pcapng", "trailing_bytes_count"): "integrity_value",
    ("pcap", "trailing_bytes"): "integrity_value", ("pcapng", "trailing_bytes"): "integrity_value",
    ("pcap", "trailing_byte_count"): "integrity_value", ("pcapng", "trailing_byte_count"): "integrity_value",
    ("pcap", "trailing_garbage_bytes"): "integrity_value", ("pcapng", "trailing_garbage_bytes"): "integrity_value",
    ("pcap", "has_trailing_bytes"): "integrity_value", ("pcapng", "has_trailing_bytes"): "integrity_value",
    ("pcap", "complete_record_count"): "integrity_value", ("pcapng", "complete_record_count"): "integrity_value",
    ("pcap", "complete_packet_count"): "integrity_value", ("pcapng", "complete_packet_count"): "integrity_value",
    ("pcap", "valid_record_count"): "integrity_value", ("pcapng", "valid_record_count"): "integrity_value",
    ("pcap", "valid_packet_count"): "integrity_value", ("pcapng", "valid_packet_count"): "integrity_value",
    ("pcap", "records_exceeding_snaplen_count"): "integrity_value",
    ("pcapng", "records_exceeding_snaplen_count"): "integrity_value",
    ("pcap", "packets_exceeding_snaplen_count"): "integrity_value",
    ("pcapng", "packets_exceeding_snaplen_count"): "integrity_value",
    ("pcap", "oversized_record_count"): "integrity_value", ("pcapng", "oversized_record_count"): "integrity_value",
    ("pcap", "records_exceeding_orig_len_count"): "integrity_value",
    ("pcapng", "records_exceeding_orig_len_count"): "integrity_value",
    ("pcap", "non_monotonic_timestamp_count"): "integrity_value",
    ("pcapng", "non_monotonic_timestamp_count"): "integrity_value",
    ("pcap", "out_of_order_timestamp_count"): "integrity_value",
    ("pcapng", "out_of_order_timestamp_count"): "integrity_value",
    ("pcap", "out_of_order_packet_count"): "integrity_value",
    ("pcapng", "out_of_order_packet_count"): "integrity_value",
    ("pcap", "time_out_of_order_count"): "integrity_value", ("pcapng", "time_out_of_order_count"): "integrity_value",
    ("pcap", "max_incl_len"): "integrity_value", ("pcapng", "max_incl_len"): "integrity_value",
    ("pcap", "max_caplen"): "integrity_value", ("pcapng", "max_caplen"): "integrity_value",
    ("pcap", "max_captured_length"): "integrity_value", ("pcapng", "max_captured_length"): "integrity_value",
    ("pcap", "largest_incl_len"): "integrity_value", ("pcapng", "largest_incl_len"): "integrity_value",
    ("pcap", "isb_ifrecv"): "integrity_value", ("pcapng", "isb_ifrecv"): "integrity_value",
    ("pcap", "isb_ifdrop"): "integrity_value", ("pcapng", "isb_ifdrop"): "integrity_value",
    ("pcap", "isb_osdrop"): "integrity_value", ("pcapng", "isb_osdrop"): "integrity_value",
    ("pcap", "isb_ifrecv_matches"): "integrity_value", ("pcapng", "isb_ifrecv_matches"): "integrity_value",
    ("pcap", "isb_ifrecv_mismatch"): "integrity_value", ("pcapng", "isb_ifrecv_mismatch"): "integrity_value",
    ("pcap", "isb_packet_count_mismatch"): "integrity_value",
    ("pcapng", "isb_packet_count_mismatch"): "integrity_value",
    ("pcap", "declared_vs_walked_mismatch"): "integrity_value",
    ("pcapng", "declared_vs_walked_mismatch"): "integrity_value",
    ("pcap", "isb_walked_packet_count"): "integrity_value", ("pcapng", "isb_walked_packet_count"): "integrity_value",
    ("synthesis", "malformed_capture_names"): "integrity_synthesis_value",
    ("synthesis", "malformed_captures"): "integrity_synthesis_value",
    ("synthesis", "malformed_capture_files"): "integrity_synthesis_value",
    ("synthesis", "malformed_capture_members"): "integrity_synthesis_value",
    ("synthesis", "malformed_pcap_names"): "integrity_synthesis_value",
    ("synthesis", "malformed_pcaps"): "integrity_synthesis_value",
    ("synthesis", "malformed_files"): "integrity_synthesis_value",
    ("synthesis", "malformed_members"): "integrity_synthesis_value",
    ("synthesis", "malformed_member_names"): "integrity_synthesis_value",
    ("synthesis", "malformed_file_names"): "integrity_synthesis_value",
    ("synthesis", "invalid_capture_names"): "integrity_synthesis_value",
    ("synthesis", "invalid_captures"): "integrity_synthesis_value",
    ("synthesis", "rejected_capture_names"): "integrity_synthesis_value",
    ("synthesis", "rejected_captures"): "integrity_synthesis_value",
    ("synthesis", "corrupt_capture_names"): "integrity_synthesis_value",
    ("synthesis", "corrupted_capture_names"): "integrity_synthesis_value",
    ("synthesis", "malformed_capture_count"): "integrity_synthesis_value",
    ("synthesis", "invalid_capture_count"): "integrity_synthesis_value",
    ("synthesis", "rejected_capture_count"): "integrity_synthesis_value",
    ("synthesis", "valid_capture_names"): "integrity_synthesis_value",
    ("synthesis", "valid_captures"): "integrity_synthesis_value",
    ("synthesis", "accepted_capture_names"): "integrity_synthesis_value",
    ("synthesis", "valid_capture_count"): "integrity_synthesis_value",
    ("synthesis", "accepted_capture_count"): "integrity_synthesis_value",
    ("synthesis", "well_formed_capture_count"): "integrity_synthesis_value",
}

_PCAP_MAGIC = {0xA1B2C3D4: (16, 6), 0xA1B23C4D: (16, 9), 0xA1B2CD34: (24, 6)}
_SHB = b"\x0a\x0d\x0d\x0a"
_CAP_NAME = re.compile(r"\.(pcap|pcapng|cap|ntar|dmp)(\.(gz|zst|lz4|xz))?$", re.I)


def _new(kind):
    return {"kind": kind, "reason": None, "complete": 0, "truncated": 0, "trailing": 0, "over_snap": 0,
            "over_orig": 0, "nonmono": 0, "max_incl": None, "isb": {}, "walked_if": {}}


def _flag(a, reason):
    if a["reason"] is None:
        a["reason"] = reason


def _rec(a, incl, orig, snap, ts):
    a["complete"] += 1
    a["max_incl"] = incl if a["max_incl"] is None else max(a["max_incl"], incl)
    if snap and incl > snap:
        a["over_snap"] += 1
        _flag(a, "incl_len_exceeds_snaplen")
    if orig is not None and incl > orig:
        a["over_orig"] += 1
        _flag(a, "incl_len_exceeds_orig_len")
    if ts is not None:
        if a.get("last_ts") is not None and ts < a["last_ts"]:
            a["nonmono"] += 1
        a["last_ts"] = ts


def _walk_pcap(b):
    e = None
    for x in "<>":
        if struct.unpack_from(x + "I", b, 0)[0] in _PCAP_MAGIC:
            e = x
            break
    if e is None:
        return None
    rh, digits = _PCAP_MAGIC[struct.unpack_from(e + "I", b, 0)[0]]
    a = _new("pcap")
    vmaj, = struct.unpack_from(e + "H", b, 4)
    snap, = struct.unpack_from(e + "I", b, 16)
    if vmaj != 2:
        _flag(a, "bad_version")
    off = 24
    while off < len(b):
        if off + rh > len(b):
            _flag(a, "trailing_bytes")
            break
        sec, frac, incl, orig = struct.unpack_from(e + "IIII", b, off)
        if off + rh + incl > len(b):
            a["truncated"] = 1
            _flag(a, "incl_len_exceeds_snaplen" if snap and incl > snap else "truncated_record")
            break
        _rec(a, incl, orig, snap, sec * 10 ** digits + frac)
        off += rh + incl
    a["trailing"] = len(b) - off
    return a


def _walk_pcapng(b):
    from .pcap import _opts
    if len(b) < 12 or bytes(b[:4]) != _SHB:
        return None
    a = _new("pcapng")
    off, e, idbs, sec_no = 0, "<", [], -1
    while off < len(b):
        if off + 12 > len(b):
            _flag(a, "trailing_bytes")
            break
        if bytes(b[off:off + 4]) == _SHB:
            bom = bytes(b[off + 8:off + 12])
            e = "<" if bom == b"\x4d\x3c\x2b\x1a" else ">" if bom == b"\x1a\x2b\x3c\x4d" else None
            if e is None:
                _flag(a, "bad_magic")
                break
            idbs, sec_no = [], sec_no + 1
            if off + 16 <= len(b) and struct.unpack_from(e + "H", b, off + 12)[0] != 1:
                _flag(a, "bad_version")
        btype, blen = struct.unpack_from(e + "II", b, off)
        if blen < 12 or blen % 4:
            _flag(a, "block_length_mismatch")
            break
        if off + blen > len(b):
            a["truncated"] = 1
            _flag(a, "truncated_record")
            break
        if struct.unpack_from(e + "I", b, off + blen - 4)[0] != blen:
            _flag(a, "block_length_mismatch")
            break
        body, end = off + 8, off + blen - 4
        if btype == 1 and end - body >= 8:
            lt, _r, snap = struct.unpack_from(e + "HHI", b, body)
            idbs.append(snap)
        elif btype in (6, 2):
            hdr = e + ("IIIII" if btype == 6 else "HHIIII")
            if end - body < 20:
                _flag(a, "block_length_mismatch")
            else:
                v = struct.unpack_from(hdr, b, body)
                ifid, hi, lo, cap, orig = (v[0],) + v[-4:]
                if body + 20 + cap > end:
                    _flag(a, "block_length_mismatch")
                if ifid >= len(idbs):
                    _flag(a, "undefined_interface")
                a["walked_if"][(sec_no, ifid)] = a["walked_if"].get((sec_no, ifid), 0) + 1
                _rec(a, cap, orig, idbs[ifid] if ifid < len(idbs) else 0, (hi << 32) | lo)
        elif btype == 3 and end - body >= 4:
            orig, = struct.unpack_from(e + "I", b, body)
            cap = min(orig, idbs[0]) if idbs and idbs[0] else orig
            _rec(a, cap, None, 0, None)
        elif btype == 5 and end - body >= 12:
            ifid, = struct.unpack_from(e + "I", b, body)
            if ifid >= len(idbs):
                _flag(a, "undefined_interface")
            st = a["isb"].setdefault((sec_no, ifid), {})
            for code, val in _opts(b, body + 12, end, e):
                if code in (4, 5, 7) and len(val) >= 8:
                    st[code] = struct.unpack_from(e + "Q", val, 0)[0]
        off += blen
    a["trailing"] = len(b) - off
    return a


def _looks_capture(b):
    if len(b) >= 8 and bytes(b[:4]) == _SHB:
        return True
    return len(b) >= 24 and any(struct.unpack_from(x + "HH", b, 4) in ((2, 4), (2, 3), (2, 2)) for x in "<>")


def analyse(data):
    """The integrity record of one capture (see module doc), or None when the bytes are not a capture."""
    if not data:
        return None
    b = bytes(data)
    a = None
    for cand in (b, None):
        if cand is None:
            from .pcap import _unwrap
            cand = _unwrap(b)
            if not cand:
                break
        if len(cand) >= 4 and cand[:4] == _SHB:
            a = _walk_pcapng(cand)
        elif len(cand) >= 24:
            a = _walk_pcap(cand)
        if a is None and _looks_capture(cand):
            a = _new("pcapng" if cand[:4] == _SHB else "pcap")
            a["reason"] = "bad_magic"
        if a is not None:
            break
    return a


def _isb_sum(a, code):
    vals = [st[code] for st in a["isb"].values() if code in st]
    return sum(vals) if vals else None


def integrity_value(data, ctx):
    """pcap.<integrity field> / pcapng.<integrity field> (see the module docstring)."""
    try:
        a = analyse(data)
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
    if a is None:
        return "none" if data else None
    f = ctx.get("field") or ""
    bad = a["reason"] is not None
    if f in ("is_malformed", "malformed", "is_corrupt", "is_corrupted"):
        return bad
    if f in ("is_valid", "valid", "is_well_formed", "well_formed"):
        return not bad
    if f.endswith("reason") or f == "malformation":
        return a["reason"] or "none"
    if f in ("is_truncated", "truncated"):
        return bool(a["truncated"])
    if f.startswith("truncated"):
        return a["truncated"]
    if f == "has_trailing_bytes":
        return a["trailing"] > 0
    if f.startswith("trailing"):
        return a["trailing"]
    if f.startswith(("complete_", "valid_")):
        return a["complete"]
    if f in ("records_exceeding_snaplen_count", "packets_exceeding_snaplen_count", "oversized_record_count"):
        return a["over_snap"]
    if f == "records_exceeding_orig_len_count":
        return a["over_orig"]
    if f in ("non_monotonic_timestamp_count", "out_of_order_timestamp_count", "out_of_order_packet_count",
             "time_out_of_order_count"):
        return a["nonmono"]
    if f in ("max_incl_len", "max_caplen", "max_captured_length", "largest_incl_len"):
        return "none" if a["max_incl"] is None else a["max_incl"]
    if f.startswith("isb_") or f == "declared_vs_walked_mismatch":
        code = {"isb_ifrecv": 4, "isb_ifdrop": 5, "isb_osdrop": 7}.get(f)
        if code:
            v = _isb_sum(a, code)
            return "none" if v is None else v
        keys = [k for k, st in a["isb"].items() if 4 in st]
        if not keys:
            return "none"
        walked = sum(a["walked_if"].get(k, 0) for k in keys)
        if f == "isb_walked_packet_count":
            return walked
        match = sum(a["isb"][k][4] for k in keys) == walked
        return match if f == "isb_ifrecv_matches" else not match
    return None


def integrity_synthesis_value(data, ctx):
    """synthesis.malformed_capture_names / valid_capture_count / ... over several capture members."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        bad, good = [], []
        for n in names:
            b = read(n)
            if b is None:
                return None
            a = analyse(b)
            if a is None:
                if _CAP_NAME.search(n):
                    bad.append(n)
                continue
            (bad if a["reason"] else good).append(n)
        if not bad and not good:
            return "none" if from_zip else None
        f = ctx.get("field") or ""
        pick = sorted(good) if f.startswith(("valid", "accepted", "well_formed")) else sorted(bad)
        return len(pick) if f.endswith("_count") else pick
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
