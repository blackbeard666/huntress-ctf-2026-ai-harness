"""macOS flat installer packages = xar archives (prebuilt, SPECULATIVE -- never GM-asked yet).

xar header (big-endian): magic "xar!" @0, header_size u16 @4 (28, or larger when cksum_alg 3 appends a NUL-padded
algorithm name @28), version u16 @6, toc_length_compressed u64 @8, toc_length_uncompressed u64 @16, cksum_alg u32 @24
(0 none, 1 sha1, 2 md5, 3 = the name stored after the 28-byte header). The TOC = a zlib stream of XML right after the
header; the heap starts at header_size + toc_length_compressed and every <file><data><offset> is heap-relative,
<encoding style> application/x-gzip (really a zlib stream) / x-bzip2 / x-lzma / x-xz / octet-stream.
- file_names: every TOC <file> (directories included, like `xar -t` / `7z l`) as its '/'-joined path, TOC document
  order; file_count = that list's length.
- Product archive `Distribution` (root file): <options hostArchitectures="x86_64,arm64"/> -> list in stored order;
  first <os-version min=> (inside <allowed-os-versions>, root or under <volume-check>).
- package_identifiers / package_versions: every `PackageInfo` (<pkg-info identifier= version=>) in TOC order (a
  component package has one at the root, a product archive one per `*.pkg/` directory).
- signature_present: TOC <signature> or <x-signature>; signer_cert_cn = CN of the FIRST X509Certificate of the
  <signature> KeyInfo (the leaf; rcodesign / productsign order), else of <x-signature>.
Not xar / truncated / bad TOC -> "none"; a field absent from a valid package -> "none"."""
import base64
import bz2
import lzma
import re
import struct
import zlib
from xml.etree import ElementTree

FIELDS = {
    ("pkg", "xar_version"): "header_value",
    ("pkg", "version"): "header_value",
    ("pkg", "header_version"): "header_value",
    ("pkg", "header_size"): "header_value",
    ("pkg", "toc_length_compressed"): "header_value",
    ("pkg", "toc_length_uncompressed"): "header_value",
    ("pkg", "toc_checksum_alg"): "header_value",
    ("pkg", "checksum_alg"): "header_value",
    ("pkg", "cksum_alg"): "header_value",
    ("pkg", "toc_checksum_algorithm"): "header_value",
    ("pkg", "checksum_algorithm"): "header_value",
    ("pkg", "file_names"): "toc_value",
    ("pkg", "toc_file_names"): "toc_value",
    ("pkg", "member_names"): "toc_value",
    ("pkg", "file_count"): "toc_value",
    ("pkg", "toc_file_count"): "toc_value",
    ("pkg", "member_count"): "toc_value",
    ("pkg", "signature_present"): "toc_value",
    ("pkg", "has_signature"): "toc_value",
    ("pkg", "is_signed"): "toc_value",
    ("pkg", "signer_cert_cn"): "toc_value",
    ("pkg", "signer_cn"): "toc_value",
    ("pkg", "signer_common_name"): "toc_value",
    ("pkg", "signing_cert_cn"): "toc_value",
    ("pkg", "signature_cert_cn"): "toc_value",
    ("pkg", "distribution_host_architectures"): "distribution_value",
    ("pkg", "host_architectures"): "distribution_value",
    ("pkg", "distribution_min_os"): "distribution_value",
    ("pkg", "distribution_min_os_version"): "distribution_value",
    ("pkg", "min_os_version"): "distribution_value",
    ("pkg", "minimum_os_version"): "distribution_value",
    ("pkg", "distribution_title"): "distribution_value",
    ("pkg", "package_identifiers"): "pkginfo_value",
    ("pkg", "package_versions"): "pkginfo_value",
    ("pkg", "package_identifier"): "pkginfo_value",
    ("pkg", "package_version"): "pkginfo_value",
    ("pkg", "pkg_info_identifiers"): "pkginfo_value",
    ("pkg", "pkg_info_versions"): "pkginfo_value",
    ("pkg", "install_locations"): "pkginfo_value",
    ("xar", "xar_version"): "header_value",
    ("xar", "version"): "header_value",
    ("xar", "header_version"): "header_value",
    ("xar", "header_size"): "header_value",
    ("xar", "toc_length_compressed"): "header_value",
    ("xar", "toc_length_uncompressed"): "header_value",
    ("xar", "toc_checksum_alg"): "header_value",
    ("xar", "checksum_alg"): "header_value",
    ("xar", "cksum_alg"): "header_value",
    ("xar", "toc_checksum_algorithm"): "header_value",
    ("xar", "checksum_algorithm"): "header_value",
    ("xar", "file_names"): "toc_value",
    ("xar", "toc_file_names"): "toc_value",
    ("xar", "member_names"): "toc_value",
    ("xar", "file_count"): "toc_value",
    ("xar", "toc_file_count"): "toc_value",
    ("xar", "member_count"): "toc_value",
    ("xar", "signature_present"): "toc_value",
    ("xar", "has_signature"): "toc_value",
    ("xar", "is_signed"): "toc_value",
    ("xar", "signer_cert_cn"): "toc_value",
    ("xar", "signer_cn"): "toc_value",
    ("xar", "signer_common_name"): "toc_value",
    ("xar", "signing_cert_cn"): "toc_value",
    ("xar", "signature_cert_cn"): "toc_value",
    ("xar", "distribution_host_architectures"): "distribution_value",
    ("xar", "host_architectures"): "distribution_value",
    ("xar", "distribution_min_os"): "distribution_value",
    ("xar", "distribution_min_os_version"): "distribution_value",
    ("xar", "min_os_version"): "distribution_value",
    ("xar", "minimum_os_version"): "distribution_value",
    ("xar", "distribution_title"): "distribution_value",
    ("xar", "package_identifiers"): "pkginfo_value",
    ("xar", "package_versions"): "pkginfo_value",
    ("xar", "package_identifier"): "pkginfo_value",
    ("xar", "package_version"): "pkginfo_value",
    ("xar", "pkg_info_identifiers"): "pkginfo_value",
    ("xar", "pkg_info_versions"): "pkginfo_value",
    ("xar", "install_locations"): "pkginfo_value",
    ("macos_pkg", "xar_version"): "header_value",
    ("macos_pkg", "version"): "header_value",
    ("macos_pkg", "header_version"): "header_value",
    ("macos_pkg", "header_size"): "header_value",
    ("macos_pkg", "toc_length_compressed"): "header_value",
    ("macos_pkg", "toc_length_uncompressed"): "header_value",
    ("macos_pkg", "toc_checksum_alg"): "header_value",
    ("macos_pkg", "checksum_alg"): "header_value",
    ("macos_pkg", "cksum_alg"): "header_value",
    ("macos_pkg", "toc_checksum_algorithm"): "header_value",
    ("macos_pkg", "checksum_algorithm"): "header_value",
    ("macos_pkg", "file_names"): "toc_value",
    ("macos_pkg", "toc_file_names"): "toc_value",
    ("macos_pkg", "member_names"): "toc_value",
    ("macos_pkg", "file_count"): "toc_value",
    ("macos_pkg", "toc_file_count"): "toc_value",
    ("macos_pkg", "member_count"): "toc_value",
    ("macos_pkg", "signature_present"): "toc_value",
    ("macos_pkg", "has_signature"): "toc_value",
    ("macos_pkg", "is_signed"): "toc_value",
    ("macos_pkg", "signer_cert_cn"): "toc_value",
    ("macos_pkg", "signer_cn"): "toc_value",
    ("macos_pkg", "signer_common_name"): "toc_value",
    ("macos_pkg", "signing_cert_cn"): "toc_value",
    ("macos_pkg", "signature_cert_cn"): "toc_value",
    ("macos_pkg", "distribution_host_architectures"): "distribution_value",
    ("macos_pkg", "host_architectures"): "distribution_value",
    ("macos_pkg", "distribution_min_os"): "distribution_value",
    ("macos_pkg", "distribution_min_os_version"): "distribution_value",
    ("macos_pkg", "min_os_version"): "distribution_value",
    ("macos_pkg", "minimum_os_version"): "distribution_value",
    ("macos_pkg", "distribution_title"): "distribution_value",
    ("macos_pkg", "package_identifiers"): "pkginfo_value",
    ("macos_pkg", "package_versions"): "pkginfo_value",
    ("macos_pkg", "package_identifier"): "pkginfo_value",
    ("macos_pkg", "package_version"): "pkginfo_value",
    ("macos_pkg", "pkg_info_identifiers"): "pkginfo_value",
    ("macos_pkg", "pkg_info_versions"): "pkginfo_value",
    ("macos_pkg", "install_locations"): "pkginfo_value",
}

_CKSUM = {0: "none", 1: "sha1", 2: "md5"}
_MAX_OUT = 32 << 20


def xar_header(b):
    """The xar header as a dict, or None (not xar / truncated)."""
    if not b or len(b) < 28 or bytes(b[:4]) != b"xar!":
        return None
    hsz, ver, tlc, tlu, alg = struct.unpack_from(">HHQQI", b, 4)
    if hsz < 28 or hsz > len(b):
        return None
    name = _CKSUM.get(alg)
    if name is None:
        raw = bytes(b[28:hsz]).split(b"\x00", 1)[0] if alg == 3 and hsz > 28 else b""
        name = raw.decode("ascii", "replace").strip() or str(alg)
    return {"header_size": hsz, "version": ver, "toc_c": tlc, "toc_u": tlu, "alg": alg, "alg_name": name}


def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _xml(raw):
    """ElementTree root of untrusted XML bytes (entity declarations refused), or None."""
    if not raw or re.search(rb"<!ENTITY", raw[:4096], re.I):
        return None
    try:
        return ElementTree.fromstring(raw)
    except ElementTree.ParseError:
        return None


def _toc(b):
    """(header, toc root element), or None."""
    h = xar_header(b)
    if h is None:
        return None
    blob = bytes(b[h["header_size"]:h["header_size"] + h["toc_c"]])
    try:
        d = zlib.decompressobj()
        xml = d.decompress(blob, _MAX_OUT)
    except zlib.error:
        return None
    root = _xml(xml)
    if root is None or _local(root.tag) != "xar":
        return None
    toc = next((c for c in root if _local(c.tag) == "toc"), None)
    return None if toc is None else (h, toc)


def _child(el, name):
    return next((c for c in el if _local(c.tag) == name), None)


def toc_files(toc):
    """[(path, <file> element)] in TOC document order, directories included."""
    out = []

    def walk(el, prefix):
        for c in el:
            if _local(c.tag) != "file":
                continue
            n = _child(c, "name")
            name = (n.text or "").strip() if n is not None else ""
            path = prefix + name
            out.append((path, c))
            walk(c, path + "/")
    walk(toc, "")
    return out


def _heap_file(b, h, fel):
    """Decoded content of a TOC <file> (its <data> in the heap), or None."""
    d = _child(fel, "data")
    if d is None:
        return None
    try:
        off = int((_child(d, "offset").text or "").strip())
        ln = int((_child(d, "length").text or "").strip())
    except (AttributeError, ValueError):
        return None
    start = h["header_size"] + h["toc_c"] + off
    if off < 0 or ln < 0 or start + ln > len(b):
        return None
    raw = bytes(b[start:start + ln])
    enc = _child(d, "encoding")
    style = (enc.get("style") or "") if enc is not None else ""
    try:
        if "gzip" in style:
            if raw[:2] == b"\x1f\x8b":
                return zlib.decompressobj(31).decompress(raw, _MAX_OUT)
            return zlib.decompressobj().decompress(raw, _MAX_OUT)
        if "bzip2" in style:
            return bz2.BZ2Decompressor().decompress(raw, _MAX_OUT)
        if "lzma" in style or "xz" in style:
            return lzma.LZMADecompressor().decompress(raw, _MAX_OUT)
    except (zlib.error, OSError, EOFError, lzma.LZMAError, ValueError):
        return None
    return raw


def _field(ctx):
    return (ctx or {}).get("field") or ""


def header_value(data, ctx):
    if data is None:
        return None
    try:
        h = xar_header(data)
    except Exception:
        return None
    if h is None:
        return "none"
    f = _field(ctx)
    if "checksum" in f or "cksum" in f:
        return h["alg_name"]
    if f == "header_size":
        return h["header_size"]
    if f == "toc_length_compressed":
        return h["toc_c"]
    if f == "toc_length_uncompressed":
        return h["toc_u"]
    if "version" in f:
        return h["version"]
    return None


def _cert_cn(der):
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        cert = x509.load_der_x509_certificate(der)
        cns = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return str(cns[0].value) if cns else "none"
    except Exception:
        return None


def toc_value(data, ctx):
    if data is None:
        return None
    try:
        t = _toc(data)
        if t is None:
            return "none"
        h, toc = t
        f = _field(ctx)
        if "name" in f and "cn" not in f:
            return [p for p, _ in toc_files(toc)]
        if "count" in f:
            return len(toc_files(toc))
        sigs = [c for c in toc if _local(c.tag) in ("signature", "x-signature")]
        if f in ("signature_present", "has_signature", "is_signed"):
            return bool(sigs)
        sigs.sort(key=lambda c: _local(c.tag) != "signature")
        for s in sigs:
            certs = [e for e in s.iter() if _local(e.tag) == "X509Certificate" and (e.text or "").strip()]
            if certs:
                der = base64.b64decode(re.sub(r"\s+", "", certs[0].text))
                return _cert_cn(der)
        return "none"
    except Exception:
        return None


def _distribution(data):
    """(found_xar, Distribution root element or None)."""
    t = _toc(data)
    if t is None:
        return False, None
    h, toc = t
    for path, fel in toc_files(toc):
        if path == "Distribution":
            raw = _heap_file(data, h, fel)
            return True, _xml(raw) if raw else None
    return True, None


def distribution_value(data, ctx):
    if data is None:
        return None
    try:
        ok, dist = _distribution(data)
        if not ok or dist is None:
            return "none"
        f = _field(ctx)
        if "arch" in f:
            for e in dist.iter():
                if _local(e.tag) == "options" and e.get("hostArchitectures") is not None:
                    return [a.strip() for a in e.get("hostArchitectures").split(",") if a.strip()]
            return "none"
        if "os" in f:
            for e in dist.iter():
                if _local(e.tag) == "os-version" and e.get("min"):
                    return e.get("min").strip()
            return "none"
        if "title" in f:
            e = next((e for e in dist.iter() if _local(e.tag) == "title"), None)
            return (e.text or "").strip() if e is not None and (e.text or "").strip() else "none"
    except Exception:
        return None
    return None


def pkginfos(data):
    """[<pkg-info> element] of every PackageInfo in TOC order, or None (not xar)."""
    t = _toc(data)
    if t is None:
        return None
    h, toc = t
    out = []
    for path, fel in toc_files(toc):
        if path.rsplit("/", 1)[-1] == "PackageInfo":
            root = _xml(_heap_file(data, h, fel))
            if root is not None and _local(root.tag) == "pkg-info":
                out.append(root)
    return out


def pkginfo_value(data, ctx):
    if data is None:
        return None
    try:
        infos = pkginfos(data)
    except Exception:
        return None
    if not infos:
        return "none"
    f = _field(ctx)
    attr = "identifier" if "identifier" in f else "version" if "version" in f else \
        "install-location" if "location" in f else None
    if attr is None:
        return None
    vals = [(i.get(attr) or "").strip() for i in infos]
    if f.endswith("s"):
        return vals
    return vals[0] or "none"
