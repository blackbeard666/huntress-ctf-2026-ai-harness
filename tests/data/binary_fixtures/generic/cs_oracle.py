"""Independent reader for the cross-group fixtures: zipfile + its own record decoder (no lib.binary). Prints JSON
facts: per-day consensus campaign (majority), configless members, distinct counts, sorted/ordered sha256 joins."""
import hashlib, json, re, struct, sys, zipfile, zlib
z = zipfile.ZipFile(sys.argv[1])
per, nocfg, elf = {}, [], 0
for i in z.infolist():
    b = z.read(i)
    elf += b[:4] == b"\x7fELF"
    c = None
    for mg in (b"HCFG", b"HGRF"):
        o = b.rfind(mg)
        if o >= 0:
            v, k, n, crc = struct.unpack_from("<BBHI", b, o + 4)
            p = bytes(x ^ k for x in b[o + 12:o + 12 + n])
            if zlib.crc32(p) == crc:
                j = json.loads(p)
                c = j.get("config", j)
    day = re.match(r"d(\d\d)--", i.filename).group(1)
    per.setdefault(day, []).append(c and c["campaign"])
    if c is None:
        nocfg.append(i.filename)
cons = {}
for d, vs in sorted(per.items()):
    vs = [v for v in vs if v]
    if vs:
        cons[d] = max(set(vs), key=vs.count)
camps = list(cons.values())
H = lambda s: hashlib.sha256(s.encode()).hexdigest()
print(json.dumps({"consensus": cons, "configless": nocfg, "configless_count": len(nocfg),
                  "distinct_campaign_count": len(set(camps)),
                  "distinct_member_campaign_count": len({v for vs in per.values() for v in vs if v}),
                  "sorted_lf_sha256": H("\n".join(sorted(camps))), "ordered_colon_sha256": H(":".join(camps)),
                  "shared_groups": [d for d, v in cons.items() if camps.count(v) > 1], "elf_count": elf}, indent=1))
