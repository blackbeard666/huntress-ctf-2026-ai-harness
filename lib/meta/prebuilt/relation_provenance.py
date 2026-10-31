"""Claimed provenance vs evidence on a cluster zip (`cluster-NNN.zip`) that carries a delivery manifest
(`delivery-manifest.json`, schema `huntress.artifact_delivery_manifest.v1`: artifacts[] = {id, filename, path,
content_type, family, producer_id, size_bytes, sha256}). Speculative tier: in D30 every claim was TRUE (single) and the
timed kits had no manifest; the D30 flavor text ("... and claimed provenance -- then expose the fabricated cluster")
names this relation kind as the unasked one.

Each manifest claim is checked against the REAL member bytes (member found by `path`, else by `filename`/basename):
  sha256_claim_mismatch_ids (= claimed_hash_mismatch_ids): claimed sha256 != sha256(bytes)
  size_claim_mismatch_ids: claimed size_bytes != len(bytes)
  content_type_mismatch_ids: claimed content_type vs magic -- image/png needs \\x89PNG, application/zip needs PK,
      application/json needs a leading JSON object/array (raw_decode: the
      D30 cluster-001 charlie-* json members are `{...}` + a literal backslash-n and their claims were TRUE), text/plain needs UTF-8 text without NUL (JSON text is text too)
  family_mismatch_ids: family png/zip/json as above; text/script = any UTF-8 text
  unsupported_duplicate_ref_ids: producer_id duplicate_ref whose bytes match no member produced by a non-duplicate_ref
      producer (text_template / structured_image / structured_zip)
  missing_member_ids: claimed but no such member in the zip
  unlisted_member_names: members present (non-dir, not the manifest) that no artifact claims -- basenames
      (`_paths` = zip paths, `_ids` = basename without extension)
  provenance_mismatch_ids: union of the id lists above (unlisted members have no id: excluded)
Labels = manifest `id`; lists sorted -> compact JSON; `[]` when every claim holds. *_count = len. No manifest / not a
zip -> "none" (the claim relation does not exist). `relation.fabricated_ids` belongs to relation_near (near-duplicate
semantics) and is NOT registered here. One parse per container sha256 (never id())."""
import hashlib
import io
import json
import struct
import zlib

FIELDS = {
    ("relation", "provenance_mismatch_ids"): "provenance_value",
    ("relation", "provenance_mismatch_count"): "provenance_value",
    ("relation", "provenance_mismatch_member_ids"): "provenance_value",
    ("relation", "claimed_provenance_mismatch_ids"): "provenance_value",
    ("relation", "claim_mismatch_ids"): "provenance_value",
    ("relation", "claim_mismatch_count"): "provenance_value",
    ("relation", "false_claim_ids"): "provenance_value",
    ("relation", "unsupported_claim_ids"): "provenance_value",
    ("relation", "manifest_mismatch_ids"): "provenance_value",
    ("relation", "manifest_mismatch_count"): "provenance_value",
    ("relation", "provenance_consistent_ids"): "provenance_value",
    ("relation", "verified_claim_ids"): "provenance_value",
    ("relation", "claimed_hash_mismatch_ids"): "provenance_value",
    ("relation", "claimed_hash_mismatch_count"): "provenance_value",
    ("relation", "claimed_sha256_mismatch_ids"): "provenance_value",
    ("relation", "sha256_claim_mismatch_ids"): "provenance_value",
    ("relation", "sha256_claim_mismatch_count"): "provenance_value",
    ("relation", "sha256_mismatch_ids"): "provenance_value",
    ("relation", "hash_claim_mismatch_ids"): "provenance_value",
    ("relation", "hash_mismatch_ids"): "provenance_value",
    ("relation", "size_claim_mismatch_ids"): "provenance_value",
    ("relation", "size_claim_mismatch_count"): "provenance_value",
    ("relation", "claimed_size_mismatch_ids"): "provenance_value",
    ("relation", "size_mismatch_ids"): "provenance_value",
    ("relation", "content_type_mismatch_ids"): "provenance_value",
    ("relation", "content_type_mismatch_count"): "provenance_value",
    ("relation", "content_type_claim_mismatch_ids"): "provenance_value",
    ("relation", "claimed_content_type_mismatch_ids"): "provenance_value",
    ("relation", "mime_mismatch_ids"): "provenance_value",
    ("relation", "mime_type_mismatch_ids"): "provenance_value",
    ("relation", "family_mismatch_ids"): "provenance_value",
    ("relation", "family_mismatch_count"): "provenance_value",
    ("relation", "family_claim_mismatch_ids"): "provenance_value",
    ("relation", "claimed_family_mismatch_ids"): "provenance_value",
    ("relation", "unsupported_duplicate_ref_ids"): "provenance_value",
    ("relation", "unsupported_duplicate_ref_count"): "provenance_value",
    ("relation", "unsupported_duplicate_ids"): "provenance_value",
    ("relation", "unsupported_duplicate_claim_ids"): "provenance_value",
    ("relation", "false_duplicate_ref_ids"): "provenance_value",
    ("relation", "duplicate_ref_mismatch_ids"): "provenance_value",
    ("relation", "orphan_duplicate_ref_ids"): "provenance_value",
    ("relation", "missing_member_ids"): "provenance_value",
    ("relation", "missing_member_count"): "provenance_value",
    ("relation", "missing_ids"): "provenance_value",
    ("relation", "missing_artifact_ids"): "provenance_value",
    ("relation", "claimed_missing_ids"): "provenance_value",
    ("relation", "unlisted_member_names"): "provenance_value",
    ("relation", "unlisted_member_count"): "provenance_value",
    ("relation", "unlisted_member_paths"): "provenance_value",
    ("relation", "unlisted_member_ids"): "provenance_value",
    ("relation", "unlisted_members"): "provenance_value",
    ("relation", "unlisted_names"): "provenance_value",
    ("relation", "unclaimed_member_names"): "provenance_value",
    ("relation", "unmanifested_member_names"): "provenance_value",
}

_CACHE = {}       # container sha256 -> report dict (never keyed on id())
_ORIGINAL = ("text_template", "structured_image", "structured_zip")


def _members(data):
    """[(path, bytes)] of every non-directory entry, read via zipfile; a bad-CRC entry is re-read raw from its LFH."""
    import zipfile
    z = zipfile.ZipFile(io.BytesIO(data))
    out = []
    for zi in z.infolist():
        if zi.is_dir() or zi.filename.endswith("/"):
            continue
        try:
            b = z.read(zi)
        except Exception:  # noqa: BLE001 - bad CRC / odd method: raw LFH read
            b = _raw_read(data, zi)
        if b is not None:
            out.append((zi.filename, b))
    return out


def _raw_read(data, zi):
    try:
        o = zi.header_offset
        if data[o:o + 4] != b"PK\x03\x04":
            return None
        nl, xl = struct.unpack_from("<HH", data, o + 26)
        s = o + 30 + nl + xl
        raw = data[s:s + zi.compress_size]
        if zi.compress_type == 0:
            return raw
        if zi.compress_type == 8:
            return zlib.decompressobj(-15).decompress(raw)
    except Exception:  # noqa: BLE001
        return None
    return None


def _manifest(members):
    """(manifest path, artifacts list) of the delivery manifest, or (None, None)."""
    best = (None, None)
    for path, b in members:
        base = path.rsplit("/", 1)[-1].lower()
        if not base.endswith(".json") or ("manifest" not in base and base != "index.json"):
            continue
        try:
            j = json.loads(b.decode("utf-8-sig"))
        except Exception:  # noqa: BLE001
            continue
        arts = j.get("artifacts") if isinstance(j, dict) else None
        if isinstance(arts, list) and any(isinstance(a, dict) and a.get("id") for a in arts):
            if best[0] is None or "delivery" in base:
                best = (path, [a for a in arts if isinstance(a, dict)])
    return best


def _text(b):
    if b"\x00" in b:
        return None
    try:
        return b.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def _is_json(b):
    t = _text(b)
    if t is None or not t.strip():
        return False
    try:     # prefix sniff: the D30 GM's own TRUE json members end in a literal `\\n` after the object
        v, _ = json.JSONDecoder().raw_decode(t.lstrip())
        return isinstance(v, (dict, list))
    except ValueError:
        return False


def _kind_ok(claim, b):
    """Does the claimed content_type / family agree with the bytes? None = unknown claim (not judged)."""
    c = (claim or "").strip().lower()
    if not c:
        return None
    if c in ("image/png", "png"):
        return b[:8] == b"\x89PNG\r\n\x1a\n"
    if c in ("application/zip", "application/x-zip-compressed", "zip"):
        return b[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
    if c in ("application/json", "text/json", "json"):
        return _is_json(b)
    if c in ("text/plain", "text", "script", "text/x-powershell", "application/x-powershell", "ps1", "powershell"):
        return _text(b) is not None and b[:8] != b"\x89PNG\r\n\x1a\n" and b[:2] != b"PK"
    if c in ("image/jpeg", "jpeg", "jpg"):
        return b[:3] == b"\xff\xd8\xff"
    if c in ("image/gif", "gif"):
        return b[:6] in (b"GIF87a", b"GIF89a")
    if c in ("application/pdf", "pdf"):
        return b[:5] == b"%PDF-"
    return None


def _report(data):
    members = _members(data)
    mpath, arts = _manifest(members)
    if mpath is None:
        return None
    by_path = {p: b for p, b in members if p != mpath}
    by_base = {}
    for p, b in by_path.items():
        by_base.setdefault(p.rsplit("/", 1)[-1], b)
    sha = {p: hashlib.sha256(b).hexdigest() for p, b in by_path.items()}
    claimed = set()
    found = {}
    r = {k: set() for k in ("sha", "size", "ctype", "family", "dupref", "missing")}
    for a in arts:
        aid = str(a.get("id"))
        p = a.get("path")
        fn = a.get("filename")
        path = None
        if isinstance(p, str) and p in by_path:
            path = p
        else:
            for cand in (fn, (p or "").rsplit("/", 1)[-1] if isinstance(p, str) else None):
                if isinstance(cand, str) and cand:
                    hits = [q for q in by_path if q.rsplit("/", 1)[-1] == cand]
                    if hits:
                        path = sorted(hits)[0]
                        break
        if path is None:
            r["missing"].add(aid)
            continue
        claimed.add(path)
        b = by_path[path]
        found[aid] = (a, path)
        cs = a.get("sha256")
        if isinstance(cs, str) and cs.strip() and cs.strip().lower() != sha[path]:
            r["sha"].add(aid)
        sz = a.get("size_bytes")
        if sz is not None:
            try:
                if int(sz) != len(b):
                    r["size"].add(aid)
            except (TypeError, ValueError):
                r["size"].add(aid)
        if _kind_ok(a.get("content_type"), b) is False:
            r["ctype"].add(aid)
        if _kind_ok(a.get("family"), b) is False:
            r["family"].add(aid)
    originals = {sha[path] for a, path in found.values()
                 if str(a.get("producer_id") or "").strip().lower() != "duplicate_ref"}
    for aid, (a, path) in found.items():
        if str(a.get("producer_id") or "").strip().lower() == "duplicate_ref" and sha[path] not in originals:
            r["dupref"].add(aid)
    unlisted = sorted(p for p in by_path if p not in claimed)
    union = set().union(*r.values())
    return {"sha": sorted(r["sha"]), "size": sorted(r["size"]), "ctype": sorted(r["ctype"]),
            "family": sorted(r["family"]), "dupref": sorted(r["dupref"]), "missing": sorted(r["missing"]),
            "union": sorted(union), "ok": sorted(set(found) - union),
            "unlisted_paths": unlisted, "unlisted_names": sorted(p.rsplit("/", 1)[-1] for p in unlisted),
            "unlisted_ids": sorted(p.rsplit("/", 1)[-1].rsplit(".", 1)[0] for p in unlisted)}


def _key(field):
    f = field
    if f.startswith("unlisted") or f.startswith("unclaimed") or f.startswith("unmanifested"):
        if "path" in f:
            return "unlisted_paths"
        return "unlisted_ids" if f.endswith("_ids") else "unlisted_names"
    if "duplicate" in f or "dup_ref" in f:
        return "dupref"
    if "missing" in f:
        return "missing"
    if "content_type" in f or "mime" in f:
        return "ctype"
    if "family" in f:
        return "family"
    if "size" in f:
        return "size"
    if "hash" in f or "sha256" in f:
        return "sha"
    if "consistent" in f or "verified" in f:
        return "ok"
    return "union"


def provenance_value(data, ctx):
    if not data or data[:2] != b"PK":
        return "none"
    h = hashlib.sha256(data).hexdigest()
    if h not in _CACHE:
        try:
            _CACHE[h] = _report(data)
        except Exception:  # noqa: BLE001 - not a readable zip
            _CACHE[h] = None
    rep = _CACHE[h]
    if rep is None:
        return "none"
    field = (ctx or {}).get("field") or ""
    v = rep[_key(field)]
    return len(v) if field.endswith("_count") else v
