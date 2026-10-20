"""MSIX/AppX packages and bundles (.msix/.appx/.msixbundle/.appxbundle) fields (prebuilt, SPECULATIVE -- never
GM-asked yet).

A package is a ZIP (OPC) holding AppxManifest.xml, AppxBlockMap.xml, [Content_Types].xml and, when signed,
AppxSignature.p7x. A bundle holds AppxMetadata/AppxBundleManifest.xml (<Bundle><Identity/><Packages><Package
Type= Architecture= FileName= .../></Packages></Bundle>) plus the inner .appx/.msix members. Elements are matched by
LOCAL name (the manifest mixes foundation/uap/rescap/... namespaces). Every value is the attribute text verbatim
(ProcessorArchitecture stays `x64`/`x86`/`arm64`/`neutral` as stored -- no case folding).
Lists are stored document order: target_device_families = ["<Name> <MinVersion>", ...] per <TargetDeviceFamily>;
bundle_package_architectures / _file_names = per <Package> in the bundle's <Packages> (resource packages too, when
they carry the attribute); capabilities = the Name of every child of <Capabilities> (Capability, uap:/rescap:
Capability, DeviceCapability) in stored order.
signature_present = an `AppxSignature.p7x` member exists; block_map_hash_method = <BlockMap HashMethod=> verbatim
(a URI such as http://www.w3.org/2001/04/xmlenc#sha256).
package_family_name / publisher_id: Windows' PublisherId = first 8 bytes of SHA-256(UTF-16LE Publisher) read as a
65-bit big-endian number (64 bits + one 0 pad bit) in 13 Crockford base32 chars (0-9a-z without i l o u) -- the
documented `8wekyb3d8bbwe` for "CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US".
Not a ZIP / no manifest / attribute absent -> "none" (an ordinary .zip or a .nupkg renamed .msix is a decoy)."""
import hashlib
import io
import zipfile
import xml.etree.ElementTree as ET

_FMTS = ("msix", "appx", "msixbundle", "appxbundle")
FIELDS = {
    ("msix", "identity_name"): "identity_name",
    ("msix", "package_name"): "identity_name",
    ("msix", "name"): "identity_name",
    ("msix", "identity_publisher"): "identity_publisher",
    ("msix", "publisher"): "identity_publisher",
    ("msix", "identity_version"): "identity_version",
    ("msix", "package_version"): "identity_version",
    ("msix", "version"): "identity_version",
    ("msix", "identity_processor_architecture"): "identity_arch",
    ("msix", "processor_architecture"): "identity_arch",
    ("msix", "architecture"): "identity_arch",
    ("msix", "identity_architecture"): "identity_arch",
    ("msix", "identity_resource_id"): "identity_resource_id",
    ("msix", "resource_id"): "identity_resource_id",
    ("msix", "publisher_id"): "publisher_id",
    ("msix", "package_family_name"): "package_family_name",
    ("msix", "package_full_name"): "package_full_name",
    ("msix", "display_name"): "display_name",
    ("msix", "properties_display_name"): "display_name",
    ("msix", "publisher_display_name"): "publisher_display_name",
    ("msix", "properties_publisher_display_name"): "publisher_display_name",
    ("msix", "target_device_families"): "target_device_families",
    ("msix", "target_device_family"): "target_device_families",
    ("msix", "bundle_package_architectures"): "bundle_package_architectures",
    ("msix", "package_architectures"): "bundle_package_architectures",
    ("msix", "bundle_package_file_names"): "bundle_package_file_names",
    ("msix", "package_file_names"): "bundle_package_file_names",
    ("msix", "bundle_package_count"): "bundle_package_count",
    ("msix", "package_count"): "bundle_package_count",
    ("msix", "executable"): "executable",
    ("msix", "application_executable"): "executable",
    ("msix", "app_executable"): "executable",
    ("msix", "application_executables"): "application_executables",
    ("msix", "application_ids"): "application_ids",
    ("msix", "application_id"): "application_id",
    ("msix", "entry_point"): "entry_point",
    ("msix", "application_entry_point"): "entry_point",
    ("msix", "capabilities"): "capabilities",
    ("msix", "capability_names"): "capabilities",
    ("msix", "signature_present"): "signature_present",
    ("msix", "is_signed"): "signature_present",
    ("msix", "has_signature"): "signature_present",
    ("msix", "block_map_hash_method"): "block_map_hash_method",
    ("msix", "blockmap_hash_method"): "block_map_hash_method",
    ("msix", "hash_method"): "block_map_hash_method",
    ("msix", "manifest_name"): "manifest_name",
    ("msix", "is_bundle"): "is_bundle",
    ("appx", "identity_name"): "identity_name",
    ("appx", "package_name"): "identity_name",
    ("appx", "name"): "identity_name",
    ("appx", "identity_publisher"): "identity_publisher",
    ("appx", "publisher"): "identity_publisher",
    ("appx", "identity_version"): "identity_version",
    ("appx", "package_version"): "identity_version",
    ("appx", "version"): "identity_version",
    ("appx", "identity_processor_architecture"): "identity_arch",
    ("appx", "processor_architecture"): "identity_arch",
    ("appx", "architecture"): "identity_arch",
    ("appx", "identity_architecture"): "identity_arch",
    ("appx", "identity_resource_id"): "identity_resource_id",
    ("appx", "resource_id"): "identity_resource_id",
    ("appx", "publisher_id"): "publisher_id",
    ("appx", "package_family_name"): "package_family_name",
    ("appx", "package_full_name"): "package_full_name",
    ("appx", "display_name"): "display_name",
    ("appx", "properties_display_name"): "display_name",
    ("appx", "publisher_display_name"): "publisher_display_name",
    ("appx", "properties_publisher_display_name"): "publisher_display_name",
    ("appx", "target_device_families"): "target_device_families",
    ("appx", "target_device_family"): "target_device_families",
    ("appx", "bundle_package_architectures"): "bundle_package_architectures",
    ("appx", "package_architectures"): "bundle_package_architectures",
    ("appx", "bundle_package_file_names"): "bundle_package_file_names",
    ("appx", "package_file_names"): "bundle_package_file_names",
    ("appx", "bundle_package_count"): "bundle_package_count",
    ("appx", "package_count"): "bundle_package_count",
    ("appx", "executable"): "executable",
    ("appx", "application_executable"): "executable",
    ("appx", "app_executable"): "executable",
    ("appx", "application_executables"): "application_executables",
    ("appx", "application_ids"): "application_ids",
    ("appx", "application_id"): "application_id",
    ("appx", "entry_point"): "entry_point",
    ("appx", "application_entry_point"): "entry_point",
    ("appx", "capabilities"): "capabilities",
    ("appx", "capability_names"): "capabilities",
    ("appx", "signature_present"): "signature_present",
    ("appx", "is_signed"): "signature_present",
    ("appx", "has_signature"): "signature_present",
    ("appx", "block_map_hash_method"): "block_map_hash_method",
    ("appx", "blockmap_hash_method"): "block_map_hash_method",
    ("appx", "hash_method"): "block_map_hash_method",
    ("appx", "manifest_name"): "manifest_name",
    ("appx", "is_bundle"): "is_bundle",
    ("msixbundle", "identity_name"): "identity_name",
    ("msixbundle", "package_name"): "identity_name",
    ("msixbundle", "name"): "identity_name",
    ("msixbundle", "identity_publisher"): "identity_publisher",
    ("msixbundle", "publisher"): "identity_publisher",
    ("msixbundle", "identity_version"): "identity_version",
    ("msixbundle", "package_version"): "identity_version",
    ("msixbundle", "version"): "identity_version",
    ("msixbundle", "identity_processor_architecture"): "identity_arch",
    ("msixbundle", "processor_architecture"): "identity_arch",
    ("msixbundle", "architecture"): "identity_arch",
    ("msixbundle", "publisher_id"): "publisher_id",
    ("msixbundle", "package_family_name"): "package_family_name",
    ("msixbundle", "bundle_package_architectures"): "bundle_package_architectures",
    ("msixbundle", "package_architectures"): "bundle_package_architectures",
    ("msixbundle", "bundle_package_file_names"): "bundle_package_file_names",
    ("msixbundle", "package_file_names"): "bundle_package_file_names",
    ("msixbundle", "bundle_package_count"): "bundle_package_count",
    ("msixbundle", "package_count"): "bundle_package_count",
    ("msixbundle", "target_device_families"): "target_device_families",
    ("msixbundle", "executable"): "executable",
    ("msixbundle", "capabilities"): "capabilities",
    ("msixbundle", "signature_present"): "signature_present",
    ("msixbundle", "is_signed"): "signature_present",
    ("msixbundle", "has_signature"): "signature_present",
    ("msixbundle", "block_map_hash_method"): "block_map_hash_method",
    ("msixbundle", "blockmap_hash_method"): "block_map_hash_method",
    ("msixbundle", "manifest_name"): "manifest_name",
    ("msixbundle", "is_bundle"): "is_bundle",
    ("appxbundle", "identity_name"): "identity_name",
    ("appxbundle", "package_name"): "identity_name",
    ("appxbundle", "name"): "identity_name",
    ("appxbundle", "identity_publisher"): "identity_publisher",
    ("appxbundle", "publisher"): "identity_publisher",
    ("appxbundle", "identity_version"): "identity_version",
    ("appxbundle", "package_version"): "identity_version",
    ("appxbundle", "version"): "identity_version",
    ("appxbundle", "identity_processor_architecture"): "identity_arch",
    ("appxbundle", "processor_architecture"): "identity_arch",
    ("appxbundle", "architecture"): "identity_arch",
    ("appxbundle", "publisher_id"): "publisher_id",
    ("appxbundle", "package_family_name"): "package_family_name",
    ("appxbundle", "bundle_package_architectures"): "bundle_package_architectures",
    ("appxbundle", "package_architectures"): "bundle_package_architectures",
    ("appxbundle", "bundle_package_file_names"): "bundle_package_file_names",
    ("appxbundle", "package_file_names"): "bundle_package_file_names",
    ("appxbundle", "bundle_package_count"): "bundle_package_count",
    ("appxbundle", "package_count"): "bundle_package_count",
    ("appxbundle", "target_device_families"): "target_device_families",
    ("appxbundle", "executable"): "executable",
    ("appxbundle", "capabilities"): "capabilities",
    ("appxbundle", "signature_present"): "signature_present",
    ("appxbundle", "is_signed"): "signature_present",
    ("appxbundle", "has_signature"): "signature_present",
    ("appxbundle", "block_map_hash_method"): "block_map_hash_method",
    ("appxbundle", "blockmap_hash_method"): "block_map_hash_method",
    ("appxbundle", "manifest_name"): "manifest_name",
    ("appxbundle", "is_bundle"): "is_bundle",
}

_PKG_MANIFEST = "appxmanifest.xml"
_BUNDLE_MANIFEST = "appxmetadata/appxbundlemanifest.xml"
_CROCKFORD = "0123456789abcdefghjkmnpqrstvwxyz"


def _ln(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _parse_xml(blob):
    try:
        return ET.fromstring(blob)
    except Exception:  # noqa: BLE001
        return None


def package(b):
    """{zip names, manifest root, kind ('package'|'bundle'), member name} of an MSIX/AppX package/bundle, or None."""
    if not b or bytes(b[:2]) != b"PK":
        return None
    try:
        zf = zipfile.ZipFile(io.BytesIO(bytes(b)))
        names = zf.namelist()
    except Exception:  # noqa: BLE001
        return None
    low = {n.replace("\\", "/").lower(): n for n in names}
    for key, kind in ((_BUNDLE_MANIFEST, "bundle"), (_PKG_MANIFEST, "package")):
        n = low.get(key)
        if n is None:
            continue
        try:
            root = _parse_xml(zf.read(n))
        except Exception:  # noqa: BLE001
            root = None
        if root is None or _ln(root.tag) not in ("Package", "Bundle"):
            continue
        return {"zf": zf, "names": names, "low": low, "root": root, "kind": kind, "manifest": n}
    return None


def _child(el, name):
    for c in el:
        if _ln(c.tag) == name:
            return c
    return None


def _children(el, name):
    return [c for c in el if _ln(c.tag) == name] if el is not None else []


def _attr(el, name):
    if el is None:
        return None
    for k, v in el.attrib.items():
        if _ln(k) == name:
            return v
    return None


def _run(fn, data):
    if data is None:
        return None
    try:
        p = package(data)
        if p is None:
            return "none"
        v = fn(p)
    except Exception:  # noqa: BLE001
        return None
    if v is None or v == "" or v == []:
        return "none"
    return v


def _identity_attr(p, name):
    v = _attr(_child(p["root"], "Identity"), name)
    return v.strip() if isinstance(v, str) else v


def _publisher_id(publisher):
    h = hashlib.sha256(publisher.encode("utf-16-le")).digest()[:8]
    n = int.from_bytes(h, "big") << 1                     # 64 bits + one zero pad bit = 65 bits = 13 x 5
    return "".join(_CROCKFORD[(n >> (5 * (12 - i))) & 31] for i in range(13))


def _apps(p):
    return _children(_child(p["root"], "Applications"), "Application")


def _identity_name(p):
    return _identity_attr(p, "Name")


def _identity_publisher(p):
    return _identity_attr(p, "Publisher")


def _identity_version(p):
    return _identity_attr(p, "Version")


def _identity_arch(p):
    return _identity_attr(p, "ProcessorArchitecture")


def _identity_resource_id(p):
    return _identity_attr(p, "ResourceId")


def _publisher_id_f(p):
    pub = _identity_attr(p, "Publisher")
    return _publisher_id(pub) if pub else None


def _family(p):
    name, pub = _identity_attr(p, "Name"), _identity_attr(p, "Publisher")
    return f"{name}_{_publisher_id(pub)}" if name and pub else None


def _full(p):
    # Name_Version_Architecture_ResourceId_PublisherId; a package without ProcessorArchitecture is "neutral"
    name, pub, ver = _identity_attr(p, "Name"), _identity_attr(p, "Publisher"), _identity_attr(p, "Version")
    if not (name and pub and ver) or p["kind"] != "package":
        return None
    arch = _identity_attr(p, "ProcessorArchitecture") or "neutral"
    return f"{name}_{ver}_{arch}_{_identity_attr(p, 'ResourceId') or ''}_{_publisher_id(pub)}"


def _prop(p, name):
    el = _child(_child(p["root"], "Properties"), name) if _child(p["root"], "Properties") is not None else None
    return (el.text or "").strip() if el is not None else None


def _display_name(p):
    return _prop(p, "DisplayName")


def _publisher_display_name(p):
    return _prop(p, "PublisherDisplayName")


def _tdf(p):
    out = []
    for el in _children(_child(p["root"], "Dependencies"), "TargetDeviceFamily"):
        out.append(" ".join(x for x in (_attr(el, "Name"), _attr(el, "MinVersion")) if x))
    return out


def _bundle_pkgs(p):
    return _children(_child(p["root"], "Packages"), "Package") if p["kind"] == "bundle" else []


def _bundle_arches(p):
    return [a for a in (_attr(e, "Architecture") for e in _bundle_pkgs(p)) if a is not None]


def _bundle_files(p):
    return [a for a in (_attr(e, "FileName") for e in _bundle_pkgs(p)) if a is not None]


def _bundle_count(p):
    return len(_bundle_pkgs(p)) if p["kind"] == "bundle" else None


def _executable(p):
    for a in _apps(p):
        v = _attr(a, "Executable")
        if v:
            return v
    return None


def _executables(p):
    return [v for v in (_attr(a, "Executable") for a in _apps(p)) if v]


def _app_ids(p):
    return [v for v in (_attr(a, "Id") for a in _apps(p)) if v]


def _app_id(p):
    return next((v for v in (_attr(a, "Id") for a in _apps(p)) if v), None)


def _entry_point(p):
    return next((v for v in (_attr(a, "EntryPoint") for a in _apps(p)) if v), None)


def _capabilities(p):
    caps = _child(p["root"], "Capabilities")
    return [v for v in (_attr(c, "Name") for c in (caps if caps is not None else [])) if v]


def _signature(p):
    return "appxsignature.p7x" in p["low"]


def _hash_method(p):
    n = p["low"].get("appxblockmap.xml")
    if n is None:
        return None
    root = _parse_xml(p["zf"].read(n))
    return _attr(root, "HashMethod") if root is not None and _ln(root.tag) == "BlockMap" else None


def _manifest_name(p):
    return p["manifest"]


def _is_bundle(p):
    return p["kind"] == "bundle"


def identity_name(data, ctx):
    return _run(_identity_name, data)


def identity_publisher(data, ctx):
    return _run(_identity_publisher, data)


def identity_version(data, ctx):
    return _run(_identity_version, data)


def identity_arch(data, ctx):
    return _run(_identity_arch, data)


def identity_resource_id(data, ctx):
    return _run(_identity_resource_id, data)


def publisher_id(data, ctx):
    return _run(_publisher_id_f, data)


def package_family_name(data, ctx):
    return _run(_family, data)


def package_full_name(data, ctx):
    return _run(_full, data)


def display_name(data, ctx):
    return _run(_display_name, data)


def publisher_display_name(data, ctx):
    return _run(_publisher_display_name, data)


def target_device_families(data, ctx):
    return _run(_tdf, data)


def bundle_package_architectures(data, ctx):
    return _run(_bundle_arches, data)


def bundle_package_file_names(data, ctx):
    return _run(_bundle_files, data)


def bundle_package_count(data, ctx):
    return _run(_bundle_count, data)


def executable(data, ctx):
    return _run(_executable, data)


def application_executables(data, ctx):
    return _run(_executables, data)


def application_ids(data, ctx):
    return _run(_app_ids, data)


def application_id(data, ctx):
    return _run(_app_id, data)


def entry_point(data, ctx):
    return _run(_entry_point, data)


def capabilities(data, ctx):
    return _run(_capabilities, data)


def signature_present(data, ctx):
    return _run(_signature, data)


def block_map_hash_method(data, ctx):
    return _run(_hash_method, data)


def manifest_name(data, ctx):
    return _run(_manifest_name, data)


def is_bundle(data, ctx):
    return _run(_is_bundle, data)
