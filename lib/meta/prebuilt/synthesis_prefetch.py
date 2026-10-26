"""Cross-TRACE prefetch synthesis: connect execution traces to hosts and executables (prebuilt, SPECULATIVE; the
spelling was never GM-verified). Coverage-atlas row "prefetch-host-synthesis" (D26 flavor "connect execution traces to
the correct hosts"). Ids `metadata-day-NN-synthesis-<key>`.
Members come from the question's `Files: [...]` list (parsed like lib.meta.synthesis.digest_order), read through
ctx["read"], else from `data` when the artifact IS the container zip (all members, zip order, when no Files list).
A member is a TRACE by magic only: SCCA @4 or a MAM wrapper that decompresses to SCCA (prebuilt/prefetch.py _scca);
names / extensions are never trusted. Per trace: header executable name (UTF-16LE @16), first volume entry (device
path, creation FILETIME, serial u32) and the newest non-zero last-run FILETIME slot.
HOST KEY of a trace = (volume serial, device path casefolded, volume creation FILETIME) of its FIRST volume.
Link evidence from sibling members (optional): LNK LinkInfo VolumeID DriveSerialNumber (u32) + TrackerDataBlock
(0xA0000003) MachineID (NetBIOS, NUL-terminated ANSI);
LinkInfo is ignored when LinkFlags ForceNoLinkInfo 0x100 is set, as LnkParse3 / the shell do;
NTFS VBR serial u64 @0x48 (low 32 bits = the prefetch / LNK volume serial). A trace's HOSTNAME = the MachineID of an
LNK whose serial equals the trace's volume serial (NetBIOS names upper-cased as Windows stores them). EVTX <Computer> /
hive ComputerName siblings carry no volume serial, so they are NOT used to link (TODO if a GM set needs it).
Fields (lists -> compact JSON; an empty answer -> "none"):
  host_groups (when the set holds traces; synthesis_evtx.py hands the shared key here) / prefetch_host_groups /
    trace_host_groups / volume_host_groups = list of sorted trace-name lists, one per host key, groups sorted by
    first name (singletons included);
  same_host_as_<member> = the OTHER traces sharing <member>'s host key, sorted ("none" when it is alone); <member> is
    matched on the id-normalised name (lowercase, every non-alnum run -> "_") or named in the question text; an LNK /
    VBR member resolves through its volume serial;
  renamed_traces / renamed_files / renamed_members = traces whose filename stem (basename minus ".pf" and the
    "-XXXXXXXX" hash suffix) differs (casefold) from the header executable name, Files order (sorted when the text
    says sorted / alphabetical);
  last_run_order / execution_order / ... = traces by newest last-run FILETIME, OLDEST first unless the text says
    descending / newest first / most recent first; ties by name; traces without a last run go last;
  odd_host / odd_host_trace / odd_trace = the lone trace whose host key no other trace shares (exactly one singleton
    beside a group of >= 2; otherwise None);
  host_of_<member> / hostname_of_<member> = the linked hostname of a trace ("none" when no LNK names its serial);
  traces_by_host / trace_host_map / prefetch_by_host = {hostname: sorted traces} (keys sorted; unlinked hosts keyed by
    "0x%08x" serial); files_by_host / host_group_map hand-offs answer this map too;
  host_count / distinct_host_count = number of distinct host keys among the traces."""
import re
import struct

FIELDS = {
    ("synthesis", "prefetch_host_groups"): "prefetch_synthesis_value",
    ("synthesis", "trace_host_groups"): "prefetch_synthesis_value",
    ("synthesis", "volume_host_groups"): "prefetch_synthesis_value",
    ("synthesis", "execution_host_groups"): "prefetch_synthesis_value",
    ("synthesis", "same_host_as_*"): "prefetch_synthesis_value",
    ("synthesis", "same_host_traces_as_*"): "prefetch_synthesis_value",
    ("synthesis", "renamed_traces"): "prefetch_synthesis_value",
    ("synthesis", "renamed_files"): "prefetch_synthesis_value",
    ("synthesis", "renamed_members"): "prefetch_synthesis_value",
    ("synthesis", "renamed_prefetch_files"): "prefetch_synthesis_value",
    ("synthesis", "renamed_prefetch"): "prefetch_synthesis_value",
    ("synthesis", "renamed_trace"): "prefetch_synthesis_value",
    ("synthesis", "last_run_order"): "prefetch_synthesis_value",
    ("synthesis", "last_run_time_order"): "prefetch_synthesis_value",
    ("synthesis", "last_execution_order"): "prefetch_synthesis_value",
    ("synthesis", "execution_order"): "prefetch_synthesis_value",
    ("synthesis", "run_order"): "prefetch_synthesis_value",
    ("synthesis", "run_time_order"): "prefetch_synthesis_value",
    ("synthesis", "odd_host"): "prefetch_synthesis_value",
    ("synthesis", "odd_host_trace"): "prefetch_synthesis_value",
    ("synthesis", "odd_host_member"): "prefetch_synthesis_value",
    ("synthesis", "odd_host_file"): "prefetch_synthesis_value",
    ("synthesis", "odd_trace"): "prefetch_synthesis_value",
    ("synthesis", "odd_volume"): "prefetch_synthesis_value",
    ("synthesis", "foreign_trace"): "prefetch_synthesis_value",
    ("synthesis", "host_of_*"): "prefetch_synthesis_value",
    ("synthesis", "hostname_of_*"): "prefetch_synthesis_value",
    ("synthesis", "traces_by_host"): "prefetch_synthesis_value",
    ("synthesis", "trace_host_map"): "prefetch_synthesis_value",
    ("synthesis", "prefetch_by_host"): "prefetch_synthesis_value",
    ("synthesis", "host_count"): "prefetch_synthesis_value",
    ("synthesis", "distinct_host_count"): "prefetch_synthesis_value",
}

_LNK_HDR = b"\x4c\x00\x00\x00\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46"
_TRACKER = b"\x60\x00\x00\x00\x03\x00\x00\xa0"


def trace(b):
    """{exe, key, serial, last} of a prefetch member, or None (not a trace / undecodable)."""
    from .prefetch import _scca, _last_runs, _utf16z, _volume
    s = _scca(b)
    if not isinstance(s, tuple):
        return None
    raw = s[0]
    if len(raw) < 84:
        return None
    ver = struct.unpack_from("<I", raw, 0)[0]
    vol = _volume(raw, ver)
    if not isinstance(vol, tuple):
        return None
    path, serial, ctime = vol
    runs = [t for t in (_last_runs(raw, ver) or []) if t]
    return {"exe": _utf16z(raw, 16, 60), "serial": serial, "key": (serial, (path or "").casefold(), ctime),
            "last": max(runs) if runs else None}


def lnk_link(b):
    """(volume serial | None, MachineID | None) of an LNK member, or None (not a shell link)."""
    b = bytes(b or b"")
    if len(b) < 0x4C or b[:20] != _LNK_HDR:
        return None
    flags, = struct.unpack_from("<I", b, 0x14)
    o, serial, host = 0x4C, None, None
    if flags & 1:
        o += 2 + struct.unpack_from("<H", b, o)[0]
    if flags & 2 and not flags & 0x100 and o + 16 <= len(b):   # ForceNoLinkInfo: LinkInfo ignored (MS-SHLLINK)
        lif, vio = struct.unpack_from("<I", b, o + 8)[0], struct.unpack_from("<I", b, o + 12)[0]
        if lif & 1 and o + vio + 12 <= len(b):
            serial = struct.unpack_from("<I", b, o + vio + 8)[0]
    i = b.find(_TRACKER, 0x4C)
    if i >= 0 and i + 32 <= len(b):
        mid = b[i + 16:i + 32].split(b"\0")[0].decode("latin-1").strip()
        host = mid.upper() or None
    return serial, host


def vbr_serial(b):
    b = bytes(b or b"")
    if len(b) >= 0x50 and b[3:11] == b"NTFS    " and b[510:512] == b"\x55\xaa":
        return struct.unpack_from("<Q", b, 0x48)[0] & 0xFFFFFFFF
    return None


def _norm(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).lower()).strip("_")


def _stem(name):
    base = re.split(r"[\\/]", name)[-1]
    base = re.sub(r"\.pf$", "", base, flags=re.I)
    return re.sub(r"-[0-9A-Fa-f]{8}$", "", base)


def _target(param, names, text):
    p = _norm(param or "")
    if p:
        for n in names:
            if _norm(n) == p or _norm(n.rsplit("/", 1)[-1]) == p:
                return n
    hits = [n for n in names if n in text]
    return max(hits, key=len) if hits else None


def _groups(tr):
    by = {}
    for n, t in tr.items():
        by.setdefault(t["key"], []).append(n)
    return sorted((sorted(g) for g in by.values()), key=lambda g: g[0])


def synth_value_of(names, get_bytes, field, text="", param=None):
    tr, other = {}, {}
    for n in names:
        b = get_bytes(n)
        if b is None:
            continue
        t = trace(b)
        if t is not None:
            tr[n] = t
            continue
        lk = lnk_link(b)
        if lk is not None:
            other[n] = lk
            continue
        vs = vbr_serial(b)
        if vs is not None:
            other[n] = (vs, None)
    if not tr:
        return "none"
    serial_host = {}
    for s, h in other.values():
        if s is not None and h:
            serial_host.setdefault(s, h)
    low = text.lower()
    if field in ("host_groups", "prefetch_host_groups", "trace_host_groups", "volume_host_groups",
                 "execution_host_groups"):
        return _groups(tr)
    if field in ("host_count", "distinct_host_count"):
        return len({t["key"] for t in tr.values()})
    if field.startswith(("same_host_as_", "same_host_traces_as_")):
        n = _target(param, list(tr) + list(other), text)
        if n is None:
            return None
        if n in tr:
            mates = [m for m in tr if m != n and tr[m]["key"] == tr[n]["key"]]
        else:
            s = other[n][0]
            mates = [m for m in tr if s is not None and tr[m]["serial"] == s]
        return sorted(mates) or "none"
    if field.startswith(("host_of_", "hostname_of_")):
        n = _target(param, list(tr), text)
        if n is None:
            return None
        return serial_host.get(tr[n]["serial"]) or "none"
    if field.startswith("renamed"):
        out = [n for n in names if n in tr and _stem(n).casefold() != tr[n]["exe"].casefold()]
        if re.search(r"\b(sorted|alphabetical|ascending)\b", low):
            out.sort()
        if field == "renamed_trace" and len(out) == 1:
            return out[0]
        return out or "none"
    if field in ("last_run_order", "last_run_time_order", "last_execution_order", "execution_order", "run_order",
                 "run_time_order"):
        desc = bool(re.search(r"descending|newest first|most recent first|latest first|newest to oldest", low))
        have = sorted((n for n in tr if tr[n]["last"]), key=lambda n: ((-1 if desc else 1) * tr[n]["last"], n))
        return have + sorted(n for n in tr if not tr[n]["last"])
    if field in ("odd_host", "odd_host_trace", "odd_host_member", "odd_host_file", "odd_trace", "odd_volume",
                 "foreign_trace"):
        gs = _groups(tr)
        single = [g[0] for g in gs if len(g) == 1]
        return single[0] if len(single) == 1 and len(gs) >= 2 and len(tr) >= 3 else None
    if field in ("traces_by_host", "trace_host_map", "prefetch_by_host", "files_by_host", "host_group_map"):
        out = {}
        for n, t in tr.items():
            out.setdefault(serial_host.get(t["serial"]) or "0x%08x" % (t["serial"] or 0), []).append(n)
        return {k: sorted(out[k]) for k in sorted(out)}
    return None


def any_trace(names, get_bytes):
    """True when at least one member is a prefetch trace (the hand-off test of the shared synthesis keys)."""
    for n in names:
        b = get_bytes(n)
        if b is not None and (bytes(b[4:8]) == b"SCCA" or bytes(b[:3]) == b"MAM"):
            return True
    return False


def prefetch_synthesis_value(data, ctx):
    """synthesis.<cross-trace prefetch field> (see the module docstring)."""
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
        v = synth_value_of(names, read, ctx.get("field") or "", text, ctx.get("param"))
        return v if (v != "none" or from_zip) else None
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
