"""OneNote (.one, MS-ONESTORE revision store) embedded-file fields (prebuilt, SPECULATIVE -- never GM-asked yet).

File header (1024 bytes): guidFileType @0 = {7B5C52E4-D88C-4DA7-AEB1-5378D02996D3} (.one section) or
{43FF2FA1-EFD9-4C76-9EE2-10EA5722765F} (.onetoc2 table of contents), guidFileFormat @48 =
{109ADD3F-911B-49F5-A5D0-1791EDC8AED8}. An inserted/attached file lives in a FileDataStoreObject ([MS-ONESTORE]
2.6.13): guidHeader {BDE316E7-2665-4511-A4C4-8D4D0B7A9EAC} (bytes_le), cbLength u64le, unused u32, reserved u64,
FileData[cbLength], zero padding to 8 bytes, guidFooter {71FBA722-0F79-4A0B-BB13-899256426B24}. Like the malware-triage
tools (onedump / OneNoteAnalyzer carving), the objects are found by scanning for guidHeader rather than walking the
FileNodeList tree (a damaged tree still yields the blobs); each hit is skipped past whole so a nested blob is not
re-counted. embedded_file_count = number of FileDataStoreObjects; embedded_file_sha256s (md5s/sha1s/sizes) = one entry
per object in file order, lowercase hex digests of FileData (pyOneNote get_files() content). No embedded file ->
count 0, the digest lists "none". Not a OneNote revision store (decoy / renamed) -> "none"."""
import hashlib
import struct

FIELDS = {
    ("onenote", "embedded_file_count"): "onenote_value",
    ("onenote", "embedded_files_count"): "onenote_value",
    ("onenote", "file_data_store_object_count"): "onenote_value",
    ("onenote", "filedatastore_object_count"): "onenote_value",
    ("onenote", "file_data_object_count"): "onenote_value",
    ("onenote", "attachment_count"): "onenote_value",
    ("onenote", "embedded_object_count"): "onenote_value",
    ("onenote", "embedded_file_sha256s"): "onenote_value",
    ("onenote", "embedded_file_sha256"): "onenote_value",
    ("onenote", "embedded_files_sha256"): "onenote_value",
    ("onenote", "first_embedded_file_sha256"): "onenote_value",
    ("onenote", "file_data_store_object_sha256s"): "onenote_value",
    ("onenote", "attachment_sha256s"): "onenote_value",
    ("onenote", "embedded_file_md5s"): "onenote_value",
    ("onenote", "embedded_file_sha1s"): "onenote_value",
    ("onenote", "embedded_file_sizes"): "onenote_value",
    ("onenote", "embedded_file_sizes_bytes"): "onenote_value",
    ("onenote", "embedded_file_size_bytes"): "onenote_value",
    ("onenote", "embedded_file_magic_hex"): "onenote_value",
    ("onenote", "file_type_guid"): "onenote_value",
}

_ONE = bytes.fromhex("e4525c7b8cd8a74daeb15378d02996d3")      # {7B5C52E4-D88C-4DA7-AEB1-5378D02996D3} bytes_le
_TOC = bytes.fromhex("a12fff43d9ef764c9ee210ea5722765f")      # {43FF2FA1-EFD9-4C76-9EE2-10EA5722765F}
_HDR = bytes.fromhex("e716e3bd65261145a4c48d4d0b7a9eac")      # {BDE316E7-2665-4511-A4C4-8D4D0B7A9EAC}


def blobs(b):
    """FileData of every FileDataStoreObject in file order, or None when b is not a OneNote revision store."""
    if len(b) < 1024 or b[:16] not in (_ONE, _TOC):
        return None
    out, i = [], 1024
    while True:
        i = b.find(_HDR, i)
        if i < 0 or i + 36 > len(b):
            break
        n, = struct.unpack_from("<Q", b, i + 16)
        if i + 36 + n > len(b):
            i += 16
            continue
        out.append(b[i + 36:i + 36 + n])
        i += 36 + n
    return out


def _guid_text(g):
    a, b2, c = struct.unpack_from("<IHH", g)
    return "%08x-%04x-%04x-%s-%s" % (a, b2, c, g[8:10].hex(), g[10:16].hex())


def onenote_value(data, ctx):
    if data is None:
        return None
    b = bytes(data)
    try:
        fs = blobs(b)
    except Exception:
        return None
    if fs is None:
        return "none"
    f = ctx.get("field") or ""
    if f == "file_type_guid":
        return _guid_text(b[:16])
    if f.endswith("_count"):
        return len(fs)
    if not fs:
        return "none"
    if "sha256" in f:
        out = [hashlib.sha256(x).hexdigest() for x in fs]
        return out[0] if f.startswith("first_") or (f == "embedded_file_sha256" and len(out) == 1) else out
    if "sha1" in f:
        return [hashlib.sha1(x).hexdigest() for x in fs]
    if "md5" in f:
        return [hashlib.md5(x).hexdigest() for x in fs]
    if "size" in f:
        return [len(x) for x in fs]
    if f == "embedded_file_magic_hex":
        return [x[:8].hex() for x in fs]
    return None
