"""Go buildinfo / Go build ID and Rust toolchain provenance inside ELF / PE / Mach-O (prebuilt, SPECULATIVE --
never GM-asked yet). Format tokens `go`, `golang` (every field), `rust` (rustc_*), and `elf` / `pe` / `macho` /
`binary` for the toolchain-specific names that do not collide with the header modules (no goarch/goos there: those
tokens already mean the ELF/PE machine).

Go buildinfo (debug/buildinfo, cmd/go `go version -m`): the 16-byte header `\\xff Go buildinf:` + ptr size @14 +
flags @15 (bit0 big-endian, bit1 inline strings). Go >= 1.18 (flags&2): the header is 32 bytes, then two uvarint-
length-prefixed strings -- the runtime version (`go1.22.3`) and modinfo. Older (flags&2 == 0): two pointers at +16
and +16+ptrsize, each to a Go string header {data ptr, len}, mapped vaddr -> file offset through ELF PT_LOAD / PE
sections / Mach-O LC_SEGMENT(_64). Modinfo keeps 16-byte sentinels on each end (stripped when line 17 from the end is
'\\n'). Lines (tab-separated): `path <main pkg>`, `mod <path> <version> [<sum>]`, `dep <path> <version> [<sum>]`,
`=> <path> <version> [<sum>]` (replacement of the previous mod/dep), `build <key>=<value>` (key/value
strconv.Quote'd when they hold spaces/quotes/'=': unquoted here, as `go version -m` shows the quoted form but
debug/buildinfo.BuildInfo.Settings holds the raw value).
- go_version: runtime version verbatim (go1.26.0). module_path: the `mod` path (main module; falls back to `path`);
  main_path / main_package_path / path: the `path` line. main_module_version: the `mod` version verbatim
  (`(devel)` or a pseudo-version); main_module_sum: the h1: sum, absent -> "none".
- build_settings: JSON object of every `build` line in stored order (spell -> compact JSON); build_setting_keys: list.
  goos / goarch / cgo_enabled / compiler / buildmode / ldflags / tags / trimpath / vcs / vcs_revision / vcs_time /
  vcs_modified / goamd64 / goarm64 / go386 / goarm / default_godebug: one setting value verbatim (string, e.g.
  vcs.modified -> "false"); absent -> "none". build_setting_*: any key (`build_setting_cgo_cflags` -> CGO_CFLAGS).
- deps / dep_paths / dep_versions / dep_count: the `dep` lines in stored order (`deps` = "path@version").
- go_build_id: ELF note owner "Go" type 4 (.note.go.buildid) desc verbatim, else the `\\xff Go build ID: "..."`
  string the linker puts at the start of text on every OS (what `go tool buildid` prints).
No buildinfo blob -> "none" (a C binary / PE / text file is a decoy, not an error).

Rust: rustc_version = the semver of the `.comment` / anywhere-in-file string `rustc version 1.93.1 (01f6ddf75
2026-02-11)` -> "1.93.1"; rustc_version_string = that whole string verbatim (readelf -p .comment).
rustc_commit = the 40-hex hash of the first `/rustc/<hash>/library` path (official rustup builds embed it in panic
locations); distro builds remap to `library/...` and keep only the short hash in .comment -> rustc_commit_short /
rustc_commit_date read from the version string. Nothing found -> "none"."""
import re
import struct

from ..spell import Hex

_MAGIC = b"\xff Go buildinf:"
_BUILDID = re.compile(rb'\xff Go build ID: "([^"\n]{1,200})"\n \xff')
_RUSTC = re.compile(rb"rustc version (\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?)(?: \(([0-9a-f]{7,40}) (\d{4}-\d{2}-\d{2})\))?"
                    rb"[^\x00\n]*")
_RUSTC_PATH = re.compile(rb"/rustc/([0-9a-f]{40})/")


def _uvarint(b, o):
    v = s = 0
    while o < len(b) and s < 64:
        c = b[o]
        o += 1
        v |= (c & 0x7F) << s
        if c < 0x80:
            return v, o
        s += 7
    return None, o


def _segments(data):
    """[(vaddr, size, fileoff)] of an ELF / PE / Mach-O image, or []."""
    segs = []
    try:
        if data[:4] == b"\x7fELF":
            c64, end = data[4] == 2, "<" if data[5] == 1 else ">"
            if c64:
                phoff, = struct.unpack_from(end + "Q", data, 0x20)
                phentsize, phnum = struct.unpack_from(end + "HH", data, 0x36)
            else:
                phoff, = struct.unpack_from(end + "I", data, 0x1C)
                phentsize, phnum = struct.unpack_from(end + "HH", data, 0x2A)
            for i in range(min(phnum, 256)):
                o = phoff + i * phentsize
                if c64:
                    pt, _, off, va, _, fsz = struct.unpack_from(end + "IIQQQQ", data, o)
                else:
                    pt, off, va, _, fsz = struct.unpack_from(end + "IIIII", data, o)
                if pt == 1:
                    segs.append((va, fsz, off))
        elif data[:2] == b"MZ":
            pe, = struct.unpack_from("<I", data, 0x3C)
            if data[pe:pe + 4] != b"PE\0\0":
                return []
            nsec, = struct.unpack_from("<H", data, pe + 6)
            optsz, = struct.unpack_from("<H", data, pe + 20)
            magic, = struct.unpack_from("<H", data, pe + 24)
            base = struct.unpack_from("<Q" if magic == 0x20B else "<I", data, pe + 24 + (24 if magic == 0x20B else 28))[0]
            so = pe + 24 + optsz
            for i in range(min(nsec, 96)):
                vsz, va, rsz, roff = struct.unpack_from("<IIII", data, so + i * 40 + 8)
                segs.append((base + va, min(vsz or rsz, rsz), roff))
        elif data[:4] in (b"\xcf\xfa\xed\xfe", b"\xce\xfa\xed\xfe"):
            m64 = data[0] == 0xCF
            ncmds, = struct.unpack_from("<I", data, 16)
            o = 32 if m64 else 28
            for _ in range(min(ncmds, 512)):
                cmd, sz = struct.unpack_from("<II", data, o)
                if cmd == 0x19:
                    va, _, off, fsz = struct.unpack_from("<QQQQ", data, o + 24)
                    segs.append((va, fsz, off))
                elif cmd == 0x1:
                    va, _, off, fsz = struct.unpack_from("<IIII", data, o + 24)
                    segs.append((va, fsz, off))
                if sz < 8:
                    break
                o += sz
    except (struct.error, IndexError):
        return segs
    return segs


def _read_gostr(data, segs, addr, ps, end):
    """The Go string whose header sits at vaddr `addr` (pre-1.18 buildinfo), or None."""
    def at(va, n):
        for sva, ssz, off in segs:
            if sva <= va and va + n <= sva + ssz:
                return data[off + va - sva: off + va - sva + n]
        return None
    hdr = at(addr, 2 * ps)
    if not hdr or len(hdr) < 2 * ps:
        return None
    p, n = struct.unpack(end + ("QQ" if ps == 8 else "II"), hdr)
    if n > 1 << 20:
        return None
    s = at(p, n) if n else b""
    return None if s is None else s.decode("utf-8", "replace")


def buildinfo(data):
    """(go_version, modinfo_text) of the first buildinfo blob, or None."""
    if not data:
        return None
    i = data.find(_MAGIC)
    while i >= 0:
        hdr = data[i:i + 32]
        if len(hdr) >= 16:
            ps, flags = hdr[14], hdr[15]
            if flags & 2:
                o = i + 32
                n, o = _uvarint(data, o)
                if n is not None and n < 4096 and o + n <= len(data):
                    ver = data[o:o + n].decode("utf-8", "replace")
                    o += n
                    m, o = _uvarint(data, o)
                    if m is not None and m < (1 << 22) and o + m <= len(data):
                        return ver, data[o:o + m].decode("utf-8", "replace")
            elif ps in (4, 8):
                end = ">" if flags & 1 else "<"
                segs = _segments(data)
                fmt = end + ("Q" if ps == 8 else "I")
                try:
                    va, = struct.unpack_from(fmt, data, i + 16)
                    ma, = struct.unpack_from(fmt, data, i + 16 + ps)
                except struct.error:
                    va = ma = None
                if segs and va is not None:
                    ver, mod = _read_gostr(data, segs, va, ps, end), _read_gostr(data, segs, ma, ps, end)
                    if ver and ver.startswith("go") or ver == "devel":
                        return ver, mod or ""
        i = data.find(_MAGIC, i + 1)
    return None


def _unquote(s):
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        try:
            import json
            return json.loads(s)
        except ValueError:
            return s[1:-1]
    return s


def _split_setting(rest):
    """`key=value` with strconv.Quote'd parts -> (key, value)."""
    if rest.startswith('"'):
        m = re.match(r'"((?:[^"\\]|\\.)*)"=(.*)$', rest)
        if m:
            return _unquote('"' + m.group(1) + '"'), _unquote(m.group(2))
    k, _, v = rest.partition("=")
    return k, _unquote(v)


def parse_modinfo(text):
    """{path, mod:[path,ver,sum], deps:[[path,ver,sum]], settings:{k:v}} from modinfo text."""
    if len(text) >= 33 and text[-17] == "\n":
        text = text[16:-16]
    out = {"path": None, "mod": None, "deps": [], "settings": {}}
    last = None
    for line in text.split("\n"):
        kind, _, rest = line.partition("\t")
        parts = rest.split("\t")
        if kind == "path":
            out["path"] = rest
        elif kind in ("mod", "dep"):
            ent = (parts + ["", "", ""])[:3]
            if kind == "mod":
                out["mod"] = ent
            else:
                out["deps"].append(ent)
            last = ent
        elif kind == "=>" and last is not None:
            last.append((parts + ["", ""])[:3])
        elif kind == "build" and rest:
            k, v = _split_setting(rest)
            out["settings"].setdefault(k, v)
    return out


def go_build_id(data):
    if not data:
        return None
    if data[:4] == b"\x7fELF":
        # NT note namesz=4, descsz, type=4, owner "Go\0\0" (LE then BE), within the first 64 KiB (note segment)
        for m in re.finditer(rb"\x04\x00\x00\x00(.{4})\x04\x00\x00\x00Go\x00\x00", data[:1 << 16], re.S):
            n, = struct.unpack("<I", m.group(1))
            s = data[m.end():m.end() + n]
            if 0 < n < 256 and len(s) == n:
                return s.rstrip(b"\0").decode("utf-8", "replace")
        for m in re.finditer(rb"\x00\x00\x00\x04(.{4})\x00\x00\x00\x04Go\x00\x00", data[:1 << 16], re.S):
            n, = struct.unpack(">I", m.group(1))
            s = data[m.end():m.end() + n]
            if 0 < n < 256 and len(s) == n:
                return s.rstrip(b"\0").decode("utf-8", "replace")
    m = _BUILDID.search(data)
    return m.group(1).decode("utf-8", "replace") if m else None


_SETTING = {"goos": "GOOS", "goarch": "GOARCH", "cgo_enabled": "CGO_ENABLED", "compiler": "-compiler",
            "buildmode": "-buildmode", "build_mode": "-buildmode", "ldflags": "-ldflags", "tags": "-tags",
            "build_tags": "-tags", "trimpath": "-trimpath", "gcflags": "-gcflags", "asmflags": "-asmflags",
            "vcs": "vcs", "vcs_revision": "vcs.revision", "vcs_time": "vcs.time", "vcs_modified": "vcs.modified",
            "goamd64": "GOAMD64", "goarm64": "GOARM64", "go386": "GO386", "goarm": "GOARM", "gomips": "GOMIPS",
            "default_godebug": "DefaultGODEBUG", "race": "-race", "cgo_cflags": "CGO_CFLAGS",
            "cgo_ldflags": "CGO_LDFLAGS"}
_STRIP = re.compile(r"^(?:go_|golang_)?(?:build_?info_|buildinf_|go_)?")


def go_value(data, ctx):
    if data is None:
        return None
    field = ctx.get("field") or ""
    f = _STRIP.sub("", field)
    if f in ("build_id", "go_build_id"):
        return go_build_id(data) or "none"
    try:
        bi = buildinfo(data)
    except Exception:  # noqa: BLE001
        return None
    if f in ("ptr_size", "pointer_size", "flags_u8_hex", "flags"):
        i = data.find(_MAGIC)
        if i < 0 or i + 16 > len(data):
            return "none"
        return data[i + 14] if f.startswith("p") else Hex(data[i + 15], 2)
    if bi is None:
        return "none"
    ver, text = bi
    if f in ("version", "go_version", "runtime_version", "toolchain_version", "compiler_version"):
        return ver
    info = parse_modinfo(text)
    mod, sets, deps = info["mod"], info["settings"], info["deps"]
    if f in ("path", "main_path", "main_package_path", "package_path", "main_package"):
        return info["path"] or "none"
    if f in ("module_path", "main_module_path", "main_module", "module", "mod_path"):
        return (mod[0] if mod else info["path"]) or "none"
    if f in ("main_module_version", "module_version", "mod_version"):
        return (mod[1] if mod and mod[1] else "none")
    if f in ("main_module_sum", "module_sum", "mod_sum"):
        return (mod[2] if mod and mod[2] else "none")
    if f in ("settings", "build_settings"):
        return dict(sets)
    if f in ("setting_keys", "build_setting_keys", "build_settings_keys"):
        return list(sets)
    if f in ("deps", "dependencies", "dep_modules", "dependency_modules"):
        return [f"{d[0]}@{d[1]}" for d in deps]
    if f in ("dep_paths", "dependency_paths", "dep_module_paths"):
        return [d[0] for d in deps]
    if f in ("dep_versions", "dependency_versions"):
        return [d[1] for d in deps]
    if f in ("dep_count", "dependency_count", "deps_count", "number_of_deps"):
        return len(deps)
    key = _SETTING.get(f)
    if key is None and f.startswith("build_"):
        key = _SETTING.get(f[6:])
    if key is None and ctx.get("param"):
        p = ctx["param"]
        key = next((k for k in sets if k.lower().replace(".", "_").replace("-", "") == p.lower()), p)
    if key is None:
        return None
    v = sets.get(key)
    return "none" if v is None else v


def rust_value(data, ctx):
    if data is None:
        return None
    field = _STRIP.sub("", ctx.get("field") or "")
    m = _RUSTC.search(data)
    if field in ("rustc_version", "rust_version", "compiler_version", "toolchain_version", "version"):
        return m.group(1).decode() if m else "none"
    if field in ("rustc_version_string", "rustc_comment", "rustc_version_full"):
        return m.group(0).decode("utf-8", "replace").strip() if m else "none"
    if field in ("rustc_commit_short", "rustc_short_commit", "rustc_commit_hash_short"):
        return m.group(2).decode() if m and m.group(2) else "none"
    if field in ("rustc_commit_date", "rustc_date", "rustc_release_date"):
        return m.group(3).decode() if m and m.group(3) else "none"
    if field in ("rustc_commit", "rustc_commit_hash", "rustc_hash", "rust_commit", "commit_hash", "commit"):
        p = _RUSTC_PATH.search(data)
        return p.group(1).decode() if p else "none"
    return None


FIELDS = {
    ('go', 'go_version'): 'go_value',
    ('go', 'version'): 'go_value',
    ('go', 'runtime_version'): 'go_value',
    ('go', 'module_path'): 'go_value',
    ('go', 'main_module_path'): 'go_value',
    ('go', 'main_module'): 'go_value',
    ('go', 'path'): 'go_value',
    ('go', 'main_path'): 'go_value',
    ('go', 'main_package_path'): 'go_value',
    ('go', 'main_module_version'): 'go_value',
    ('go', 'module_version'): 'go_value',
    ('go', 'main_module_sum'): 'go_value',
    ('go', 'build_settings'): 'go_value',
    ('go', 'build_setting_keys'): 'go_value',
    ('go', 'goos'): 'go_value',
    ('go', 'goarch'): 'go_value',
    ('go', 'cgo_enabled'): 'go_value',
    ('go', 'compiler'): 'go_value',
    ('go', 'buildmode'): 'go_value',
    ('go', 'build_mode'): 'go_value',
    ('go', 'ldflags'): 'go_value',
    ('go', 'tags'): 'go_value',
    ('go', 'build_tags'): 'go_value',
    ('go', 'trimpath'): 'go_value',
    ('go', 'gcflags'): 'go_value',
    ('go', 'vcs'): 'go_value',
    ('go', 'vcs_revision'): 'go_value',
    ('go', 'vcs_time'): 'go_value',
    ('go', 'vcs_modified'): 'go_value',
    ('go', 'goamd64'): 'go_value',
    ('go', 'goarm64'): 'go_value',
    ('go', 'go386'): 'go_value',
    ('go', 'goarm'): 'go_value',
    ('go', 'default_godebug'): 'go_value',
    ('go', 'deps'): 'go_value',
    ('go', 'dep_paths'): 'go_value',
    ('go', 'dep_versions'): 'go_value',
    ('go', 'dep_count'): 'go_value',
    ('go', 'dependencies'): 'go_value',
    ('go', 'go_build_id'): 'go_value',
    ('go', 'build_id'): 'go_value',
    ('go', 'buildinfo_ptr_size'): 'go_value',
    ('go', 'buildinfo_flags_u8_hex'): 'go_value',
    ('go', 'build_setting_*'): 'go_value',
    ('go', 'rustc_version'): 'rust_value',
    ('go', 'rustc_version_string'): 'rust_value',
    ('go', 'rustc_commit'): 'rust_value',
    ('go', 'rustc_commit_hash'): 'rust_value',
    ('go', 'rustc_commit_short'): 'rust_value',
    ('go', 'rustc_commit_date'): 'rust_value',
    ('golang', 'go_version'): 'go_value',
    ('golang', 'version'): 'go_value',
    ('golang', 'runtime_version'): 'go_value',
    ('golang', 'module_path'): 'go_value',
    ('golang', 'main_module_path'): 'go_value',
    ('golang', 'main_module'): 'go_value',
    ('golang', 'path'): 'go_value',
    ('golang', 'main_path'): 'go_value',
    ('golang', 'main_package_path'): 'go_value',
    ('golang', 'main_module_version'): 'go_value',
    ('golang', 'module_version'): 'go_value',
    ('golang', 'main_module_sum'): 'go_value',
    ('golang', 'build_settings'): 'go_value',
    ('golang', 'build_setting_keys'): 'go_value',
    ('golang', 'goos'): 'go_value',
    ('golang', 'goarch'): 'go_value',
    ('golang', 'cgo_enabled'): 'go_value',
    ('golang', 'compiler'): 'go_value',
    ('golang', 'buildmode'): 'go_value',
    ('golang', 'build_mode'): 'go_value',
    ('golang', 'ldflags'): 'go_value',
    ('golang', 'tags'): 'go_value',
    ('golang', 'build_tags'): 'go_value',
    ('golang', 'trimpath'): 'go_value',
    ('golang', 'gcflags'): 'go_value',
    ('golang', 'vcs'): 'go_value',
    ('golang', 'vcs_revision'): 'go_value',
    ('golang', 'vcs_time'): 'go_value',
    ('golang', 'vcs_modified'): 'go_value',
    ('golang', 'goamd64'): 'go_value',
    ('golang', 'goarm64'): 'go_value',
    ('golang', 'go386'): 'go_value',
    ('golang', 'goarm'): 'go_value',
    ('golang', 'default_godebug'): 'go_value',
    ('golang', 'deps'): 'go_value',
    ('golang', 'dep_paths'): 'go_value',
    ('golang', 'dep_versions'): 'go_value',
    ('golang', 'dep_count'): 'go_value',
    ('golang', 'dependencies'): 'go_value',
    ('golang', 'go_build_id'): 'go_value',
    ('golang', 'build_id'): 'go_value',
    ('golang', 'buildinfo_ptr_size'): 'go_value',
    ('golang', 'buildinfo_flags_u8_hex'): 'go_value',
    ('golang', 'build_setting_*'): 'go_value',
    ('golang', 'rustc_version'): 'rust_value',
    ('golang', 'rustc_version_string'): 'rust_value',
    ('golang', 'rustc_commit'): 'rust_value',
    ('golang', 'rustc_commit_hash'): 'rust_value',
    ('golang', 'rustc_commit_short'): 'rust_value',
    ('golang', 'rustc_commit_date'): 'rust_value',
    ('rust', 'rustc_version'): 'rust_value',
    ('rust', 'rustc_version_string'): 'rust_value',
    ('rust', 'rustc_commit'): 'rust_value',
    ('rust', 'rustc_commit_hash'): 'rust_value',
    ('rust', 'rustc_commit_short'): 'rust_value',
    ('rust', 'rustc_commit_date'): 'rust_value',
    ('rust', 'rust_version'): 'rust_value',
    ('rust', 'compiler_version'): 'rust_value',
    ('elf', 'go_version'): 'go_value',
    ('elf', 'go_runtime_version'): 'go_value',
    ('elf', 'go_module_path'): 'go_value',
    ('elf', 'go_main_module_path'): 'go_value',
    ('elf', 'go_main_package_path'): 'go_value',
    ('elf', 'go_path'): 'go_value',
    ('elf', 'go_main_module_version'): 'go_value',
    ('elf', 'go_main_module_sum'): 'go_value',
    ('elf', 'go_build_settings'): 'go_value',
    ('elf', 'go_build_setting_keys'): 'go_value',
    ('elf', 'go_goos'): 'go_value',
    ('elf', 'go_goarch'): 'go_value',
    ('elf', 'go_cgo_enabled'): 'go_value',
    ('elf', 'go_ldflags'): 'go_value',
    ('elf', 'go_vcs'): 'go_value',
    ('elf', 'go_vcs_revision'): 'go_value',
    ('elf', 'go_vcs_time'): 'go_value',
    ('elf', 'go_vcs_modified'): 'go_value',
    ('elf', 'go_deps'): 'go_value',
    ('elf', 'go_dep_paths'): 'go_value',
    ('elf', 'go_dep_count'): 'go_value',
    ('elf', 'go_build_id'): 'go_value',
    ('elf', 'go_buildinfo_ptr_size'): 'go_value',
    ('elf', 'go_buildinfo_flags_u8_hex'): 'go_value',
    ('elf', 'go_build_setting_*'): 'go_value',
    ('elf', 'vcs_revision'): 'go_value',
    ('elf', 'vcs_time'): 'go_value',
    ('elf', 'vcs_modified'): 'go_value',
    ('elf', 'main_module_version'): 'go_value',
    ('elf', 'module_path'): 'go_value',
    ('elf', 'build_settings'): 'go_value',
    ('elf', 'buildinfo_ptr_size'): 'go_value',
    ('elf', 'buildinfo_flags_u8_hex'): 'go_value',
    ('elf', 'rustc_version'): 'rust_value',
    ('elf', 'rustc_version_string'): 'rust_value',
    ('elf', 'rustc_commit'): 'rust_value',
    ('elf', 'rustc_commit_hash'): 'rust_value',
    ('elf', 'rustc_commit_short'): 'rust_value',
    ('elf', 'rustc_commit_date'): 'rust_value',
    ('pe', 'go_version'): 'go_value',
    ('pe', 'go_runtime_version'): 'go_value',
    ('pe', 'go_module_path'): 'go_value',
    ('pe', 'go_main_module_path'): 'go_value',
    ('pe', 'go_main_package_path'): 'go_value',
    ('pe', 'go_path'): 'go_value',
    ('pe', 'go_main_module_version'): 'go_value',
    ('pe', 'go_main_module_sum'): 'go_value',
    ('pe', 'go_build_settings'): 'go_value',
    ('pe', 'go_build_setting_keys'): 'go_value',
    ('pe', 'go_goos'): 'go_value',
    ('pe', 'go_goarch'): 'go_value',
    ('pe', 'go_cgo_enabled'): 'go_value',
    ('pe', 'go_ldflags'): 'go_value',
    ('pe', 'go_vcs'): 'go_value',
    ('pe', 'go_vcs_revision'): 'go_value',
    ('pe', 'go_vcs_time'): 'go_value',
    ('pe', 'go_vcs_modified'): 'go_value',
    ('pe', 'go_deps'): 'go_value',
    ('pe', 'go_dep_paths'): 'go_value',
    ('pe', 'go_dep_count'): 'go_value',
    ('pe', 'go_build_id'): 'go_value',
    ('pe', 'go_buildinfo_ptr_size'): 'go_value',
    ('pe', 'go_buildinfo_flags_u8_hex'): 'go_value',
    ('pe', 'go_build_setting_*'): 'go_value',
    ('pe', 'vcs_revision'): 'go_value',
    ('pe', 'vcs_time'): 'go_value',
    ('pe', 'vcs_modified'): 'go_value',
    ('pe', 'main_module_version'): 'go_value',
    ('pe', 'module_path'): 'go_value',
    ('pe', 'build_settings'): 'go_value',
    ('pe', 'buildinfo_ptr_size'): 'go_value',
    ('pe', 'buildinfo_flags_u8_hex'): 'go_value',
    ('pe', 'rustc_version'): 'rust_value',
    ('pe', 'rustc_version_string'): 'rust_value',
    ('pe', 'rustc_commit'): 'rust_value',
    ('pe', 'rustc_commit_hash'): 'rust_value',
    ('pe', 'rustc_commit_short'): 'rust_value',
    ('pe', 'rustc_commit_date'): 'rust_value',
    ('macho', 'go_version'): 'go_value',
    ('macho', 'go_runtime_version'): 'go_value',
    ('macho', 'go_module_path'): 'go_value',
    ('macho', 'go_main_module_path'): 'go_value',
    ('macho', 'go_main_package_path'): 'go_value',
    ('macho', 'go_path'): 'go_value',
    ('macho', 'go_main_module_version'): 'go_value',
    ('macho', 'go_main_module_sum'): 'go_value',
    ('macho', 'go_build_settings'): 'go_value',
    ('macho', 'go_build_setting_keys'): 'go_value',
    ('macho', 'go_goos'): 'go_value',
    ('macho', 'go_goarch'): 'go_value',
    ('macho', 'go_cgo_enabled'): 'go_value',
    ('macho', 'go_ldflags'): 'go_value',
    ('macho', 'go_vcs'): 'go_value',
    ('macho', 'go_vcs_revision'): 'go_value',
    ('macho', 'go_vcs_time'): 'go_value',
    ('macho', 'go_vcs_modified'): 'go_value',
    ('macho', 'go_deps'): 'go_value',
    ('macho', 'go_dep_paths'): 'go_value',
    ('macho', 'go_dep_count'): 'go_value',
    ('macho', 'go_build_id'): 'go_value',
    ('macho', 'go_buildinfo_ptr_size'): 'go_value',
    ('macho', 'go_buildinfo_flags_u8_hex'): 'go_value',
    ('macho', 'go_build_setting_*'): 'go_value',
    ('macho', 'vcs_revision'): 'go_value',
    ('macho', 'vcs_time'): 'go_value',
    ('macho', 'vcs_modified'): 'go_value',
    ('macho', 'main_module_version'): 'go_value',
    ('macho', 'module_path'): 'go_value',
    ('macho', 'build_settings'): 'go_value',
    ('macho', 'buildinfo_ptr_size'): 'go_value',
    ('macho', 'buildinfo_flags_u8_hex'): 'go_value',
    ('macho', 'rustc_version'): 'rust_value',
    ('macho', 'rustc_version_string'): 'rust_value',
    ('macho', 'rustc_commit'): 'rust_value',
    ('macho', 'rustc_commit_hash'): 'rust_value',
    ('macho', 'rustc_commit_short'): 'rust_value',
    ('macho', 'rustc_commit_date'): 'rust_value',
    ('binary', 'go_version'): 'go_value',
    ('binary', 'go_runtime_version'): 'go_value',
    ('binary', 'go_module_path'): 'go_value',
    ('binary', 'go_main_module_path'): 'go_value',
    ('binary', 'go_main_package_path'): 'go_value',
    ('binary', 'go_path'): 'go_value',
    ('binary', 'go_main_module_version'): 'go_value',
    ('binary', 'go_main_module_sum'): 'go_value',
    ('binary', 'go_build_settings'): 'go_value',
    ('binary', 'go_build_setting_keys'): 'go_value',
    ('binary', 'go_goos'): 'go_value',
    ('binary', 'go_goarch'): 'go_value',
    ('binary', 'go_cgo_enabled'): 'go_value',
    ('binary', 'go_ldflags'): 'go_value',
    ('binary', 'go_vcs'): 'go_value',
    ('binary', 'go_vcs_revision'): 'go_value',
    ('binary', 'go_vcs_time'): 'go_value',
    ('binary', 'go_vcs_modified'): 'go_value',
    ('binary', 'go_deps'): 'go_value',
    ('binary', 'go_dep_paths'): 'go_value',
    ('binary', 'go_dep_count'): 'go_value',
    ('binary', 'go_build_id'): 'go_value',
    ('binary', 'go_buildinfo_ptr_size'): 'go_value',
    ('binary', 'go_buildinfo_flags_u8_hex'): 'go_value',
    ('binary', 'go_build_setting_*'): 'go_value',
    ('binary', 'vcs_revision'): 'go_value',
    ('binary', 'vcs_time'): 'go_value',
    ('binary', 'vcs_modified'): 'go_value',
    ('binary', 'main_module_version'): 'go_value',
    ('binary', 'module_path'): 'go_value',
    ('binary', 'build_settings'): 'go_value',
    ('binary', 'buildinfo_ptr_size'): 'go_value',
    ('binary', 'buildinfo_flags_u8_hex'): 'go_value',
    ('binary', 'rustc_version'): 'rust_value',
    ('binary', 'rustc_version_string'): 'rust_value',
    ('binary', 'rustc_commit'): 'rust_value',
    ('binary', 'rustc_commit_hash'): 'rust_value',
    ('binary', 'rustc_commit_short'): 'rust_value',
    ('binary', 'rustc_commit_date'): 'rust_value',
}
