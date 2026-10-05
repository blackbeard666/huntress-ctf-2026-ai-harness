#!/usr/bin/env python3
"""Chunk Norris: PNG structure facts (png.<field>) of the named archive member, parsed by walking its chunks.

The declared geometry lives in IHDR (width, height, bit depth, colour type, interlace); file names and rendering can
lie. GM-confirmed form for png.ihdr_dimensions_pixels: '<width>x<height>' (e.g. 269x153). The "structural passenger"
is any non-standard chunk or bytes trailing IEND; those fields are answered best-effort."""
import argparse, json, re, struct, sys, zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from lib.common import load_contract, find_artifact_hinted, normalize
from lib.knowledge import BOOL, PNG_DIMENSIONS_FMT

SIG = b"\x89PNG\r\n\x1a\n"
STANDARD = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"cHRM", b"gAMA", b"iCCP", b"sBIT", b"sRGB", b"cICP",
            b"mDCv", b"cLLi", b"tEXt", b"zTXt", b"iTXt", b"bKGD", b"hIST", b"pHYs", b"sPLT", b"eXIf", b"tIME",
            b"acTL", b"fcTL", b"fdAT"}
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


def log(*a):
    print(*a, file=sys.stderr)


def chunks(data):
    """Return ([(type, payload, crc_ok, offset)], trailing_bytes_after_IEND), walking declared lengths."""
    i = data.find(SIG)
    if i < 0:
        raise ValueError(f"not a PNG (head {data[:8].hex()})")
    i += 8
    out = []
    while i + 12 <= len(data):
        (ln,) = struct.unpack(">I", data[i:i + 4])
        typ = data[i + 4:i + 8]
        body = data[i + 8:i + 8 + ln]
        (crc,) = struct.unpack(">I", data[i + 8 + ln:i + 12 + ln].ljust(4, b"\0"))
        out.append((typ, body, zlib.crc32(typ + body) == crc, i))
        i += 12 + ln
        if typ == b"IEND":
            break
    return out, data[i:]


def ihdr(cs):
    for typ, body, _, _ in cs:
        if typ == b"IHDR" and len(body) >= 13:
            w, h, bd, ct, cm, fm, il = struct.unpack(">IIBBBBB", body[:13])
            return {"width": w, "height": h, "bit_depth": bd, "color_type": ct, "interlace": il}
    return None


def expected_raw(hd):
    bpp = CHANNELS.get(hd["color_type"], 1) * hd["bit_depth"]
    return hd["height"] * (1 + (hd["width"] * bpp + 7) // 8)


def inflated_len(cs):
    try:
        return len(zlib.decompress(b"".join(b for t, b, _, _ in cs if t == b"IDAT")))
    except zlib.error:
        return None


def passengers(cs, trailer):
    extra = [t.decode("latin-1") for t, *_ in cs if t not in STANDARD]
    if trailer.strip(b"\0"):
        extra.append("trailing_data")
    return extra


def field_of(q, aid):
    m = re.search(r"\bpng\.([a-z0-9_]+)", q.get("question", ""), re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"-png-\d+-png-([a-z0-9-]+)$", aid.split(".")[-1])
    return m.group(1).replace("-", "_") if m else None


def answer(field, data):
    cs, trailer = chunks(data)
    hd = ihdr(cs)
    if field in ("ihdr_dimensions_pixels", "dimensions_pixels", "ihdr_dimensions"):
        return PNG_DIMENSIONS_FMT.format(**hd) if hd else "none"
    if field in ("ihdr_width", "ihdr_width_pixels", "width_pixels", "width"):
        return str(hd["width"]) if hd else "none"
    if field in ("ihdr_height", "ihdr_height_pixels", "height_pixels", "height"):
        return str(hd["height"]) if hd else "none"
    if field in ("ihdr_bit_depth", "bit_depth"):
        return str(hd["bit_depth"]) if hd else "none"
    if field in ("ihdr_color_type", "color_type"):
        return str(hd["color_type"]) if hd else "none"
    if field in ("chunk_count",):
        return str(len(cs))
    if field in ("unexpected_chunk", "extra_chunk", "passenger_chunk", "unknown_chunk", "structural_passenger"):
        p = passengers(cs, trailer)
        return p[0] if p else "none"
    if field in ("has_passenger", "has_unexpected_chunk", "passenger_present", "has_trailing_data"):
        return BOOL[bool(passengers(cs, trailer))]
    if field in ("trailing_bytes", "trailing_data_bytes", "bytes_after_iend"):
        return str(len(trailer))
    if field in ("geometry_valid", "geometry_matches", "ihdr_matches_idat"):
        return BOOL[bool(hd) and inflated_len(cs) == expected_raw(hd)]
    if field in ("crc_valid", "crcs_valid"):
        return BOOL[all(ok for *_, ok, _ in cs)]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--artifacts", required=True)
    a = ap.parse_args()
    _, pairs = load_contract(a.contract)
    out = {}
    for aid, q in pairs:
        if not q or not q.get("artifact"):
            continue
        field = field_of(q, aid)
        if not field:
            continue
        try:
            fm = re.search(r"for\s+(\S+?)\.?$", q.get("question", "").strip())
            hint = fm.group(1) if fm else aid.split(".")[-1].split("-png-")[0]
            data, src = find_artifact_hinted(a.artifacts, q["artifact"], hint)
            v = answer(field, data)
        except Exception as e:
            log(f"{aid}: {e}")
            continue
        if v is None:
            log(f"{aid}: unrecognized field png.{field}, skipped")
            continue
        out[aid] = normalize(v, q)
        cs, trailer = chunks(data)
        hd = ihdr(cs)
        log(f"{aid}: {src} ({len(data)} bytes) ihdr={hd} chunks={[c[0].decode('latin-1') for c in cs]} "
            f"raw={inflated_len(cs)}/{expected_raw(hd) if hd else None} passengers={passengers(cs, trailer)} "
            f"png.{field} -> {out[aid]}")
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
