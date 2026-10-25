"""Independent oracle for the unityfs_* fixtures: UnityPy's BundleFile parser (pip UnityPy, installed under
tools/unitypy) reads the bundle's nodes; the descriptor hex in a node is decoded to the plan, else 'none'.
Usage: PYTHONPATH=tools/unitypy python3 unityfs_oracle.py <fixture.json>"""
import base64
import json
import re
import sys

from UnityPy.files import BundleFile
from UnityPy.streams import EndianBinaryReader

fx = json.load(open(sys.argv[1]))
found = "none"
try:
    bf = BundleFile(EndianBinaryReader(base64.b64decode(fx["material"])), None)
    for name, f in bf.files.items():
        r = getattr(f, "reader", f)            # node parsed as SerializedFile or kept raw: its byte stream
        data = r.bytes
        for h in re.findall(rb"[0-9a-f]{40,}", bytes(data)):
            p = bytes.fromhex(h.decode()).decode()
            if p.startswith("v=3|"):
                found = p
except Exception as e:  # noqa: BLE001
    found = f"none ({type(e).__name__})"
print(found)
