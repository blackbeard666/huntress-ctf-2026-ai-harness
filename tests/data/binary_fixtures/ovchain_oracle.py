"""Independent reader for the ovchain_* fixtures (no lib.* code): pyelftools image end, re.finditer magic hits,
hashlib sha256 check of the D19 PK19 header, inverse transform ror3(b^k2)^k1, zlib inflate, json of the HCFG record.
usage (repo root): python3 -I tests/data/binary_fixtures/ovchain_oracle.py <file.bin>  -> expected json on stdout"""
import hashlib, io, json, re, struct, sys, zlib
from elftools.elf.elffile import ELFFile


def image_end(b):
    if b[:4] != b"\x7fELF":
        return 0
    e = ELFFile(io.BytesIO(b))
    h = e.header
    end = max(h.e_ehsize, h.e_phoff + h.e_phnum * h.e_phentsize, h.e_shoff + h.e_shnum * h.e_shentsize)
    for s in e.iter_segments():
        end = max(end, s["p_offset"] + s["p_filesz"])
    for s in e.iter_sections():
        if s["sh_type"] != "SHT_NOBITS":
            end = max(end, s["sh_offset"] + s["sh_size"])
    return end


def verified(b, o):
    n = struct.unpack("<I", b[o + 8:o + 12])[0]
    if o + 44 + n > len(b):
        return None
    k1, k2 = b[o + 5], b[o + 6]
    p = bytes((((x ^ k2) >> 3 | (x ^ k2) << 5) & 255) ^ k1 for x in b[o + 44:o + 44 + n])
    return p if hashlib.sha256(p).digest() == b[o + 12:o + 44] else None


b = open(sys.argv[1], "rb").read()
outer, buf, depth, kinds, layers, decoys, final = b, b, 0, [], 0, [], None
while depth <= 4:
    hits = [m.start() for m in re.finditer(b"(?=PK19|RS20)", buf)]
    lo = 0 if (depth and buf[:4] == b"PK19") else image_end(buf)
    good = [(o, p) for o in hits if o >= lo for p in [verified(buf, o)] if p is not None]
    if depth == 0:
        decoys = [o for o in hits if not good or o != good[-1][0]]
        first = good[-1][0] if good else None
    if not good:
        try:
            d = zlib.decompressobj(); z = d.decompress(buf)
            if depth and d.eof:
                kinds.append("zlib"); buf, depth = z, depth + 1; continue
        except zlib.error:
            pass
        break
    o, p = good[-1]
    if depth and buf[:4] != b"PK19":
        kinds.append("elf" if buf[:4] == b"\x7fELF" else "blob")
    kinds.append("overlay"); layers += 1; final = (o, depth); buf, depth = p, depth + 1
exp = {"layer_count": layers, "decoy_offsets": decoys, "decoy_count": len(decoys)}
if layers:
    key, n = buf[5], struct.unpack("<H", buf[6:8])[0]
    exp.update({"overlay_offset": first, "overlay_size": len(outer) - first, "final_overlay_offset": final[0],
                "final_overlay_depth": final[1], "final_overlay_magic": "PK19", "payload_kind": ">".join(kinds),
                "hcfg_offset": 0, "config": json.loads(bytes(x ^ key for x in buf[12:12 + n])),
                "unpacked_sha256": hashlib.sha256(buf).hexdigest()})
else:
    exp.update(dict.fromkeys(("overlay_offset", "final_overlay_offset", "payload_kind", "config"), "none"))
print(json.dumps(exp))
