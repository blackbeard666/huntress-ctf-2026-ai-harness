# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_bf4718f9 = "14,95,13,9,95,14,88,13,10,92,65,24,31,3,4,81,8,5,51,24,31,3,4,16,14,95,13,9,95,14,88,13,10,92,65,2,11,5,13,28,1,13,15,81,8,5,51,2,11,5,13,28,1,13,15,16,9,20,9,51,2,3,4,24,21,28,51,24,15,9,30,5,8,81,2,5,13,4,15,51,31,27,3,8,2,5,27,16,9,15,30,25,3,31,51,27,13,30,81,30,9,5,30,30,13,15,16,21,0,2,3,51,1,30,3,10,31,2,13,30,24,81,2,3,5,24,13,15,31,25,10,14,3,16,31,2,3,5,24,15,2,25,10,51,2,5,13,0,28,81,20,13,24,2,21,31,16,93,81,24,2,25,3,15,51,9,11,13,24,31,16,9,15,13,28,31,9,1,13,2,51,9,31,30,13,28,11,30,13,81,30,9,24,28,13,8,13,16,2,3,5,24,13,30,25,11,5,10,2,3,15,51,2,30,25,24,9,30,64,2,3,5,24,13,30,25,11,5,10,2,3,15,51,9,8,3,15,9,8,81,31,28,9,24,31,16,94,81,26"
CODEC_bf4718f9 = "decimal_csv|reverse_then_xor|6c"

def load_bf4718f9():
    return bytes(int(item) for item in MATERIAL_bf4718f9.split(","))

def decode_bf4718f9(e):
    return bytes(value ^ 108 for value in reversed(e))

def recover_bf4718f9():
    n = (3, 5, 8, 13)[1:3]
    _pass = 0
    while _pass < 1:
        d = decode_bf4718f9(load_bf4718f9())
        _pass += 1
    t = d.decode("ascii", "strict")
    return t

def inspect_bf4718f9():
    return recover_bf4718f9()

def surface_bf4718f9():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_bf4718f9():
    return "transform_only"

def plan_bf4718f9():
    fields = dict(item.split("=", 1) for item in inspect_bf4718f9().split("|"))
    analysis_surface = surface_bf4718f9()
    obfuscation_surface = obfuscation_bf4718f9()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_bf4718f9())

# reconstruction complete