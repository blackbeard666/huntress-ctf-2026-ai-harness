"""Multi-cluster corpus: expose the FABRICATED cluster among several `cluster-NNN.zip` members of one evidence zip
(the unasked half of the D30 flavor "... then expose the fabricated cluster"). Speculative tier.

Input = the evidence zip that holds >= 2 cluster zips (entries `*.zip` whose basename contains `cluster`, else every
inner zip that carries a delivery manifest or an `artifacts/` dir; any depth). A lone cluster zip / non-zip -> "none".

Per cluster, from the sibling analysers (relation_provenance claims, relation_near near-copies / bad CRC):
  claims   = provenance mismatch ids + missing + unlisted members (manifest claims that do not hold)
  near     = near-duplicate (1-2 byte edit) members, crc = members holding a bad-CRC entry
  shared   = members whose sha256 also occurs in ANOTHER cluster (cross-cluster copy)
  future   = cluster entries whose DOS mtime is later than the outer evidence entry of that cluster (or than now)
  flat_dos = 1 when every entry of the cluster has the same DOS time (one-shot fabrication)
D30 timed kits had near-copies + bad-CRC inner zips in EVERY cluster, so each signal scores only its EXCESS over the
median across clusters: score = 4*claims + 2*crc + 2*near + 2*future + flat_dos + shared (each max(0, v - median)).
  fabricated_cluster: the single max-score cluster's evidence basename VERBATIM (`cluster-003.zip`); a tie at the top
    -> None (cannot answer); all zero -> "none". `_id`/`_stem`/`_label` variants: the basename without `.zip`.
  cluster_with_claim_mismatches: the cluster(s) whose claims fail (one -> the name, several -> sorted list).
  clusters_sharing_content_groups: connected components (>= 2) of clusters linked by an identical member sha256,
    names sorted inside, groups sorted (`_ids` -> stems).
  cross_cluster_identical_groups: sha256 classes spanning >= 2 clusters, labels `<cluster stem>/<member label>`
    (label = manifest id, else basename without extension, as relation_variants), sorted in + out.
  cluster_count / cluster_names: the clusters found.
One parse per evidence sha256 (never id())."""
import hashlib
import io
import re

FIELDS = {
    ("relation", "fabricated_cluster"): "cluster_value",
    ("relation", "fabricated_cluster_id"): "cluster_value",
    ("relation", "fabricated_cluster_name"): "cluster_value",
    ("relation", "fabricated_cluster_filename"): "cluster_value",
    ("relation", "fabricated_cluster_stem"): "cluster_value",
    ("relation", "fabricated_cluster_label"): "cluster_value",
    ("relation", "fabricated_cluster_member"): "cluster_value",
    ("relation", "forged_cluster"): "cluster_value",
    ("relation", "tampered_cluster"): "cluster_value",
    ("relation", "suspicious_cluster"): "cluster_value",
    ("relation", "odd_cluster"): "cluster_value",
    ("relation", "odd_one_out_cluster"): "cluster_value",
    ("relation", "cluster_with_claim_mismatches"): "cluster_value",
    ("relation", "cluster_with_claim_mismatch"): "cluster_value",
    ("relation", "clusters_with_claim_mismatches"): "cluster_value",
    ("relation", "cluster_with_provenance_mismatches"): "cluster_value",
    ("relation", "clusters_with_provenance_mismatches"): "cluster_value",
    ("relation", "clusters_sharing_content_groups"): "cluster_value",
    ("relation", "clusters_sharing_content_ids"): "cluster_value",
    ("relation", "clusters_sharing_content"): "cluster_value",
    ("relation", "cluster_sharing_groups"): "cluster_value",
    ("relation", "cross_cluster_identical_groups"): "cluster_value",
    ("relation", "cross_cluster_duplicate_groups"): "cluster_value",
    ("relation", "cross_cluster_shared_groups"): "cluster_value",
    ("relation", "cross_cluster_identical_group_count"): "cluster_value",
    ("relation", "cluster_count"): "cluster_value",
    ("relation", "cluster_names"): "cluster_value",
}

_CACHE = {}    # evidence sha256 -> analysis | None
_CL = re.compile(r"cluster", re.I)


def _dos(dt):
    return "%04d-%02d-%02dT%02d:%02d:%02d" % tuple(dt)


def _clusters(data):
    """[(basename, bytes, outer dos text)] of the cluster zips inside the evidence zip, or None."""
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        infos = [zi for zi in z.infolist() if not zi.is_dir() and zi.filename.lower().endswith(".zip")]
    except Exception:  # noqa: BLE001 - not a zip
        return None
    cand = []
    for zi in infos:
        try:
            b = z.read(zi)
        except Exception:  # noqa: BLE001
            continue
        if b[:2] != b"PK":
            continue
        cand.append((zi.filename.replace("\\", "/").rsplit("/", 1)[-1], b, _dos(zi.date_time)))
    named = [c for c in cand if _CL.search(c[0])]
    if len(named) >= 2:
        return named
    shaped = []
    for c in cand:
        try:
            names = zipfile.ZipFile(io.BytesIO(c[1])).namelist()
        except Exception:  # noqa: BLE001
            continue
        if any("manifest" in n.lower() or n.startswith("artifacts/") for n in names):
            shaped.append(c)
    return shaped if len(shaped) >= 2 else None


def _entry_dos(b):
    import zipfile
    try:
        return [_dos(zi.date_time) for zi in zipfile.ZipFile(io.BytesIO(b)).infolist() if not zi.is_dir()]
    except Exception:  # noqa: BLE001
        return []


def _median(vals):
    s = sorted(vals)
    return s[len(s) // 2] if len(s) % 2 else (s[len(s) // 2 - 1] + s[len(s) // 2]) / 2


def _analyse(data):
    import datetime
    from . import relation_near as _near
    from . import relation_provenance as _prov
    cls = _clusters(data)
    if not cls:
        return None
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    rows, owners = [], {}
    for name, b, outer in cls:
        stem = name[:-4] if name.lower().endswith(".zip") else name
        try:
            pr = _prov._report(b)
        except Exception:  # noqa: BLE001
            pr = None
        claims = 0 if pr is None else len(pr["union"]) + len(pr["unlisted_paths"])
        try:
            nr = _near._analyse(b) or {}
        except Exception:  # noqa: BLE001
            nr = {}
        try:
            mem = _near._members(b) or []
        except Exception:  # noqa: BLE001
            mem = []
        for label, mb, _ in mem:
            owners.setdefault(hashlib.sha256(mb).hexdigest(), []).append((name, stem + "/" + label))
        dts = _entry_dos(b)
        lim = max(outer, now) if outer < "1981" else outer   # a 1980 outer stamp = unset: compare with now
        rows.append({"name": name, "stem": stem, "claims": claims, "near": len(nr.get("near", [])),
                     "crc": len(nr.get("crc", [])), "future": sum(1 for d in dts if d > lim and d > "1981"),
                     "flat": int(len(dts) >= 3 and len(set(dts)) == 1), "shared": 0})
    cross, edges = [], {}
    for h, own in owners.items():
        cl = {n for n, _ in own}
        if len(cl) < 2:
            continue
        cross.append(sorted(lbl for _, lbl in own))
        for r in rows:
            if r["name"] in cl:
                r["shared"] += sum(1 for n, _ in own if n == r["name"])
        cl = sorted(cl)
        for c in cl[1:]:
            edges.setdefault(cl[0], set()).add(c)
            edges.setdefault(c, set()).add(cl[0])
    seen, sharing = set(), []
    for r in rows:
        if r["name"] in seen or r["name"] not in edges:
            continue
        comp, todo = set(), [r["name"]]
        while todo:
            x = todo.pop()
            if x not in comp:
                comp.add(x)
                todo.extend(edges.get(x, ()))
        seen |= comp
        sharing.append(sorted(comp))
    weights = {"claims": 4, "crc": 2, "near": 2, "future": 2, "flat": 1, "shared": 1}
    med = {k: _median([r[k] for r in rows]) for k in weights}
    for r in rows:
        r["score"] = sum(w * max(0, r[k] - med[k]) for k, w in weights.items())
    top = max(r["score"] for r in rows)
    best = [r for r in rows if r["score"] == top]
    if top <= 0:
        fab = "none"
    elif len(best) == 1:
        fab = best[0]
    else:
        fab = None
    return {"rows": rows, "fab": fab, "cross": sorted(cross), "sharing": sorted(sharing),
            "claims": sorted(r["name"] for r in rows if r["claims"] > 0)}


def cluster_value(data, ctx):
    if not data or data[:2] != b"PK":
        return "none"
    key = hashlib.sha256(data).hexdigest()
    if key not in _CACHE:
        try:
            res = _analyse(data)
        except Exception:  # noqa: BLE001
            res = None
        if len(_CACHE) > 32:
            _CACHE.clear()
        _CACHE[key] = res
    res = _CACHE[key]
    if res is None:
        return "none"
    asked = (ctx or {}).get("asked") or (ctx or {}).get("field") or ""
    field = (ctx or {}).get("field") or ""
    stems = {r["name"]: r["stem"] for r in res["rows"]}
    if field == "cluster_count":
        return len(res["rows"])
    if field == "cluster_names":
        return sorted(stems)
    if field.startswith("cross_cluster"):
        return len(res["cross"]) if field.endswith("_count") else res["cross"]
    if "sharing" in field:
        if field.endswith("_ids"):
            return [[stems[n] for n in g] for g in res["sharing"]]
        return res["sharing"]
    if "claim" in field or "provenance" in field:
        lst = res["claims"]
        if not lst:
            return "none"
        return lst[0] if len(lst) == 1 and not field.startswith("clusters") else lst
    fab = res["fab"]
    if not isinstance(fab, dict):
        return fab
    if asked.endswith(("_id", "_stem", "_label")):
        return fab["stem"]
    return fab["name"]
