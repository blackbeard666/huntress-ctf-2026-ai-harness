"""Node / Electron runnable packages: Electron `app.asar` archives and npm `package.json` (prebuilt, SPECULATIVE --
never GM-asked yet).

asar (alias electron): Chromium Pickle header -- u32 LE 4, u32 header_buf_size, then a Pickle of header_buf_size
bytes = u32 payload size, u32 json_len, UTF-8 JSON {"files": {name: {"files": {...}} (directory) |
{"offset": "<decimal string>", "size": n, "executable"?, "unpacked"?, "integrity"?: {algorithm, hash, blockSize,
blocks}} (file) | {"link": "..."}}}. File bytes live at 8 + header_buf_size + int(offset); "unpacked" files are in
app.asar.unpacked/ (not in the archive). Written/listed by @electron/asar (`asar pack` / `asar list`).
npm / node: package.json read from raw JSON, an `npm pack` .tgz (`package/package.json`), a plain tar, a zip, or the
root package.json inside an app.asar. Keys verbatim; objects as compact JSON in stored key order.
Wrong format (decoy / truncated) -> "none". Stdlib only: struct/json/tarfile/zipfile."""
import io
import json
import struct
import tarfile
import zipfile
import zlib

FIELDS = {
    ("asar", "file_names"): "asar_value",
    ("asar", "file_paths"): "asar_value",
    ("asar", "file_list"): "asar_value",
    ("asar", "file_count"): "asar_value",
    ("asar", "number_of_files"): "asar_value",
    ("asar", "files_count"): "asar_value",
    ("asar", "directory_names"): "asar_value",
    ("asar", "directory_count"): "asar_value",
    ("asar", "entry_names"): "asar_value",
    ("asar", "entry_count"): "asar_value",
    ("asar", "unpacked_files"): "asar_value",
    ("asar", "unpacked_file_names"): "asar_value",
    ("asar", "unpacked_file_count"): "asar_value",
    ("asar", "has_unpacked_files"): "asar_value",
    ("asar", "executable_files"): "asar_value",
    ("asar", "link_names"): "asar_value",
    ("asar", "integrity_algorithm"): "asar_value",
    ("asar", "integrity_algorithms"): "asar_value",
    ("asar", "has_integrity"): "asar_value",
    ("asar", "header_size"): "asar_value",
    ("asar", "header_buf_size"): "asar_value",
    ("asar", "header_json_size"): "asar_value",
    ("asar", "header_json_length"): "asar_value",
    ("asar", "json_length"): "asar_value",
    ("asar", "header_string_length"): "asar_value",
    ("asar", "data_offset"): "asar_value",
    ("asar", "package_name"): "asar_value",
    ("asar", "package_main"): "asar_value",
    ("asar", "package_version"): "asar_value",
    ("asar", "package_description"): "asar_value",
    ("asar", "package_product_name"): "asar_value",
    ("asar", "package_type"): "asar_value",
    ("asar", "package_author"): "asar_value",
    ("asar", "package_license"): "asar_value",
    ("asar", "package_dependencies"): "asar_value",
    ("asar", "package_dev_dependencies"): "asar_value",
    ("asar", "package_scripts"): "asar_value",
    ("asar", "package_bin"): "asar_value",
    ("asar", "package_exports"): "asar_value",
    ("asar", "package_scripts_preinstall"): "asar_value",
    ("asar", "package_scripts_install"): "asar_value",
    ("asar", "package_scripts_postinstall"): "asar_value",
    ("asar", "package_scripts_*"): "asar_value",
    ("electron", "file_names"): "asar_value",
    ("electron", "file_paths"): "asar_value",
    ("electron", "file_list"): "asar_value",
    ("electron", "file_count"): "asar_value",
    ("electron", "number_of_files"): "asar_value",
    ("electron", "files_count"): "asar_value",
    ("electron", "directory_names"): "asar_value",
    ("electron", "directory_count"): "asar_value",
    ("electron", "entry_names"): "asar_value",
    ("electron", "entry_count"): "asar_value",
    ("electron", "unpacked_files"): "asar_value",
    ("electron", "unpacked_file_names"): "asar_value",
    ("electron", "unpacked_file_count"): "asar_value",
    ("electron", "has_unpacked_files"): "asar_value",
    ("electron", "executable_files"): "asar_value",
    ("electron", "link_names"): "asar_value",
    ("electron", "integrity_algorithm"): "asar_value",
    ("electron", "integrity_algorithms"): "asar_value",
    ("electron", "has_integrity"): "asar_value",
    ("electron", "header_size"): "asar_value",
    ("electron", "header_buf_size"): "asar_value",
    ("electron", "header_json_size"): "asar_value",
    ("electron", "header_json_length"): "asar_value",
    ("electron", "json_length"): "asar_value",
    ("electron", "header_string_length"): "asar_value",
    ("electron", "data_offset"): "asar_value",
    ("electron", "package_name"): "asar_value",
    ("electron", "package_main"): "asar_value",
    ("electron", "package_version"): "asar_value",
    ("electron", "package_description"): "asar_value",
    ("electron", "package_product_name"): "asar_value",
    ("electron", "package_type"): "asar_value",
    ("electron", "package_author"): "asar_value",
    ("electron", "package_license"): "asar_value",
    ("electron", "package_dependencies"): "asar_value",
    ("electron", "package_dev_dependencies"): "asar_value",
    ("electron", "package_scripts"): "asar_value",
    ("electron", "package_bin"): "asar_value",
    ("electron", "package_exports"): "asar_value",
    ("electron", "package_scripts_preinstall"): "asar_value",
    ("electron", "package_scripts_install"): "asar_value",
    ("electron", "package_scripts_postinstall"): "asar_value",
    ("electron", "package_scripts_*"): "asar_value",
    ("npm", "name"): "npm_value",
    ("npm", "version"): "npm_value",
    ("npm", "main"): "npm_value",
    ("npm", "description"): "npm_value",
    ("npm", "license"): "npm_value",
    ("npm", "type"): "npm_value",
    ("npm", "module"): "npm_value",
    ("npm", "types"): "npm_value",
    ("npm", "typings"): "npm_value",
    ("npm", "homepage"): "npm_value",
    ("npm", "author"): "npm_value",
    ("npm", "author_name"): "npm_value",
    ("npm", "repository"): "npm_value",
    ("npm", "keywords"): "npm_value",
    ("npm", "private"): "npm_value",
    ("npm", "engines"): "npm_value",
    ("npm", "os"): "npm_value",
    ("npm", "cpu"): "npm_value",
    ("npm", "files"): "npm_value",
    ("npm", "browser"): "npm_value",
    ("npm", "product_name"): "npm_value",
    ("npm", "package_manager"): "npm_value",
    ("npm", "bin"): "npm_value",
    ("npm", "bin_names"): "npm_value",
    ("npm", "exports"): "npm_value",
    ("npm", "imports"): "npm_value",
    ("npm", "scripts"): "npm_value",
    ("npm", "script_names"): "npm_value",
    ("npm", "scripts_preinstall"): "npm_value",
    ("npm", "scripts_install"): "npm_value",
    ("npm", "scripts_postinstall"): "npm_value",
    ("npm", "scripts_prepare"): "npm_value",
    ("npm", "scripts_start"): "npm_value",
    ("npm", "scripts_*"): "npm_value",
    ("npm", "has_install_scripts"): "npm_value",
    ("npm", "dependencies"): "npm_value",
    ("npm", "dependency_names"): "npm_value",
    ("npm", "dependency_count"): "npm_value",
    ("npm", "dev_dependencies"): "npm_value",
    ("npm", "peer_dependencies"): "npm_value",
    ("npm", "optional_dependencies"): "npm_value",
    ("npm", "bundle_dependencies"): "npm_value",
    ("npm", "bundled_dependencies"): "npm_value",
    ("npm", "package_name"): "npm_value",
    ("npm", "package_version"): "npm_value",
    ("npm", "package_main"): "npm_value",
    ("node", "name"): "npm_value",
    ("node", "version"): "npm_value",
    ("node", "main"): "npm_value",
    ("node", "description"): "npm_value",
    ("node", "license"): "npm_value",
    ("node", "type"): "npm_value",
    ("node", "module"): "npm_value",
    ("node", "types"): "npm_value",
    ("node", "typings"): "npm_value",
    ("node", "homepage"): "npm_value",
    ("node", "author"): "npm_value",
    ("node", "author_name"): "npm_value",
    ("node", "repository"): "npm_value",
    ("node", "keywords"): "npm_value",
    ("node", "private"): "npm_value",
    ("node", "engines"): "npm_value",
    ("node", "os"): "npm_value",
    ("node", "cpu"): "npm_value",
    ("node", "files"): "npm_value",
    ("node", "browser"): "npm_value",
    ("node", "product_name"): "npm_value",
    ("node", "package_manager"): "npm_value",
    ("node", "bin"): "npm_value",
    ("node", "bin_names"): "npm_value",
    ("node", "exports"): "npm_value",
    ("node", "imports"): "npm_value",
    ("node", "scripts"): "npm_value",
    ("node", "script_names"): "npm_value",
    ("node", "scripts_preinstall"): "npm_value",
    ("node", "scripts_install"): "npm_value",
    ("node", "scripts_postinstall"): "npm_value",
    ("node", "scripts_prepare"): "npm_value",
    ("node", "scripts_start"): "npm_value",
    ("node", "scripts_*"): "npm_value",
    ("node", "has_install_scripts"): "npm_value",
    ("node", "dependencies"): "npm_value",
    ("node", "dependency_names"): "npm_value",
    ("node", "dependency_count"): "npm_value",
    ("node", "dev_dependencies"): "npm_value",
    ("node", "peer_dependencies"): "npm_value",
    ("node", "optional_dependencies"): "npm_value",
    ("node", "bundle_dependencies"): "npm_value",
    ("node", "bundled_dependencies"): "npm_value",
    ("node", "package_name"): "npm_value",
    ("node", "package_version"): "npm_value",
    ("node", "package_main"): "npm_value",
    ("electron", "name"): "npm_value",
    ("electron", "version"): "npm_value",
    ("electron", "main"): "npm_value",
    ("electron", "description"): "npm_value",
    ("electron", "license"): "npm_value",
    ("electron", "type"): "npm_value",
    ("electron", "module"): "npm_value",
    ("electron", "types"): "npm_value",
    ("electron", "typings"): "npm_value",
    ("electron", "homepage"): "npm_value",
    ("electron", "author"): "npm_value",
    ("electron", "author_name"): "npm_value",
    ("electron", "repository"): "npm_value",
    ("electron", "keywords"): "npm_value",
    ("electron", "private"): "npm_value",
    ("electron", "engines"): "npm_value",
    ("electron", "os"): "npm_value",
    ("electron", "cpu"): "npm_value",
    ("electron", "files"): "npm_value",
    ("electron", "browser"): "npm_value",
    ("electron", "product_name"): "npm_value",
    ("electron", "package_manager"): "npm_value",
    ("electron", "bin"): "npm_value",
    ("electron", "bin_names"): "npm_value",
    ("electron", "exports"): "npm_value",
    ("electron", "imports"): "npm_value",
    ("electron", "scripts"): "npm_value",
    ("electron", "script_names"): "npm_value",
    ("electron", "scripts_preinstall"): "npm_value",
    ("electron", "scripts_install"): "npm_value",
    ("electron", "scripts_postinstall"): "npm_value",
    ("electron", "scripts_prepare"): "npm_value",
    ("electron", "scripts_start"): "npm_value",
    ("electron", "scripts_*"): "npm_value",
    ("electron", "has_install_scripts"): "npm_value",
    ("electron", "dependencies"): "npm_value",
    ("electron", "dependency_names"): "npm_value",
    ("electron", "dependency_count"): "npm_value",
    ("electron", "dev_dependencies"): "npm_value",
    ("electron", "peer_dependencies"): "npm_value",
    ("electron", "optional_dependencies"): "npm_value",
    ("electron", "bundle_dependencies"): "npm_value",
    ("electron", "bundled_dependencies"): "npm_value",
}


def _asar_header(b):
    """(header dict, data base offset) of an Electron asar archive, or None.
    Layout: Chromium Pickle #1 = u32 payload size (always 4) + u32 header_buf_size; Pickle #2 (header_buf_size bytes)
    = u32 payload size + u32 json_len + JSON (padded to 4). File data starts at 8 + header_buf_size."""
    if not b or len(b) < 16:
        return None
    four, hsize = struct.unpack_from("<II", b, 0)
    payload, jlen = struct.unpack_from("<II", b, 8)
    if four != 4 or hsize < 8 or 8 + hsize > len(b) or jlen > hsize - 8 or payload > hsize:
        return None
    try:
        h = json.loads(b[16:16 + jlen].decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(h, dict) or not isinstance(h.get("files"), dict):
        return None
    return h, 8 + hsize, hsize, jlen


def _asar_walk(node, prefix="", inherit=False, out=None, dirs=None):
    """Depth-first, stored (JSON key) order: out = [(path, entry, unpacked)] leaves, dirs = [path] directories."""
    out = [] if out is None else out
    dirs = [] if dirs is None else dirs
    for name, ent in (node.get("files") or {}).items():
        if not isinstance(ent, dict):
            continue
        path = prefix + name
        unp = inherit or ent.get("unpacked") is True
        if isinstance(ent.get("files"), dict):
            dirs.append(path)
            _asar_walk(ent, path + "/", unp, out, dirs)
        else:
            out.append((path, ent, unp))
    return out, dirs


def _asar_file(b, hdr, path):
    """Bytes of an in-archive file (None when unpacked / a link / out of range)."""
    h, base = hdr[0], hdr[1]
    for p, ent, unp in _asar_walk(h)[0]:
        if p == path:
            if unp or "offset" not in ent:
                return None
            try:
                off, size = int(ent["offset"]), int(ent.get("size", 0))
            except (TypeError, ValueError):
                return None
            if off < 0 or size < 0 or base + off + size > len(b):
                return None
            return b[base + off:base + off + size]
    return None


def _pick_pkg(names):
    """The package.json a tool would read: root `package.json`, npm-pack's `package/package.json`, else the
    shallowest */package.json outside node_modules (then any)."""
    names = [n for n in names if n.rsplit("/", 1)[-1] == "package.json"]
    for want in ("package.json", "package/package.json"):
        if want in names:
            return want
    for pool in ([n for n in names if "node_modules/" not in n], names):
        if pool:
            return min(pool, key=lambda n: (n.count("/"), len(n)))
    return None


def _json_obj(raw):
    try:
        v = json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError, AttributeError):
        return None
    return v if isinstance(v, dict) else None


def _from_tar(b):
    try:
        with tarfile.open(fileobj=io.BytesIO(b), mode="r:*") as tf:
            mem = {m.name.lstrip("./"): m for m in tf.getmembers() if m.isfile()}
            n = _pick_pkg(list(mem))
            if n is None:
                return None
            f = tf.extractfile(mem[n])
            return _json_obj(f.read(4 << 20)) if f else None
    except (tarfile.TarError, OSError, EOFError, ValueError, zlib.error):
        return None


def _from_zip(b):
    try:
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            n = _pick_pkg([i.filename for i in z.infolist() if not i.is_dir()])
            return _json_obj(z.read(n)) if n else None
    except (zipfile.BadZipFile, OSError, ValueError, KeyError, NotImplementedError, RuntimeError):
        return None


def package_json(b):
    """The parsed package.json carried by `b` (raw JSON, .tgz/.tar from `npm pack`, zip, or app.asar), or None."""
    if not b:
        return None
    s = b.lstrip(b"\xef\xbb\xbf \t\r\n")
    if s[:1] == b"{":
        return _json_obj(b)
    hdr = _asar_header(b)
    if hdr:
        n = _pick_pkg([p for p, _, _ in _asar_walk(hdr[0])[0]])
        raw = _asar_file(b, hdr, n) if n else None
        return _json_obj(raw) if raw is not None else None
    if b[:2] == b"\x1f\x8b" or b[:3] == b"BZh" or b[:6] == b"\xfd7zXZ\x00" or b[257:262] == b"ustar":
        return _from_tar(b)
    if b[:4] == b"PK\x03\x04":
        return _from_zip(b)
    return None


_NPM_KEY = {"dev_dependencies": "devDependencies", "peer_dependencies": "peerDependencies",
            "optional_dependencies": "optionalDependencies", "bundle_dependencies": "bundleDependencies",
            "bundled_dependencies": "bundledDependencies", "product_name": "productName", "types": "types",
            "package_manager": "packageManager", "publish_config": "publishConfig"}


def _npm_field(pkg, field, param):
    if field.startswith("package_") and field[8:] not in ("manager",):
        field = field[8:]
    if field in ("scripts_*",) or param is not None and field.endswith("_*"):
        sc = pkg.get("scripts")
        if not isinstance(sc, dict):
            return "none"
        for k in (param, param.replace("_", ":"), param.replace("_", "-"), param.replace("_", ".")):
            if k in sc:
                return sc[k]
        return "none"
    if field.startswith("scripts_"):     # explicit scripts_preinstall / install / postinstall keys
        return _npm_field(pkg, "scripts_*", field[8:])
    if field in ("dependency_names", "dependencies_names"):
        d = pkg.get("dependencies")
        return list(d) if isinstance(d, dict) else "none"
    if field in ("dependency_count", "dependencies_count"):
        d = pkg.get("dependencies")
        return len(d) if isinstance(d, dict) else "none"
    if field in ("script_names", "scripts_names"):
        d = pkg.get("scripts")
        return list(d) if isinstance(d, dict) else "none"
    if field in ("has_install_scripts", "install_scripts_present", "has_lifecycle_scripts"):
        sc = pkg.get("scripts")
        return isinstance(sc, dict) and any(k in sc for k in ("preinstall", "install", "postinstall"))
    if field in ("bin_names", "bin_command_names"):
        v = pkg.get("bin")
        if isinstance(v, dict):
            return list(v)
        if isinstance(v, str):      # npm: a string bin installs under the (unscoped) package name
            n = pkg.get("name")
            return [n.rsplit("/", 1)[-1]] if isinstance(n, str) else "none"
        return "none"
    if field in ("author_name",):
        v = pkg.get("author")
        if isinstance(v, dict):
            v = v.get("name")
        return v if isinstance(v, str) and v.strip() else "none"
    key = _NPM_KEY.get(field, field)
    if key not in pkg:
        return "none"
    v = pkg[key]
    if v is None:
        return "none"
    if isinstance(v, bool) or isinstance(v, (dict, list)):
        return v
    if isinstance(v, (int, float)):
        return v
    return str(v).strip()


def npm_value(data, ctx):
    """npm/node.<field>: the package.json key as stored. Objects/arrays (bin as an object, exports, dependencies,
    scripts, engines) -> compact JSON in stored key order; strings verbatim (a string `bin` stays the bare path
    string, not npm's normalized {name: path}); absent key -> "none". scripts_<name> = scripts[<name>]
    (`_` also tried as `:` / `-` / `.`)."""
    if data is None:
        return None
    pkg = package_json(data)
    if pkg is None:
        return "none"
    return _npm_field(pkg, ctx.get("field") or "", ctx.get("param"))


def asar_value(data, ctx):
    """asar/electron.<field>. file_names = every file (leaf, incl. links) path relative to the archive root, '/'
    separators, no leading slash, depth-first in stored header order (what `asar list` walks, minus directories);
    directory_names / entry_names add the directories. unpacked_files = files flagged (or inherited from a
    directory flagged) "unpacked": true -> [] when none. integrity_algorithm = the first file's
    integrity.algorithm as stored ("SHA256"). header_size = Pickle #1 header_buf_size; header_json_size = json_len;
    data_offset = 8 + header_buf_size. package_* = the root package.json's keys (npm_value rules)."""
    if data is None:
        return None
    field = ctx.get("field") or ""
    hdr = _asar_header(data)
    if hdr is None:
        return "none"
    h, base, hsize, jlen = hdr
    files, dirs = _asar_walk(h)
    if field in ("file_names", "file_paths", "files", "file_list"):
        return [p for p, _, _ in files]
    if field in ("file_count", "number_of_files", "files_count"):
        return len(files)
    if field in ("directory_names", "dir_names"):
        return dirs
    if field in ("directory_count", "dir_count"):
        return len(dirs)
    if field in ("entry_names", "entry_paths"):
        order = []
        _entries(h, "", order)
        return order
    if field in ("entry_count",):
        return len(files) + len(dirs)
    if field in ("unpacked_files", "unpacked_file_names", "unpacked_paths"):
        return [p for p, _, u in files if u]
    if field in ("unpacked_file_count", "unpacked_count"):
        return sum(1 for _, _, u in files if u)
    if field in ("has_unpacked", "has_unpacked_files"):
        return any(u for _, _, u in files)
    if field in ("executable_files", "executable_file_names"):
        return [p for p, e, _ in files if e.get("executable") is True]
    if field in ("link_names", "symlink_names"):
        return [p for p, e, _ in files if "link" in e]
    if field in ("integrity_algorithm", "integrity_algorithms"):
        algs = []
        for _, e, _ in files:
            a = (e.get("integrity") or {}).get("algorithm") if isinstance(e.get("integrity"), dict) else None
            if a and a not in algs:
                algs.append(a)
        if field == "integrity_algorithms":
            return algs
        return algs[0] if algs else "none"
    if field in ("has_integrity", "integrity_present"):
        return any(isinstance(e.get("integrity"), dict) for _, e, _ in files)
    if field in ("header_size", "header_buf_size", "header_pickle_size"):
        return hsize
    if field in ("header_json_size", "header_json_length", "json_len", "json_length", "header_string_length"):
        return jlen
    if field in ("data_offset", "file_data_offset", "data_base_offset"):
        return base
    if field.startswith("package_") or field in ("name", "version", "main", "description", "product_name",
                                                 "dependencies", "scripts"):
        n = _pick_pkg([p for p, _, _ in files])
        raw = _asar_file(data, hdr, n) if n else None
        pkg = _json_obj(raw) if raw is not None else None
        if pkg is None:
            return "none"
        f = field[8:] if field.startswith("package_") else field
        return _npm_field(pkg, f, ctx.get("param"))
    return None


def _entries(node, prefix, out):
    for name, ent in (node.get("files") or {}).items():
        if isinstance(ent, dict):
            out.append(prefix + name)
            if isinstance(ent.get("files"), dict):
                _entries(ent, prefix + name + "/", out)
