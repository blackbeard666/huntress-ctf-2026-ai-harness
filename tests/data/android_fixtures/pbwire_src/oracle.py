"""Independent reader: google.protobuf's UnknownFieldSet over an Empty message (no schema, no lib.android).
usage: python3 oracle.py <file> [b64|hex]  -> prints `path wiretype value` per leaf."""
import base64, sys
from google.protobuf import empty_pb2
from google.protobuf.unknown_fields import UnknownFieldSet
raw = open(sys.argv[1], "rb").read()
mode = sys.argv[2] if len(sys.argv) > 2 else ""
if mode == "b64": raw = base64.b64decode(raw.splitlines()[-1])
if mode == "hex": raw = bytes.fromhex(raw.decode().strip())
def walk(b, path):
    m = empty_pb2.Empty(); m.ParseFromString(b)
    for f in UnknownFieldSet(m):
        p = f"{path}.{f.field_number}" if path else str(f.field_number)
        if f.wire_type == 2:
            try:
                sub = empty_pb2.Empty(); sub.ParseFromString(f.data)
                if len(UnknownFieldSet(sub)) and f.data[:1] in (b"\x08", b"\x0a", b"\x10", b"\x12"):
                    walk(f.data, p); continue
            except Exception: pass
            print(p, 2, f.data)
        else:
            print(p, f.wire_type, f.data)
walk(raw, "")
