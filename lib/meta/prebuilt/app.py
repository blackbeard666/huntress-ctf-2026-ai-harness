"""Zipped macOS/iOS bundles (`.app`, `.framework`, `.appex`, `.bundle`, `.ipa` Payload/): Info.plist advertised
architectures / minimum OS vs the real executable (prebuilt, SPECULATIVE -- never GM-asked yet; target D20-style
"identify what truly supports the advertised fleet"). Format tokens: app (aliases app_bundle, bundle, macos_app) +
the Info.plist-only keys under plist / info_plist.

Input `data`: a zip (the bundle zipped, or an evidence zip holding one or more bundles), an Info.plist itself (XML or
`bplist00`), or the bundle's Mach-O executable itself (executable_* fields only).
Bundle layout (Apple "Bundle Programming Guide"):
  macOS app      X.app/Contents/Info.plist, executable X.app/Contents/MacOS/<CFBundleExecutable>
  iOS app / ipa  [Payload/]X.app/Info.plist, executable X.app/<CFBundleExecutable>
  framework      X.framework/Versions/<V>/Resources/Info.plist, executable X.framework/Versions/<V>/<exe>
                 (X.framework/Resources and X.framework/<exe> are symlinks; zip -y stores a symlink as a member whose
                 data is the link target and whose external_attr high 16 bits carry S_IFLNK 0o120000 -- resolved).
Several bundles in one zip: the one whose name the question's member names, else the OUTERMOST (shortest path) --
nested helpers/frameworks never win by default. `__MACOSX/` AppleDouble shadows are ignored.
Values: plist strings verbatim (LSMinimumSystemVersion "11.0" stays "11.0"); bools true/false; arrays compact JSON in
stored order. executable_cpu_type_set = lib.meta.macho.cpu_type_set (GM-verified D20 spelling: "0x%08x" per slice,
fat_arch order). executable_min_os = LC_BUILD_VERSION minos else LC_VERSION_MIN_* (otool -l spelling "13.2.1"/"10.13",
first slice of a fat file, prebuilt macho.py). advertised_vs_actual_mismatch = true when an LSArchitecturePriority
arch has no matching slice: arm64 -> cputype 0x0100000c (subtype != 2), arm64e -> 0x0100000c subtype 2,
x86_64 -> 0x01000007, i386 -> 7, ppc -> 18, ppc64 -> 0x01000012, arm64_32 -> 0x0200000c.
Not a zip/plist/Mach-O, no bundle, key absent -> "none"; executable fields from a bare Info.plist -> None."""
import io
import plistlib
import posixpath
import re
import struct
import zipfile

_FMTS = ("app", "app_bundle", "bundle", "macos_app")
_KEYS = {
    "bundle_identifier": "CFBundleIdentifier", "bundle_id": "CFBundleIdentifier",
    "cf_bundle_identifier": "CFBundleIdentifier",
    "bundle_executable": "CFBundleExecutable", "cf_bundle_executable": "CFBundleExecutable",
    "executable_name": "CFBundleExecutable",
    "bundle_short_version": "CFBundleShortVersionString", "bundle_short_version_string": "CFBundleShortVersionString",
    "cf_bundle_short_version_string": "CFBundleShortVersionString", "short_version_string": "CFBundleShortVersionString",
    "bundle_version": "CFBundleVersion", "cf_bundle_version": "CFBundleVersion",
    "bundle_name": "CFBundleName", "cf_bundle_name": "CFBundleName",
    "bundle_display_name": "CFBundleDisplayName", "cf_bundle_display_name": "CFBundleDisplayName",
    "bundle_package_type": "CFBundlePackageType", "cf_bundle_package_type": "CFBundlePackageType",
    "minimum_system_version": "LSMinimumSystemVersion", "ls_minimum_system_version": "LSMinimumSystemVersion",
    "minimum_os_version": "MinimumOSVersion",
    "architecture_priority": "LSArchitecturePriority", "ls_architecture_priority": "LSArchitecturePriority",
    "advertised_architectures": "LSArchitecturePriority",
    "requires_native_execution": "LSRequiresNativeExecution",
    "ls_requires_native_execution": "LSRequiresNativeExecution",
    "supported_platforms": "CFBundleSupportedPlatforms", "cf_bundle_supported_platforms": "CFBundleSupportedPlatforms",
    "requires_iphone_os": "LSRequiresIPhoneOS", "ls_requires_iphone_os": "LSRequiresIPhoneOS",
    "ui_required_device_capabilities": "UIRequiredDeviceCapabilities",
    "dt_platform_name": "DTPlatformName", "dt_sdk_name": "DTSDKName",
}
_EXEC = ("executable_cpu_type_set", "executable_cpu_types", "executable_cputype_set", "cpu_type_set",
         "executable_cpu_subtype_set", "executable_arch_names", "executable_architectures", "actual_architectures",
         "executable_min_os", "executable_min_os_version", "executable_minos", "executable_minimum_os_version",
         "executable_slice_count", "executable_is_fat", "executable_path", "executable_present",
         "advertised_vs_actual_mismatch", "architecture_mismatch", "arch_mismatch",
         "missing_architectures", "missing_advertised_architectures", "unsupported_advertised_architectures",
         "info_plist_path", "info_plist_format", "bundle_path", "bundle_count", "bundle_names")

FIELDS = {
    ("app", "bundle_identifier"): "app_value", ("app", "bundle_id"): "app_value",
    ("app", "cf_bundle_identifier"): "app_value",
    ("app", "bundle_executable"): "app_value", ("app", "cf_bundle_executable"): "app_value",
    ("app", "executable_name"): "app_value",
    ("app", "bundle_short_version"): "app_value", ("app", "bundle_short_version_string"): "app_value",
    ("app", "cf_bundle_short_version_string"): "app_value", ("app", "short_version_string"): "app_value",
    ("app", "bundle_version"): "app_value", ("app", "cf_bundle_version"): "app_value",
    ("app", "bundle_name"): "app_value", ("app", "cf_bundle_name"): "app_value",
    ("app", "bundle_display_name"): "app_value", ("app", "cf_bundle_display_name"): "app_value",
    ("app", "bundle_package_type"): "app_value", ("app", "cf_bundle_package_type"): "app_value",
    ("app", "minimum_system_version"): "app_value", ("app", "ls_minimum_system_version"): "app_value",
    ("app", "minimum_os_version"): "app_value",
    ("app", "architecture_priority"): "app_value", ("app", "ls_architecture_priority"): "app_value",
    ("app", "advertised_architectures"): "app_value",
    ("app", "requires_native_execution"): "app_value", ("app", "ls_requires_native_execution"): "app_value",
    ("app", "supported_platforms"): "app_value", ("app", "cf_bundle_supported_platforms"): "app_value",
    ("app", "requires_iphone_os"): "app_value", ("app", "ls_requires_iphone_os"): "app_value",
    ("app", "ui_required_device_capabilities"): "app_value",
    ("app", "dt_platform_name"): "app_value", ("app", "dt_sdk_name"): "app_value",
    ("app", "executable_cpu_type_set"): "app_value", ("app", "executable_cpu_types"): "app_value",
    ("app", "executable_cputype_set"): "app_value", ("app", "cpu_type_set"): "app_value",
    ("app", "executable_cpu_subtype_set"): "app_value",
    ("app", "executable_arch_names"): "app_value", ("app", "executable_architectures"): "app_value",
    ("app", "actual_architectures"): "app_value",
    ("app", "executable_min_os"): "app_value", ("app", "executable_min_os_version"): "app_value",
    ("app", "executable_minos"): "app_value", ("app", "executable_minimum_os_version"): "app_value",
    ("app", "executable_slice_count"): "app_value", ("app", "executable_is_fat"): "app_value",
    ("app", "executable_path"): "app_value", ("app", "executable_present"): "app_value",
    ("app", "advertised_vs_actual_mismatch"): "app_value", ("app", "architecture_mismatch"): "app_value",
    ("app", "arch_mismatch"): "app_value",
    ("app", "missing_architectures"): "app_value", ("app", "missing_advertised_architectures"): "app_value",
    ("app", "unsupported_advertised_architectures"): "app_value",
    ("app", "info_plist_path"): "app_value", ("app", "info_plist_format"): "app_value",
    ("app", "bundle_path"): "app_value", ("app", "bundle_count"): "app_value", ("app", "bundle_names"): "app_value",
    ("app", "value_*"): "app_value",
    ("app_bundle", "bundle_identifier"): "app_value", ("app_bundle", "bundle_executable"): "app_value",
    ("app_bundle", "bundle_short_version"): "app_value", ("app_bundle", "bundle_version"): "app_value",
    ("app_bundle", "minimum_system_version"): "app_value", ("app_bundle", "architecture_priority"): "app_value",
    ("app_bundle", "requires_native_execution"): "app_value", ("app_bundle", "supported_platforms"): "app_value",
    ("app_bundle", "executable_cpu_type_set"): "app_value", ("app_bundle", "executable_min_os"): "app_value",
    ("app_bundle", "advertised_vs_actual_mismatch"): "app_value", ("app_bundle", "value_*"): "app_value",
    ("bundle", "bundle_identifier"): "app_value", ("bundle", "bundle_executable"): "app_value",
    ("bundle", "bundle_short_version"): "app_value", ("bundle", "bundle_version"): "app_value",
    ("bundle", "minimum_system_version"): "app_value", ("bundle", "architecture_priority"): "app_value",
    ("bundle", "requires_native_execution"): "app_value", ("bundle", "supported_platforms"): "app_value",
    ("bundle", "executable_cpu_type_set"): "app_value", ("bundle", "executable_min_os"): "app_value",
    ("bundle", "advertised_vs_actual_mismatch"): "app_value", ("bundle", "value_*"): "app_value",
    ("macos_app", "bundle_identifier"): "app_value", ("macos_app", "bundle_executable"): "app_value",
    ("macos_app", "bundle_short_version"): "app_value", ("macos_app", "bundle_version"): "app_value",
    ("macos_app", "minimum_system_version"): "app_value", ("macos_app", "architecture_priority"): "app_value",
    ("macos_app", "requires_native_execution"): "app_value", ("macos_app", "supported_platforms"): "app_value",
    ("macos_app", "executable_cpu_type_set"): "app_value", ("macos_app", "executable_min_os"): "app_value",
    ("macos_app", "advertised_vs_actual_mismatch"): "app_value", ("macos_app", "value_*"): "app_value",
    # Info.plist keys not yet covered by prebuilt plist.py (a bare Info.plist member, or a zip holding a bundle)
    ("plist", "architecture_priority"): "app_value", ("plist", "ls_architecture_priority"): "app_value",
    ("plist", "requires_native_execution"): "app_value", ("plist", "ls_requires_native_execution"): "app_value",
    ("plist", "supported_platforms"): "app_value", ("plist", "cf_bundle_supported_platforms"): "app_value",
    ("plist", "advertised_vs_actual_mismatch"): "app_value", ("plist", "executable_cpu_type_set"): "app_value",
    ("info_plist", "architecture_priority"): "app_value", ("info_plist", "ls_architecture_priority"): "app_value",
    ("info_plist", "requires_native_execution"): "app_value",
    ("info_plist", "ls_requires_native_execution"): "app_value",
    ("info_plist", "supported_platforms"): "app_value", ("info_plist", "cf_bundle_supported_platforms"): "app_value",
}

_BUNDLE = re.compile(r"[^/]+\.(?:app|framework|appex|bundle|xpc|plugin|kext)/", re.I)
_ARCH = {"arm64": (0x0100000c, None), "arm64e": (0x0100000c, 2), "x86_64": (0x01000007, None),
         "x86_64h": (0x01000007, 8), "i386": (7, None), "x86": (7, None), "ppc": (18, None),
         "ppc64": (0x01000012, None), "arm64_32": (0x0200000c, None), "armv7": (12, 9), "armv7s": (12, 11)}
_NAMES = {0x01000007: "x86_64", 7: "i386", 0x0100000c: "arm64", 12: "arm", 18: "ppc", 0x01000012: "ppc64",
          0x0200000c: "arm64_32"}
_MAX = 256 << 20


def _plist(b):
    if not b:
        return None
    s = bytes(b).lstrip(b"\xef\xbb\xbf \t\r\n")
    if not (s.startswith(b"bplist00") or s.startswith(b"<?xml") or s.startswith(b"<plist")
            or s.startswith(b"<!DOCTYPE plist")):
        return None
    try:
        v = plistlib.loads(s)
    except Exception:
        return None
    return v if isinstance(v, dict) else None


def _is_macho(b):
    return len(b) >= 8 and b[:4] in (b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xce",
                                     b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf")


class _Zip:
    """Member reader with zip-symlink resolution (S_IFLNK in external_attr; the member data is the target)."""

    def __init__(self, z):
        self.z = z
        self.info = {}
        for i in z.infolist():
            n = i.filename.rstrip("/")
            if n and not n.startswith("__MACOSX/") and not posixpath.basename(n).startswith("._"):
                self.info.setdefault(n, i)

    def _link(self, i):
        return i is not None and (i.external_attr >> 16) & 0o170000 == 0o120000

    def resolve(self, path):
        """The real member name for `path`, following symlinked path components (<= 16 hops), or None."""
        parts, done, hops = [p for p in path.split("/") if p], [], 0
        while parts:
            cur = "/".join(done + [parts.pop(0)])
            i = self.info.get(cur)
            if self._link(i):
                hops += 1
                if hops > 16 or i.file_size > 4096:
                    return None
                tgt = self.z.read(i).decode("utf-8", "replace").strip()
                base = "/".join(done)
                new = posixpath.normpath(posixpath.join(base, tgt)) if not tgt.startswith("/") else None
                if not new or new.startswith(".."):
                    return None
                parts = [p for p in new.split("/") if p and p != "."] + parts
                done = []
                continue
            done.append(cur.rsplit("/", 1)[-1])
        name = "/".join(done)
        i = self.info.get(name)
        return name if i is not None and not i.is_dir() else None

    def read(self, path):
        n = self.resolve(path)
        if n is None:
            return None
        i = self.info[n]
        if i.file_size > _MAX:
            return None
        try:
            return self.z.read(i)
        except Exception:
            return None


def _is_bundle(name):
    return bool(_BUNDLE.fullmatch(name + "/"))


def _candidates(zr):
    """[(bundle_path, info_plist_member, kind)] of every bundle Info.plist in the zip, outermost first."""
    out = []
    for n in zr.info:
        if posixpath.basename(n) != "Info.plist":
            continue
        d = posixpath.dirname(n)
        base, parent = posixpath.basename(d), posixpath.dirname(d)
        if base == "Contents" and _is_bundle(posixpath.basename(parent)):
            out.append((parent, n, "macos"))
        elif base == "Resources" and posixpath.basename(posixpath.dirname(parent)) == "Versions" \
                and _is_bundle(posixpath.basename(posixpath.dirname(posixpath.dirname(parent)))):
            out.append((posixpath.dirname(posixpath.dirname(parent)), n, "framework"))
        elif base == "Resources" and _is_bundle(posixpath.basename(parent)):
            out.append((parent, n, "framework_flat"))
        elif _is_bundle(base):
            out.append((d, n, "ios"))
    seen, uniq = set(), []
    for c in sorted(out, key=lambda c: (c[0].count("/"), "/Current/" in c[1], len(c[1]), c[1])):
        if c[0] not in seen:      # one entry per bundle (a framework's Versions/A and Versions/Current copies)
            seen.add(c[0])
            uniq.append(c)
    return uniq


def _pick(cands, ctx):
    if not cands:
        return None
    hint = " ".join(str((ctx or {}).get(k) or "") for k in ("member", "artifact")).lower()
    q = ((ctx or {}).get("question") or {})
    hint += " " + str(q.get("question") or "").lower()
    named = [c for c in cands if posixpath.basename(c[0]).lower() in hint]
    if named:
        return max(named, key=lambda c: (len(posixpath.basename(c[0])), -c[0].count("/")))
    return cands[0]


def _exe_path(bundle, plist_member, kind, exe):
    if kind == "macos":
        return [f"{bundle}/Contents/MacOS/{exe}"]
    if kind == "framework":
        vdir = posixpath.dirname(posixpath.dirname(plist_member))
        return [f"{vdir}/{exe}", f"{bundle}/{exe}"]
    if kind == "framework_flat":
        return [f"{bundle}/{exe}", f"{bundle}/Versions/Current/{exe}", f"{bundle}/Versions/A/{exe}"]
    return [f"{bundle}/{exe}"]


def _load(b, ctx):
    """dict(plist=, exe=bytes|None|False, ...) -- exe False = cannot know (bare Info.plist); None = absent."""
    if b[:4] == b"PK\x03\x04" or b[:4] == b"PK\x05\x06":
        try:
            zr = _Zip(zipfile.ZipFile(io.BytesIO(b)))
        except Exception:
            return None
        cands = _candidates(zr)
        c = _pick(cands, ctx)
        if c is None:
            return {"cands": cands}
        bundle, pm, kind = c
        raw = zr.read(pm)
        pl = _plist(raw)
        st = {"cands": cands, "bundle": bundle, "plist_member": pm, "plist": pl, "exe": None, "exe_path": None,
              "plist_format": ("binary" if raw and raw.startswith(b"bplist00") else "xml") if pl is not None else None}
        exe = (pl or {}).get("CFBundleExecutable")
        if isinstance(exe, str) and exe and "/" not in exe:
            for p in _exe_path(bundle, pm, kind, exe):
                data = zr.read(p)
                if data is not None:
                    st["exe"], st["exe_path"] = data, zr.resolve(p)
                    break
        return st
    pl = _plist(b)
    if pl is not None:
        return {"plist": pl, "exe": False, "plist_format": "binary" if b.lstrip()[:8] == b"bplist00" else "xml"}
    if _is_macho(b):
        return {"plist": None, "exe": b, "bare_exe": True}
    return None


def _slices(exe):
    """[(cputype, cpusubtype & 0xffffff)] in fat_arch order (thin = its header), or None when not Mach-O."""
    from .macho import _fat, _thin
    fat = _fat(exe)
    if fat is not None:
        out = []
        magic = struct.unpack_from(">I", exe, 0)[0]
        w = 20 if magic == 0xcafebabe else 32
        for k in range(len(fat)):
            cpu, sub = struct.unpack_from(">II", exe, 8 + k * w)
            out.append((cpu, sub & 0xffffff))
        return out
    h = _thin(exe)
    return [(h["cpu"], h["sub"] & 0xffffff)] if h else None


def _arch_name(cpu, sub):
    if cpu == 0x0100000c and sub == 2:
        return "arm64e"
    if cpu == 0x01000007 and sub == 8:
        return "x86_64h"
    return _NAMES.get(cpu, "0x%08x" % cpu)


def _missing(adv, sl):
    out = []
    for a in adv:
        want = _ARCH.get(str(a).strip().lower())
        if want is None:
            out.append(a)
            continue
        cpu, sub = want
        ok = any(c == cpu and (s == sub if sub is not None else not (cpu == 0x0100000c and s == 2)) for c, s in sl)
        if not ok:
            out.append(a)
    return out


def _squash(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def app_value(data, ctx):
    if data is None:
        return None
    try:
        return _value(bytes(data), ctx or {})
    except Exception:
        return None


def _value(b, ctx):
    f = ctx.get("field") or ""
    st = _load(b, ctx)
    if st is None:
        return "none"
    if f == "bundle_count":
        return len(st.get("cands") or []) if "cands" in st else ("none" if st.get("bare_exe") else 1)
    if f == "bundle_names":
        return [posixpath.basename(c[0]) for c in st["cands"]] if "cands" in st else "none"
    if f == "bundle_path":
        return st.get("bundle") or "none"
    if f == "info_plist_path":
        return st.get("plist_member") or "none"
    if f == "info_plist_format":
        return st.get("plist_format") or "none"
    pl = st.get("plist")
    if f.startswith("value_"):
        if pl is None:
            return "none"
        want = _squash(ctx.get("param") or f[len("value_"):])
        for k, v in pl.items():
            if _squash(k) == want:
                return _render(v)
        return "none"
    if f in _KEYS:
        if pl is None:
            return "none"
        v = pl.get(_KEYS[f])
        if f == "minimum_system_version" and v is None:
            v = pl.get("MinimumOSVersion")
        return "none" if v is None else _render(v)
    if f not in _EXEC:
        return None
    exe = st.get("exe")
    if exe is False:
        return None                       # a bare Info.plist: the executable is not in this member
    if f == "executable_present":
        return exe is not None
    if f == "executable_path":
        return st.get("exe_path") or "none"
    sl = _slices(exe) if exe else None
    if f in ("advertised_vs_actual_mismatch", "architecture_mismatch", "arch_mismatch", "missing_architectures",
             "missing_advertised_architectures", "unsupported_advertised_architectures"):
        adv = (pl or {}).get("LSArchitecturePriority")
        if not isinstance(adv, list) or not adv:
            return "none"
        if sl is None:                    # executable absent / not Mach-O: nothing advertised is backed
            if exe is None and st.get("plist") is None:
                return "none"
            miss = list(adv)
        else:
            miss = _missing(adv, sl)
        return bool(miss) if f.endswith("mismatch") else miss
    if sl is None:
        return "none"
    if f in ("executable_cpu_type_set", "executable_cpu_types", "executable_cputype_set", "cpu_type_set"):
        from lib.meta.macho import cpu_type_set
        return cpu_type_set(exe, ctx)
    if f == "executable_cpu_subtype_set":
        return ["0x%08x" % s for _, s in sl]
    if f in ("executable_arch_names", "executable_architectures", "actual_architectures"):
        return [_arch_name(c, s) for c, s in sl]
    if f == "executable_slice_count":
        return len(sl)
    if f == "executable_is_fat":
        return exe[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf")
    if f.startswith("executable_min"):
        from .macho import _fat, _thin, _version_cmd, _ver
        fat = _fat(exe)
        h = next((x for x in (_thin(exe, off) for _, off, _ in fat) if x), None) if fat else _thin(exe)
        vc = _version_cmd(h) if h else None
        return _ver(vc[1], ctx) if vc else "none"
    return None


def _render(v):
    if isinstance(v, (bool, int, list, dict)):
        return v
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, bytes):
        return v.hex()
    return str(v).strip()
