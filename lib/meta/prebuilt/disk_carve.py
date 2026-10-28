"""Raw disk image -> EMBEDDED EVIDENCE located by offset (prebuilt, SPECULATIVE). D28 prompt: "Disk images hold every
previous artifact family in context ... locate evidence by offset". The image (unwrapped first through
disk_layout._unwrap: gzip/xz/bz2, fixed/dynamic VHD, VMDK, qcow2) is scanned for every family magic the lane has seen;
each hit is VALIDATED by its own structure and carved by the format's OWN length (never "to the next hit"):
  png  89504e47 + IHDR, chunk walk to IEND        jpeg ffd8ff, segment walk + entropy scan to FFD9
  gif  GIF87a/89a block walk to 0x3B              bmp  BM, bfSize (DIB header 12/40/56/108/124)
  pdf  %PDF-n.n, last %%EOF before the next hit (+ its EOL)
  zip  PK0304 + an EOCD whose cd_off+cd_size lands on it (+ comment) -> apk / jar / ooxml by central-directory names
  pe   MZ + e_lfanew -> PE\\0\\0; max(SizeOfHeaders, section raw ends, certificate table end); dotnet = CLR dir set
  elf  7f454c46, max(ehdr, phdr/shdr tables, segment/section file extents)
  macho feedface/feedfacf (either byte order): segment / symtab / code-signature extents; cafebabe FAT (nfat 1..20,
       so a Java class -- major>=45 in the same u32 -- is rejected): max(arch offset+size)
  ole  d0cf11e0a1b11ae1: (highest FAT-used sector + 2) x sector size; msi = root CLSID {000C1084-...-46}
  lnk  4c000000 + CLSID 00021401: header / IDList / LinkInfo / StringData / ExtraData walk
  sqlite `SQLite format 3\\0`: page_size (1 = 65536) x in-header page count
  evtx ElfFile: 4096 + chunk_count x 65536        registry regf: 4096 + hbins size @0x28
  prefetch SCCA@4: file size @0x0C (MAM\\x04 compressed: offset only, no carve length)
  pcap a1b2c3d4/a1b23c4d (both orders): 24 + record walk; pcapng 0a0d0d0a block walk (lengths repeated)
  ogg OggS page walk; riff RIFF size+8 (-> wav/avi/webp); mp4 ftyp box walk (-> mov/m4a/3gp/heic/avif by brand)
A hit lying INSIDE an already-accepted member (a PNG in a zip, a PE in an OLE) is not a separate member.
Offsets are decimal bytes from the start of the (unwrapped) image; LBA = offset // sector size (GPT probe size, else
512); partition_index = 0-based TABLE slot of the partition containing the start (extended MBR containers skipped),
partition_number = slot + 1; offset_in_partition_bytes = offset - partition start x sector size.
Fields: <family>_<x> (png_offset_bytes, pdf_start_lba, pe_sha256 ...) and evidence_/embedded_/carved_<x>
(evidence_offset_bytes, embedded_family_sequence, embedded_member_count ...); also bare evidence.<x>.
Which member: a family word in the field, else a file named in the question (`panel-001.png` -> png; with several of
that family, its -NNN ordinal when in range), else the only member, else the first SECTOR-ALIGNED one (else first).
No member of that family / no evidence at all -> "none". Filesystem mapping (FAT/NTFS/ext names) is NOT done: names
are matched by magic + family only."""
import hashlib
import re
import struct

from .disk_layout import _unwrap, layout

FIELDS = {
    ("disk", "evidence_*"): "carve_value",
    ("disk", "embedded_*"): "carve_value",
    ("disk", "carved_*"): "carve_value",
    ("disk", "png_*"): "carve_value",
    ("disk", "jpeg_*"): "carve_value",
    ("disk", "jpg_*"): "carve_value",
    ("disk", "gif_*"): "carve_value",
    ("disk", "bmp_*"): "carve_value",
    ("disk", "pdf_*"): "carve_value",
    ("disk", "zip_*"): "carve_value",
    ("disk", "ooxml_*"): "carve_value",
    ("disk", "docx_*"): "carve_value",
    ("disk", "apk_*"): "carve_value",
    ("disk", "jar_*"): "carve_value",
    ("disk", "pe_*"): "carve_value",
    ("disk", "exe_*"): "carve_value",
    ("disk", "dll_*"): "carve_value",
    ("disk", "dotnet_*"): "carve_value",
    ("disk", "elf_*"): "carve_value",
    ("disk", "macho_*"): "carve_value",
    ("disk", "ole_*"): "carve_value",
    ("disk", "cfb_*"): "carve_value",
    ("disk", "msi_*"): "carve_value",
    ("disk", "lnk_*"): "carve_value",
    ("disk", "sqlite_*"): "carve_value",
    ("disk", "evtx_*"): "carve_value",
    ("disk", "registry_*"): "carve_value",
    ("disk", "regf_*"): "carve_value",
    ("disk", "hive_*"): "carve_value",
    ("disk", "prefetch_*"): "carve_value",
    ("disk", "pcap_*"): "carve_value",
    ("disk", "pcapng_*"): "carve_value",
    ("disk", "ogg_*"): "carve_value",
    ("disk", "wav_*"): "carve_value",
    ("disk", "riff_*"): "carve_value",
    ("disk", "mp4_*"): "carve_value",
    ("disk", "mov_*"): "carve_value",
    ("image", "evidence_*"): "carve_value",
    ("image", "embedded_*"): "carve_value",
    ("image", "carved_*"): "carve_value",
    ("image", "png_*"): "carve_value",
    ("image", "jpeg_*"): "carve_value",
    ("image", "jpg_*"): "carve_value",
    ("image", "gif_*"): "carve_value",
    ("image", "bmp_*"): "carve_value",
    ("image", "pdf_*"): "carve_value",
    ("image", "zip_*"): "carve_value",
    ("image", "ooxml_*"): "carve_value",
    ("image", "docx_*"): "carve_value",
    ("image", "apk_*"): "carve_value",
    ("image", "jar_*"): "carve_value",
    ("image", "pe_*"): "carve_value",
    ("image", "exe_*"): "carve_value",
    ("image", "dll_*"): "carve_value",
    ("image", "dotnet_*"): "carve_value",
    ("image", "elf_*"): "carve_value",
    ("image", "macho_*"): "carve_value",
    ("image", "ole_*"): "carve_value",
    ("image", "cfb_*"): "carve_value",
    ("image", "msi_*"): "carve_value",
    ("image", "lnk_*"): "carve_value",
    ("image", "sqlite_*"): "carve_value",
    ("image", "evtx_*"): "carve_value",
    ("image", "registry_*"): "carve_value",
    ("image", "regf_*"): "carve_value",
    ("image", "hive_*"): "carve_value",
    ("image", "prefetch_*"): "carve_value",
    ("image", "pcap_*"): "carve_value",
    ("image", "pcapng_*"): "carve_value",
    ("image", "ogg_*"): "carve_value",
    ("image", "wav_*"): "carve_value",
    ("image", "riff_*"): "carve_value",
    ("image", "mp4_*"): "carve_value",
    ("image", "mov_*"): "carve_value",
    ("evidence", "evidence_*"): "carve_value",
    ("evidence", "embedded_*"): "carve_value",
    ("evidence", "carved_*"): "carve_value",
    ("evidence", "png_*"): "carve_value",
    ("evidence", "jpeg_*"): "carve_value",
    ("evidence", "jpg_*"): "carve_value",
    ("evidence", "gif_*"): "carve_value",
    ("evidence", "bmp_*"): "carve_value",
    ("evidence", "pdf_*"): "carve_value",
    ("evidence", "zip_*"): "carve_value",
    ("evidence", "ooxml_*"): "carve_value",
    ("evidence", "docx_*"): "carve_value",
    ("evidence", "apk_*"): "carve_value",
    ("evidence", "jar_*"): "carve_value",
    ("evidence", "pe_*"): "carve_value",
    ("evidence", "exe_*"): "carve_value",
    ("evidence", "dll_*"): "carve_value",
    ("evidence", "dotnet_*"): "carve_value",
    ("evidence", "elf_*"): "carve_value",
    ("evidence", "macho_*"): "carve_value",
    ("evidence", "ole_*"): "carve_value",
    ("evidence", "cfb_*"): "carve_value",
    ("evidence", "msi_*"): "carve_value",
    ("evidence", "lnk_*"): "carve_value",
    ("evidence", "sqlite_*"): "carve_value",
    ("evidence", "evtx_*"): "carve_value",
    ("evidence", "registry_*"): "carve_value",
    ("evidence", "regf_*"): "carve_value",
    ("evidence", "hive_*"): "carve_value",
    ("evidence", "prefetch_*"): "carve_value",
    ("evidence", "pcap_*"): "carve_value",
    ("evidence", "pcapng_*"): "carve_value",
    ("evidence", "ogg_*"): "carve_value",
    ("evidence", "wav_*"): "carve_value",
    ("evidence", "riff_*"): "carve_value",
    ("evidence", "mp4_*"): "carve_value",
    ("evidence", "mov_*"): "carve_value",
    ("evidence", "offset_bytes"): "carve_value",
    ("evidence", "offset"): "carve_value",
    ("evidence", "byte_offset"): "carve_value",
    ("evidence", "start_offset_bytes"): "carve_value",
    ("evidence", "start_lba"): "carve_value",
    ("evidence", "lba"): "carve_value",
    ("evidence", "start_sector"): "carve_value",
    ("evidence", "partition_index"): "carve_value",
    ("evidence", "partition_number"): "carve_value",
    ("evidence", "offset_in_partition_bytes"): "carve_value",
    ("evidence", "partition_relative_offset_bytes"): "carve_value",
    ("evidence", "sha256"): "carve_value",
    ("evidence", "sha1"): "carve_value",
    ("evidence", "md5"): "carve_value",
    ("evidence", "size_bytes"): "carve_value",
    ("evidence", "length_bytes"): "carve_value",
    ("evidence", "end_offset_bytes"): "carve_value",
    ("evidence", "family"): "carve_value",
    ("evidence", "family_sequence"): "carve_value",
    ("evidence", "family_list"): "carve_value",
    ("evidence", "families"): "carve_value",
    ("evidence", "member_count"): "carve_value",
    ("evidence", "count"): "carve_value",
    ("evidence", "offset_bytes_sequence"): "carve_value",
    ("evidence", "offsets_bytes"): "carve_value",
    ("evidence", "start_lba_sequence"): "carve_value",
    ("evidence", "sha256_sequence"): "carve_value",
}

_SCAN_CAP = 256 << 20


def _be(fmt, b, o):
    return struct.unpack_from(fmt, b, o)


# ---- per-family validators: (b, start, limit) -> (family, end) or None -------------------------------------------
def _png(b, s, lim):
    if b[s + 12:s + 16] != b"IHDR":
        return None
    o = s + 8
    while o + 12 <= lim:
        n, = _be(">I", b, o)
        t = b[o + 4:o + 8]
        if n > lim or not t.isalpha():
            return None
        o += 12 + n
        if t == b"IEND":
            return ("png", o) if o <= lim else None
    return None


def _jpeg(b, s, lim):
    if b[s + 3] not in b"\xe0\xe1\xe2\xe3\xe8\xed\xee\xef\xdb\xc0\xc2\xc4\xfe":
        return None
    o = s + 2
    while o + 4 <= lim:
        if b[o] != 0xFF:
            return None
        m = b[o + 1]
        if m == 0xFF:
            o += 1
            continue
        if m == 0xD9:
            return "jpeg", o + 2
        if 0xD0 <= m <= 0xD7 or m == 0x01:
            o += 2
            continue
        n, = _be(">H", b, o + 2)
        if n < 2:
            return None
        o += 2 + n
        if m == 0xDA:
            while o + 1 < lim:
                o = b.find(b"\xff", o, lim)
                if o < 0:
                    return None
                nx = b[o + 1]
                if nx == 0 or 0xD0 <= nx <= 0xD7 or nx == 0xFF:
                    o += 1 if nx == 0xFF else 2
                    continue
                break
    return None


def _gif(b, s, lim):
    if b[s + 3:s + 6] not in (b"87a", b"89a"):
        return None
    flags = b[s + 10]
    o = s + 13 + (3 << ((flags & 7) + 1) if flags & 0x80 else 0)

    def sub(o):
        while o < lim:
            n = b[o]
            o += 1 + n
            if n == 0:
                return o
        return None
    while o and o < lim:
        c = b[o]
        if c == 0x3B:
            return "gif", o + 1
        if c == 0x21:
            o = sub(o + 2)
        elif c == 0x2C:
            f = b[o + 9]
            o += 10 + (3 << ((f & 7) + 1) if f & 0x80 else 0)
            o = sub(o + 1)
        else:
            return None
    return None


def _bmp(b, s, lim):
    size, res, off, dib = _be("<IIII", b, s + 2)
    if res or dib not in (12, 40, 56, 108, 124) or not 14 + dib <= off <= size or s + size > lim:
        return None
    return "bmp", s + size


def _pdf(b, s, lim):
    if not re.match(rb"%PDF-\d\.\d", b[s:s + 8]):
        return None
    e = b.find(b"%%EOF", s, lim)        # first %%EOF, extended over incremental updates that follow it
    if e < 0:
        return None
    e += 5
    while True:
        m = re.compile(rb"[\r\n\t \0]*(?:\d+ \d+ obj|xref|%(?!PDF))").match(b, e, min(lim, e + 64))
        nx = b.find(b"%%EOF", e, lim) if m else -1
        if nx < 0:
            break
        e = nx + 5
    if b[e:e + 2] == b"\r\n":
        e += 2
    elif b[e:e + 1] in (b"\r", b"\n"):
        e += 1
    return "pdf", e


def _zip(b, s, lim):
    o = s
    while True:
        e = b.find(b"PK\x05\x06", o, lim)
        if e < 0 or e + 22 > lim:
            return None
        cds, cdo, cl = _be("<IIH", b, e + 12)
        if s + cdo + cds == e and e + 22 + cl <= lim:
            cd = b[s + cdo:e]
            fam = "apk" if b"AndroidManifest.xml" in cd else "ooxml" if b"[Content_Types].xml" in cd else \
                "jar" if b"META-INF/MANIFEST.MF" in cd else "zip"
            return fam, e + 22 + cl
        o = e + 4


def _pe(b, s, lim):
    lf, = _be("<I", b, s + 0x3C)
    p = s + lf
    if not 0x40 <= lf < 0x1000 or p + 24 > lim or b[p:p + 4] != b"PE\0\0":
        return None
    nsec, = _be("<H", b, p + 6)
    osz, = _be("<H", b, p + 20)
    opt = p + 24
    mg, = _be("<H", b, opt)
    if mg not in (0x10B, 0x20B):
        return None
    end = _be("<I", b, opt + 60)[0]
    dd = opt + (96 if mg == 0x10B else 112)
    ndd, = _be("<I", b, dd - 4)
    for i in range(nsec):
        sh = opt + osz + 40 * i
        rs, rp = _be("<II", b, sh + 16)
        if rs:
            end = max(end, rp + rs)
    clr = False
    if ndd > 4:
        co, cs = _be("<II", b, dd + 32)
        if co and cs:
            end = max(end, co + cs)
    if ndd > 14:
        clr = any(_be("<II", b, dd + 112))
    return ("dotnet" if clr else "pe"), s + end


def _elf(b, s, lim):
    cl, en, ver = b[s + 4], b[s + 5], b[s + 6]
    if cl not in (1, 2) or en not in (1, 2) or ver != 1:
        return None
    e = "<" if en == 1 else ">"
    if cl == 1:
        phoff, shoff = _be(e + "II", b, s + 28)
        ehs, phes, phn, shes, shn = _be(e + "HHHHH", b, s + 40)
        phf = lambda o: (_be(e + "I", b, o + 4)[0], _be(e + "I", b, o + 16)[0])  # noqa: E731
        shf = lambda o: (_be(e + "I", b, o + 4)[0], _be(e + "I", b, o + 16)[0], _be(e + "I", b, o + 20)[0])  # noqa: E731
    else:
        phoff, shoff = _be(e + "QQ", b, s + 32)
        ehs, phes, phn, shes, shn = _be(e + "HHHHH", b, s + 52)
        phf = lambda o: (_be(e + "Q", b, o + 8)[0], _be(e + "Q", b, o + 32)[0])  # noqa: E731
        shf = lambda o: (_be(e + "I", b, o + 4)[0], _be(e + "Q", b, o + 24)[0], _be(e + "Q", b, o + 32)[0])  # noqa: E731
    if ehs not in (52, 64) or phn > 512 or shn > 4096:
        return None
    end = ehs
    if phn:
        end = max(end, phoff + phn * phes)
        for i in range(phn):
            o = s + phoff + i * phes
            if o + phes > lim:
                return None
            off, fs = phf(o)
            end = max(end, off + fs)
    if shn:
        end = max(end, shoff + shn * shes)
        for i in range(shn):
            o = s + shoff + i * shes
            if o + shes > lim:
                return None
            t, off, sz = shf(o)
            if t != 8:   # SHT_NOBITS has no file bytes
                end = max(end, off + sz)
    return ("elf", s + end) if s + end <= lim else None


def _macho(b, s, lim):
    m = b[s:s + 4]
    if m == b"\xca\xfe\xba\xbe":
        n, = _be(">I", b, s + 4)
        if not 1 <= n <= 20:
            return None
        end = 8 + 20 * n
        for i in range(n):
            ct, _st, off, sz = _be(">IIII", b, s + 8 + 20 * i)
            if off < 8 + 20 * n:
                return None
            end = max(end, off + sz)
        return ("macho", s + end) if s + end <= lim else None
    e = "<" if m in (b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe") else ">"
    is64 = m in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf")
    _ct, _st, ft, nc, szc = _be(e + "iIIII", b, s + 4)
    hs = 32 if is64 else 28
    if not 1 <= ft <= 12 or nc > 1024 or szc > 1 << 20:
        return None
    end, o = hs + szc, s + hs
    for _ in range(nc):
        cmd, csz = _be(e + "II", b, o)
        if csz < 8 or o + csz > lim:
            return None
        if cmd == 0x19:
            fo, fs = _be(e + "QQ", b, o + 40)
            end = max(end, fo + fs)
        elif cmd == 0x1:
            fo, fs = _be(e + "II", b, o + 32)
            end = max(end, fo + fs)
        elif cmd == 0x2:
            so, ns, sto, sts = _be(e + "IIII", b, o + 8)
            end = max(end, so + ns * (16 if is64 else 12), sto + sts)
        elif cmd in (0x1D, 0x1E, 0x26, 0x29, 0x2B, 0x80000033, 0x80000034):
            do, ds = _be(e + "II", b, o + 8)
            end = max(end, do + ds)
        o += csz
    return ("macho", s + end) if s + end <= lim else None


_MSI_CLSID = bytes.fromhex("84100c0000000000c000000000000046")  # {000C1084-0000-0000-C000-000000000046}


def _ole(b, s, lim):
    if b[s + 8:s + 24] != b"\0" * 16:
        return None
    sh, = _be("<H", b, s + 0x1E)
    if sh not in (9, 12):
        return None
    ss = 1 << sh
    nfat, dir1 = _be("<II", b, s + 0x2C)
    difat1, ndifat = _be("<II", b, s + 0x44)
    secs = [x for x in _be("<109I", b, s + 0x4C) if x < 0xFFFFFFFA]
    cur = difat1
    for _ in range(min(ndifat, 4096)):
        if cur >= 0xFFFFFFFA:
            break
        o = s + ss + cur * ss
        v = _be("<%dI" % (ss // 4), b, o)
        secs += [x for x in v[:-1] if x < 0xFFFFFFFA]
        cur = v[-1]
    secs = secs[:nfat]
    top = -1
    for k, fs in enumerate(secs):
        o = s + ss + fs * ss
        if o + ss > lim:
            return None
        for i, x in enumerate(_be("<%dI" % (ss // 4), b, o)):
            if x != 0xFFFFFFFF:
                top = max(top, k * (ss // 4) + i)
    if top < 0:
        return None
    fam = "ole"
    ro = s + ss + dir1 * ss
    if ro + 128 <= lim and b[ro + 0x50:ro + 0x60] == _MSI_CLSID:
        fam = "msi"
    return (fam, s + (top + 2) * ss) if s + (top + 2) * ss <= lim else None


def _lnk(b, s, lim):
    if b[s + 4:s + 20] != bytes.fromhex("0114020000000000c000000000000046"):
        return None
    fl, = _be("<I", b, s + 0x14)
    o = s + 76
    if fl & 1:
        o += 2 + _be("<H", b, o)[0]
    if fl & 2:
        o += _be("<I", b, o)[0]
    for bit in (4, 8, 0x10, 0x20, 0x40):
        if fl & bit:
            n, = _be("<H", b, o)
            o += 2 + n * (2 if fl & 0x80 else 1)
    for _ in range(64):
        if o + 4 > lim:
            return None
        n, = _be("<I", b, o)
        if n < 4:
            return "lnk", o + 4
        o += n
    return None


def _sqlite(b, s, lim):
    ps, = _be(">H", b, s + 16)
    ps = 65536 if ps == 1 else ps
    if ps < 512 or ps & (ps - 1):
        return None
    n, = _be(">I", b, s + 28)
    cc, vv = _be(">I", b, s + 24)[0], _be(">I", b, s + 92)[0]
    if not n or cc != vv or s + n * ps > lim:
        return None
    return "sqlite", s + n * ps


def _evtx(b, s, lim):
    hs, = _be("<I", b, s + 0x20)
    bs, nc = _be("<HH", b, s + 0x28)
    if hs != 128 or bs != 4096:
        return None
    e = s + 4096 + nc * 65536
    while e + 8 <= lim and b[e:e + 8] == b"ElfChnk\0":   # chunks beyond a stale header count
        e += 65536
    return "evtx", min(e, lim)


def _regf(b, s, lim):
    n, = _be("<I", b, s + 0x28)
    if not n or n % 4096 or b[s + 4096:s + 4100] != b"hbin":
        return None
    return "registry", min(s + 4096 + n, lim)


def _scca(b, s, lim):            # hit is at "SCCA"; the file starts 4 bytes earlier
    s -= 4
    v, = _be("<I", b, s)
    if v not in (17, 23, 26, 30, 31):
        return None
    n, = _be("<I", b, s + 12)
    return ("prefetch", s + n) if 0x54 <= n and s + n <= lim else None


def _mam(b, s, lim):
    n, = _be("<I", b, s + 4)
    return ("prefetch", None) if 0x54 <= n < 1 << 26 else None


def _pcap(b, s, lim):
    m = b[s:s + 4]
    e = "<" if m in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1") else ">"
    vmaj, vmin, _tz, _sf, snap, lt = _be(e + "HHiIII", b, s + 4)
    if vmaj != 2 or lt > 0xFFFF:
        return None
    o, cap = s + 24, max(snap, 262144)
    while o + 16 <= lim:
        ts, _us, il, ol = _be(e + "IIII", b, o)
        if il == 0 and ol == 0 and ts == 0 or il > cap or o + 16 + il > lim:
            break
        o += 16 + il
    return "pcap", o


def _pcapng(b, s, lim):
    bom = b[s + 8:s + 12]
    e = "<" if bom == b"\x4d\x3c\x2b\x1a" else ">" if bom == b"\x1a\x2b\x3c\x4d" else None
    if e is None:
        return None
    o = s
    while o + 12 <= lim:
        t, n = _be(e + "II", b, o)
        if n < 12 or n % 4 or o + n > lim or _be(e + "I", b, o + n - 4)[0] != n or not t or t > 0x80000000:
            break
        if t == 0x0A0D0D0A and o != s:
            break
        o += n
    return ("pcapng", o) if o > s else None


def _ogg(b, s, lim):
    o = s
    while o + 27 <= lim and b[o:o + 4] == b"OggS":
        ns = b[o + 26]
        o += 27 + ns + sum(b[o + 27:o + 27 + ns])
    return ("ogg", o) if b[s + 4] == 0 and o <= lim else None


def _riff(b, s, lim):
    n, = _be("<I", b, s + 4)
    form = b[s + 8:s + 12]
    if n < 4 or not form.isalnum() and form not in (b"AVI ",):
        return None
    e = s + 8 + n + (n & 1)
    fam = {b"WAVE": "wav", b"AVI ": "avi", b"WEBP": "webp"}.get(form, "riff")
    return fam, min(e, lim)


def _ftyp(b, s, lim):          # hit is at "ftyp"; the box (and file) starts 4 bytes earlier
    s -= 4
    o = s
    while o + 8 <= lim:
        n, t = _be(">I", b, o)[0], b[o + 4:o + 8]
        if n == 1:
            n, = _be(">Q", b, o + 8)
        if n < 8 or not re.match(rb"^[a-z0-9 ]{4}$", t, re.I) or o + n > lim:
            break
        o += n
    br = b[s + 8:s + 12]
    fam = "mov" if br == b"qt  " else "m4a" if br.startswith(b"M4A") else "3gp" if br.startswith(b"3g") else \
        "heic" if br in (b"heic", b"heix", b"mif1") else "avif" if br == b"avif" else "mp4"
    return (fam, o) if o > s + 8 else None


_MAGIC = [(b"\x89PNG\r\n\x1a\n", _png), (b"\xff\xd8\xff", _jpeg), (b"GIF8", _gif), (b"BM", _bmp), (b"%PDF-", _pdf),
          (b"PK\x03\x04", _zip), (b"MZ", _pe), (b"\x7fELF", _elf), (b"\xca\xfe\xba\xbe", _macho),
          (b"\xce\xfa\xed\xfe", _macho), (b"\xcf\xfa\xed\xfe", _macho), (b"\xfe\xed\xfa\xce", _macho),
          (b"\xfe\xed\xfa\xcf", _macho), (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", _ole), (b"L\0\0\0\x01\x14\x02\0", _lnk),
          (b"SQLite format 3\0", _sqlite), (b"ElfFile\0", _evtx), (b"regf", _regf), (b"SCCA", _scca),
          (b"MAM\x04", _mam), (b"\xd4\xc3\xb2\xa1", _pcap), (b"\xa1\xb2\xc3\xd4", _pcap), (b"\x4d\x3c\xb2\xa1", _pcap),
          (b"\xa1\xb2\x3c\x4d", _pcap), (b"\x0a\x0d\x0d\x0a", _pcapng), (b"OggS", _ogg), (b"RIFF", _riff),
          (b"ftyp", _ftyp)]
_BACK = {_scca: 4, _ftyp: 4}
_BMP_MAX = 4096          # `BM` is two bytes: only sector-aligned BMP hits are tried


def _scan(b):
    """[{family, off, end|None}] in offset order, nested hits dropped."""
    cands = []
    n = len(b)
    for mg, fn in _MAGIC:
        o = b.find(mg)
        k = 0
        while o >= 0 and k < 20000:
            k += 1
            st = o - _BACK.get(fn, 0)
            if st >= 0 and not (fn is _bmp and st % 512):
                cands.append((st, o, fn))
            o = b.find(mg, o + 1)
    cands.sort(key=lambda c: c[0])
    out, cover = [], -1
    for st, o, fn in cands:
        if st < cover:
            continue
        try:
            r = fn(b, o, n)
        except (struct.error, IndexError, ValueError, OverflowError):
            r = None
        if not r:
            continue
        fam, end = r
        if out and out[-1]["off"] == st:
            continue
        out.append({"family": fam, "off": st, "end": end})
        cover = end if end else st + 1
    return out


_CACHE = {}


def _evidence(data):
    """(hits, layout|None, image bytes) for the image, memoised on the bytes' digest (never on id())."""
    key = hashlib.sha1(data).digest() + len(data).to_bytes(8, "little")
    hit = _CACHE.get(key)
    if hit is not None:
        return hit
    img = _unwrap(data)
    if not isinstance(img, (bytes, bytearray)):
        img = img[0:min(len(img), _SCAN_CAP)]
    img = bytes(img[:_SCAN_CAP])
    try:
        lay = layout(data)
    except Exception:  # noqa: BLE001
        lay = None
    out = (_scan(img), lay, img)
    if len(_CACHE) > 8:
        _CACHE.clear()
    _CACHE[key] = out
    return out


# requested family word -> hit families it covers (exact first, then the group)
_GROUP = {"jpg": ("jpeg",), "jpeg": ("jpeg",), "pe": ("pe", "dotnet"), "exe": ("pe", "dotnet"), "dll": ("pe", "dotnet"),
          "dotnet": ("dotnet",), "zip": ("zip", "apk", "jar", "ooxml"), "docx": ("ooxml",), "ooxml": ("ooxml",),
          "ole": ("ole", "msi"), "cfb": ("ole", "msi"), "msi": ("msi",), "regf": ("registry",), "hive": ("registry",),
          "registry": ("registry",), "pcap": ("pcap", "pcapng"), "pcapng": ("pcapng",), "riff": ("wav", "avi", "webp", "riff"),
          "mp4": ("mp4", "mov", "m4a", "3gp"), "mov": ("mov",)}
_EXT = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "bmp": "bmp", "pdf": "pdf", "zip": "zip",
        "docx": "ooxml", "xlsx": "ooxml", "pptx": "ooxml", "docm": "ooxml", "xlsm": "ooxml", "apk": "apk", "jar": "jar",
        "exe": "pe", "dll": "pe", "sys": "pe", "elf": "elf", "so": "elf", "bin": None, "dylib": "macho",
        "macho": "macho", "doc": "ole", "xls": "ole", "ppt": "ole", "msi": "msi", "lnk": "lnk", "db": "sqlite",
        "sqlite": "sqlite", "sqlite3": "sqlite", "evtx": "evtx", "dat": "registry", "hive": "registry",
        "pf": "prefetch", "pcap": "pcap", "pcapng": "pcapng", "cap": "pcap", "ogg": "ogg", "opus": "ogg",
        "wav": "wav", "avi": "avi", "webp": "webp", "mp4": "mp4", "mov": "mov", "m4a": "m4a"}
_IMG_EXT = ("img", "dd", "raw", "vhd", "vhdx", "vmdk", "qcow2", "e01", "iso", "gz", "xz", "bz2", "zip")
_NAME = re.compile(r"([\w.-]+)\.([A-Za-z0-9]{1,7})\b")


def _of(hits, fam):
    want = _GROUP.get(fam, (fam,))
    exact = [h for h in hits if h["family"] == fam]
    return exact or [h for h in hits if h["family"] in want]


def _pick(hits, ctx, fam):
    """(chosen hit | None, candidate list)."""
    if fam not in ("evidence", "embedded", "carved"):
        c = _of(hits, fam)
        return (c[0] if c else None), c
    cands, num = hits, None
    q = ctx.get("question")
    q = str((q.get("question") if isinstance(q, dict) else q) or "")
    q = re.sub(r"^.*?\bDetermine\s+\S+\s+", "", q)          # drop the `fmt.field` token itself
    for stem, ext in _NAME.findall(q + " " + str(ctx.get("member") or "")):
        if ext.lower() in _IMG_EXT and stem.lower() + "." + ext.lower() == str(ctx.get("member") or "").lower():
            continue
        f = _EXT.get(ext.lower())
        if f:
            cands = _of(hits, f)
            m = re.search(r"(\d+)$", stem)
            num = int(m.group(1)) if m else None
            break
    if not cands:
        return None, cands
    if len(cands) > 1 and num and 1 <= num <= len(cands):
        return cands[num - 1], cands
    al = [h for h in cands if h["off"] % 512 == 0]
    return (al or cands)[0], cands


def _part(lay, off):
    if not lay:
        return None
    ss = lay["ss"]
    for p in lay["parts"]:
        if p.get("ext"):
            continue
        if p["start"] * ss <= off <= p["end"] * ss + ss - 1:
            return p
    return None


_COLL = {"family_sequence": "fam", "family_list": "fam", "families": "fam", "format_sequence": "fam",
         "type_sequence": "fam", "member_family_sequence": "fam", "member_count": "n", "count": "n",
         "file_count": "n", "members_count": "n", "offset_bytes_sequence": "off", "offsets_bytes": "off",
         "offset_sequence": "off", "offsets": "off", "start_lba_sequence": "lba", "lba_sequence": "lba",
         "sha256_sequence": "sha", "sha256s": "sha"}


def carve_value(data, ctx):
    """disk/image/evidence.<family|evidence|embedded|carved>_<x> and evidence.<x>: see the module docstring."""
    try:
        return _carve_value(data, ctx)
    except Exception:  # noqa: BLE001 -- a hostile image never raises past the extractor
        return None


def _carve_value(data, ctx):
    if data is None:
        return None
    field = ctx.get("field") or ""
    fam, sub = field.split("_", 1) if "_" in field else (field, "")
    if ctx.get("fmt") == "evidence" and fam not in _GROUP and fam not in _EXT.values() and \
            fam not in ("evidence", "embedded", "carved", "elf", "macho", "ole", "evtx", "registry", "prefetch"):
        fam, sub = "evidence", field
    try:
        hits, lay, img = _evidence(bytes(data))
    except Exception:  # noqa: BLE001
        return None
    ss = lay["ss"] if lay else 512
    pool = hits if fam in ("evidence", "embedded", "carved") else _of(hits, fam)
    col = _COLL.get(sub)
    if col:
        if col == "n":
            return len(pool)
        if not pool:
            return "none"
        if col == "fam":
            return [h["family"] for h in pool]
        if col == "off":
            return [h["off"] for h in pool]
        if col == "lba":
            return [h["off"] // ss for h in pool]
        return [hashlib.sha256(img[h["off"]:h["end"]]).hexdigest() if h["end"] else None for h in pool]
    h, _c = _pick(hits, ctx, fam)
    if h is None:
        return "none"
    off, end = h["off"], h["end"]
    if sub in ("offset_bytes", "offset", "byte_offset", "start_offset_bytes", "offset_decimal", "start_offset",
               "image_offset_bytes", "disk_offset_bytes", "absolute_offset_bytes"):
        return off
    if sub in ("start_lba", "lba", "start_sector", "sector", "first_lba", "lba_offset"):
        return off // ss
    if sub in ("family", "format", "type", "file_type"):
        return h["family"]
    if sub in ("partition_index", "partition_slot", "partition_number", "partition_num",
               "offset_in_partition_bytes", "partition_relative_offset_bytes", "relative_offset_bytes",
               "partition_offset_bytes", "offset_within_partition_bytes", "partition_start_lba"):
        p = _part(lay, off)
        if p is None:
            return "none"
        if sub in ("partition_index", "partition_slot"):
            return p["slot"]
        if sub in ("partition_number", "partition_num"):
            return p["slot"] + 1
        if sub == "partition_start_lba":
            return p["start"]
        return off - p["start"] * ss
    if end is None:
        return None
    if sub in ("size_bytes", "length_bytes", "carved_size_bytes", "carved_length_bytes", "size", "length"):
        return end - off
    if sub in ("end_offset_bytes", "end_offset"):
        return end
    if sub in ("sha256", "carved_sha256", "sha256_hex"):
        return hashlib.sha256(img[off:end]).hexdigest()
    if sub in ("sha1", "carved_sha1"):
        return hashlib.sha1(img[off:end]).hexdigest()
    if sub in ("md5", "carved_md5"):
        return hashlib.md5(img[off:end]).hexdigest()
    return None
