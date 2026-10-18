#!/usr/bin/env python3
"""Metadata-forensics LANE solver: every GM-verified field family D1..today through lib.meta (+ speculative breadth).

    solve.py --contract <contract.json> --artifacts <dir>   ->  prints {answer_id: value} as JSON on the last line

The harness RACES it beside the LLM worker (reuse race; `_day_key` 999 = always tried first); it never blocks the
worker. A field is "confident" only when lib.meta's entry for it is GM-verified (hctf/solvers.py _known_ids).
Seeded into a day's solver dir (HCTF_LANE_SEED_LANES): the worker adds ONLY today's new field in `local_answer()`;
the post-run ratchet folds it into lib/meta.

Runs on the Homebase VM inside a ~6-7 s window for EVERY Mastery set: stdlib + lib.* + pyzipper/pyelftools/pefile/
capstone/pycryptodome/androguard only, no subprocess, all sets well under 1 s. Also runs from the race snapshot copy
(.run/spec-dayNN/<chal>-race/solver/solve.py): parents[4] is the project root at every one of these depths."""
import argparse
import json
import os
import struct
import re
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from lib import meta  # noqa: E402
from lib.common import (_zip_open, _zip_read, container_by_sha, delivery_missing, find_artifact,  # noqa: E402
                        find_artifact_hinted, group_by_set, iter_files, load_contract, normalize, read_member)

FAST_INDEX = os.environ.get("HCTF_META_FAST_INDEX", "1") != "0"   # per-process member index (0 = find_artifact only)

_cache = {}
_index = {}
_ROOT = None   # artifacts dir of the running _solve_pairs (synthesis fields read sibling members)


def _once(load):
    memo = []
    return lambda: memo[0] if memo else (memo.append(load()) or memo[0])


def _entries(root):
    """[(name, parent, loader)] of every file under root and every (nested) zip member, in find_artifact's order, built
    ONCE per process; a member is decompressed only when it is a zip (2-byte peek) or asked for. find_artifact re-walks
    and inflates every member per question: D9 Mastery (65 ids, 5 sets) spent 0.9 of 1.2 s there."""
    root = str(root)
    if root in _index:
        return _index[root]
    out = []

    def walk(name, load, parent, depth, peek):
        load = _once(load)
        out.append((name, parent, load))
        if depth >= 4:
            return
        try:
            if peek() != b"PK":
                return
            z = _zip_open(load())
        except Exception:  # noqa: BLE001 - unreadable member: a leaf
            return
        if z is None:
            return
        for n in z.namelist():
            if n.endswith("/"):
                continue

            def pk(z=z, n=n):
                try:
                    with z.open(n) as f:
                        return f.read(2)
                except Exception:  # noqa: BLE001 - encrypted: the password-aware full read
                    return _zip_read(z, n)[:2]
            walk(Path(n).name, (lambda z=z, n=n: _zip_read(z, n)), name, depth + 1, pk)

    for p in iter_files(root):
        walk(p.name, p.read_bytes, None, 0, (lambda p=p: p.open("rb").read(2)))
    _index[root] = out
    return out


def _fast_member(root, artifact):
    """'container -> member' bytes via the per-process index (same precedence as lib.common.find_artifact: a top-level
    file named like the container, then the member whose parent is the container, then any same-named member).
    None -> fall back to find_artifact (odd shapes)."""
    container, _, member = (x.strip() for x in artifact.partition("->"))
    if not member:
        return None
    cbase = Path(container).name
    for p in iter_files(root):
        if p.name in (artifact, container, cbase):
            if not zipfile.is_zipfile(p):
                return None
            try:
                return read_member(p, member)
            except KeyError:
                continue
    target, loose = Path(member).name, None
    for name, parent, load in _entries(root):
        if name != target:
            continue
        if parent == cbase:
            return load()
        loose = loose or load
    return loose() if loose else None


def artifact_bytes(root, contract, artifact, hint=""):
    """Bytes for a question's `artifact` string (cached per artifact): sha256 pairing first (same-named per-set
    deliveries), then by name; a member the question names but the archive lacks -> the member matching `hint`."""
    key = (artifact, hint)
    if key in _cache:
        return _cache[key]
    container, _, member = (x.strip() for x in artifact.partition("->"))
    data = None
    p = container_by_sha(root, contract, container)
    if p is not None and not member:
        data = p.read_bytes()
    elif not delivery_missing(root, contract, container):
        for cand in (artifact, container.split(": ", 1)[-1] + (f" -> {member}" if member else "")):
            try:
                data = _fast_member(root, cand) if FAST_INDEX else None
                data = data if data is not None else find_artifact(root, cand)
                break
            except (FileNotFoundError, KeyError):
                continue
        if data is None and artifact and hint:
            try:   # stale question text vs the real archive (D2 TT: question says roster.csv, the zip holds readme.exe)
                data = find_artifact_hinted(root, artifact, hint)[0]
            except (FileNotFoundError, KeyError):
                pass
    _cache[key] = data
    return data


def _hint(answer_id):
    tail = re.sub(r"^(?:set|slot)[._-]?\d+[._-]", "", answer_id).split(".")[-1]
    return re.split(r"-(?:magic|sha256|sha1|md5|size|filename|text|d\d\d)\b", tail)[0]


_WAV_TAGS = {0x0002: "adpcm_ms", 0x0006: "pcm_alaw", 0x0007: "pcm_mulaw", 0x0011: "adpcm_ima_wav",
             0x0031: "gsm_ms", 0x0050: "mp2", 0x0055: "mp3", 0x0092: "ac3", 0x00FF: "aac", 0x1610: "aac",
             0x2000: "ac3", 0x2001: "dts", 0xF1AC: "flac", 0x0161: "wmav2", 0x0160: "wmav1", 0x0162: "wmapro"}


def _pcm_name(tag, bits, be=False, unsigned8=True):
    e = "be" if be else "le"
    if tag == 3:
        return "pcm_f%d%s" % (bits or 32, e)
    if bits == 8 and unsigned8:
        return "pcm_u8"
    if bits == 8:
        return "pcm_s8"
    return "pcm_s%d%s" % (bits or 16, e)


def _riff_codec(data):
    be = data[:4] == b"RIFX"
    en = ">" if be else "<"
    i = 12
    while i + 8 <= len(data):
        cid, ln = data[i:i + 4], struct.unpack(en + "I", data[i + 4:i + 8])[0]
        if cid == b"fmt ":
            body = data[i + 8:i + 8 + ln]
            tag, = struct.unpack(en + "H", body[:2])
            bits = struct.unpack(en + "H", body[14:16])[0] if len(body) >= 16 else 16
            if tag == 0xFFFE and len(body) >= 40:  # WAVE_FORMAT_EXTENSIBLE: SubFormat GUID's first u16
                tag = struct.unpack(en + "H", body[24:26])[0]
            if tag in (1, 3):
                return _pcm_name(tag, bits, be)
            return _WAV_TAGS.get(tag)
        i += 8 + ln + (ln & 1)
    return None


def _aiff_codec(data):
    aifc = data[8:12] == b"AIFC"
    i = 12
    while i + 8 <= len(data):
        cid, ln = data[i:i + 4], struct.unpack(">I", data[i + 4:i + 8])[0]
        if cid == b"COMM":
            bits = struct.unpack(">H", data[i + 14:i + 16])[0]
            comp = data[i + 26:i + 30] if aifc else b"NONE"
            m = {b"NONE": _pcm_name(1, bits, True, False), b"twos": _pcm_name(1, bits, True, False),
                 b"sowt": _pcm_name(1, bits, False, False), b"fl32": "pcm_f32be", b"FL32": "pcm_f32be",
                 b"fl64": "pcm_f64be", b"alaw": "pcm_alaw", b"ulaw": "pcm_mulaw", b"ima4": "adpcm_ima_qt"}
            return m.get(comp, comp.decode("latin-1").strip() or None)
        i += 8 + ln + (ln & 1)
    return None


def _mpeg_audio_codec(data):
    i = 0
    if data[:3] == b"ID3" and len(data) > 10:
        sz = data[6:10]
        i = 10 + ((sz[0] << 21) | (sz[1] << 14) | (sz[2] << 7) | sz[3])
    for j in range(i, min(len(data) - 1, i + 65536)):
        if data[j] == 0xFF and (data[j + 1] & 0xE0) == 0xE0:
            if (data[j + 1] & 0x06) == 0:  # layer bits 00 = ADTS AAC
                return "aac" if (data[j + 1] & 0xF6) == 0xF0 else None
            return {1: "mp3", 2: "mp2", 3: "mp1"}.get((data[j + 1] >> 1) & 3)
    return None


def _audio_codec(data):
    """ffprobe-style codec_name of the first audio stream, from the container header bytes."""
    if data[:4] in (b"RIFF", b"RIFX", b"RF64") and data[8:12] == b"WAVE":
        return _riff_codec(data)
    if data[:4] == b"FORM" and data[8:12] in (b"AIFF", b"AIFC"):
        return _aiff_codec(data)
    if data[:4] == b"fLaC":
        return "flac"
    if data[:4] == b"OggS":
        head = data[28:64]
        for sig, n in ((b"OpusHead", "opus"), (b"\x01vorbis", "vorbis"), (b"\x7fFLAC", "flac"), (b"Speex", "speex")):
            if head.startswith(sig):
                return n
        return None
    if data[:6] == b"#!AMR\n":
        return "amr_nb"
    if data[:9] == b"#!AMR-WB\n":
        return "amr_wb"
    if data[:4] == b".snd":
        enc = struct.unpack(">I", data[12:16])[0]
        return {1: "pcm_mulaw", 2: "pcm_s8", 3: "pcm_s16be", 4: "pcm_s24be", 5: "pcm_s32be", 6: "pcm_f32be",
                7: "pcm_f64be", 27: "pcm_alaw"}.get(enc)
    if data[4:8] == b"ftyp":
        for sig, n in ((b"mp4a", "aac"), (b"alac", "alac"), (b"Opus", "opus"), (b"fLaC", "flac"),
                       (b"ac-3", "ac3"), (b"ec-3", "eac3"), (b"samr", "amr_nb"), (b"sawb", "amr_wb")):
            k = data.find(b"stsd")
            if k >= 0 and data.find(sig, k, k + 64) >= 0:
                return n
        return None
    if data[:4] == b"\x1a\x45\xdf\xa3":
        for sig, n in ((b"A_OPUS", "opus"), (b"A_VORBIS", "vorbis"), (b"A_AAC", "aac"), (b"A_FLAC", "flac"),
                       (b"A_MPEG/L3", "mp3"), (b"A_AC3", "ac3"), (b"A_PCM/INT/LIT", "pcm_s16le")):
            if sig in data[:65536]:
                return n
        return None
    return _mpeg_audio_codec(data)


def local_answer(answer_id, question, data, contract):
    """TODAY's new field (the worker adds it here; None = not today's). Derive it from `data`; never hard-code."""
    aid = answer_id.lower()
    qt = str(question.get("question", "")).lower() if isinstance(question, dict) else ""
    sm = re.search(r"synthesis-(md5|sha1|sha256|sha512)-order$", aid)
    if sm:   # D15+ synthesis: the `Files: [...]` siblings of the artifact's own container, ordered by digest
        if _ROOT is None:
            return None
        from lib.meta.synthesis import digest_order
        container = ((question or {}).get("artifact") or "").partition("->")[0].strip()
        return digest_order(question, lambda n: artifact_bytes(
            _ROOT, contract, f"{container} -> {n}" if container else n, n), sm.group(1))
    if aid.endswith("audio-codec-name") or "audio_codec_name" in qt:
        try:
            return _audio_codec(data) if data else None
        except Exception:
            return None
    return None


def answer(answer_id, question, data, contract):
    v = local_answer(answer_id, question, data, contract)
    if v is not None:
        return v
    v, _tier = meta.answer(answer_id, question, data)
    return v


def _past_deadline():
    """The timed runner's HCTF_SOLVE_DEADLINE (epoch) has passed: print the answers found so far instead."""
    try:
        return time.time() > float(os.environ["HCTF_SOLVE_DEADLINE"])
    except (KeyError, ValueError):
        return False


def _solve_pairs(job):
    """Answer one group of (answer_id, question) pairs -- a whole Mastery set, or the whole contract."""
    global _ROOT
    root, contract, pairs = job
    _ROOT = root
    out = {}
    for aid, q in pairs:
        if _past_deadline():
            break
        data = artifact_bytes(root, contract, q.get("artifact") or "", _hint(aid))
        try:
            v = answer(aid, q, data, contract)
        except Exception as e:  # noqa: BLE001 - one bad field must not sink the other answers
            print(f"{aid}: {e!r}", file=sys.stderr)
            v = None
        if v is not None:
            out[aid] = normalize(v, q)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    contract, pairs = load_contract(a.contract)
    groups = group_by_set(pairs)
    out = {}
    if len(groups) >= 2 and os.environ.get("HCTF_SOLVER_PARALLEL", "1") != "0":
        # Mastery: every set runs inside ONE clock -- one forked process per set. Same results as the sequential loop.
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        try:
            with ProcessPoolExecutor(max_workers=min(len(groups), os.cpu_count() or 2),
                                     mp_context=mp.get_context("fork")) as ex:
                for part in ex.map(_solve_pairs, [(a.artifacts, contract, g) for g in groups.values()]):
                    out.update(part)
        except Exception as e:  # noqa: BLE001 - never lose a solve to the pool: fall back to sequential
            print(f"parallel sets failed ({e!r}); sequential", file=sys.stderr)
            out = _solve_pairs((a.artifacts, contract, pairs))
    else:
        out = _solve_pairs((a.artifacts, contract, pairs))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
