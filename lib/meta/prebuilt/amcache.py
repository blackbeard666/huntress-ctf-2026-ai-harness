"""Amcache.hve execution evidence (prebuilt, SPECULATIVE -- never GM-asked yet).

Amcache.hve is a regf hive (Win10/11): root nk (a {GUID} name) -> Root -> InventoryApplicationFile -> one subkey per
file (name like `cmd.exe|9d3a...`), values (REG_SZ unless noted): LowerCaseLongPath, Name, FileId ("0000" + SHA-1 of
the first 31 MB, lowercase hex), LinkDate ("MM/DD/YYYY HH:MM:SS", PE link time as text), ProductName, Publisher,
Version, BinaryType, Size (REG_QWORD; older builds REG_SZ hex "0x..."), ProgramId ("0000" + hash). Walked with the
regf.py cell helpers (nk -> lf/lh/li/ri -> nk, value list -> vk, big data db).

Fields (the amcache fmt; distinctive names also registered under regf):
  application_file_count  = number of InventoryApplicationFile subkeys.
  file_paths              = LowerCaseLongPath of every entry, SORTED (a set; JSON list), entries lacking it skipped.
  sha1_list               = FileId minus the 4-zero prefix, lowercased, SORTED.
  first_file_path         = LowerCaseLongPath of the first subkey in STORED index order (lf/lh lists are kept
                            name-sorted by Windows, so this is the alphabetically first key name).
  per-entry values (sha1, file_id, link_date, product_name, publisher, size, version, name, lower_case_long_path,
  program_id, binary_type): of the entry the question names (a file name / path / sha1 appearing in the question text,
  or `entry_<name>` / `<value>_for_<name>` in the field), else of the ONLY entry; ambiguous -> None.
  file_id = the raw stored string ("0000"+sha1); sha1 = without the prefix. size = int (base 10).
Not regf -> "none"; regf without Root\\InventoryApplicationFile (e.g. a SYSTEM/NTUSER hive) -> "none"."""
import re
import struct

from .regf import _data, _find, _root, _subkeys, _values

FIELDS = {
    ("amcache", "application_file_count"): "amcache_value",
    ("amcache", "inventory_application_file_count"): "amcache_value",
    ("amcache", "file_count"): "amcache_value",
    ("amcache", "entry_count"): "amcache_value",
    ("amcache", "file_paths"): "amcache_value",
    ("amcache", "lower_case_long_paths"): "amcache_value",
    ("amcache", "paths"): "amcache_value",
    ("amcache", "sha1_list"): "amcache_value",
    ("amcache", "sha1s"): "amcache_value",
    ("amcache", "file_sha1s"): "amcache_value",
    ("amcache", "sha1_hashes"): "amcache_value",
    ("amcache", "first_file_path"): "amcache_value",
    ("amcache", "first_path"): "amcache_value",
    ("amcache", "sha1"): "amcache_value",
    ("amcache", "file_sha1"): "amcache_value",
    ("amcache", "file_id"): "amcache_value",
    ("amcache", "link_date"): "amcache_value",
    ("amcache", "product_name"): "amcache_value",
    ("amcache", "publisher"): "amcache_value",
    ("amcache", "size"): "amcache_value",
    ("amcache", "file_size"): "amcache_value",
    ("amcache", "version"): "amcache_value",
    ("amcache", "name"): "amcache_value",
    ("amcache", "lower_case_long_path"): "amcache_value",
    ("amcache", "program_id"): "amcache_value",
    ("amcache", "binary_type"): "amcache_value",
    ("amcache", "entry_*"): "amcache_value",
    ("amcache", "sha1_for_*"): "amcache_value",
    ("amcache", "file_id_for_*"): "amcache_value",
    ("amcache", "link_date_for_*"): "amcache_value",
    ("amcache", "path_for_*"): "amcache_value",
    ("regf", "application_file_count"): "amcache_value",
    ("regf", "inventory_application_file_count"): "amcache_value",
    ("regf", "amcache_file_paths"): "amcache_value",
    ("regf", "amcache_sha1_list"): "amcache_value",
    ("regf", "amcache_first_file_path"): "amcache_value",
}

_VALS = {"sha1": "FileId", "file_sha1": "FileId", "file_id": "FileId", "link_date": "LinkDate",
         "product_name": "ProductName", "publisher": "Publisher", "size": "Size", "file_size": "Size",
         "version": "Version", "name": "Name", "lower_case_long_path": "LowerCaseLongPath", "path": "LowerCaseLongPath",
         "program_id": "ProgramId", "binary_type": "BinaryType"}
_TAGRX = re.compile(r"\[assigned-artifact-sha256:[^\]]*\]")


def entries(b):
    """[(key name, {value name lower: decoded value})] of Root\\InventoryApplicationFile in stored order, or None
    (not regf / no such key)."""
    h, root = _root(b)
    if h is None or root is None:
        return None
    inv = _find(b, root, ("Root", "InventoryApplicationFile"))
    if inv is None:
        return None
    out = []
    for k in _subkeys(b, inv):
        vals = {}
        for n, t, d in _values(b, k):
            v = _data(t, d)
            vals[n.lower()] = v.strip() if isinstance(v, str) else v
        out.append((k["name"], vals))
    return out


def _sha1(v):
    s = str(v or "").strip().lower()
    if len(s) == 44 and s.startswith("0000"):
        s = s[4:]
    return s if re.fullmatch(r"[0-9a-f]{40}", s) else None


def _size(v):
    if isinstance(v, int):
        return v
    s = str(v or "").strip()
    try:
        return int(s, 16) if s.lower().startswith("0x") else int(s)
    except ValueError:
        return None


def _pick(ents, hint, question):
    """The entry the field param / question names, else the only one, else None."""
    def keys(name, vals):
        p = str(vals.get("lowercaselongpath") or "").lower()
        return {x for x in (name.lower(), name.split("|")[0].lower(), p, p.rsplit("\\", 1)[-1],
                            str(vals.get("name") or "").lower(), _sha1(vals.get("fileid")) or "") if x}
    if hint:
        h = hint.lower().strip("_")
        hs = {h, h.replace("_", "."), re.sub(r"_(exe|dll|sys|com|scr|ps1|bat|msi)$", r".\1", h)}
        hit = [e for e in ents if keys(*e) & hs]
        if len(hit) == 1:
            return hit[0]
    q = question.get("question") if isinstance(question, dict) else question
    text = _TAGRX.sub("", str(q or "")).lower()
    hit = [e for e in ents if any(k and len(k) > 3 and k in text for k in keys(*e))]
    if len(hit) == 1:
        return hit[0]
    return ents[0] if len(ents) == 1 else None


def amcache_value(data, ctx):
    """amcache.<field>: InventoryApplicationFile counts / sorted path + sha1 sets / per-entry values."""
    if data is None:
        return None
    try:
        ents = entries(data)
        if ents is None:
            return "none"
        f = (ctx.get("field") or "").replace("amcache_", "")
        if f.endswith("_count"):
            return len(ents)
        if f in ("file_paths", "lower_case_long_paths", "paths"):
            ps = sorted(str(v["lowercaselongpath"]) for _, v in ents if v.get("lowercaselongpath"))
            return ps or "none"
        if f in ("sha1_list", "sha1s", "file_sha1s", "sha1_hashes"):
            hs = sorted(s for s in (_sha1(v.get("fileid")) for _, v in ents) if s)
            return hs or "none"
        if f in ("first_file_path", "first_path"):
            p = ents[0][1].get("lowercaselongpath") if ents else None
            return p or "none"
        param = ctx.get("param") or ""
        what = f
        if f.startswith("entry_"):          # entry_<name>: the whole entry? -> its sha1 (the identity value)
            what, param = "sha1", param or f[6:]
        m = re.match(r"^(.*)_for_(.*)$", f)
        if m:
            what, param = m.group(1), param or m.group(2)
        vname = _VALS.get(what)
        if vname is None or not ents:
            return None
        e = _pick(ents, param, ctx.get("question"))
        if e is None:
            return None
        v = e[1].get(vname.lower())
        if v is None or v == "":
            return "none"
        if what in ("sha1", "file_sha1"):
            return _sha1(v) or "none"
        if what in ("size", "file_size"):
            return _size(v)
        if isinstance(v, int) and what == "link_date":
            return struct.pack("<Q", v).hex()
        return v
    except Exception:
        return None
