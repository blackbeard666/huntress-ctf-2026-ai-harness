# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_1674a9ed = [131, 221, 137, 216, 140, 218, 221, 143, 221, 140, 148, 213, 212, 211, 207, 194, 235, 200, 200, 222, 201, 207, 213, 206, 243, 134, 207, 213, 222, 220, 218, 228, 201, 222, 200, 206, 199, 194, 203, 149, 140, 143, 218, 136, 131, 131, 131, 140, 148, 223, 210, 215, 218, 205, 213, 210, 149, 222, 215, 203, 214, 218, 195, 222, 149, 131, 221, 137, 216, 140, 218, 221, 143, 221, 140, 148, 148, 129, 200, 203, 207, 207, 211, 134, 215, 201, 206, 199, 131, 221, 137, 216, 140, 218, 221, 143, 221, 140, 150, 213, 220, 210, 218, 203, 214, 218, 216, 134, 223, 210, 228, 213, 220, 210, 218, 203, 214, 218, 216, 199, 213, 212, 211, 207, 194, 203, 228, 212, 207, 228, 207, 203, 210, 201, 216, 200, 204, 134, 213, 210, 218, 211, 216, 228, 200, 204, 212, 223, 213, 210, 204, 199, 223, 222, 207, 218, 216, 200, 206, 221, 217, 212, 228, 201, 212, 214, 201, 218, 194, 203, 134, 201, 222, 210, 201, 201, 218, 216, 199, 213, 218, 215, 203, 228, 222, 203, 212, 215, 222, 205, 213, 222, 228, 215, 218, 211, 200, 201, 218, 214, 134, 213, 212, 210, 207, 218, 216, 200, 206, 221, 217, 212, 199, 213, 212, 210, 200, 200, 222, 201, 203, 195, 222, 228, 213, 212, 210, 207, 203, 222, 216, 195, 222, 134, 195, 218, 207, 213, 194, 200, 199, 138, 134, 207, 213, 206, 212, 216, 228, 222, 220, 218, 207, 200, 199, 194, 201, 212, 214, 222, 214, 228, 207, 213, 222, 210, 215, 216, 228, 203, 207, 207, 211, 134, 201, 222, 207, 203, 218, 223, 218, 199, 194, 201, 212, 214, 222, 214, 228, 211, 216, 207, 218, 203, 200, 210, 223, 151, 222, 207, 212, 214, 222, 201, 228, 222, 201, 210, 206, 202, 216, 218, 134, 200, 203, 222, 207, 200, 199, 137, 134, 205]
CODEC_1674a9ed = "integer_list|reverse_then_xor|bb"

def load_1674a9ed():
    return bytes(MATERIAL_1674a9ed)

def decode_1674a9ed(e):
    return bytes(value ^ 187 for value in reversed(e))

def recover_1674a9ed():
    n = ":".join(("north", "south"))
    try:
        d = decode_1674a9ed(load_1674a9ed())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    t = d.decode("ascii", "strict")
    return t

def inspect_1674a9ed():
    return recover_1674a9ed()

def surface_1674a9ed():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_1674a9ed():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_1674a9ed():
    fields = dict(item.split("=", 1) for item in inspect_1674a9ed().split("|"))
    analysis_surface = surface_1674a9ed()
    obfuscation_surface = obfuscation_1674a9ed()
    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_1674a9ed())

# reconstruction complete