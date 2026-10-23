"""Minimal RPM v3 writer (stdlib struct only): 96-byte lead, signature header (8-byte padded), main header with
NAME/VERSION/RELEASE + one script tag and its *PROG argv. Usage:
  python3 -I pkg_rpm_gen.py out.rpm <script tag> <prog> <body file> [--bad-magic]
Tags: 1023 PREIN, 1024 POSTIN, 1025 PREUN, 1026 POSTUN; prog tag = tag + 62 (1085..1088)."""
import struct
import sys


def header(entries):
    idx, store = b"", b""
    for tag, typ, val in entries:
        if typ == 4:
            while len(store) % 4:
                store += b"\x00"
            off, data, cnt = len(store), struct.pack(">I", val), 1
        elif typ == 8:
            off, data, cnt = len(store), b"".join(v.encode() + b"\x00" for v in val), len(val)
        else:
            off, data, cnt = len(store), val.encode() + b"\x00", 1
        store += data
        idx += struct.pack(">IIII", tag, typ, off, cnt)
    return b"\x8e\xad\xe8\x01\x00\x00\x00\x00" + struct.pack(">II", len(entries), len(store)) + idx + store


out, tag, prog = sys.argv[1], int(sys.argv[2]), sys.argv[3]
with open(sys.argv[4]) as fh:
    body = fh.read()
lead = b"\xed\xab\xee\xdb\x03\x00\x00\x00\x00\x01" + b"huntress-agent-1.0-1".ljust(66, b"\x00") + \
    struct.pack(">HH", 1, 5) + b"\x00" * 16
sig = header([(1000, 4, 0)])
sig += b"\x00" * (-len(sig) % 8)
main = header([(1000, 6, "huntress-agent"), (1001, 6, "1.0"), (1002, 6, "1"), (tag, 6, body),
               (tag + 62, 8, prog.split())])
data = lead + sig + main + b"\x1f\x8b\x08\x00" + b"\x00" * 16
if "--bad-magic" in sys.argv:
    data = b"\xde\xad\xbe\xef" + data[4:]
with open(out, "wb") as fh:
    fh.write(data)
