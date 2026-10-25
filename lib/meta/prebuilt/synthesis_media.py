"""Cross-RECORDING equivalence / odd-one-out synthesis (prebuilt, SPECULATIVE; spelling never GM-verified).
Coverage-atlas row #98 ("connect equivalent recordings"): the question lists `Files: [...]` audio members of the
artifact's container (WAV / FLAC / MP3 / Ogg / AIFF / MP4) and asks which are the same recording. Per file:
  * tag key: a correlation id = the first >= 12-hex-digit token of any tag value (D17 WAV INAM "Huntress audio
    evidence <12 hex>"), else the title (WAV INAM, ID3 TIT2, Vorbis TITLE, MP4 \\xa9nam; casefolded, trimmed) --
    tags read with lib.meta.prebuilt.media_tags (ffmpeg key mapping);
  * content key: md5 of the decoded PCM in FLAC's STREAMINFO-MD5 layout (signed little-endian, interleaved) -- a WAV /
    AIFF data chunk is normalized to it (8-bit unsigned -> signed, AIFF big-endian -> LE), a FLAC contributes its
    STREAMINFO MD5 (all-zero = unset -> none), so a lossless transcode links to its source;
  * sample count / duration: WAV data size / block_align, FLAC STREAMINFO total samples, AIFF COMM numSampleFrames,
    Ogg last granule (Opus: - pre-skip, 48 kHz), MP3 Xing/Info frame count * samples-per-frame - LAME encoder delay
    - padding (the gapless decoded length, ffmpeg-style) else counted frames, MP4 audio trak mdhd duration.
    duration key = round(seconds * 100) (10 ms units).
equivalence_groups = union-find over equal tag key OR equal content key; every group's names sorted, groups ordered by
their first name, singletons kept -> compact JSON array of arrays. The *_groups siblings group by ONE criterion
(title/correlation tag, duration, sample count, content hash). odd_one_out = the only singleton group (None when there
is not exactly one); duplicate_count = sum(len(group) - 1); group_count = number of groups.
digest_order(question, get_bytes, algo) adds the md5/sha1/sha512/size siblings of lib.meta.synthesis.digest_order
(size = byte length ascending, ties by name; "descending" in the text reverses). Solver-facing ONLY, not in FIELDS:
registering `synthesis.<algo>_order` makes the D15-D17 `...-synthesis-sha256-order` ids parse into lib.meta.answer,
whose lane call holds only the lone member (no siblings) -> "registered but no answer" regressions.
equivalence_groups(question, get_bytes, field) is the solver-facing call; through lib.meta.answer the extractor reads
siblings from ctx["read"] when supplied, else from `data` when the artifact IS the container zip (all its audio
members when the question has no Files list). A lone member / no reader -> None; a container with no audio -> "none"
(odd_* / outlier_* over a set holding regf hives -> synthesis_regf.py's planted hive)."""
import hashlib
import io
import json
import re
import struct

FIELDS = {
    ("synthesis", "equivalence_groups"): "media_value",
    ("synthesis", "audio_equivalence_groups"): "media_value",
    ("synthesis", "media_equivalence_groups"): "media_value",
    ("synthesis", "recording_equivalence_groups"): "media_value",
    ("synthesis", "equivalent_recording_groups"): "media_value",
    ("synthesis", "equivalent_recordings"): "media_value",
    ("synthesis", "recording_groups"): "media_value",
    ("synthesis", "same_recording_groups"): "media_value",
    ("synthesis", "audio_groups"): "media_value",
    ("synthesis", "title_groups"): "media_value",
    ("synthesis", "tag_groups"): "media_value",
    ("synthesis", "correlation_groups"): "media_value",
    ("synthesis", "correlation_id_groups"): "media_value",
    ("synthesis", "correlation_tag_groups"): "media_value",
    ("synthesis", "duration_groups"): "media_value",
    ("synthesis", "sample_count_groups"): "media_value",
    ("synthesis", "content_groups"): "media_value",
    ("synthesis", "content_hash_groups"): "media_value",
    ("synthesis", "pcm_hash_groups"): "media_value",
    ("synthesis", "pcm_sha256_groups"): "media_value",
    ("synthesis", "audio_hash_groups"): "media_value",
    ("synthesis", "audio_md5_groups"): "media_value",
    ("synthesis", "flac_md5_groups"): "media_value",
    ("synthesis", "odd_one_out"): "media_value",
    ("synthesis", "odd_one_out_filename"): "media_value",
    ("synthesis", "odd_one_out_file"): "media_value",
    ("synthesis", "odd_recording"): "media_value",
    ("synthesis", "odd_recording_filename"): "media_value",
    ("synthesis", "odd_file"): "media_value",
    ("synthesis", "outlier_filename"): "media_value",
    ("synthesis", "outlier_file"): "media_value",
    ("synthesis", "duplicate_count"): "media_value",
    ("synthesis", "duplicate_recording_count"): "media_value",
    ("synthesis", "equivalent_duplicate_count"): "media_value",
    ("synthesis", "group_count"): "media_value",
    ("synthesis", "equivalence_group_count"): "media_value",
    ("synthesis", "recording_count"): "media_value",
    ("synthesis", "unique_recording_count"): "media_value",
    ("synthesis", "distinct_recording_count"): "media_value",
}

_FILES = re.compile(r"Files:\s*(\[.*?\])", re.S)
_CORR = re.compile(r"(?<![0-9A-Fa-f])([0-9A-Fa-f]{12,})(?![0-9A-Fa-f])")
_MP3_BR = {1: [0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448],
           2: [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384],
           3: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
           4: [0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256],
           5: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
_MP3_SR = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


# ---------------------------------------------------------------- per-format sample count + PCM digest

def _pcm_md5(pcm, bits, signed8, be):
    """md5 hex of PCM in FLAC's MD5 layout (signed, little-endian, byte-aligned)."""
    width = (bits + 7) // 8
    if width == 1 and not signed8:
        pcm = bytes((c - 128) & 0xFF for c in pcm)
    elif be and width > 1:
        n = len(pcm) - len(pcm) % width
        pcm = b"".join(pcm[i:i + width][::-1] for i in range(0, n, width))
    return hashlib.md5(pcm).hexdigest()


def _wav(b):
    if len(b) < 12 or b[:4] not in (b"RIFF", b"RIFX") or b[8:12] != b"WAVE":
        return None
    e = "<" if b[:4] == b"RIFF" else ">"
    fmt, data, i = None, None, 12
    while i + 8 <= len(b):
        cid, sz = b[i:i + 4], struct.unpack_from(e + "I", b, i + 4)[0]
        body = b[i + 8:i + 8 + sz]
        if cid == b"fmt " and len(body) >= 16:
            tag, ch, rate, _abps, align, bits = struct.unpack_from(e + "HHIIHH", body, 0)
            if tag == 0xFFFE and len(body) >= 26:
                tag = struct.unpack_from(e + "H", body, 24)[0]
            fmt = (tag, ch, rate, align, bits)
        elif cid == b"data" and data is None:
            data = body
        i += 8 + sz + (sz & 1)
    if fmt is None or data is None:
        return None
    tag, ch, rate, align, bits = fmt
    out = {"rate": rate, "samples": len(data) // align if align else None,
           "pcm_sha256": hashlib.sha256(data).hexdigest()}
    if tag == 1:
        out["pcm_md5"] = _pcm_md5(data[:len(data) - len(data) % align] if align else data, bits, False, e == ">")
    return out


def _ext80(x):
    exp, mant = struct.unpack(">HQ", x)
    sign, exp = exp >> 15, exp & 0x7FFF
    if exp == 0 and mant == 0:
        return 0.0
    v = mant * 2.0 ** (exp - 16383 - 63)
    return -v if sign else v


def _aiff(b):
    if len(b) < 12 or b[:4] != b"FORM" or b[8:12] not in (b"AIFF", b"AIFC"):
        return None
    comm, ssnd, i = None, None, 12
    while i + 8 <= len(b):
        cid, sz = b[i:i + 4], struct.unpack_from(">I", b, i + 4)[0]
        body = b[i + 8:i + 8 + sz]
        if cid == b"COMM" and len(body) >= 18:
            ch, frames, bits = struct.unpack_from(">HIH", body, 0)
            comp = body[18:22] if b[8:12] == b"AIFC" and len(body) >= 22 else b"NONE"
            comm = (ch, frames, bits, int(round(_ext80(body[8:18]))), comp)
        elif cid == b"SSND" and len(body) >= 8:
            off = struct.unpack_from(">I", body, 0)[0]
            ssnd = body[8 + off:]
        i += 8 + sz + (sz & 1)
    if comm is None:
        return None
    ch, frames, bits, rate, comp = comm
    out = {"rate": rate, "samples": frames}
    if ssnd is not None:
        n = frames * ch * ((bits + 7) // 8)
        pcm = ssnd[:n]
        out["pcm_sha256"] = hashlib.sha256(pcm).hexdigest()
        if comp in (b"NONE", b"twos", b"sowt"):
            out["pcm_md5"] = _pcm_md5(pcm, bits, True, comp != b"sowt")
    return out


def _flac(b):
    i = 0
    if b[:3] == b"ID3" and len(b) >= 10:
        i = 10 + ((b[6] & 0x7F) << 21 | (b[7] & 0x7F) << 14 | (b[8] & 0x7F) << 7 | (b[9] & 0x7F))
    if b[i:i + 4] != b"fLaC" or len(b) < i + 42 or b[i + 4] & 0x7F != 0:
        return None
    si = b[i + 8:i + 42]
    x = int.from_bytes(si[10:18], "big")
    rate, total = x >> 44, x & ((1 << 36) - 1)
    md5 = si[18:34].hex()
    return {"rate": rate, "samples": total or None, "pcm_md5": None if md5 == "0" * 32 else md5}


def _ogg(b):
    if b[:4] != b"OggS":
        return None
    serial, rate, skip, last, i, first = None, None, 0, None, 0, True
    while i + 27 <= len(b) and b[i:i + 4] == b"OggS":
        gran, ser = struct.unpack_from("<qI", b, i + 6)
        nseg = b[i + 26]
        lace = b[i + 27:i + 27 + nseg]
        body = i + 27 + nseg
        if first:
            serial, first = ser, False
            p = b[body:body + sum(lace)]
            if p[:7] == b"\x01vorbis" and len(p) >= 16:
                rate = struct.unpack_from("<I", p, 12)[0]
            elif p[:8] == b"OpusHead" and len(p) >= 12:
                rate, skip = 48000, struct.unpack_from("<H", p, 10)[0]
            elif p[:5] == b"\x7fFLAC" and len(p) >= 51:
                rate = int.from_bytes(p[27:35], "big") >> 44
            else:
                return None
        if ser == serial and gran >= 0:
            last = gran
        i = body + sum(lace)
    if rate is None:
        return None
    return {"rate": rate, "samples": max(last - skip, 0) if last is not None else None}


def _mp3_hdr(b, i):
    if i + 4 > len(b) or b[i] != 0xFF or b[i + 1] & 0xE0 != 0xE0:
        return None
    ver, layer = (b[i + 1] >> 3) & 3, (b[i + 1] >> 1) & 3
    bri, sri, pad = b[i + 2] >> 4, (b[i + 2] >> 2) & 3, (b[i + 2] >> 1) & 1
    if ver == 1 or layer == 0 or bri in (0, 15) or sri == 3:
        return None
    rate = _MP3_SR[ver][sri]
    if layer == 3:
        br, spf = _MP3_BR[1 if ver == 3 else 4][bri], 384
        size = (12 * br * 1000 // rate + pad) * 4
    else:
        br = _MP3_BR[(2 if layer == 2 else 3) if ver == 3 else 5][bri]
        spf = 1152 if (layer == 2 or ver == 3) else 576
        size = spf // 8 * br * 1000 // rate + pad
    return rate, spf, size, ver, b[i + 3] >> 6


def _mp3(b):
    i = 0
    if b[:3] == b"ID3" and len(b) >= 10:
        i = 10 + ((b[6] & 0x7F) << 21 | (b[7] & 0x7F) << 14 | (b[8] & 0x7F) << 7 | (b[9] & 0x7F))
    while i < len(b) and b[i] == 0:          # tag padding only: never scan arbitrary bytes for a sync word
        i += 1
    h = _mp3_hdr(b, i)
    if h is None or (i + h[2] < len(b) and _mp3_hdr(b, i + h[2]) is None):
        return None
    rate, spf, size, ver, mode = h
    side = (32 if mode != 3 else 17) if ver == 3 else (17 if mode != 3 else 9)
    x = i + 4 + side
    if b[x:x + 4] in (b"Xing", b"Info"):
        flags = struct.unpack_from(">I", b, x + 4)[0]
        if flags & 1:
            frames = struct.unpack_from(">I", b, x + 8)[0]
            o = x + 8 + 4 * bool(flags & 1) + 4 * bool(flags & 2) + 100 * bool(flags & 4) + 4 * bool(flags & 8)
            delay = padding = 0
            if b[o:o + 4] in (b"LAME", b"Lavf", b"Lavc") and o + 24 <= len(b):
                d = int.from_bytes(b[o + 21:o + 24], "big")
                delay, padding = d >> 12, d & 0xFFF
            return {"rate": rate, "samples": max(frames * spf - delay - padding, 0)}
        i += size
    n = 0
    while True:
        h = _mp3_hdr(b, i)
        if h is None:
            break
        n += 1
        i += h[2]
    return {"rate": rate, "samples": n * spf}


def _mp4(b):
    if b[4:8] != b"ftyp":
        return None
    from . import media_streams
    for s in media_streams.streams(b) or []:
        if s.get("codec_type") == "audio" and s.get("duration") and s.get("sample_rate"):
            rate = int(s["sample_rate"])
            return {"rate": rate, "samples": int(round(float(s["duration"]) * rate))}
    return {"rate": None, "samples": None}


def _title_corr(b):
    from . import media_tags
    r = media_tags._load(b)
    if not isinstance(r, tuple):
        return None, None
    corr = None
    for k, v in list(r[0]) + list(r[1]):
        m = _CORR.search(str(v))
        if m:
            corr = m.group(1).lower()
            break
    title = media_tags._find(r, "title")
    return (title.strip().casefold() if title and title.strip() else None), corr


def audio_info(b):
    """{rate, samples, seconds, title, corr, pcm_md5?, pcm_sha256?} of one audio member, or None (not audio)."""
    b = bytes(b)
    for fn in (_wav, _aiff, _flac, _ogg, _mp4, _mp3):
        try:
            r = fn(b)
        except (ValueError, IndexError, struct.error, OverflowError, TypeError, ZeroDivisionError, KeyError):
            r = None
        if r is not None:
            break
    else:
        return None
    try:
        r["title"], r["corr"] = _title_corr(b)
    except Exception:  # noqa: BLE001 - a damaged tag block leaves the tag keys unset
        r["title"], r["corr"] = None, None
    rate, n = r.get("rate"), r.get("samples")
    r["seconds"] = n / rate if rate and n is not None else None
    return r


# ---------------------------------------------------------------- grouping

def _groups(names, keyfns):
    """Union-find: two names join when any keyfn gives both the same non-None key. Groups sorted, by first name."""
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for kf in keyfns:
        seen = {}
        for n in names:
            k = kf(n)
            if k is None:
                continue
            if k in seen:
                a, c = find(seen[k]), find(n)
                if a != c:
                    parent[c] = a
            else:
                seen[k] = n
    out = {}
    for n in names:
        out.setdefault(find(n), []).append(n)
    return sorted((sorted(g) for g in out.values()), key=lambda g: g[0])


def _criterion(field):
    f = field or ""
    if "duration" in f:
        return "duration"
    if "sample_count" in f:
        return "samples"
    if any(t in f for t in ("content", "pcm", "hash", "md5")):
        return "content"
    if any(t in f for t in ("title", "tag", "correlation")):
        return "tag"
    return "all"


def equivalence(names, get_bytes, crit="all"):
    """{"groups", "odd", "duplicates", "count"} over the audio members among `names`, or None (a file unreadable /
    no audio member)."""
    info = {}
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        a = audio_info(b)
        if a is not None:
            info[n] = a
    if not info:
        return None
    tag = lambda n: info[n]["corr"] or (("title", info[n]["title"]) if info[n]["title"] else None)  # noqa: E731
    content = lambda n: info[n].get("pcm_md5") or info[n].get("pcm_sha256")  # noqa: E731
    dur = lambda n: None if info[n]["seconds"] is None else int(round(info[n]["seconds"] * 100))  # noqa: E731
    samples = lambda n: info[n].get("samples")  # noqa: E731
    keyfns = {"all": (tag, content), "tag": (tag,), "content": (content,), "duration": (dur,),
              "samples": (samples,)}[crit]
    groups = _groups(list(info), keyfns)
    singles = [g[0] for g in groups if len(g) == 1]
    return {"groups": groups, "odd": singles[0] if len(singles) == 1 and len(groups) > 1 else None,
            "duplicates": sum(len(g) - 1 for g in groups), "count": len(groups)}


def _pick(t, field):
    f = field or ""
    if "odd" in f or "outlier" in f:
        return t["odd"]
    if "duplicate" in f:
        return t["duplicates"]
    if f.endswith("count"):
        return t["count"]
    return t["groups"]


def file_list(question):
    """The question's `Files: [...]` names, or None."""
    text = (question or {}).get("question") if isinstance(question, dict) else question
    m = _FILES.search(str(text or ""))
    if not m:
        return None
    try:
        v = json.loads(m.group(1))
    except ValueError:
        return None
    return [str(x) for x in v] if isinstance(v, list) else None


def equivalence_groups(question, get_bytes, field="equivalence_groups"):
    """The `field` value (raw list / str / int) over the question's Files list read via get_bytes(name), or None."""
    names = file_list(question)
    if not names:
        return None
    t = equivalence(names, get_bytes, _criterion(field))
    return _pick(t, field) if t is not None else None


def digest_order(question, get_bytes, algo=None):
    """`Files: [...]` names ordered by hashlib.<algo> hexdigest (md5/sha1/sha256/sha512) or by byte size ("size"),
    ascending unless the text says descending (ties by name); a list, or None when a file can't be read."""
    text = str(((question or {}).get("question") if isinstance(question, dict) else question) or "")
    names = file_list(question)
    if algo is None:
        low = text.lower().replace("-", "")
        m = re.search(r"\b(md5|sha1|sha256|sha512)\b", low)
        algo = m.group(1) if m else ("size" if re.search(r"\b(size|bytes|length)\b", low) else None)
    if not names or not algo:
        return None
    keyed = []
    for n in names:
        b = get_bytes(n)
        if b is None:
            return None
        keyed.append((len(b) if algo == "size" else hashlib.new(algo, bytes(b)).hexdigest(), n))
    keyed.sort(reverse=bool(re.search(r"\bdescending\b", text, re.I)))
    return [n for _, n in keyed]


# ---------------------------------------------------------------- lib.meta.answer entry points

def _zip_reader(data):
    """(reader(name) -> bytes|None, [member names in archive order]) over a zip's bytes, or None."""
    import zipfile
    try:
        z = zipfile.ZipFile(io.BytesIO(bytes(data)))
        infos = [i for i in z.infolist() if not i.is_dir()]
    except (zipfile.BadZipFile, ValueError, OSError, EOFError, NotImplementedError):
        return None
    by_name = {i.filename: i for i in infos}
    by_base = {}
    for i in infos:
        by_base.setdefault(i.filename.rsplit("/", 1)[-1], i)

    def read(n):
        i = by_name.get(n) or by_base.get(str(n).rsplit("/", 1)[-1])
        if i is None:
            return None
        try:
            return z.read(i)
        except (zipfile.BadZipFile, ValueError, OSError, EOFError, NotImplementedError, RuntimeError):
            return None
    return read, [i.filename for i in infos]


def _source(data, ctx):
    """(read, names, from_zip) or None."""
    names = file_list(ctx.get("question") or {})
    read = ctx.get("read") if callable(ctx.get("read")) else None
    if read is None and data is not None and bytes(data[:4]) == b"PK\x03\x04":
        zr = _zip_reader(data)
        if zr is None:
            return None
        return zr[0], names or zr[1], True
    if read is None or not names:
        return None
    return read, names, False


def media_value(data, ctx):
    """synthesis.<equivalence field> (see the module docstring)."""
    try:
        src = _source(data, ctx)
        if src is None:
            return None
        read, names, from_zip = src
        if not names:
            return "none"
        field = ctx.get("field") or ""
        t = equivalence(names, read, _criterion(field))
        if t is None:
            if ("odd" in field or "outlier" in field):   # no audio: a hive set's planted hive (synthesis_regf.py)
                from .synthesis_regf import any_regf, regf_synthesis_value
                if any_regf(names, read):
                    return regf_synthesis_value(data, ctx)
            return "none" if from_zip else None
        return _pick(t, field)
    except Exception:  # noqa: BLE001 - a decoy / damaged input must never raise past the extractor
        return None

