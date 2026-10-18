# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b7bdf972 = (50, 121, 118, 56, 55, 48, 33, 52, 55, 121, 37, 39, 53, 49, 45, 54, 33, 27, 54, 33, 41, 43, 48, 33, 104, 32, 45, 55, 52, 37, 48, 39, 44, 27, 41, 33, 41, 43, 54, 61, 56, 37, 32, 37, 52, 48, 33, 54, 121, 44, 48, 48, 52, 27, 39, 40, 45, 33, 42, 48, 27, 41, 33, 41, 43, 54, 61, 56, 55, 48, 37, 35, 33, 27, 39, 43, 49, 42, 48, 121, 117, 56, 55, 61, 42, 48, 37, 60, 121, 40, 45, 55, 48, 27, 39, 43, 41, 52, 54, 33, 44, 33, 42, 55, 45, 43, 42, 56, 43, 38, 34, 49, 55, 39, 37, 48, 45, 43, 42, 121, 34, 43, 54, 41, 37, 48, 27, 41, 37, 52, 56, 39, 37, 54, 54, 45, 33, 54, 121, 51, 44, 33, 33, 40, 27, 37, 54, 39, 44, 45, 50, 33, 56, 51, 45, 42, 32, 43, 51, 55, 27, 39, 44, 37, 45, 42, 121, 52, 43, 51, 33, 54, 55, 44, 33, 40, 40, 27, 48, 43, 27, 52, 61, 48, 44, 43, 42, 56, 39, 37, 41, 52, 37, 45, 35, 42, 27, 45, 32, 121, 39, 37, 41, 52, 37, 45, 35, 42, 105, 119, 119, 125, 124, 38, 33, 117, 33, 125, 32, 56, 49, 54, 40, 121, 44, 48, 48, 52, 55, 126, 107, 107, 119, 119, 125, 124, 38, 33, 117, 33, 125, 32, 106, 33, 60, 37, 41, 52, 40, 33, 106, 45, 42, 50, 37, 40, 45, 32, 107, 114, 118, 112, 112, 125, 32, 117, 119, 106, 52, 61, 56, 49, 55, 33, 54, 27, 37, 35, 33, 42, 48, 121, 12, 49, 42, 48, 54, 33, 55, 55, 20, 61, 48, 44, 43, 42, 107, 119, 119, 125, 124, 38, 33, 117, 33, 125, 32,)
CODEC_b7bdf972 = "integer_tuple|single_byte_xor|44"

def load_b7bdf972():
    return bytes(MATERIAL_b7bdf972)

def decode_b7bdf972(item1):
    return bytes(value ^ 68 for value in item1)

def recover_b7bdf972():
    item4 = ":".join(("north", "south"))
    item7 = "decode"
    while item7 != "done":
        if item7 == "decode":
            item2 = decode_b7bdf972(load_b7bdf972())
            item7 = "done"
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_b7bdf972():
    return recover_b7bdf972()

def surface_b7bdf972():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_b7bdf972():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_b7bdf972():
    fields = dict(item.split("=", 1) for item in inspect_b7bdf972().split("|"))
    analysis_surface = surface_b7bdf972()
    obfuscation_surface = obfuscation_b7bdf972()
    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b7bdf972())

# reconstruction complete