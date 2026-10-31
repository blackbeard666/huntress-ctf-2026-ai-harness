"""Cross-member relation fields of a cluster archive. COPIED from the GM-verified D30 solver (Seeing Double):

relation.identical_sha256_groups = the members of the cluster zip (minus its delivery-manifest.json) grouped by the
SHA-256 of their REAL bytes; only groups of >= 2; each group = the members' delivery-manifest artifact `id` ("alpha-01":
no `artifacts/` path, no extension) sorted, the groups sorted -> compact JSON list of lists. Member paths
(`artifacts/alpha-01.txt`) and basenames (`alpha-01.txt`) were REJECTED on the D30 single (lib.knowledge)."""
import hashlib
import io
import json
import zipfile


def _manifest_ids(z):
    """{path or filename: artifact id} from every *manifest.json member."""
    ids = {}
    for zi in z.infolist():
        if not zi.filename.rsplit("/", 1)[-1].lower().endswith("manifest.json"):
            continue
        try:
            arts = json.loads(z.read(zi)).get("artifacts", [])
        except Exception:  # noqa: BLE001 - not the delivery manifest
            continue
        for a in arts if isinstance(arts, list) else []:
            if isinstance(a, dict) and a.get("id"):
                for k in ("path", "filename"):
                    if a.get(k):
                        ids.setdefault(a[k], a["id"])
    return ids


def identical_sha256_groups(data, ctx=None):
    if not data or data[:2] != b"PK":
        return None
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # noqa: BLE001 - not a zip
        return None
    ids = _manifest_ids(z)
    groups = {}
    for zi in z.infolist():
        base = zi.filename.rsplit("/", 1)[-1]
        if zi.is_dir() or base.lower().endswith("manifest.json"):
            continue
        try:
            b = z.read(zi)
        except Exception:  # noqa: BLE001 - encrypted member: the password-aware read
            from lib.common import read_member
            b = read_member(io.BytesIO(data), zi.filename)
        name = ids.get(zi.filename) or ids.get(base) or base.rsplit(".", 1)[0]
        groups.setdefault(hashlib.sha256(b).hexdigest(), []).append(name)
    return sorted(sorted(g) for g in groups.values() if len(g) > 1)
