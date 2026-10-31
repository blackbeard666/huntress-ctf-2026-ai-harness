#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_910531cf = [63, 175, 221, 194, 120, 107, 171, 217, 206, 120, 38, 160, 135, 159, 62, 112, 158, 155, 132, 47, 123, 186, 134, 130, 2, 52, 186, 134, 146, 45, 104, 145, 154, 146, 57, 124, 178, 145, 135, 100, 107, 247, 139, 150, 47, 59, 252, 142, 216, 46, 96, 162, 137, 129, 36, 96, 224, 141, 155, 58, 100, 175, 144, 146, 100, 63, 175, 221, 194, 120, 107, 171, 217, 206, 120, 38, 225, 210, 132, 58, 125, 186, 128, 202, 38, 123, 187, 148, 193, 43, 60, 251, 218, 149, 47, 56, 247, 218, 218, 36, 110, 167, 137, 135, 39, 104, 173, 213, 147, 35, 86, 160, 143, 158, 43, 121, 163, 137, 148, 54, 103, 161, 128, 131, 51, 121, 145, 135, 131, 21, 125, 190, 129, 133, 41, 122, 185, 213, 153, 35, 104, 166, 139, 168, 57, 126, 161, 140, 153, 35, 126, 178, 140, 146, 62, 104, 173, 155, 130, 44, 107, 161, 183, 133, 37, 100, 188, 137, 142, 58, 52, 188, 141, 158, 56, 123, 175, 139, 139, 36, 104, 162, 152, 168, 47, 121, 161, 132, 146, 60, 103, 171, 183, 155, 43, 97, 189, 154, 150, 39, 52, 160, 135, 158, 62, 104, 173, 155, 130, 44, 107, 161, 148, 153, 37, 96, 189, 155, 146, 56, 121, 182, 141, 168, 36, 102, 167, 156, 135, 47, 106, 182, 141, 202, 50, 104, 186, 134, 142, 57, 117, 255, 213, 131, 36, 124, 161, 139, 168, 47, 110, 175, 156, 132, 54, 112, 188, 135, 154, 47, 100, 145, 138, 158, 38, 101, 188, 157, 202, 56, 108, 186, 152, 150, 46, 104, 178, 145, 133, 37, 100, 171, 133, 168, 34, 106, 186, 137, 135, 57, 96, 170, 196, 146, 62, 102, 163, 141, 133, 21, 108, 188, 129, 130, 59, 106, 175, 213, 132, 58, 108, 186, 155, 139, 120, 52, 184]
CODEC_910531cf = "reversed_integer_list|repeating_key_xor|ce,09,4a,f7,e8"

def load_910531cf():
    return bytes(reversed(MATERIAL_910531cf))

def decode_910531cf(e):
    key_bytes = (206, 9, 74, 247, 232,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

def recover_910531cf():
    n = "left" if 2 > 1 else "right"
    _pass = 0
    while _pass < 1:
        d = decode_910531cf(load_910531cf())
        _pass += 1
    t = d.decode("ascii", "strict")
    return t

def inspect_910531cf():
    stream = io.BytesIO(recover_910531cf().encode("ascii"))
    return stream.read().decode("ascii")

def surface_910531cf():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_910531cf():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_910531cf():
    fields = dict(item.split("=", 1) for item in inspect_910531cf().split("|"))
    analysis_surface = surface_910531cf()
    obfuscation_surface = obfuscation_910531cf()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_910531cf())
