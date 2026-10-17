"""Independent oracle for the dnsf_* fixtures: NO lib.binary. Finds the IL dll each bundle embeds by CONTENT (bytes.find of
the publish's obj/ dll for stored entries; a raw-inflate attempt at every file offset whose output equals that dll for
compressed ones), parses the HCFG header with struct + zlib.crc32, and reads R2R from dnfile/pefile + `file`.
usage: .venv/bin/python -I tests/data/binary_fixtures/dnsf_oracle.py FIXDIR INPUTDIR(sf_il.dll cz_il.dll cs_il.dll cd_il.dll)"""
import base64, json, struct, subprocess, sys, zlib
from pathlib import Path
import dnfile

fx, inp = Path(sys.argv[1]), Path(sys.argv[2])


def blob(b):
    ver, key, n, crc = struct.unpack_from("<BBHI", b, 4)
    body = b[12:12 + n]
    return {"crc_ok": zlib.crc32(body) == crc, "config": json.loads(body) if zlib.crc32(body) == crc else None}


def inflate_at(data, want):
    for o in range(len(data)):
        try:
            d = zlib.decompressobj(-15)
            if d.decompress(data[o:o + 4096], 2) == b"MZ" and d.decompress(data[o + 4096:o + len(want) * 2]) is not None:
                full = zlib.decompressobj(-15).decompress(data[o:])
                if full[:len(want)] == want:
                    return o
        except zlib.error:
            pass
    return None


for name, il in (("singlefile_stored", "sf"), ("bundle_deflate", "cz"), ("bundle_us_b64", "cs"), ("decoy_bundle_badcrc", "cd")):
    data, dll = (fx / f"dnsf_{name}.bin").read_bytes(), (inp / f"{il}_il.dll").read_bytes()
    ftype = subprocess.run(["file", "-b", str(fx / f"dnsf_{name}.bin")], capture_output=True, text=True).stdout.strip()
    stored = data.find(dll)
    if stored >= 0:
        h = dll.find(b"HCFG")
        print(name, "| file:", ftype[:40], "| dll stored @", stored, "| HCFG @", stored + h, blob(dll[h:]))
        continue
    c = inflate_at(data, dll)
    u = dll.find(b"H\0C\0F\0G\0")
    if dll.find(b"HCFG") >= 0:
        h = dll.find(b"HCFG")
        print(name, "| file:", ftype[:40], "| dll deflated @", c, "| HCFG at+", h, blob(dll[h:]))
    else:
        s = dll.find("SENGR".encode("utf-16-le"))
        e = dll.find(b"\0\0", s) + 1
        txt = dll[s:e].decode("utf-16-le")
        print(name, "| file:", ftype[:40], "| dll deflated @", c, "| utf16 base64 @ (inside dll)", s, blob(base64.b64decode(txt)))
for name in ("r2r", "il"):
    p = fx / f"dnsf_{name}.bin"
    d = dnfile.dnPE(str(p))
    st = d.net.struct
    mnh = st.ManagedNativeHeaderRva
    sig = d.get_data(mnh, 4) if mnh else b""
    dll = p.read_bytes()
    h = dll.find(b"HCFG")
    print(name, "| file:", subprocess.run(["file", "-b", str(p)], capture_output=True, text=True).stdout.strip()[:60],
          "| COR flags", hex(st.Flags), "| ManagedNativeHeader", hex(mnh), sig, "| HCFG @", h, blob(dll[h:]) if h >= 0 else None)
