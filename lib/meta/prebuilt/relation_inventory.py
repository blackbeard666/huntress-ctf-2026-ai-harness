"""Finale-style corpus inventory of a cluster zip (`cluster-NNN.zip`, the D30 relation container): every member's
family decided by its MAGIC bytes (never its extension), the extension liars, and the aggregates. Speculative tier.

Members / labels exactly as relation_variants.py (the D30 GM-verified identical_sha256_groups convention): every
non-directory entry at any depth minus the delivery manifest (`*manifest*.json`, or an `index.json` that parses as an
artifact list); label = manifest `id` by member path then basename, else basename without extension. Non-zip -> "none".

Family words = the metadata lane's GM fmt tokens, decided in this order (first hit wins):
  pe (MZ + PE\\0\\0 at e_lfanew) | elf | macho (thin/fat; fat 0xcafebabe only when nfat_arch < 0x20, else `class`) |
  zip subtypes from the central directory: apk (AndroidManifest.xml) > ooxml ([Content_Types].xml) > jar
  (META-INF/MANIFEST.MF or *.class) > zip | CFB: msi (root CLSID 000C1084/1086/1082-...-C000-000000000046) else ole |
  lnk (4C000000 + LinkCLSID) | pdf (%PDF- in the first 1 KiB) | png | jpeg | gif | sqlite | evtx (ElfFile) |
  registry (regf) | prefetch (SCCA @4 or MAM\\x04) | pcap (pcap both endians, ns variants, pcapng) |
  disk (EFI PART @512/@4096, conectix/vhdxfile/QFI\\xfb/KDMV, CD001 @0x8001, MBR 55AA with a partition entry) |
  media (RIFF WAVE/AVI, ftyp (heic/avif -> image), OggS, fLaC, ID3, EBML, ASF, FORM AIFF, caff, .snd, MPEG frame) |
  image (BMP/WEBP/TIFF/ICO/heic) | x509 (PEM CERTIFICATE block or a DER that cryptography loads) |
  then text: email (an RFC 822 header block with >= 2 of From/To/Subject/Date/Received/Message-ID/Return-Path),
  json (whole text parses to an object/array), text (any other UTF-8/UTF-16 text without NUL; .ps1 is text) |
  unknown.

Fields (each under fmt relation / corpus / inventory):
  family_by_magic        {label: family} JSON object, keys sorted;  family_by_magic_pairs = sorted [[label, family]]
  family_counts          {family: count}, keys sorted
  magic_family_set       sorted distinct families;  distinct_family_count = its length
  members_by_family_<f>  sorted labels whose family is <f> (`[]` when none);  count_by_family_<f> = its length
  extension_mismatch_ids sorted labels whose extension CLAIMS a family (map below) different from the magic family;
                         no / unknown extension claims nothing. json content satisfies a text extension.
  largest_member_id      label of the largest member (ties -> smallest label);  smallest_member_id likewise
  total_bytes            sum of member sizes (raw uncompressed bytes), base-10
One parse per container sha256 (never id())."""
import hashlib
import io
import json
import re
import struct
import zlib

FIELDS = {
    ("relation", "family_by_magic"): "inventory_value",
    ("relation", "family_by_magic_pairs"): "inventory_value",
    ("relation", "family_by_magic_list"): "inventory_value",
    ("relation", "magic_family_by_id"): "inventory_value",
    ("relation", "member_families"): "inventory_value",
    ("relation", "member_family_map"): "inventory_value",
    ("relation", "family_counts"): "inventory_value",
    ("relation", "magic_family_counts"): "inventory_value",
    ("relation", "family_count_map"): "inventory_value",
    ("relation", "magic_family_set"): "inventory_value",
    ("relation", "family_set"): "inventory_value",
    ("relation", "magic_families"): "inventory_value",
    ("relation", "distinct_family_count"): "inventory_value",
    ("relation", "magic_family_count"): "inventory_value",
    ("relation", "members_by_family_*"): "inventory_value",
    ("relation", "ids_by_family_*"): "inventory_value",
    ("relation", "count_by_family_*"): "inventory_value",
    ("relation", "member_count_by_family_*"): "inventory_value",
    ("relation", "extension_mismatch_ids"): "inventory_value",
    ("relation", "extension_mismatch_count"): "inventory_value",
    ("relation", "extension_liar_ids"): "inventory_value",
    ("relation", "extension_liars"): "inventory_value",
    ("relation", "extension_magic_mismatch_ids"): "inventory_value",
    ("relation", "magic_extension_mismatch_ids"): "inventory_value",
    ("relation", "ext_mismatch_ids"): "inventory_value",
    ("relation", "largest_member_id"): "inventory_value",
    ("relation", "largest_member_size_bytes"): "inventory_value",
    ("relation", "smallest_member_id"): "inventory_value",
    ("relation", "total_bytes"): "inventory_value",
    ("relation", "total_size_bytes"): "inventory_value",
    ("relation", "member_total_bytes"): "inventory_value",
    ("relation", "total_member_bytes"): "inventory_value",
    ("corpus", "family_by_magic"): "inventory_value",
    ("corpus", "family_by_magic_pairs"): "inventory_value",
    ("corpus", "family_by_magic_list"): "inventory_value",
    ("corpus", "magic_family_by_id"): "inventory_value",
    ("corpus", "member_families"): "inventory_value",
    ("corpus", "member_family_map"): "inventory_value",
    ("corpus", "family_counts"): "inventory_value",
    ("corpus", "magic_family_counts"): "inventory_value",
    ("corpus", "family_count_map"): "inventory_value",
    ("corpus", "magic_family_set"): "inventory_value",
    ("corpus", "family_set"): "inventory_value",
    ("corpus", "magic_families"): "inventory_value",
    ("corpus", "distinct_family_count"): "inventory_value",
    ("corpus", "magic_family_count"): "inventory_value",
    ("corpus", "members_by_family_*"): "inventory_value",
    ("corpus", "ids_by_family_*"): "inventory_value",
    ("corpus", "count_by_family_*"): "inventory_value",
    ("corpus", "member_count_by_family_*"): "inventory_value",
    ("corpus", "extension_mismatch_ids"): "inventory_value",
    ("corpus", "extension_mismatch_count"): "inventory_value",
    ("corpus", "extension_liar_ids"): "inventory_value",
    ("corpus", "extension_liars"): "inventory_value",
    ("corpus", "extension_magic_mismatch_ids"): "inventory_value",
    ("corpus", "magic_extension_mismatch_ids"): "inventory_value",
    ("corpus", "ext_mismatch_ids"): "inventory_value",
    ("corpus", "largest_member_id"): "inventory_value",
    ("corpus", "largest_member_size_bytes"): "inventory_value",
    ("corpus", "smallest_member_id"): "inventory_value",
    ("corpus", "total_bytes"): "inventory_value",
    ("corpus", "total_size_bytes"): "inventory_value",
    ("corpus", "member_total_bytes"): "inventory_value",
    ("corpus", "total_member_bytes"): "inventory_value",
    ("inventory", "family_by_magic"): "inventory_value",
    ("inventory", "family_by_magic_pairs"): "inventory_value",
    ("inventory", "family_by_magic_list"): "inventory_value",
    ("inventory", "magic_family_by_id"): "inventory_value",
    ("inventory", "member_families"): "inventory_value",
    ("inventory", "member_family_map"): "inventory_value",
    ("inventory", "family_counts"): "inventory_value",
    ("inventory", "magic_family_counts"): "inventory_value",
    ("inventory", "family_count_map"): "inventory_value",
    ("inventory", "magic_family_set"): "inventory_value",
    ("inventory", "family_set"): "inventory_value",
    ("inventory", "magic_families"): "inventory_value",
    ("inventory", "distinct_family_count"): "inventory_value",
    ("inventory", "magic_family_count"): "inventory_value",
    ("inventory", "members_by_family_*"): "inventory_value",
    ("inventory", "ids_by_family_*"): "inventory_value",
    ("inventory", "count_by_family_*"): "inventory_value",
    ("inventory", "member_count_by_family_*"): "inventory_value",
    ("inventory", "extension_mismatch_ids"): "inventory_value",
    ("inventory", "extension_mismatch_count"): "inventory_value",
    ("inventory", "extension_liar_ids"): "inventory_value",
    ("inventory", "extension_liars"): "inventory_value",
    ("inventory", "extension_magic_mismatch_ids"): "inventory_value",
    ("inventory", "magic_extension_mismatch_ids"): "inventory_value",
    ("inventory", "ext_mismatch_ids"): "inventory_value",
    ("inventory", "largest_member_id"): "inventory_value",
    ("inventory", "largest_member_size_bytes"): "inventory_value",
    ("inventory", "smallest_member_id"): "inventory_value",
    ("inventory", "total_bytes"): "inventory_value",
    ("inventory", "total_size_bytes"): "inventory_value",
    ("inventory", "member_total_bytes"): "inventory_value",
    ("inventory", "total_member_bytes"): "inventory_value",
}

# extension -> the families it claims (first = the canonical claim)
_EXT = {}
for _fam, _exts in {
        "pe": "exe dll sys scr cpl ocx efi drv mui", "elf": "elf so o ko axf", "macho": "dylib macho bundle",
        "apk": "apk", "jar": "jar war ear", "ooxml": "docx xlsx pptx docm xlsm pptm dotx xltx potx",
        "zip": "zip", "msi": "msi msp mst", "ole": "doc xls ppt msg dot xlt pot", "lnk": "lnk", "pdf": "pdf",
        "png": "png", "jpeg": "jpg jpeg jpe jfif", "gif": "gif", "sqlite": "db sqlite sqlite3 db3 sqlitedb",
        "evtx": "evtx", "registry": "hiv hve", "prefetch": "pf", "pcap": "pcap pcapng cap",
        "disk": "img dd raw vhd vhdx vmdk qcow2 iso e01", "email": "eml", "x509": "crt cer pem der",
        "media": "wav mp3 mp4 m4a mov avi ogg oga opus flac mkv webm wma wmv aif aiff caf au 3gp",
        "image": "bmp webp tif tiff ico heic avif", "class": "class", "json": "json",
        "text": "txt log csv md ps1 psm1 psd1 bat cmd vbs js py sh xml html htm ini cfg conf yml yaml tsv"}.items():
    for _e in _exts.split():
        _EXT[_e] = (_fam, "json") if _fam == "text" else (_fam,)

_MSI_CLSIDS = {"000c1084-0000-0000-c000-000000000046", "000c1086-0000-0000-c000-000000000046",
               "000c1082-0000-0000-c000-000000000046"}
_LNK_CLSID = bytes.fromhex("0114020000000000c000000000000046")
_HDR = re.compile(r"^(from|to|subject|date|received|message-id|return-path|mime-version|cc|reply-to)\s*:", re.I)
_EMAIL_KEYS = {"from", "to", "subject", "date", "received", "message-id", "return-path"}


def _zip_family(b):
    import zipfile
    try:
        names = zipfile.ZipFile(io.BytesIO(b)).namelist()
    except Exception:  # noqa: BLE001 - damaged directory: still a zip by magic
        return "zip"
    low = {n.replace("\\", "/").lower() for n in names}
    if "androidmanifest.xml" in low:
        return "apk"
    if "[content_types].xml" in low:
        return "ooxml"
    if "meta-inf/manifest.mf" in low or any(n.endswith(".class") for n in low):
        return "jar"
    return "zip"


def _cfb_family(b):
    try:
        import olefile
        ole = olefile.OleFileIO(io.BytesIO(b))
        clsid = (ole.root.clsid or "").lower()
        ole.close()
    except Exception:  # noqa: BLE001 - CFB magic but unparsable
        clsid = ""
    return "msi" if clsid in _MSI_CLSIDS else "ole"


def _is_cert_der(b):
    if b[:1] != b"\x30" or len(b) < 64:
        return False
    try:
        from cryptography import x509
        x509.load_der_x509_certificate(b)
        return True
    except Exception:  # noqa: BLE001
        return False


def _text(b):
    """The member as text, or None when it is binary."""
    if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
        try:
            s = b.decode("utf-16")
        except UnicodeDecodeError:
            return None
    else:
        try:
            s = b.decode("utf-8-sig")
        except UnicodeDecodeError:
            return None
    if "\x00" in s or any(ord(c) < 9 or 13 < ord(c) < 32 and c != "\x1b" for c in s[:4096]):
        return None
    return s


def _text_family(s):
    if "-----BEGIN CERTIFICATE-----" in s:
        return "x509"
    st = s.strip()
    if st[:1] in "{[":
        try:
            if isinstance(json.loads(st), (dict, list)):
                return "json"
        except ValueError:
            pass
    keys = set()
    for ln in s.splitlines()[:60]:
        if not ln.strip():
            break
        m = _HDR.match(ln)
        if m:
            keys.add(m.group(1).lower())
        elif not ln[:1].isspace() and not re.match(r"^[A-Za-z0-9-]+\s*:", ln):
            keys = set()
            break
    if len(keys & _EMAIL_KEYS) >= 2:
        return "email"
    return "text"


def family(b):
    """The GM family word of one member's bytes, by magic."""
    if not b:
        return "unknown"
    h = bytes(b[:16])
    if h[:2] == b"MZ" and len(b) >= 0x40:
        lf, = struct.unpack_from("<I", b, 0x3C)
        if lf + 4 <= len(b) and b[lf:lf + 4] == b"PE\0\0":
            return "pe"
    if h[:4] == b"\x7fELF":
        return "elf"
    if h[:4] in (b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf",
                 b"\xbe\xba\xfe\xca"):
        return "macho"
    if h[:4] == b"\xca\xfe\xba\xbe" and len(b) >= 8:
        n, = struct.unpack_from(">I", b, 4)
        return "macho" if 0 < n < 0x20 else "class"
    if h[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"):
        return _zip_family(b)
    if h[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return _cfb_family(b)
    if h[:4] == b"L\0\0\0" and h[4:16] == _LNK_CLSID[:12]:
        return "lnk"
    if b"%PDF-" in b[:1024]:
        return "pdf"
    if h[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if h[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if h[:4] == b"GIF8":
        return "gif"
    if h == b"SQLite format 3\0":
        return "sqlite"
    if h[:8] == b"ElfFile\0":
        return "evtx"
    if h[:4] == b"regf":
        return "registry"
    if h[4:8] == b"SCCA" or h[:4] == b"MAM\x04":
        return "prefetch"
    if h[:4] in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d",
                 b"\x0a\x0d\x0d\x0a"):
        return "pcap"
    if (b[512:520] == b"EFI PART" or b[4096:4104] == b"EFI PART" or h[:8] in (b"conectix", b"vhdxfile")
            or h[:4] in (b"QFI\xfb", b"KDMV") or b[0x8001:0x8006] == b"CD001" or b[-512:-504] == b"conectix"):
        return "disk"
    if h[:4] == b"RIFF":
        form = h[8:12]
        return "media" if form in (b"WAVE", b"AVI ") else "image" if form == b"WEBP" else "unknown"
    if h[4:8] == b"ftyp":
        return "image" if h[8:12] in (b"heic", b"heix", b"mif1", b"avif") else "media"
    if (h[:4] in (b"OggS", b"fLaC", b"\x1aE\xdf\xa3", b"caff", b".snd") or h[:3] == b"ID3"
            or h[:16] == bytes.fromhex("3026b2758e66cf11a6d900aa0062ce6c")
            or (h[:4] == b"FORM" and h[8:12] in (b"AIFF", b"AIFC"))):
        return "media"
    if h[:2] == b"BM" and len(b) >= 26 or h[:4] in (b"II*\0", b"MM\0*", b"\0\0\1\0"):
        return "image"
    if _is_cert_der(b):
        return "x509"
    s = _text(b)
    if s is not None:
        return _text_family(s)
    if len(b) >= 512 and b[510:512] == b"\x55\xaa" and any(b[446 + 16 * i + 4] for i in range(4)):
        return "disk"
    if len(b) >= 4 and h[0] == 0xFF and h[1] & 0xE0 == 0xE0 and h[1] & 0x06:
        return "media"
    return "unknown"


# --- members (relation_variants.py convention, self-contained) ---------------------------------------------------
_CACHE = {}   # container sha256 -> [(label, path, raw bytes)] | None
_LIST_KEYS = ("artifacts", "members", "files", "entries", "items")
_PATH_KEYS = ("path", "filename", "file", "name", "member", "member_path")


def _manifest_artifacts(raw):
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except Exception:  # noqa: BLE001 - not json
        return None
    if isinstance(doc, list):
        arts = doc
    elif isinstance(doc, dict):
        arts = next((doc[k] for k in _LIST_KEYS if isinstance(doc.get(k), list)), None)
    else:
        arts = None
    if arts is None or not all(isinstance(a, dict) for a in arts):
        return None
    return arts


def _raw_read(data, zi):
    off = zi.header_offset
    if data[off:off + 4] != b"PK\x03\x04":
        return None
    nlen, xlen = struct.unpack_from("<HH", data, off + 26)
    start = off + 30 + nlen + xlen
    comp = data[start:start + zi.compress_size]
    if zi.compress_type == 0:
        return bytes(comp)
    if zi.compress_type == 8:
        return zlib.decompressobj(-15).decompress(comp)
    return None


def _read(z, zi, data):
    try:
        return z.read(zi)
    except (RuntimeError, NotImplementedError):          # encrypted member: the password-aware read
        try:
            from lib.common import read_member
            return read_member(io.BytesIO(data), zi.filename)
        except Exception:  # noqa: BLE001
            return None
    except Exception:  # noqa: BLE001 - bad CRC on the OUTER zip: raw local-header read
        try:
            return _raw_read(data, zi)
        except Exception:  # noqa: BLE001
            return None


def _members(data):
    if not data or data[:2] != b"PK":
        return None
    key = hashlib.sha256(data).hexdigest()
    if key in _CACHE:
        return _CACHE[key]
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        infos = [zi for zi in z.infolist() if not zi.is_dir() and not zi.filename.endswith(("/", "\\"))]
    except Exception:  # noqa: BLE001 - not a zip
        _CACHE[key] = None
        return None
    ids, manifests = {}, set()
    for zi in infos:
        base = zi.filename.replace("\\", "/").rsplit("/", 1)[-1].lower()
        if not base.endswith(".json") or not ("manifest" in base or base == "index.json"):
            continue
        raw = _read(z, zi, data)
        arts = _manifest_artifacts(raw) if raw is not None else None
        if arts is None:
            if "manifest" in base:
                manifests.add(zi.filename)
            continue
        manifests.add(zi.filename)
        for a in arts:
            if a.get("id") is None:
                continue
            for k in _PATH_KEYS:
                if isinstance(a.get(k), str) and a[k]:
                    ids.setdefault(a[k], str(a["id"]))
    out = []
    for zi in infos:
        if zi.filename in manifests:
            continue
        b = _read(z, zi, data)
        if b is None:
            _CACHE[key] = None
            return None
        path = zi.filename.replace("\\", "/")
        base = path.rsplit("/", 1)[-1]
        label = ids.get(zi.filename) or ids.get(path) or ids.get(base)
        if label is None:
            label = base.rsplit(".", 1)[0] if "." in base.lstrip(".") else base
        out.append((label, base, b))
    if len(_CACHE) > 64:
        _CACHE.clear()
    _CACHE[key] = out
    return out


def _ext(base):
    return base.rsplit(".", 1)[1].lower() if "." in base.lstrip(".") else ""


def _param(field, ctx):
    p = (ctx or {}).get("param")
    if p:
        return str(p).strip("_").lower()
    for pre in ("members_by_family_", "ids_by_family_", "member_count_by_family_", "count_by_family_"):
        if field.startswith(pre):
            return field[len(pre):]
    return ""


def inventory_value(data, ctx):
    ctx = ctx or {}
    field = ctx.get("field") or ""
    members = _members(data)
    if members is None:
        return "none"
    fams = [(label, family(b), _ext(base), len(b)) for label, base, b in members]
    if field in ("family_by_magic", "magic_family_by_id", "member_families", "member_family_map"):
        return {k: v for k, v in sorted((lb, f) for lb, f, _, _ in fams)}
    if field in ("family_by_magic_pairs", "family_by_magic_list"):
        return sorted([lb, f] for lb, f, _, _ in fams)
    if field in ("family_counts", "magic_family_counts", "family_count_map"):
        cnt = {}
        for _, f, _, _ in fams:
            cnt[f] = cnt.get(f, 0) + 1
        return dict(sorted(cnt.items()))
    fset = sorted({f for _, f, _, _ in fams})
    if field in ("magic_family_set", "family_set", "magic_families"):
        return fset
    if field in ("distinct_family_count", "magic_family_count"):
        return len(fset)
    if field.startswith(("members_by_family", "ids_by_family", "count_by_family", "member_count_by_family")):
        want = _param(field, ctx)
        if not want:
            return None
        ids = sorted(lb for lb, f, _, _ in fams if f == want)
        return len(ids) if "count_by_family" in field else ids
    if "mismatch" in field or field.startswith("extension_liar"):
        liars = sorted(lb for lb, f, e, _ in fams if e in _EXT and f not in _EXT[e])
        return len(liars) if field.endswith("_count") else liars
    if field in ("largest_member_id", "largest_member_size_bytes", "smallest_member_id"):
        if not fams:
            return "none"
        if field.startswith("smallest"):
            return min(fams, key=lambda t: (t[3], t[0]))[0]
        top = min(fams, key=lambda t: (-t[3], t[0]))
        return top[3] if field.endswith("_bytes") else top[0]
    if field in ("total_bytes", "total_size_bytes", "member_total_bytes", "total_member_bytes"):
        return sum(t[3] for t in fams)
    return None
