"""Container images (prebuilt, SPECULATIVE -- never GM-asked yet): `docker save` tarballs and OCI image layouts.

Input = the member's bytes: a tar (optionally gzip/zstd/xz-wrapped) holding EITHER
  * docker-save: `manifest.json` = [{"Config": "<path>", "RepoTags": [...], "Layers": [...]}] (+ legacy `repositories`).
    Legacy saves name the config `<hex>.json`; Docker >= 25 writes `blobs/sha256/<hex>` (and an OCI layout beside it).
  * OCI image layout: `oci-layout` {"imageLayoutVersion"}, `index.json` manifests[] (digest/mediaType/annotations
    `org.opencontainers.image.ref.name`), `blobs/<alg>/<hex>`. A manifests[] entry may itself be an image index
    (containerd image store / multi-platform): it is followed to the first image manifest whose platform is not
    `unknown/unknown` (BuildKit attestation manifests are skipped). manifest.config.digest -> the config blob.
docker-save's manifest.json wins when both are present (it is what `docker load` reads); the FIRST image is used.

Fields come from the image CONFIG JSON (what `docker image inspect` shows): architecture, os, variant, created
(verbatim RFC 3339 text as stored -- no re-rendering, docker keeps the build-host offset + nanoseconds),
config_entrypoint / config_cmd / config_env / history_created_by / rootfs_diff_ids / repo_tags (compact JSON lists,
stored order), config_labels (compact JSON object, stored key order), exposed_ports (JSON list of the port keys,
sorted), config_working_dir / config_user (verbatim), layer_count (manifest layers, else rootfs.diff_ids),
config_digest (`sha256:` + sha256 of the config blob bytes = the image ID for single-platform images).
history_created_by keeps only entries that HAVE `created_by` (e.g. a `docker import` base row has none).
A null / empty / missing value -> "none"; not a container image (wrong format / no config) -> "none"."""
import gzip
import hashlib
import io
import json
import lzma
import tarfile

_F = {
    "architecture": ("architecture", "arch", "config_architecture", "image_architecture"),
    "os": ("os", "config_os", "image_os"),
    "variant": ("variant", "config_variant", "platform_variant"),
    "created": ("created", "config_created", "image_created"),
    "config_entrypoint": ("config_entrypoint", "entrypoint", "container_config_entrypoint"),
    "config_cmd": ("config_cmd", "cmd", "command"),
    "config_working_dir": ("config_working_dir", "working_dir", "workdir", "config_workdir"),
    "config_user": ("config_user", "user"),
    "config_env": ("config_env", "env", "environment"),
    "config_labels": ("config_labels", "labels"),
    "exposed_ports": ("exposed_ports", "config_exposed_ports"),
    "history_created_by": ("history_created_by", "created_by", "history"),
    "history_count": ("history_count", "history_entry_count"),
    "layer_count": ("layer_count", "layers_count", "number_of_layers", "manifest_layer_count"),
    "rootfs_diff_ids": ("rootfs_diff_ids", "diff_ids", "rootfs_layers"),
    "layer_digests": ("layer_digests", "manifest_layer_digests"),
    "repo_tags": ("repo_tags", "repotags", "tags", "image_tags"),
    "ref_name": ("ref_name", "image_ref_name", "org_opencontainers_image_ref_name", "annotation_ref_name"),
    "image_name": ("image_name", "containerd_image_name", "io_containerd_image_name"),
    "config_digest": ("config_digest", "image_id", "config_sha256"),
    "manifest_digest": ("manifest_digest",),
    "image_layout_version": ("image_layout_version", "oci_layout_version", "layout_version"),
    "image_format": ("image_format", "layout_format", "archive_format"),
}
FIELDS = {
    ("oci", "architecture"): "oci_value",
    ("oci", "arch"): "oci_value",
    ("oci", "config_architecture"): "oci_value",
    ("oci", "image_architecture"): "oci_value",
    ("oci", "os"): "oci_value",
    ("oci", "config_os"): "oci_value",
    ("oci", "image_os"): "oci_value",
    ("oci", "variant"): "oci_value",
    ("oci", "config_variant"): "oci_value",
    ("oci", "platform_variant"): "oci_value",
    ("oci", "created"): "oci_value",
    ("oci", "config_created"): "oci_value",
    ("oci", "image_created"): "oci_value",
    ("oci", "config_entrypoint"): "oci_value",
    ("oci", "entrypoint"): "oci_value",
    ("oci", "container_config_entrypoint"): "oci_value",
    ("oci", "config_cmd"): "oci_value",
    ("oci", "cmd"): "oci_value",
    ("oci", "command"): "oci_value",
    ("oci", "config_working_dir"): "oci_value",
    ("oci", "working_dir"): "oci_value",
    ("oci", "workdir"): "oci_value",
    ("oci", "config_workdir"): "oci_value",
    ("oci", "config_user"): "oci_value",
    ("oci", "user"): "oci_value",
    ("oci", "config_env"): "oci_value",
    ("oci", "env"): "oci_value",
    ("oci", "environment"): "oci_value",
    ("oci", "config_labels"): "oci_value",
    ("oci", "labels"): "oci_value",
    ("oci", "exposed_ports"): "oci_value",
    ("oci", "config_exposed_ports"): "oci_value",
    ("oci", "history_created_by"): "oci_value",
    ("oci", "created_by"): "oci_value",
    ("oci", "history"): "oci_value",
    ("oci", "history_count"): "oci_value",
    ("oci", "history_entry_count"): "oci_value",
    ("oci", "layer_count"): "oci_value",
    ("oci", "layers_count"): "oci_value",
    ("oci", "number_of_layers"): "oci_value",
    ("oci", "manifest_layer_count"): "oci_value",
    ("oci", "rootfs_diff_ids"): "oci_value",
    ("oci", "diff_ids"): "oci_value",
    ("oci", "rootfs_layers"): "oci_value",
    ("oci", "layer_digests"): "oci_value",
    ("oci", "manifest_layer_digests"): "oci_value",
    ("oci", "repo_tags"): "oci_value",
    ("oci", "repotags"): "oci_value",
    ("oci", "tags"): "oci_value",
    ("oci", "image_tags"): "oci_value",
    ("oci", "ref_name"): "oci_value",
    ("oci", "image_ref_name"): "oci_value",
    ("oci", "org_opencontainers_image_ref_name"): "oci_value",
    ("oci", "annotation_ref_name"): "oci_value",
    ("oci", "image_name"): "oci_value",
    ("oci", "containerd_image_name"): "oci_value",
    ("oci", "io_containerd_image_name"): "oci_value",
    ("oci", "config_digest"): "oci_value",
    ("oci", "image_id"): "oci_value",
    ("oci", "config_sha256"): "oci_value",
    ("oci", "manifest_digest"): "oci_value",
    ("oci", "image_layout_version"): "oci_value",
    ("oci", "oci_layout_version"): "oci_value",
    ("oci", "layout_version"): "oci_value",
    ("oci", "image_format"): "oci_value",
    ("oci", "layout_format"): "oci_value",
    ("oci", "archive_format"): "oci_value",
    ("docker", "architecture"): "oci_value",
    ("docker", "arch"): "oci_value",
    ("docker", "config_architecture"): "oci_value",
    ("docker", "image_architecture"): "oci_value",
    ("docker", "os"): "oci_value",
    ("docker", "config_os"): "oci_value",
    ("docker", "image_os"): "oci_value",
    ("docker", "variant"): "oci_value",
    ("docker", "config_variant"): "oci_value",
    ("docker", "platform_variant"): "oci_value",
    ("docker", "created"): "oci_value",
    ("docker", "config_created"): "oci_value",
    ("docker", "image_created"): "oci_value",
    ("docker", "config_entrypoint"): "oci_value",
    ("docker", "entrypoint"): "oci_value",
    ("docker", "container_config_entrypoint"): "oci_value",
    ("docker", "config_cmd"): "oci_value",
    ("docker", "cmd"): "oci_value",
    ("docker", "command"): "oci_value",
    ("docker", "config_working_dir"): "oci_value",
    ("docker", "working_dir"): "oci_value",
    ("docker", "workdir"): "oci_value",
    ("docker", "config_workdir"): "oci_value",
    ("docker", "config_user"): "oci_value",
    ("docker", "user"): "oci_value",
    ("docker", "config_env"): "oci_value",
    ("docker", "env"): "oci_value",
    ("docker", "environment"): "oci_value",
    ("docker", "config_labels"): "oci_value",
    ("docker", "labels"): "oci_value",
    ("docker", "exposed_ports"): "oci_value",
    ("docker", "config_exposed_ports"): "oci_value",
    ("docker", "history_created_by"): "oci_value",
    ("docker", "created_by"): "oci_value",
    ("docker", "history"): "oci_value",
    ("docker", "history_count"): "oci_value",
    ("docker", "history_entry_count"): "oci_value",
    ("docker", "layer_count"): "oci_value",
    ("docker", "layers_count"): "oci_value",
    ("docker", "number_of_layers"): "oci_value",
    ("docker", "manifest_layer_count"): "oci_value",
    ("docker", "rootfs_diff_ids"): "oci_value",
    ("docker", "diff_ids"): "oci_value",
    ("docker", "rootfs_layers"): "oci_value",
    ("docker", "layer_digests"): "oci_value",
    ("docker", "manifest_layer_digests"): "oci_value",
    ("docker", "repo_tags"): "oci_value",
    ("docker", "repotags"): "oci_value",
    ("docker", "tags"): "oci_value",
    ("docker", "image_tags"): "oci_value",
    ("docker", "ref_name"): "oci_value",
    ("docker", "image_ref_name"): "oci_value",
    ("docker", "org_opencontainers_image_ref_name"): "oci_value",
    ("docker", "annotation_ref_name"): "oci_value",
    ("docker", "image_name"): "oci_value",
    ("docker", "containerd_image_name"): "oci_value",
    ("docker", "io_containerd_image_name"): "oci_value",
    ("docker", "config_digest"): "oci_value",
    ("docker", "image_id"): "oci_value",
    ("docker", "config_sha256"): "oci_value",
    ("docker", "manifest_digest"): "oci_value",
    ("docker", "image_layout_version"): "oci_value",
    ("docker", "oci_layout_version"): "oci_value",
    ("docker", "layout_version"): "oci_value",
    ("docker", "image_format"): "oci_value",
    ("docker", "layout_format"): "oci_value",
    ("docker", "archive_format"): "oci_value",
    ("container", "architecture"): "oci_value",
    ("container", "arch"): "oci_value",
    ("container", "config_architecture"): "oci_value",
    ("container", "image_architecture"): "oci_value",
    ("container", "os"): "oci_value",
    ("container", "config_os"): "oci_value",
    ("container", "image_os"): "oci_value",
    ("container", "variant"): "oci_value",
    ("container", "config_variant"): "oci_value",
    ("container", "platform_variant"): "oci_value",
    ("container", "created"): "oci_value",
    ("container", "config_created"): "oci_value",
    ("container", "image_created"): "oci_value",
    ("container", "config_entrypoint"): "oci_value",
    ("container", "entrypoint"): "oci_value",
    ("container", "container_config_entrypoint"): "oci_value",
    ("container", "config_cmd"): "oci_value",
    ("container", "cmd"): "oci_value",
    ("container", "command"): "oci_value",
    ("container", "config_working_dir"): "oci_value",
    ("container", "working_dir"): "oci_value",
    ("container", "workdir"): "oci_value",
    ("container", "config_workdir"): "oci_value",
    ("container", "config_user"): "oci_value",
    ("container", "user"): "oci_value",
    ("container", "config_env"): "oci_value",
    ("container", "env"): "oci_value",
    ("container", "environment"): "oci_value",
    ("container", "config_labels"): "oci_value",
    ("container", "labels"): "oci_value",
    ("container", "exposed_ports"): "oci_value",
    ("container", "config_exposed_ports"): "oci_value",
    ("container", "history_created_by"): "oci_value",
    ("container", "created_by"): "oci_value",
    ("container", "history"): "oci_value",
    ("container", "history_count"): "oci_value",
    ("container", "history_entry_count"): "oci_value",
    ("container", "layer_count"): "oci_value",
    ("container", "layers_count"): "oci_value",
    ("container", "number_of_layers"): "oci_value",
    ("container", "manifest_layer_count"): "oci_value",
    ("container", "rootfs_diff_ids"): "oci_value",
    ("container", "diff_ids"): "oci_value",
    ("container", "rootfs_layers"): "oci_value",
    ("container", "layer_digests"): "oci_value",
    ("container", "manifest_layer_digests"): "oci_value",
    ("container", "repo_tags"): "oci_value",
    ("container", "repotags"): "oci_value",
    ("container", "tags"): "oci_value",
    ("container", "image_tags"): "oci_value",
    ("container", "ref_name"): "oci_value",
    ("container", "image_ref_name"): "oci_value",
    ("container", "org_opencontainers_image_ref_name"): "oci_value",
    ("container", "annotation_ref_name"): "oci_value",
    ("container", "image_name"): "oci_value",
    ("container", "containerd_image_name"): "oci_value",
    ("container", "io_containerd_image_name"): "oci_value",
    ("container", "config_digest"): "oci_value",
    ("container", "image_id"): "oci_value",
    ("container", "config_sha256"): "oci_value",
    ("container", "manifest_digest"): "oci_value",
    ("container", "image_layout_version"): "oci_value",
    ("container", "oci_layout_version"): "oci_value",
    ("container", "layout_version"): "oci_value",
    ("container", "image_format"): "oci_value",
    ("container", "layout_format"): "oci_value",
    ("container", "archive_format"): "oci_value",
    ("image_tar", "architecture"): "oci_value",
    ("image_tar", "arch"): "oci_value",
    ("image_tar", "config_architecture"): "oci_value",
    ("image_tar", "image_architecture"): "oci_value",
    ("image_tar", "os"): "oci_value",
    ("image_tar", "config_os"): "oci_value",
    ("image_tar", "image_os"): "oci_value",
    ("image_tar", "variant"): "oci_value",
    ("image_tar", "config_variant"): "oci_value",
    ("image_tar", "platform_variant"): "oci_value",
    ("image_tar", "created"): "oci_value",
    ("image_tar", "config_created"): "oci_value",
    ("image_tar", "image_created"): "oci_value",
    ("image_tar", "config_entrypoint"): "oci_value",
    ("image_tar", "entrypoint"): "oci_value",
    ("image_tar", "container_config_entrypoint"): "oci_value",
    ("image_tar", "config_cmd"): "oci_value",
    ("image_tar", "cmd"): "oci_value",
    ("image_tar", "command"): "oci_value",
    ("image_tar", "config_working_dir"): "oci_value",
    ("image_tar", "working_dir"): "oci_value",
    ("image_tar", "workdir"): "oci_value",
    ("image_tar", "config_workdir"): "oci_value",
    ("image_tar", "config_user"): "oci_value",
    ("image_tar", "user"): "oci_value",
    ("image_tar", "config_env"): "oci_value",
    ("image_tar", "env"): "oci_value",
    ("image_tar", "environment"): "oci_value",
    ("image_tar", "config_labels"): "oci_value",
    ("image_tar", "labels"): "oci_value",
    ("image_tar", "exposed_ports"): "oci_value",
    ("image_tar", "config_exposed_ports"): "oci_value",
    ("image_tar", "history_created_by"): "oci_value",
    ("image_tar", "created_by"): "oci_value",
    ("image_tar", "history"): "oci_value",
    ("image_tar", "history_count"): "oci_value",
    ("image_tar", "history_entry_count"): "oci_value",
    ("image_tar", "layer_count"): "oci_value",
    ("image_tar", "layers_count"): "oci_value",
    ("image_tar", "number_of_layers"): "oci_value",
    ("image_tar", "manifest_layer_count"): "oci_value",
    ("image_tar", "rootfs_diff_ids"): "oci_value",
    ("image_tar", "diff_ids"): "oci_value",
    ("image_tar", "rootfs_layers"): "oci_value",
    ("image_tar", "layer_digests"): "oci_value",
    ("image_tar", "manifest_layer_digests"): "oci_value",
    ("image_tar", "repo_tags"): "oci_value",
    ("image_tar", "repotags"): "oci_value",
    ("image_tar", "tags"): "oci_value",
    ("image_tar", "image_tags"): "oci_value",
    ("image_tar", "ref_name"): "oci_value",
    ("image_tar", "image_ref_name"): "oci_value",
    ("image_tar", "org_opencontainers_image_ref_name"): "oci_value",
    ("image_tar", "annotation_ref_name"): "oci_value",
    ("image_tar", "image_name"): "oci_value",
    ("image_tar", "containerd_image_name"): "oci_value",
    ("image_tar", "io_containerd_image_name"): "oci_value",
    ("image_tar", "config_digest"): "oci_value",
    ("image_tar", "image_id"): "oci_value",
    ("image_tar", "config_sha256"): "oci_value",
    ("image_tar", "manifest_digest"): "oci_value",
    ("image_tar", "image_layout_version"): "oci_value",
    ("image_tar", "oci_layout_version"): "oci_value",
    ("image_tar", "layout_version"): "oci_value",
    ("image_tar", "image_format"): "oci_value",
    ("image_tar", "layout_format"): "oci_value",
    ("image_tar", "archive_format"): "oci_value",
}
_CANON = {alias: canon for canon, aliases in _F.items() for alias in aliases}

_MAX = 256 * 1024 * 1024
_INDEX_TYPES = ("application/vnd.oci.image.index.v1+json",
                "application/vnd.docker.distribution.manifest.list.v2+json")


def _unwrap(b):
    """The tar bytes inside a gzip / xz / zstd wrapper (or the input itself)."""
    b = bytes(b)
    try:
        if b[:2] == b"\x1f\x8b":
            return gzip.decompress(b)
        if b[:6] == b"\xfd7zXZ\x00":
            return lzma.decompress(b)
        if b[:4] == b"\x28\xb5\x2f\xfd":
            import zstandard
            return zstandard.ZstdDecompressor().stream_reader(io.BytesIO(b)).read(_MAX)
    except Exception:
        return None
    return b


def _members(b):
    """{normalised name: bytes} of the small JSON-ish members (blobs are read lazily by name)."""
    raw = _unwrap(b)
    if not raw or len(raw) < 512:
        return None
    try:
        tf = tarfile.open(fileobj=io.BytesIO(raw), mode="r:")
        out = {}
        for m in tf.getmembers():
            if not m.isfile() or m.size > 64 * 1024 * 1024:
                continue
            name = m.name[2:] if m.name.startswith("./") else m.name
            out[name.lstrip("/")] = (tf, m)
        return out
    except Exception:
        return None


def _read(mem, name):
    if not name:
        return None
    ent = mem.get(name[2:] if name.startswith("./") else name.lstrip("/"))
    if ent is None:
        return None
    tf, m = ent
    try:
        return tf.extractfile(m).read()
    except Exception:
        return None


def _json(mem, name):
    b = _read(mem, name)
    if b is None:
        return None
    try:
        return json.loads(b.decode("utf-8-sig"))
    except Exception:
        return None


def _blob_path(digest):
    alg, _, hx = str(digest or "").partition(":")
    return "blobs/%s/%s" % (alg, hx) if hx else None


def _pick_manifest(mem, desc, depth=0):
    """Follow an index descriptor down to an image-manifest dict (+ its digest), or (None, None)."""
    if not isinstance(desc, dict) or depth > 4:
        return None, None
    body = _json(mem, _blob_path(desc.get("digest")))
    if not isinstance(body, dict):
        return None, None
    mt = body.get("mediaType") or desc.get("mediaType") or ""
    if mt in _INDEX_TYPES or ("manifests" in body and "config" not in body):
        subs = [d for d in body.get("manifests") or [] if isinstance(d, dict)]
        real = [d for d in subs if (d.get("platform") or {}).get("os") != "unknown"
                and "attestation" not in str((d.get("annotations") or {}).get("vnd.docker.reference.type", ""))]
        for d in real or subs:
            m, dg = _pick_manifest(mem, d, depth + 1)
            if m is not None:
                return m, dg
        return None, None
    return body, desc.get("digest")


def parse_image(b):
    """dict(kind, config bytes/json, layers, repo_tags, ref annotations, layout version), or None."""
    mem = _members(b)
    if not mem:
        return None
    info = {"layout": None, "tags": None, "ref_name": None, "image_name": None, "manifest_digest": None,
            "layers": None, "cfg_bytes": None, "kind": None}
    lay = _json(mem, "oci-layout")
    if isinstance(lay, dict):
        info["layout"] = lay.get("imageLayoutVersion")
    idx = _json(mem, "index.json")
    if isinstance(idx, dict):
        descs = [d for d in idx.get("manifests") or [] if isinstance(d, dict)]
        if descs:
            ann = descs[0].get("annotations") or {}
            info["ref_name"] = ann.get("org.opencontainers.image.ref.name")
            info["image_name"] = ann.get("io.containerd.image.name")
            man, dg = _pick_manifest(mem, descs[0])
            if isinstance(man, dict):
                cfg = man.get("config") or {}
                info["cfg_bytes"] = _read(mem, _blob_path(cfg.get("digest")))
                info["layers"] = [l.get("digest") for l in man.get("layers") or [] if isinstance(l, dict)]
                info["manifest_digest"] = dg
                info["kind"] = "oci"
    dman = _json(mem, "manifest.json")
    if isinstance(dman, list) and dman and isinstance(dman[0], dict) and dman[0].get("Config"):
        ent = dman[0]
        cb = _read(mem, ent.get("Config"))
        if cb is not None:
            info["cfg_bytes"] = cb
            info["kind"] = "docker-save+oci" if info["kind"] == "oci" else "docker-save"
            lays = ent.get("Layers")
            if isinstance(lays, list):
                info["layers"] = lays
        tags = ent.get("RepoTags")
        if isinstance(tags, list):
            info["tags"] = tags
    if info["cfg_bytes"] is None:
        return None
    try:
        info["cfg"] = json.loads(info["cfg_bytes"].decode("utf-8-sig"))
    except Exception:
        return None
    if not isinstance(info["cfg"], dict):
        return None
    return info


def _nz(v):
    return "none" if v is None or v == "" or v == [] or v == {} else v


def oci_value(data, ctx):
    if data is None:
        return None
    try:
        info = parse_image(data)
    except Exception:
        return None
    if info is None:
        return "none"
    canon = _CANON.get(ctx.get("field") or "")
    cfg = info["cfg"]
    cc = cfg.get("config") if isinstance(cfg.get("config"), dict) else {}
    rootfs = cfg.get("rootfs") if isinstance(cfg.get("rootfs"), dict) else {}
    hist = [h for h in cfg.get("history") or [] if isinstance(h, dict)]
    if canon in ("architecture", "os", "variant", "created"):
        return _nz(cfg.get(canon))
    simple = {"config_entrypoint": "Entrypoint", "config_cmd": "Cmd", "config_working_dir": "WorkingDir",
              "config_user": "User", "config_env": "Env", "config_labels": "Labels"}
    if canon in simple:
        return _nz(cc.get(simple[canon]))
    if canon == "exposed_ports":
        ep = cc.get("ExposedPorts")
        return _nz(sorted(ep)) if isinstance(ep, dict) else "none"
    if canon == "history_created_by":
        return _nz([h["created_by"] for h in hist if "created_by" in h])
    if canon == "history_count":
        return len(hist)
    if canon == "rootfs_diff_ids":
        return _nz(rootfs.get("diff_ids"))
    if canon == "layer_count":
        lays = info["layers"] if info["layers"] is not None else rootfs.get("diff_ids")
        return len(lays) if isinstance(lays, list) else "none"
    if canon == "layer_digests":
        lays = info["layers"]
        if not lays:
            return "none"
        return ["sha256:" + l.rsplit("/", 1)[-1] if "/" in l and ":" not in l else l for l in lays]
    if canon == "repo_tags":
        if info["tags"] is not None:
            return _nz(info["tags"])
        name = info["image_name"] or info["ref_name"]
        return [name] if name else "none"
    if canon == "ref_name":
        return _nz(info["ref_name"])
    if canon == "image_name":
        return _nz(info["image_name"])
    if canon == "config_digest":
        return "sha256:" + hashlib.sha256(info["cfg_bytes"]).hexdigest()
    if canon == "manifest_digest":
        return _nz(info["manifest_digest"])
    if canon == "image_layout_version":
        return _nz(info["layout"])
    if canon == "image_format":
        return info["kind"]
    return None
