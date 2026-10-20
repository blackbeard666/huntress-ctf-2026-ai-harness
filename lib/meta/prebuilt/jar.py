"""JAR/WAR/EAR packaging fields (prebuilt, SPECULATIVE -- never GM-asked yet).

A jar is a zip holding `META-INF/MANIFEST.MF` (JAR File Specification). The manifest is RFC-822-like: `Name: value`
lines (72-byte wrapped; a continuation line starts with ONE space, which is dropped), main section until the first
blank line, then per-entry sections (ignored here). Attribute names are case-insensitive (`Main-Class`).
Fields (fmt jar, aliases java_archive / war / ear; manifest + class-set fields also under fmt java):
  manifest_<attr> / <attr>: the main-section value verbatim (trimmed); `manifest_*` maps snake_case onto the header
    name ignoring case and '-' (`implementation_vendor` -> Implementation-Vendor, `bundle_symbolic_name` ->
    Bundle-SymbolicName). Absent attribute -> "none".
  manifest_multi_release: bool (Multi-Release == "true", case-insensitive; absent -> false, as the JDK reads it).
  class_path: Class-Path split on whitespace -> JSON list, stored order.
  class_major_version_set: sorted ascending distinct u16 BE majors @6 of every `*.class` member whose magic is
    0xCAFEBABE (incl. META-INF/versions/N/ and module-info.class); max_class_major_version = its max;
    java_version_min = min major - 44 as text ("8", "11", "17", "21"; 45..48 -> "1.1".."1.4").
  class_count: number of `*.class` file members (directories excluded).
  signature_files: META-INF/<name>.SF/.RSA/.DSA/.EC directly under META-INF (not subdirs), central-directory order.
Not a zip / no manifest -> "none" (class fields also accept a manifest-less zip that holds .class members)."""
import io
import re
import struct
import zipfile

_CLASS_FIELDS = {"class_major_version_set": "set", "class_major_versions": "set", "class_file_major_versions": "set",
                 "major_version_set": "set", "max_class_major_version": "max", "class_major_version_max": "max",
                 "min_class_major_version": "min", "java_version_min": "jmin", "min_java_version": "jmin",
                 "java_version_max": "jmax", "max_java_version": "jmax",
                 "class_count": "count", "class_file_count": "count", "number_of_classes": "count"}

FIELDS = {
    ("jar", "manifest_main_class"): "jar_manifest",
    ("jar", "main_class"): "jar_manifest",
    ("jar", "manifest_created_by"): "jar_manifest",
    ("jar", "created_by"): "jar_manifest",
    ("jar", "manifest_version"): "jar_manifest",
    ("jar", "manifest_manifest_version"): "jar_manifest",
    ("jar", "implementation_title"): "jar_manifest",
    ("jar", "implementation_version"): "jar_manifest",
    ("jar", "implementation_vendor"): "jar_manifest",
    ("jar", "manifest_implementation_title"): "jar_manifest",
    ("jar", "manifest_implementation_version"): "jar_manifest",
    ("jar", "manifest_implementation_vendor"): "jar_manifest",
    ("jar", "specification_title"): "jar_manifest",
    ("jar", "specification_version"): "jar_manifest",
    ("jar", "specification_vendor"): "jar_manifest",
    ("jar", "automatic_module_name"): "jar_manifest",
    ("jar", "manifest_automatic_module_name"): "jar_manifest",
    ("jar", "built_by"): "jar_manifest",
    ("jar", "manifest_built_by"): "jar_manifest",
    ("jar", "build_jdk"): "jar_manifest",
    ("jar", "build_jdk_spec"): "jar_manifest",
    ("jar", "manifest_build_jdk_spec"): "jar_manifest",
    ("jar", "launcher_agent_class"): "jar_manifest",
    ("jar", "premain_class"): "jar_manifest",
    ("jar", "agent_class"): "jar_manifest",
    ("jar", "manifest_*"): "jar_manifest",
    ("jar", "manifest_multi_release"): "jar_multi_release",
    ("jar", "multi_release"): "jar_multi_release",
    ("jar", "class_path"): "jar_class_path",
    ("jar", "manifest_class_path"): "jar_class_path",
    ("jar", "class_major_version_set"): "jar_classes",
    ("jar", "class_major_versions"): "jar_classes",
    ("jar", "class_file_major_versions"): "jar_classes",
    ("jar", "major_version_set"): "jar_classes",
    ("jar", "max_class_major_version"): "jar_classes",
    ("jar", "class_major_version_max"): "jar_classes",
    ("jar", "min_class_major_version"): "jar_classes",
    ("jar", "java_version_min"): "jar_classes",
    ("jar", "min_java_version"): "jar_classes",
    ("jar", "java_version_max"): "jar_classes",
    ("jar", "max_java_version"): "jar_classes",
    ("jar", "class_count"): "jar_classes",
    ("jar", "class_file_count"): "jar_classes",
    ("jar", "number_of_classes"): "jar_classes",
    ("jar", "signature_files"): "jar_signature_files",
    ("jar", "signature_file_names"): "jar_signature_files",
    ("jar", "signature_file_list"): "jar_signature_files",
    ("java_archive", "manifest_main_class"): "jar_manifest",
    ("java_archive", "main_class"): "jar_manifest",
    ("java_archive", "manifest_created_by"): "jar_manifest",
    ("java_archive", "created_by"): "jar_manifest",
    ("java_archive", "manifest_version"): "jar_manifest",
    ("java_archive", "implementation_title"): "jar_manifest",
    ("java_archive", "implementation_version"): "jar_manifest",
    ("java_archive", "implementation_vendor"): "jar_manifest",
    ("java_archive", "automatic_module_name"): "jar_manifest",
    ("java_archive", "manifest_*"): "jar_manifest",
    ("java_archive", "manifest_multi_release"): "jar_multi_release",
    ("java_archive", "multi_release"): "jar_multi_release",
    ("java_archive", "class_path"): "jar_class_path",
    ("java_archive", "manifest_class_path"): "jar_class_path",
    ("java_archive", "class_major_version_set"): "jar_classes",
    ("java_archive", "max_class_major_version"): "jar_classes",
    ("java_archive", "java_version_min"): "jar_classes",
    ("java_archive", "class_count"): "jar_classes",
    ("java_archive", "signature_files"): "jar_signature_files",
    ("war", "manifest_main_class"): "jar_manifest",
    ("war", "main_class"): "jar_manifest",
    ("war", "manifest_created_by"): "jar_manifest",
    ("war", "created_by"): "jar_manifest",
    ("war", "manifest_version"): "jar_manifest",
    ("war", "implementation_title"): "jar_manifest",
    ("war", "implementation_version"): "jar_manifest",
    ("war", "implementation_vendor"): "jar_manifest",
    ("war", "automatic_module_name"): "jar_manifest",
    ("war", "manifest_*"): "jar_manifest",
    ("war", "manifest_multi_release"): "jar_multi_release",
    ("war", "multi_release"): "jar_multi_release",
    ("war", "class_path"): "jar_class_path",
    ("war", "manifest_class_path"): "jar_class_path",
    ("war", "class_major_version_set"): "jar_classes",
    ("war", "max_class_major_version"): "jar_classes",
    ("war", "java_version_min"): "jar_classes",
    ("war", "class_count"): "jar_classes",
    ("war", "signature_files"): "jar_signature_files",
    ("ear", "manifest_main_class"): "jar_manifest",
    ("ear", "main_class"): "jar_manifest",
    ("ear", "manifest_created_by"): "jar_manifest",
    ("ear", "created_by"): "jar_manifest",
    ("ear", "manifest_version"): "jar_manifest",
    ("ear", "implementation_title"): "jar_manifest",
    ("ear", "implementation_version"): "jar_manifest",
    ("ear", "implementation_vendor"): "jar_manifest",
    ("ear", "automatic_module_name"): "jar_manifest",
    ("ear", "manifest_*"): "jar_manifest",
    ("ear", "manifest_multi_release"): "jar_multi_release",
    ("ear", "multi_release"): "jar_multi_release",
    ("ear", "class_path"): "jar_class_path",
    ("ear", "manifest_class_path"): "jar_class_path",
    ("ear", "class_major_version_set"): "jar_classes",
    ("ear", "max_class_major_version"): "jar_classes",
    ("ear", "java_version_min"): "jar_classes",
    ("ear", "class_count"): "jar_classes",
    ("ear", "signature_files"): "jar_signature_files",
    ("java", "manifest_main_class"): "jar_manifest",
    ("java", "manifest_created_by"): "jar_manifest",
    ("java", "manifest_version"): "jar_manifest",
    ("java", "manifest_implementation_title"): "jar_manifest",
    ("java", "manifest_implementation_version"): "jar_manifest",
    ("java", "manifest_implementation_vendor"): "jar_manifest",
    ("java", "implementation_title"): "jar_manifest",
    ("java", "implementation_version"): "jar_manifest",
    ("java", "implementation_vendor"): "jar_manifest",
    ("java", "automatic_module_name"): "jar_manifest",
    ("java", "manifest_automatic_module_name"): "jar_manifest",
    ("java", "manifest_*"): "jar_manifest",
    ("java", "manifest_multi_release"): "jar_multi_release",
    ("java", "manifest_class_path"): "jar_class_path",
    ("java", "class_major_version_set"): "jar_classes",
    ("java", "max_class_major_version"): "jar_classes",
    ("java", "java_version_min"): "jar_classes",
    ("java", "class_count"): "jar_classes",
    ("java", "signature_files"): "jar_signature_files",
}

_MF = "META-INF/MANIFEST.MF"
_SIG = re.compile(r"^META-INF/[^/]+\.(SF|RSA|DSA|EC)$", re.I)
# snake_case field -> manifest header for names that don't title-case cleanly
_ATTR = {"version": "Manifest-Version", "manifest_version": "Manifest-Version", "build_jdk_spec": "Build-Jdk-Spec"}


def _zip(data):
    if not isinstance(data, (bytes, bytearray)) or len(data) < 22 or bytes(data[:2]) != b"PK":
        return None
    try:
        return zipfile.ZipFile(io.BytesIO(bytes(data)))
    except Exception:  # noqa: BLE001 -- truncated / not a zip
        return None


def _manifest_bytes(z):
    names = {i.filename.upper(): i for i in z.infolist()}
    info = names.get(_MF)
    if info is None:
        return None
    try:
        return z.read(info)
    except Exception:  # noqa: BLE001 -- encrypted / bad CRC / unsupported method
        return None


def parse_manifest(raw):
    """Main-section attributes {lower-name: (Name, value)} of a MANIFEST.MF, or None."""
    if raw is None:
        return None
    text = raw.decode("utf-8", "replace")
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out, cur = {}, None
    for ln in lines:
        if ln == "":
            if cur is not None or out:
                break       # end of the main section
            continue
        if ln.startswith(" ") and cur is not None:
            name, val = out[cur]
            out[cur] = (name, val + ln[1:])
            continue
        name, sep, val = ln.partition(":")
        if not sep or not name.strip():
            cur = None
            continue
        key = name.strip().lower()
        out.setdefault(key, (name.strip(), val[1:] if val.startswith(" ") else val))
        cur = key
    return out


def _jar_manifest(data):
    z = _zip(data)
    if z is None:
        return None
    return parse_manifest(_manifest_bytes(z))


def _norm(s):
    return re.sub(r"[-_ ]", "", s.lower())


def _attr(mf, field):
    field = field or ""
    if field in _ATTR:
        want = _ATTR[field]
    else:
        base = field[len("manifest_"):] if field.startswith("manifest_") else field
        if base in _ATTR:
            want = _ATTR[base]
        else:
            want = "-".join(p.capitalize() for p in base.split("_"))
    hit = mf.get(want.lower())
    if hit is None:
        n = _norm(want)
        hit = next((v for k, v in mf.items() if _norm(k) == n), None)
    return None if hit is None else hit[1].strip()


def jar_manifest(data, ctx):
    """<fmt>.manifest_<attr> / <attr>: the main-section value, stored text trimmed."""
    if data is None:
        return None
    mf = _jar_manifest(data)
    if mf is None:
        return "none"
    v = _attr(mf, ctx.get("field"))
    return "none" if v is None else v


def jar_multi_release(data, ctx):
    if data is None:
        return None
    mf = _jar_manifest(data)
    if mf is None:
        return "none"
    v = _attr(mf, "multi_release")
    return (v or "").strip().lower() == "true"


def jar_class_path(data, ctx):
    if data is None:
        return None
    mf = _jar_manifest(data)
    if mf is None:
        return "none"
    v = _attr(mf, "class_path")
    return "none" if v is None else v.split()


def _jver(major):
    if major >= 49:
        return str(major - 44)
    return {45: "1.1", 46: "1.2", 47: "1.3", 48: "1.4"}.get(major)


def jar_classes(data, ctx):
    """Class-file version set / count over every *.class member."""
    if data is None:
        return None
    z = _zip(data)
    if z is None:
        return "none"
    infos = [i for i in z.infolist() if not i.is_dir() and i.filename.lower().endswith(".class")]
    if not infos and _manifest_bytes(z) is None:
        return "none"
    kind = _CLASS_FIELDS.get(ctx.get("field") or "", "set")
    if kind == "count":
        return len(infos)
    majors = set()
    for i in infos:
        try:
            with z.open(i) as fh:
                head = fh.read(8)
        except Exception:  # noqa: BLE001
            continue
        if len(head) == 8 and head[:4] == b"\xca\xfe\xba\xbe":
            major, = struct.unpack(">H", head[6:8])
            if major >= 45:
                majors.add(major)
    ms = sorted(majors)
    if kind == "set":
        return ms
    if not ms:
        return "none"
    return {"max": ms[-1], "min": ms[0], "jmin": _jver(ms[0]), "jmax": _jver(ms[-1])}[kind] or "none"


def jar_signature_files(data, ctx):
    if data is None:
        return None
    z = _zip(data)
    if z is None or _manifest_bytes(z) is None:
        return "none"
    return [i.filename for i in z.infolist() if _SIG.match(i.filename)]
