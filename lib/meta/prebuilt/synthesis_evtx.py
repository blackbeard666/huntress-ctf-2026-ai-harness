"""Cross-LOG synthesis over several EVTX members (prebuilt, SPECULATIVE; the spelling was never GM-verified).
Coverage-atlas row "evtx-multi-log-synthesis" (D24 flavor: "logs from several hosts have been duplicated, truncated,
and bundled with reports ... find the selectively shortened timeline"). Ids `metadata-day-NN-synthesis-<key>`.
Members come from the question's `Files: [...]` list (parsed like lib.meta.synthesis.digest_order), read through
ctx["read"], else from `data` when the artifact IS the container zip (all members, zip order, when no Files list).
Only members with the ElfFile magic take part (reports / renamed impostors / legacy .evt "LfLe" are skipped).
Per log, prebuilt/evtx_integrity.analyse() (the evtx.py record walk): walked (EventRecordID, written FILETIME)
pairs, header-vs-length truncation, id gaps; host = <Computer> of the first physical record (evtx_binxml BinXML
render of that one record; fallback: the UTF-16 text node after the "Computer" name in the record's template).
Fields (names verbatim as listed / stored in the zip; lists and maps -> compact JSON; nothing applies -> "none"):
  duplicate_groups = groups (size >= 2) of logs whose walked id+time sequences are identical: sorted lists of sorted
    names; duplicate_of = the ORIGINAL of the lone duplicate group (shortest basename, then name) -- or, when the
    question names a member of a group, the group's other member(s);
  truncated_member = the log cut short (file shorter than header chunk_count * 64 KiB, or a record crossing EOF);
    a JSON list when several are;
  shortened_member = the log with EventRecordID gaps (several -> fewest walked records, then name);
  host_groups = {Computer: [sorted names]} (keys sorted);
  record_count_order = names by walked record count ascending, ties by name ("descending" in the text reverses);
  earliest_member / latest_member = the log whose FIRST written time (record header FILETIME, lowest id) is the
    earliest / latest, ties by name.
A set with >= 1 prefetch trace hands host_groups / host_group_map / files_by_host to synthesis_prefetch.py;
a set with no ElfFile member but >= 1 regf hive hands host_groups / *_by_host / earliest / latest to synthesis_regf.py."""
import re
import struct

FIELDS = {
    ("synthesis", "duplicate_groups"): "evtx_synthesis_value",
    ("synthesis", "duplicate_log_groups"): "evtx_synthesis_value",
    ("synthesis", "duplicate_member_groups"): "evtx_synthesis_value",
    ("synthesis", "identical_log_groups"): "evtx_synthesis_value",
    ("synthesis", "duplicate_of"): "evtx_synthesis_value",
    ("synthesis", "duplicate_original"): "evtx_synthesis_value",
    ("synthesis", "original_of_duplicate"): "evtx_synthesis_value",
    ("synthesis", "truncated_member"): "evtx_synthesis_value",
    ("synthesis", "truncated_file"): "evtx_synthesis_value",
    ("synthesis", "truncated_log"): "evtx_synthesis_value",
    ("synthesis", "truncated_filename"): "evtx_synthesis_value",
    ("synthesis", "shortened_member"): "evtx_synthesis_value",
    ("synthesis", "shortened_file"): "evtx_synthesis_value",
    ("synthesis", "shortened_log"): "evtx_synthesis_value",
    ("synthesis", "shortened_timeline_member"): "evtx_synthesis_value",
    ("synthesis", "shortened_timeline"): "evtx_synthesis_value",
    ("synthesis", "gapped_member"): "evtx_synthesis_value",
    ("synthesis", "host_groups"): "evtx_synthesis_value",
    ("synthesis", "host_group_map"): "evtx_synthesis_value",
    ("synthesis", "computer_groups"): "evtx_synthesis_value",
    ("synthesis", "computer_name_groups"): "evtx_synthesis_value",
    ("synthesis", "logs_by_host"): "evtx_synthesis_value",
    ("synthesis", "files_by_host"): "evtx_synthesis_value",
    ("synthesis", "record_count_order"): "evtx_synthesis_value",
    ("synthesis", "event_count_order"): "evtx_synthesis_value",
    ("synthesis", "earliest_member"): "evtx_synthesis_value",
    ("synthesis", "earliest_log"): "evtx_synthesis_value",
    ("synthesis", "latest_member"): "evtx_synthesis_value",
    ("synthesis", "latest_log"): "evtx_synthesis_value",
}

_COMPUTER = "Computer".encode("utf-16-le")


def _host_scan(rec):
    """Fallback: the literal text node (0x05 0x01 len16 UTF-16) following the "Computer" name in one record."""
    i = rec.find(_COMPUTER)
    while i >= 0:
        j = rec.find(b"\x05\x01", i + len(_COMPUTER), i + len(_COMPUTER) + 48)
        if j >= 0 and j + 4 <= len(rec):
            n, = struct.unpack_from("<H", rec, j + 2)
            if 0 < n < 256 and j + 4 + 2 * n <= len(rec):
                return rec[j + 4:j + 4 + 2 * n].decode("utf-16-le", "replace").strip() or None
        i = rec.find(_COMPUTER, i + 1)
    return None


def _host(b, recs):
    if not recs:
        return None
    coff, roff = recs[0]
    size, = struct.unpack_from("<I", b, roff + 4)
    try:
        from .evtx_binxml import _Chunk, _event, render_fragment
        p = roff - coff
        h = _event(render_fragment(_Chunk(b[coff:coff + 0x10000]), p + 24, p + size - 4)).get("computer")
        if h:
            return h
    except Exception:  # noqa: BLE001 - damaged BinXML -> the string scan
        pass
    return _host_scan(b[roff:roff + size])


def profile(b):
    """{seq, n, host, cut, gaps, t} of one EVTX member, or None (not ElfFile)."""
    from .evtx import _records
    from .evtx_integrity import analyse
    b = bytes(b or b"")
    if b[:8] != b"ElfFile\x00":
        return None
    a = analyse(b)
    if a is None:
        return None
    recs = _records(b)
    rows = sorted(struct.unpack_from("<QQ", b, r + 8) for _, r in recs)
    return {"seq": tuple(rows), "n": len(rows), "host": _host(b, recs), "cut": a["truncated"],
            "gaps": bool(a["missing"]), "t": rows[0][1] if rows else None}


def _base_len(n):
    return len(n.rsplit("/", 1)[-1])


def synth_value_of(names, get_bytes, field, text="", member=""):
    logs = {}
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        p = profile(b)
        if p is not None:
            logs[n] = p
    if not logs:
        return "none"
    f = field or ""
    if f.startswith(("duplicate", "identical")) or f == "original_of_duplicate":
        g = {}
        for n, p in logs.items():
            if p["n"]:
                g.setdefault(p["seq"], []).append(n)
        dups = sorted(sorted(v) for v in g.values() if len(v) > 1)
        if f.endswith("groups"):
            return dups or "none"
        mine = [grp for grp in dups if member in grp]
        if mine:
            rest = [n for n in mine[0] if n != member]
            return rest[0] if len(rest) == 1 else rest
        if len(dups) != 1:
            return "none"
        return min(dups[0], key=lambda n: (_base_len(n), n))
    if f.startswith("truncated"):
        tr = sorted(n for n, p in logs.items() if p["cut"])
        return (tr[0] if len(tr) == 1 else tr) if tr else "none"
    if f.startswith(("shortened", "gapped")):
        sh = sorted((p["n"], n) for n, p in logs.items() if p["gaps"])
        return sh[0][1] if sh else "none"
    if f in ("host_groups", "host_group_map", "computer_groups", "computer_name_groups", "logs_by_host",
             "files_by_host"):
        g = {}
        for n, p in logs.items():
            if p["host"]:
                g.setdefault(p["host"], []).append(n)
        return {k: sorted(g[k]) for k in sorted(g)} or "none"
    if f in ("record_count_order", "event_count_order"):
        desc = bool(re.search(r"\b(descending|largest first|most first)\b", text, re.I))
        return [n for _, n in sorted(((-p["n"] if desc else p["n"]), n) for n, p in logs.items())]
    dated = [(p["t"], n) for n, p in logs.items() if p["t"] is not None]
    if not dated:
        return "none"
    if f.startswith("earliest"):
        return min(dated)[1]
    if f.startswith("latest"):
        return min(dated, key=lambda t: (-t[0], t[1]))[1]
    return None


def evtx_synthesis_value(data, ctx):
    """synthesis.<multi-log EVTX field> (see the module docstring)."""
    try:
        from .synthesis_media import _source
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        if not names:
            return "none"
        q = ctx.get("question")
        text = re.sub(r"Files:\s*\[.*?\]", "", str((q.get("question") if isinstance(q, dict) else q) or ""), flags=re.S)
        field = ctx.get("field") or ""
        if field in ("host_groups", "host_group_map", "files_by_host"):
            from .synthesis_prefetch import any_trace, prefetch_synthesis_value
            if any_trace(names, read):
                return prefetch_synthesis_value(data, ctx)   # prefetch traces: the cross-trace host synthesis
        if field.startswith(("host", "computer", "logs_by", "files_by", "earliest", "latest")):
            from .synthesis_regf import any_regf, regf_synthesis_value
            if not any(bytes((read(n) or b"")[:8]) == b"ElfFile\x00" for n in names) and any_regf(names, read):
                return regf_synthesis_value(data, ctx)   # a hive set, no EVTX: the cross-hive synthesis
        v = synth_value_of(names, read, field, text, ctx.get("member") or "")
        return v if (v != "none" or from_zip) else None
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
