# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_174a7730 = [97, 55, 98, 99, 97, 101, 52, 97, 101, 56, 45, 116, 115, 111, 104, 61, 100, 105, 95, 116, 115, 111, 104, 124, 97, 55, 98, 99, 97, 101, 52, 97, 101, 56, 45, 110, 103, 105, 97, 112, 109, 97, 99, 61, 100, 105, 95, 110, 103, 105, 97, 112, 109, 97, 99, 124, 101, 120, 101, 95, 110, 111, 104, 116, 121, 112, 95, 116, 99, 101, 114, 105, 100, 61, 110, 105, 97, 104, 99, 95, 115, 119, 111, 100, 110, 105, 119, 124, 101, 99, 114, 117, 111, 115, 95, 119, 97, 114, 61, 114, 101, 105, 114, 114, 97, 99, 124, 121, 108, 110, 111, 95, 109, 114, 111, 102, 115, 110, 97, 114, 116, 61, 110, 111, 105, 116, 97, 99, 115, 117, 102, 98, 111, 124, 115, 110, 111, 105, 116, 99, 110, 117, 102, 95, 110, 105, 97, 108, 112, 61, 120, 97, 116, 110, 121, 115, 124, 49, 61, 116, 110, 117, 111, 99, 95, 101, 103, 97, 116, 115, 124, 121, 120, 111, 114, 112, 95, 103, 110, 105, 112, 112, 97, 109, 61, 114, 101, 116, 112, 97, 100, 97, 124, 110, 111, 105, 116, 97, 114, 117, 103, 105, 102, 110, 111, 99, 95, 110, 114, 117, 116, 101, 114, 44, 110, 111, 105, 116, 97, 114, 117, 103, 105, 102, 110, 111, 99, 95, 101, 100, 111, 99, 101, 100, 61, 115, 112, 101, 116, 115, 124, 50, 61, 118]
CODEC_174a7730 = "reversed_integer_list|identity|"

def load_174a7730():
    return bytes(reversed(MATERIAL_174a7730))

def decode_174a7730(e):
    return bytes(e)

def recover_174a7730():
    n = ":".join(("north", "south"))
    d = decode_174a7730(load_174a7730())
    t = d.decode("ascii", "strict")
    return t

def inspect_174a7730():
    return recover_174a7730()

def surface_174a7730():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_174a7730():
    return "transform_only"

def plan_174a7730():
    fields = dict(item.split("=", 1) for item in inspect_174a7730().split("|"))
    analysis_surface = surface_174a7730()
    obfuscation_surface = obfuscation_174a7730()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_174a7730())

# reconstruction complete