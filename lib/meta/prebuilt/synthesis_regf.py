"""Cross-HIVE synthesis over several regf members (prebuilt, SPECULATIVE; the spelling was never GM-verified).
Coverage-atlas row "registry-planted-hive-synthesis" (D25 "Hive Mind" flavor: "registry hives from multiple systems have
been renamed and separated from host labels. Identify each true root, regroup the systems, and isolate the planted
hive"). Ids `metadata-day-NN-synthesis-<key>`. Members come from the question's `Files: [...]` list, read through
ctx["read"], else from `data` when the artifact IS the container zip (all members, zip order) -- the shared
synthesis_media._source. Only members with the `regf` magic take part (names / extensions are never trusted).
Per hive (prebuilt/regf.py walkers): base block seq1 @4 / seq2 @8 / last written FILETIME @12 / major @20 / minor @24 /
type @28 / format @32 / FileName @48 (UTF-16LE, the TAIL of the original path) / checksum @508 (XOR of dwords 0..126,
0 -> 1, 0xffffffff -> 0xfffffffe); root nk name (the D25-verified registry.hive_root_name walk); host label = the first
root value named Marker / Host / HostName / ComputerName / MachineName / MachineSid / Sid (D25 hives carry root values
Marker "HUNTRESS-HIVE-<n>" + Ordinal), else ControlSet00x|CurrentControlSet\\Control\\ComputerName\\{Active,}
ComputerName : ComputerName (a real SYSTEM hive).
Fields (names verbatim; lists / maps -> compact JSON; nothing applies -> "none"):
  host_groups = sorted list of sorted name lists, one per host label (singletons kept); the *_map / files_by_host
    siblings give {label: [sorted names]} (these keys belong to synthesis_evtx.py, which hands a regf-only set here);
  planted_hive / odd_one_out = the first criterion (priority order) that singles out EXACTLY one member:
    1 the only member whose host label is unshared (others in groups >= 2) or the only one with no label;
    2 base-block FileName stem vs root name (lowercase alnum, either a suffix of the other = the FileName keeps a path
      tail) disagree for exactly one while >= 2 agree;  3 root name differs from its host group's (>= 3, all others
      equal);  4 last written FILETIME outside its group's cluster (nearest other member > max(10 x the rest's span,
      1 day); whole set when unlabelled);  5 seq1 != seq2;  6 checksum invalid;  7 (major, minor, type, format)
      differs while all others agree.  None fires -> "none";
  order_by_last_written = names by base-block last written ascending, ties by name ("descending" in the text reverses);
  root_names_by_member = {name: root key name} (keys sorted);
  earliest/latest_member (synthesis_evtx keys) = the hive written first / last."""
import re
import struct
from collections import Counter

FIELDS = {
    ("synthesis", "planted_hive"): "regf_synthesis_value",
    ("synthesis", "planted_hive_member"): "regf_synthesis_value",
    ("synthesis", "planted_member"): "regf_synthesis_value",
    ("synthesis", "planted_file"): "regf_synthesis_value",
    ("synthesis", "planted_filename"): "regf_synthesis_value",
    ("synthesis", "odd_hive"): "regf_synthesis_value",
    ("synthesis", "odd_hive_member"): "regf_synthesis_value",
    ("synthesis", "odd_one_out_hive"): "regf_synthesis_value",
    ("synthesis", "outlier_hive"): "regf_synthesis_value",
    ("synthesis", "foreign_hive"): "regf_synthesis_value",
    ("synthesis", "order_by_last_written"): "regf_synthesis_value",
    ("synthesis", "last_written_order"): "regf_synthesis_value",
    ("synthesis", "hive_last_written_order"): "regf_synthesis_value",
    ("synthesis", "order_by_last_written_time"): "regf_synthesis_value",
    ("synthesis", "root_names_by_member"): "regf_synthesis_value",
    ("synthesis", "root_name_by_member"): "regf_synthesis_value",
    ("synthesis", "root_names_by_file"): "regf_synthesis_value",
    ("synthesis", "root_name_map"): "regf_synthesis_value",
    ("synthesis", "hive_root_names"): "regf_synthesis_value",
    ("synthesis", "true_root_names"): "regf_synthesis_value",
    ("synthesis", "hive_host_groups"): "regf_synthesis_value",
    ("synthesis", "hive_groups"): "regf_synthesis_value",
    ("synthesis", "system_groups"): "regf_synthesis_value",
    ("synthesis", "marker_groups"): "regf_synthesis_value",
    ("synthesis", "hives_by_host"): "regf_synthesis_value",
}

_HOST_VALUES = ("marker", "host", "hostname", "host_name", "computername", "computer_name", "machinename",
                "machine_name", "machinesid", "machine_sid", "sid")
_CN_PATHS = [[cs, "Control", "ComputerName", k] for cs in ("ControlSet001", "CurrentControlSet", "ControlSet002")
             for k in ("ComputerName", "ActiveComputerName")]
_DAY = 864000000000     # 1 day in FILETIME ticks


def _label(v):
    if isinstance(v, list):
        v = v[0] if v else None
    if isinstance(v, int):
        return str(v)
    return (v.strip() or None) if isinstance(v, str) else None


def _host(b, root):
    from .regf import _data, _find, _values
    vals = {n.lower(): _data(t, d) for n, t, d in _values(b, root)}
    for k in _HOST_VALUES:
        if k in vals and _label(vals[k]):
            return _label(vals[k])
    for path in _CN_PATHS:
        k = _find(b, root, path)
        if k is not None:
            for n, t, d in _values(b, k):
                if n.lower() == "computername" and _label(_data(t, d)):
                    return _label(_data(t, d))
    return None


def profile(b):
    """Per-hive dict, or None (not regf)."""
    from .regf import _nk, base_block
    b = bytes(b or b"")
    h = base_block(b)
    if h is None:
        return None
    ftype, ffmt = struct.unpack_from("<II", b, 28)
    ck = 0
    for i in range(0, 508, 4):
        ck ^= struct.unpack_from("<I", b, i)[0]
    ck = {0: 1, 0xFFFFFFFF: 0xFFFFFFFE}.get(ck, ck)
    try:
        root = _nk(b, h["root"])
        host = _host(b, root) if root else None
    except Exception:  # noqa: BLE001 - damaged cells: the base block still counts
        root, host = None, None
    return {"seq_ok": h["seq1"] == h["seq2"], "ts": h["ts"], "ver": (h["major"], h["minor"], ftype, ffmt),
            "ck_ok": ck == struct.unpack_from("<I", b, 508)[0], "fname": h["name"],
            "root": root["name"] if root else None, "host": host}


def _norm(s):
    return re.sub(r"[^0-9a-z]", "", (s or "").lower())


def _fn_stem(fn):
    tail = re.split(r"[\\/]", fn or "")[-1]
    return _norm(re.sub(r"(\.(hiv|hive|hve|dat|reg|log\d?|sav|bak))+$", "", tail, flags=re.I))


def _agree(p):
    a, b = _fn_stem(p["fname"]), _norm(p["root"])
    return bool(a and b) and (a.endswith(b) or b.endswith(a))


def groups_of(hv):
    g = {}
    for n, p in hv.items():
        if p["host"]:
            g.setdefault(p["host"], []).append(n)
    return {k: sorted(v) for k, v in g.items()}


def _one(xs):
    return xs[0] if len(xs) == 1 else None


def planted(hv):
    names = sorted(hv)
    if len(names) < 3:
        return "none"
    g = groups_of(hv)
    unlabeled = [n for n in names if not hv[n]["host"]]
    singles = [v[0] for v in g.values() if len(v) == 1]
    if g and not unlabeled and any(len(v) > 1 for v in g.values()) and len(singles) == 1:
        return singles[0]
    if len(unlabeled) == 1 and len(names) - 1 >= 2:
        return unlabeled[0]
    ag = [n for n in names if hv[n]["root"] and hv[n]["fname"]]
    dis = [n for n in ag if not _agree(hv[n])]
    if len(dis) == 1 and len(ag) - 1 >= 2:
        return dis[0]
    odd = []
    for v in g.values():
        if len(v) >= 3:
            (top, c), = Counter(hv[n]["root"] for n in v).most_common(1)
            if c == len(v) - 1:
                odd += [n for n in v if hv[n]["root"] != top]
    if _one(odd):
        return odd[0]
    out = []
    for v in (g.values() if g else [names]):
        if len(v) < 3:
            continue
        for n in v:
            rest = [hv[m]["ts"] for m in v if m != n]
            span = max(rest) - min(rest)
            if min(abs(hv[n]["ts"] - t) for t in rest) > max(10 * span, _DAY):
                out.append(n)
    if _one(out):
        return out[0]
    for key in ("seq_ok", "ck_ok"):
        bad = [n for n in names if not hv[n][key]]
        if _one(bad):
            return bad[0]
    (top, c), = Counter(hv[n]["ver"] for n in names).most_common(1)
    if c == len(names) - 1:
        return next(n for n in names if hv[n]["ver"] != top)
    return "none"


def synth_value_of(names, get_bytes, field, text=""):
    hv = {}
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        p = profile(b)
        if p is not None:
            hv[n] = p
    if not hv:
        return "none"
    f = field or ""
    if f.startswith(("planted", "odd", "outlier", "foreign")):
        return planted(hv)
    if "order" in f:
        desc = bool(re.search(r"\b(descending|newest first|latest first|most recent first)\b", text, re.I))
        return [n for _, n in sorted(((-p["ts"] if desc else p["ts"]), n) for n, p in hv.items())]
    if "root" in f:
        return {n: hv[n]["root"] for n in sorted(hv) if hv[n]["root"]} or "none"
    if f.startswith("earliest"):
        return min((p["ts"], n) for n, p in hv.items())[1]
    if f.startswith("latest"):
        return min((-p["ts"], n) for n, p in hv.items())[1]
    g = groups_of(hv)
    if not g:
        return "none"
    if f.endswith("_map") or f.startswith(("files_by", "logs_by", "hives_by")):
        return {k: g[k] for k in sorted(g)}
    return sorted(g.values())


def any_regf(names, get_bytes):
    """True when at least one member carries the regf magic (the hand-off test of the shared synthesis keys)."""
    for n in names:
        b = get_bytes(n)
        if b is not None and bytes(b[:4]) == b"regf":
            return True
    return False


def regf_synthesis_value(data, ctx):
    """synthesis.<cross-hive field> (see the module docstring)."""
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
        v = synth_value_of(names, read, ctx.get("field") or "", text)
        return v if (v != "none" or from_zip) else None
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None
