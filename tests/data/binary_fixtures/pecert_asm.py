"""Fixture writer (pefile + openssl DER): python3 pecert_asm.py <in.exe> <pkcs7.der> <out.bin> <mode> [cfg-json]
mode tail = WIN_CERTIFICATE then HCFG after it; pad = HCFG inside the certificate's 8-byte padding (inside dwLength),
stale checksum; ovl = unsigned, HCFG raw overlay (decoy for the cert fields); badptr = security dir past EOF (decoy)."""
import json, struct, sys, zlib, pefile
exe, der, out, mode = sys.argv[1:5]
cfg = json.dumps(json.loads(sys.argv[5]), separators=(",", ":")).encode() if len(sys.argv) > 5 else b""
blob = b"HCFG" + struct.pack("<BBHI", 1, 0, len(cfg), zlib.crc32(cfg)) + cfg if cfg else b""
pe = pefile.PE(exe)
img = bytearray(pe.__data__[:pe.get_overlay_data_start_offset() or len(pe.__data__)])
img += b"\0" * (-len(img) % 8)            # WIN_CERTIFICATE starts 8-aligned
p7 = open(der, "rb").read()
sec = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_SECURITY"]]
coff = len(img)
if mode == "tail":
    body = p7
    cert = struct.pack("<IHH", 8 + len(body), 0x0200, 2) + body
    cert += b"\0" * (-len(cert) % 8)
    tail = cert + blob
    sec.VirtualAddress, sec.Size = coff, len(cert)
elif mode == "pad":
    body = p7 + b"\0" * 3 + blob          # DER, then 'padding' carrying the blob, all inside dwLength
    cert = struct.pack("<IHH", 8 + len(body), 0x0200, 2) + body
    cert += b"\0" * (-len(cert) % 8)
    tail = cert
    sec.VirtualAddress, sec.Size = coff, len(cert)
elif mode == "ovl":
    tail = b"OVL0" + b"\0" * 4 + blob
elif mode == "badptr":
    tail = b"\0" * 64
    sec.VirtualAddress, sec.Size = coff + 0x10000, 0x800
pe.__data__ = bytes(img)                  # header edits only live inside the image bytes
hdr = pe.write()
data = bytearray(hdr[:len(img)]) + (bytes(img[len(hdr):]) if len(hdr) < len(img) else b"") + tail
pe2 = pefile.PE(data=bytes(data))
if mode in ("tail", "ovl"):
    pe2.OPTIONAL_HEADER.CheckSum = pe2.generate_checksum()
    data = bytearray(pe2.write())
else:
    pe2.OPTIONAL_HEADER.CheckSum = 0x1234   # stale / bogus
    data = bytearray(pe2.write())
open(out, "wb").write(data)
