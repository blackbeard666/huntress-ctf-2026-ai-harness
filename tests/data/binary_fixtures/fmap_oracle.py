"""Independent oracle for the fmap_* fixtures (file map / section-slack caves): covered ranges from a THIRD-PARTY reader
(pyelftools: ELF header, program header table, non-NULL/NOBITS sections, section header table, PT_LOAD file bytes for
the image end; pefile: headers through the section table, section raw data, VirtualSize slack (segment = its section), get_overlay_data_start_
offset), gaps = the complement inside the image end, crc-valid HCFG located with bytes.find + zlib.crc32. Prints the
expected file_map_facts subset as JSON (null = not an ELF/PE). usage: python3 fmap_oracle.py file.bin"""
import io, json, struct, sys, zlib


def valid(b, o):
    if b[o:o + 4] != b"HCFG" or len(b) < o + 12:
        return False
    _, k, n, c = struct.unpack_from("<BBHI", b, o + 4)
    p = bytes(x ^ k for x in b[o + 12:o + 12 + n])
    return n > 0 and len(p) == n and zlib.crc32(p) == c


def elf(b):
    from elftools.elf.elffile import ELFFile
    f = ELFFile(io.BytesIO(b))
    h = f.header
    cov = [(0, h["e_ehsize"])]
    if h["e_phnum"]:
        cov.append((h["e_phoff"], h["e_phoff"] + h["e_phnum"] * h["e_phentsize"]))
    if h["e_shnum"]:
        cov.append((h["e_shoff"], h["e_shoff"] + h["e_shnum"] * h["e_shentsize"]))
    for s in f.iter_sections():
        if s["sh_type"] not in ("SHT_NULL", "SHT_NOBITS") and s["sh_size"]:
            cov.append((s["sh_offset"], s["sh_offset"] + s["sh_size"]))
    loads = [(p["p_offset"], p["p_filesz"]) for p in f.iter_segments() if p["p_type"] == "PT_LOAD"]
    segs = [("LOAD[%d]" % i, o, n) for i, (o, n) in enumerate(loads) if n]
    end = max([e for _, e in cov] + [p["p_offset"] + p["p_filesz"] for p in f.iter_segments()])
    return cov, min(end, len(b)), segs, []


def pe(b):
    import pefile
    p = pefile.PE(data=b)
    st = p.sections[0].get_file_offset() if p.sections else p.OPTIONAL_HEADER.get_file_offset()
    cov = [(0, st + 40 * len(p.sections))]
    slack = []
    for s in p.sections:
        if s.SizeOfRawData:
            cov.append((s.PointerToRawData, s.PointerToRawData + s.SizeOfRawData))
            if 0 < s.Misc_VirtualSize < s.SizeOfRawData:
                slack.append((s.PointerToRawData + s.Misc_VirtualSize, s.PointerToRawData + s.SizeOfRawData,
                              s.Name.rstrip(b"\0").decode()))
    ov = p.get_overlay_data_start_offset()
    return cov, ov if ov is not None else len(b), [], slack


def main(path):
    b = open(path, "rb").read()
    if b[:4] == b"\x7fELF":
        cov, end, segs, slack = elf(b)
    elif b[:2] == b"MZ":
        cov, end, segs, slack = pe(b)
    else:
        return None
    mark = bytearray(end)
    for s, e in cov:
        mark[s:min(e, end)] = b"\1" * (min(e, end) - s) if s < end else b""
    gaps, i = [], 0
    while i < end:
        if not mark[i]:
            j = i
            while j < end and not mark[j]:
                j += 1
            gaps.append((i, j))
            i = j
        else:
            i += 1
    rows = []
    for s, e, *sec in [g + (None,) for g in gaps] + slack:   # slack: the section whose raw tail holds it
        seg = sec[0] or next((n for n, o, z in segs if o <= s < o + z), None)
        rows.append({"offset": s, "size": e - s, "nonzero": sum(1 for x in b[s:e] if x), "segment": seg})
    nz = [r for r in rows if r["nonzero"]]
    cave = max(nz, key=lambda r: (r["nonzero"], r["size"], -r["offset"])) if nz else None
    hoff = next((o for r in sorted(rows, key=lambda r: r["offset"]) for o in range(r["offset"], r["offset"] + r["size"])
                 if valid(b, o)), None)
    return {"gap_count": len(gaps), "slack_count": len(slack), "total_gap_bytes": sum(r["size"] for r in rows),
            "image_end": end, "gaps_offsets_sizes": [[r["offset"], r["size"]] for r in rows],
            "cave_offset": cave["offset"] if cave else "none", "cave_size": cave["size"] if cave else "none",
            "cave_segment": (cave["segment"] or "none") if cave else "none",
            "hcfg_gap_offset": hoff if hoff is not None else "none",
            "gap_hcfg_storage": "raw" if hoff is not None else "none"}


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1])))
