#!/usr/bin/env python3
"""Picture This: JPEG structure facts (jpeg.<field>) of the named archive member, parsed from its marker segments.

The true pixel dimensions live in the SOFn frame header (P, Y=height, X=width); file names, EXIF tags and the
extension can lie. GM-confirmed form for jpeg.sof_dimensions_pixels: '<width>x<height>' (e.g. 257x146)."""
import argparse, json, re, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from lib.common import load_contract, find_artifact_hinted, normalize
from lib.knowledge import BOOL, JPEG_DIMENSIONS_FMT

# SOF0..SOF15 minus DHT (C4), JPG (C8), DAC (CC)
SOF = {m for m in range(0xC0, 0xD0) if m not in (0xC4, 0xC8, 0xCC)}


def log(*a):
    print(*a, file=sys.stderr)


def segments(data):
    """Yield (marker, payload) for each header segment up to SOS/EOI, walking lengths rather than fixed offsets."""
    if data[:2] != b"\xff\xd8":
        raise ValueError(f"not a JPEG (head {data[:4].hex()})")
    i = 2
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            i += 1  # tolerate junk between segments
            continue
        m = data[i + 1]
        if m == 0xFF:  # fill byte
            i += 1
            continue
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:  # standalone markers
            i += 2
            continue
        if m == 0xD9:
            return
        (ln,) = struct.unpack(">H", data[i + 2:i + 4])
        yield m, data[i + 4:i + 2 + ln]
        if m == 0xDA:
            return
        i += 2 + ln


def sof(data):
    for m, p in segments(data):
        if m in SOF and len(p) >= 6:
            prec, h, w, nc = struct.unpack(">BHHB", p[:6])
            return {"marker": m, "precision": prec, "height": h, "width": w, "components": nc}
    return None


def exif_tags(data):
    """IFD0 + ExifIFD tags of the APP1 Exif block as {tag: value} (ints only; enough for dims/orientation)."""
    for m, p in segments(data):
        if m != 0xE1 or not p.startswith(b"Exif\0\0"):
            continue
        t = p[6:]
        e = "<" if t[:2] == b"II" else ">"
        out = {}

        def ifd(off, depth=0):
            if depth > 3 or off + 2 > len(t):
                return
            (n,) = struct.unpack(e + "H", t[off:off + 2])
            for k in range(n):
                ent = t[off + 2 + 12 * k: off + 14 + 12 * k]
                if len(ent) < 12:
                    return
                tag, typ, cnt = struct.unpack(e + "HHI", ent[:8])
                if typ == 3:
                    val = struct.unpack(e + "H", ent[8:10])[0]
                elif typ == 4:
                    val = struct.unpack(e + "I", ent[8:12])[0]
                else:
                    continue
                out.setdefault(tag, val)
                if tag == 0x8769:
                    ifd(val, depth + 1)

        ifd(struct.unpack(e + "I", t[4:8])[0])
        return out
    return {}


def field_of(q, aid):
    m = re.search(r"\bjpeg\.([a-z0-9_]+)", q.get("question", ""), re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"-jpeg-\d+-jpeg-([a-z0-9-]+)$", aid.split(".")[-1])
    return m.group(1).replace("-", "_") if m else None


def answer(field, data):
    f = sof(data)
    ex = exif_tags(data)
    orient = ex.get(0x0112)
    if field in ("sof_dimensions_pixels", "dimensions_pixels", "sof_dimensions"):
        return JPEG_DIMENSIONS_FMT.format(**f) if f else "none"
    if field in ("sof_width", "sof_width_pixels", "width_pixels"):
        return str(f["width"]) if f else "none"
    if field in ("sof_height", "sof_height_pixels", "height_pixels"):
        return str(f["height"]) if f else "none"
    if field in ("sof_components", "components"):
        return str(f["components"]) if f else "none"
    if field in ("sof_precision", "precision", "bits_per_sample"):
        return str(f["precision"]) if f else "none"
    if field in ("exif_orientation", "orientation"):
        return str(orient) if orient else "none"
    if field in ("exif_dimensions_pixels",):
        w, h = ex.get(0xA002) or ex.get(0x0100), ex.get(0xA003) or ex.get(0x0101)
        return f"{w}x{h}" if w and h else "none"
    if field in ("display_dimensions_pixels", "presented_dimensions_pixels", "presentation_dimensions_pixels"):
        if not f:
            return "none"
        w, h = f["width"], f["height"]
        return f"{h}x{w}" if orient in (5, 6, 7, 8) else f"{w}x{h}"
    if field in ("rotated", "orientation_mismatch", "presentation_mismatch"):
        return BOOL[bool(orient and orient != 1)]
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
            hint = fm.group(1) if fm else aid.split(".")[-1].split("-jpeg-")[0]
            data, src = find_artifact_hinted(a.artifacts, q["artifact"], hint)
            v = answer(field, data)
        except Exception as e:
            log(f"{aid}: {e}")
            continue
        if v is None:
            log(f"{aid}: unrecognized field jpeg.{field}, skipped")
            continue
        out[aid] = normalize(v, q)
        log(f"{aid}: {src} ({len(data)} bytes) sof={sof(data)} jpeg.{field} -> {out[aid]}")
    if not out:
        sys.exit("no answers produced")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
