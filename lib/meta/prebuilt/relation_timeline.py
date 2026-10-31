"""Claimed provenance CHAINS and zip TIMESTAMP relations inside a cluster zip (`cluster-NNN.zip`). Speculative tier:
D30 single cluster members carried UT (0x5455) extras + a delivery manifest; the timed kits all shared one DOS time
(2026-03-14 08:52:38) -- the timestamp/provenance relation was named by the flavor text but never asked.

Members = every non-directory entry minus the delivery manifest (*manifest*.json / index.json with artifacts[]).
Label = the manifest artifact `id` (by `path`, then `filename`), else the basename without extension -- the GM-verified
D30 relation.identical_sha256_groups convention (paths/basenames were REJECTED there).

Provenance (child -> parent claims), from:
  * manifest artifact keys derived_from / derived_from_id / parent_id / parent / source_id / source / derivedFrom /
    parentId / sourceId (a string or a list; a value names a member by id, path, filename or basename)
  * XMP inside member bytes (JPEG/PNG/PDF/OOXML XMP packets, raw scan): the child's xmpMM:DerivedFrom stRef:documentID
    / stRef:instanceID names the parent whose xmpMM:DocumentID / InstanceID / OriginalDocumentID equals it
  * a JSON sidecar member (an object with one of the manifest keys + id) -- same as a manifest claim
  provenance_chain: root->leaf ids of the single derivation path (several paths -> list of lists, sorted);
    provenance_chains always list of lists; provenance_edges = [[parent, child], ...] sorted;
    provenance_root_ids / provenance_leaf_ids; provenance_depth = longest path length (members)
  orphan_claim_ids: members whose claimed parent is not in the corpus (orphan_parent_refs = the dangling refs)
  cycle_ids: members on a derivation cycle (cycles are excluded from chains)
  No provenance claim at all -> "none" for every chain field (the relation does not exist).

Timestamps -- per member: DOS date/time of the central directory entry (naive, read AS UTC: the D30 GM wrote DOS
12:00:00 == UT 12:00:00 UTC), the UT 0x5455 mtime (unix, central first then local header), NTFS 0x000a mtime
(FILETIME). Effective mtime = UT, else NTFS, else DOS. All rendered ISO-8601 `YYYY-MM-DDTHH:MM:SSZ`.
  earliest_member_id / latest_member_id: the single member at the min/max effective mtime; a tie -> None (cannot
    answer); *_mtime_utc = that instant. mtime_order = ids by (mtime, id).
  mtime_groups: ids sharing one effective mtime, groups >= 2, sorted in + out; mtime_group_count = len;
    dos_time_groups uses the DOS time only; shared_mtime_utc = the one time when every member shares it (else "none")
  dos_vs_extended_time_mismatch_ids: |DOS - UT/NTFS mtime| >= 2 s (DOS has 2 s resolution); no member carries an
    extended time -> "none"
  future_timestamp_ids: any of DOS / UT / NTFS mtime later than the wall clock now
One parse per container sha256 (never id())."""
import hashlib
import io
import json
import re
import struct
import time
from datetime import datetime, timezone

_CHAIN = ("provenance_chain", "provenance_chains", "provenance_edges", "provenance_root_ids", "provenance_leaf_ids",
          "provenance_depth", "orphan_claim_ids", "orphan_parent_refs", "cycle_ids")
FIELDS = {
    ("relation", "provenance_chain"): "timeline_value",
    ("relation", "provenance_chain_ids"): "timeline_value",
    ("relation", "provenance_order"): "timeline_value",
    ("relation", "derivation_chain"): "timeline_value",
    ("relation", "lineage_chain"): "timeline_value",
    ("relation", "parent_child_chain"): "timeline_value",
    ("relation", "provenance_chains"): "timeline_value",
    ("relation", "derivation_chains"): "timeline_value",
    ("relation", "provenance_edges"): "timeline_value",
    ("relation", "provenance_pairs"): "timeline_value",
    ("relation", "derivation_pairs"): "timeline_value",
    ("relation", "parent_child_pairs"): "timeline_value",
    ("relation", "derived_from_pairs"): "timeline_value",
    ("relation", "provenance_root_ids"): "timeline_value",
    ("relation", "provenance_root_id"): "timeline_value",
    ("relation", "root_ids"): "timeline_value",
    ("relation", "provenance_leaf_ids"): "timeline_value",
    ("relation", "leaf_ids"): "timeline_value",
    ("relation", "provenance_depth"): "timeline_value",
    ("relation", "provenance_chain_length"): "timeline_value",
    ("relation", "chain_length"): "timeline_value",
    ("relation", "orphan_claim_ids"): "timeline_value",
    ("relation", "orphan_claim_count"): "timeline_value",
    ("relation", "orphan_ids"): "timeline_value",
    ("relation", "orphan_member_ids"): "timeline_value",
    ("relation", "orphaned_ids"): "timeline_value",
    ("relation", "dangling_parent_ids"): "timeline_value",
    ("relation", "missing_parent_ids"): "timeline_value",
    ("relation", "orphan_parent_refs"): "timeline_value",
    ("relation", "missing_parent_refs"): "timeline_value",
    ("relation", "cycle_ids"): "timeline_value",
    ("relation", "cycle_count"): "timeline_value",
    ("relation", "cycle_member_ids"): "timeline_value",
    ("relation", "provenance_cycle_ids"): "timeline_value",
    ("relation", "circular_ids"): "timeline_value",
    ("relation", "earliest_member_id"): "timeline_value",
    ("relation", "earliest_member"): "timeline_value",
    ("relation", "oldest_member_id"): "timeline_value",
    ("relation", "latest_member_id"): "timeline_value",
    ("relation", "latest_member"): "timeline_value",
    ("relation", "newest_member_id"): "timeline_value",
    ("relation", "earliest_mtime_utc"): "timeline_value",
    ("relation", "earliest_member_mtime_utc"): "timeline_value",
    ("relation", "latest_mtime_utc"): "timeline_value",
    ("relation", "latest_member_mtime_utc"): "timeline_value",
    ("relation", "mtime_order"): "timeline_value",
    ("relation", "chronological_order"): "timeline_value",
    ("relation", "time_order"): "timeline_value",
    ("relation", "mtime_groups"): "timeline_value",
    ("relation", "identical_mtime_groups"): "timeline_value",
    ("relation", "same_mtime_groups"): "timeline_value",
    ("relation", "timestamp_groups"): "timeline_value",
    ("relation", "mtime_group_count"): "timeline_value",
    ("relation", "dos_time_groups"): "timeline_value",
    ("relation", "dos_mtime_groups"): "timeline_value",
    ("relation", "shared_mtime_utc"): "timeline_value",
    ("relation", "shared_dos_time_utc"): "timeline_value",
    ("relation", "dos_vs_extended_time_mismatch_ids"): "timeline_value",
    ("relation", "dos_vs_extended_time_mismatch_count"): "timeline_value",
    ("relation", "dos_vs_ut_mismatch_ids"): "timeline_value",
    ("relation", "dos_ut_mismatch_ids"): "timeline_value",
    ("relation", "dos_extended_mismatch_ids"): "timeline_value",
    ("relation", "extended_time_mismatch_ids"): "timeline_value",
    ("relation", "timestamp_mismatch_ids"): "timeline_value",
    ("relation", "mtime_mismatch_ids"): "timeline_value",
    ("relation", "extended_time_ids"): "timeline_value",
    ("relation", "ut_extra_ids"): "timeline_value",
    ("relation", "ntfs_extra_ids"): "timeline_value",
    ("relation", "future_timestamp_ids"): "timeline_value",
    ("relation", "future_timestamp_count"): "timeline_value",
    ("relation", "future_dated_ids"): "timeline_value",
    ("relation", "future_mtime_ids"): "timeline_value",
}

_CACHE = {}     # container sha256 -> report (never keyed on id())
_PKEYS = ("derived_from", "derived_from_id", "derivedFrom", "parent_id", "parentId", "parent", "source_id",
          "sourceId", "source")
_DOCID = re.compile(rb"(?:xmpMM:(?:DocumentID|InstanceID|OriginalDocumentID))\s*(?:=\s*[\"']([^\"']+)[\"']|>([^<]+)<)")
_DERIVED = re.compile(rb"xmpMM:DerivedFrom\b(.{0,600}?)(?:/>|</xmpMM:DerivedFrom>)", re.S)
_STREF = re.compile(rb"stRef:(?:documentID|instanceID)\s*(?:=\s*[\"']([^\"']+)[\"']|>([^<]+)<)")


def _iso(ts):
    try:
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, OSError, ValueError):
        return None


def _dos_ts(dt):
    """zipfile date_time tuple, read as naive UTC -> unix seconds (None when invalid)."""
    try:
        return datetime(*dt, tzinfo=timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


def _extras(blob):
    """(UT mtime, NTFS mtime) from a zip extra-field blob."""
    ut = nt = None
    i = 0
    while i + 4 <= len(blob):
        hid, ln = struct.unpack_from("<HH", blob, i)
        body = blob[i + 4:i + 4 + ln]
        if hid == 0x5455 and len(body) >= 5 and body[0] & 1:
            ut = struct.unpack_from("<i", body, 1)[0]
        elif hid == 0x000A and len(body) >= 4:
            j = 4
            while j + 4 <= len(body):
                tag, sz = struct.unpack_from("<HH", body, j)
                if tag == 1 and sz >= 8 and j + 12 <= len(body):
                    ft = struct.unpack_from("<Q", body, j + 4)[0]
                    if ft:
                        nt = ft / 1e7 - 11644473600
                j += 4 + sz
        i += 4 + ln
    return ut, nt


def _local_extra(data, zi):
    try:
        o = zi.header_offset
        if data[o:o + 4] != b"PK\x03\x04":
            return b""
        nl, xl = struct.unpack_from("<HH", data, o + 26)
        return data[o + 30 + nl:o + 30 + nl + xl]
    except Exception:  # noqa: BLE001
        return b""


def _manifest(z, read):
    """(manifest path, artifacts) of the delivery manifest, or (None, [])."""
    for zi in z.infolist():
        base = zi.filename.rsplit("/", 1)[-1].lower()
        if zi.is_dir() or not base.endswith(".json") or ("manifest" not in base and base != "index.json"):
            continue
        try:
            j = json.loads(read(zi).decode("utf-8-sig"))
        except Exception:  # noqa: BLE001
            continue
        arts = j.get("artifacts") if isinstance(j, dict) else None
        if isinstance(arts, list) and any(isinstance(a, dict) and a.get("id") for a in arts):
            return zi.filename, [a for a in arts if isinstance(a, dict)]
    return None, []


def _refs(obj):
    out = []
    for k in _PKEYS:
        v = obj.get(k)
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, dict):
                x = x.get("id") or x.get("path") or x.get("filename")
            if isinstance(x, (str, int)) and str(x).strip():
                out.append(str(x).strip())
    return out


def _report(data):
    import zipfile
    z = zipfile.ZipFile(io.BytesIO(data))

    def read(zi):
        try:
            return z.read(zi)
        except Exception:  # noqa: BLE001 - bad CRC / encrypted: provenance scan just skips the bytes
            return b""

    mpath, arts = _manifest(z, read)
    label_of = {}
    for a in arts:
        for k in ("path", "filename"):
            if isinstance(a.get(k), str) and a[k]:
                label_of.setdefault(a[k], str(a["id"]))
    members = {}        # label -> info
    for zi in z.infolist():
        if zi.is_dir() or zi.filename.endswith("/") or zi.filename == mpath:
            continue
        base = zi.filename.rsplit("/", 1)[-1]
        lab = label_of.get(zi.filename) or label_of.get(base) or base.rsplit(".", 1)[0]
        ut, nt = _extras(zi.extra)
        if ut is None or nt is None:
            lu, ln = _extras(_local_extra(data, zi))
            ut = lu if ut is None else ut
            nt = ln if nt is None else nt
        members.setdefault(lab, {"path": zi.filename, "base": base, "dos": _dos_ts(zi.date_time),
                                 "ut": ut, "nt": nt, "zi": zi})
    if not members:
        return None
    # name resolution: id, path, filename, basename, stem -> label
    alias = {}
    for lab, m in members.items():
        for k in (lab, m["path"], m["base"], m["base"].rsplit(".", 1)[0]):
            alias.setdefault(k, lab)
            alias.setdefault(k.lower(), lab)
    for a in arts:
        if str(a.get("id")) in members:
            for k in ("path", "filename"):
                if isinstance(a.get(k), str):
                    alias.setdefault(a[k], str(a["id"]))
    claims = {}         # child label -> [parent ref strings]
    for a in arts:
        c = str(a.get("id"))
        r = _refs(a)
        if r:
            claims.setdefault(c, []).extend(r)
    docid = {}          # xmp document/instance id -> label
    xmp_parent = {}     # child label -> [xmp ids]
    for lab, m in members.items():
        b = read(m["zi"])
        if not b:
            continue
        if m["base"].lower().endswith(".json") and b[:1] in (b"{", b" ", b"\n"):
            try:
                j = json.loads(b.decode("utf-8-sig"))
                if isinstance(j, dict) and _refs(j):
                    claims.setdefault(lab, []).extend(_refs(j))
            except Exception:  # noqa: BLE001
                pass
        if b"xmpMM" not in b:
            continue
        derived = set()
        for dm in _DERIVED.finditer(b):
            for g in _STREF.finditer(dm.group(1)):
                derived.add((g.group(1) or g.group(2)).strip().decode("utf-8", "replace"))
        own = b
        for dm in _DERIVED.finditer(b):
            own = own.replace(dm.group(0), b"")
        for g in _DOCID.finditer(own):
            docid.setdefault((g.group(1) or g.group(2)).strip().decode("utf-8", "replace"), lab)
        if derived:
            xmp_parent[lab] = sorted(derived)
    for lab, ids in xmp_parent.items():
        for d in ids:
            claims.setdefault(lab, []).append(("xmp", d))
    edges, orphans, dangling = set(), set(), set()
    for child, refs in claims.items():
        for r in refs:
            if isinstance(r, tuple):
                p = docid.get(r[1])
                ref = r[1]
            else:
                p = alias.get(r) or alias.get(r.lower())
                ref = r
            if p is None or child not in members:
                if child in members:
                    orphans.add(child)
                    dangling.add(ref)
                continue
            if p != child:
                edges.add((p, child))
            else:
                edges.add((p, child))       # self-derivation = a 1-cycle
    rep = {"has_claims": bool(claims)}
    kids, pars = {}, {}
    for p, c in edges:
        kids.setdefault(p, set()).add(c)
        pars.setdefault(c, set()).add(p)
    # cycles: nodes in a strongly connected component of size > 1, or a self loop (Tarjan, iterative-safe sizes)
    cyc = set()
    idx, low, stack, on, counter = {}, {}, [], set(), [0]
    nodes = sorted({n for e in edges for n in e})

    def strong(v):
        work = [(v, iter(sorted(kids.get(v, ()))))]
        idx[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        while work:
            n, it = work[-1]
            nxt = next(it, None)
            if nxt is None:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[n])
                if low[n] == idx[n]:
                    comp = []
                    while True:
                        w = stack.pop()
                        on.discard(w)
                        comp.append(w)
                        if w == n:
                            break
                    if len(comp) > 1 or (n, n) in edges:
                        cyc.update(comp)
            elif nxt not in idx:
                idx[nxt] = low[nxt] = counter[0]
                counter[0] += 1
                stack.append(nxt)
                on.add(nxt)
                work.append((nxt, iter(sorted(kids.get(nxt, ())))))
            elif nxt in on:
                low[n] = min(low[n], idx[nxt])

    for v in nodes:
        if v not in idx:
            strong(v)
    acyc = [n for n in nodes if n not in cyc]
    roots = sorted(n for n in acyc if not (pars.get(n, set()) - cyc) and kids.get(n))
    leaves = sorted(n for n in acyc if not (kids.get(n, set()) - cyc) and (pars.get(n, set()) - cyc))
    paths = []

    def walk(n, path):
        nxt = sorted(k for k in kids.get(n, ()) if k not in cyc and k not in path)
        if not nxt:
            if len(path) > 1:
                paths.append(path)
            return
        for k in nxt:
            walk(k, path + [k])

    for r in roots:
        walk(r, [r])
    paths.sort()
    rep.update({
        "provenance_chains": paths,
        "provenance_chain": (paths[0] if len(paths) == 1 else paths) if paths else "none",
        "provenance_edges": sorted([p, c] for p, c in edges),
        "provenance_root_ids": roots, "provenance_leaf_ids": leaves,
        "provenance_depth": max((len(p) for p in paths), default=0),
        "orphan_claim_ids": sorted(orphans), "orphan_parent_refs": sorted(dangling),
        "cycle_ids": sorted(cyc)})
    # timestamps
    now = time.time()
    eff = {}
    for lab, m in members.items():
        t = m["ut"] if m["ut"] is not None else (m["nt"] if m["nt"] is not None else m["dos"])
        if t is not None:
            eff[lab] = int(t)
    order = sorted(eff, key=lambda k: (eff[k], k))
    rep["mtime_order"] = order
    for name, pick in (("earliest", min), ("latest", max)):
        if eff:
            t = pick(eff.values())
            hit = sorted(k for k, v in eff.items() if v == t)
            rep[name + "_member_id"] = hit[0] if len(hit) == 1 else None
            rep[name + "_mtime_utc"] = _iso(t)
        else:
            rep[name + "_member_id"] = rep[name + "_mtime_utc"] = "none"

    def groups(src):
        g = {}
        for k, v in src.items():
            g.setdefault(v, []).append(k)
        return sorted(sorted(x) for x in g.values() if len(x) > 1)

    rep["mtime_groups"] = groups(eff)
    rep["dos_time_groups"] = groups({k: m["dos"] for k, m in members.items() if m["dos"] is not None})
    rep["shared_mtime_utc"] = _iso(next(iter(eff.values()))) if eff and len(set(eff.values())) == 1 and \
        len(eff) > 1 else "none"
    dosv = {m["dos"] for m in members.values()}
    rep["shared_dos_time_utc"] = _iso(next(iter(dosv))) if len(dosv) == 1 and None not in dosv and \
        len(members) > 1 else "none"
    ext = {k for k, m in members.items() if m["ut"] is not None or m["nt"] is not None}
    rep["extended_time_ids"] = sorted(ext)
    rep["ut_extra_ids"] = sorted(k for k, m in members.items() if m["ut"] is not None)
    rep["ntfs_extra_ids"] = sorted(k for k, m in members.items() if m["nt"] is not None)
    mism = set()
    for k in ext:
        m = members[k]
        if m["dos"] is None:
            mism.add(k)
            continue
        for t in (m["ut"], m["nt"]):
            if t is not None and abs(m["dos"] - t) >= 2:
                mism.add(k)
    rep["dos_vs_extended_time_mismatch_ids"] = sorted(mism) if ext else "none"
    rep["future_timestamp_ids"] = sorted(k for k, m in members.items()
                                         if any(t is not None and t > now for t in (m["dos"], m["ut"], m["nt"])))
    return rep


def _key(field):
    f = field[:-6] + "_ids" if field.endswith("_count") else field
    table = (
        (("orphan_parent_refs", "missing_parent_refs"), "orphan_parent_refs"),
        (("orphan", "dangling", "missing_parent"), "orphan_claim_ids"),
        (("cycle", "circular"), "cycle_ids"),
        (("_chains",), "provenance_chains"),
        (("_edges", "_pairs"), "provenance_edges"),
        (("root",), "provenance_root_ids"), (("leaf",), "provenance_leaf_ids"),
        (("depth", "chain_length"), "provenance_depth"),
        (("provenance_chain", "provenance_order", "derivation_chain", "lineage_chain", "parent_child_chain"),
         "provenance_chain"),
        (("earliest_mtime", "earliest_member_mtime"), "earliest_mtime_utc"),
        (("latest_mtime", "latest_member_mtime"), "latest_mtime_utc"),
        (("earliest_member_id", "earliest_member", "oldest_member"), "earliest_member_id"),
        (("latest_member_id", "latest_member", "newest_member"), "latest_member_id"),
        (("order",), "mtime_order"),
        (("shared_dos",), "shared_dos_time_utc"), (("shared_mtime",), "shared_mtime_utc"),
        (("dos_time_groups", "dos_mtime_groups"), "dos_time_groups"),
        (("mismatch",), "dos_vs_extended_time_mismatch_ids"),
        (("ut_extra",), "ut_extra_ids"), (("ntfs_extra",), "ntfs_extra_ids"),
        (("extended_time_ids",), "extended_time_ids"),
        (("future",), "future_timestamp_ids"),
        (("groups", "group_ids"), "mtime_groups"),
    )
    for subs, k in table:
        if any(s in f for s in subs):
            return k
    return None


def timeline_value(data, ctx):
    if not data or data[:2] != b"PK":
        return "none"
    h = hashlib.sha256(data).hexdigest()
    if h not in _CACHE:
        try:
            _CACHE[h] = _report(data)
        except Exception:  # noqa: BLE001 - not a readable zip
            _CACHE[h] = None
    rep = _CACHE[h]
    field = (ctx or {}).get("field") or ""
    k = _key(field)
    if rep is None or k is None:
        return "none"
    if k in _CHAIN and not rep["has_claims"]:
        return "none"
    v = rep[k]
    if field.endswith("_count"):
        return len(v) if isinstance(v, list) else v
    if field.endswith("_root_id"):
        return v[0] if isinstance(v, list) and len(v) == 1 else (None if v else "none")
    return v
