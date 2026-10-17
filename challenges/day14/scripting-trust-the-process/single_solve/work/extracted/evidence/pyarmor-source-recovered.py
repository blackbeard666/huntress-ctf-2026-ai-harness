# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_c7e8f4b4 = [116, 59, 48, 122, 113, 114, 99, 110, 113, 59, 95, 97, 111, 115, 103, 112, 99, 93, 112, 99, 107, 109, 114, 99, 42, 98, 103, 113, 110, 95, 114, 97, 102, 93, 107, 99, 107, 109, 112, 119, 122, 95, 98, 95, 110, 114, 99, 112, 59, 113, 109, 97, 105, 99, 114, 93, 110, 106, 95, 108, 93, 107, 99, 107, 109, 112, 119, 122, 113, 114, 95, 101, 99, 93, 97, 109, 115, 108, 114, 59, 47, 122, 113, 119, 108, 114, 95, 118, 59, 99, 118, 97, 99, 110, 114, 103, 109, 108, 93, 99, 118, 110, 112, 99, 113, 113, 103, 109, 108, 122, 109, 96, 100, 115, 113, 97, 95, 114, 103, 109, 108, 59, 107, 95, 112, 113, 102, 95, 106, 93, 99, 108, 116, 99, 106, 109, 110, 99, 93, 110, 106, 95, 108, 122, 97, 95, 112, 112, 103, 99, 112, 59, 110, 119, 95, 112, 107, 109, 112, 93, 109, 96, 100, 115, 113, 97, 95, 114, 99, 98, 122, 117, 103, 108, 98, 109, 117, 113, 93, 97, 102, 95, 103, 108, 59, 117, 113, 97, 112, 103, 110, 114, 93, 114, 109, 93, 110, 119, 114, 102, 109, 108, 122, 97, 95, 107, 110, 95, 103, 101, 108, 93, 103, 98, 59, 97, 95, 107, 110, 95, 103, 101, 108, 43, 97, 54, 46, 97, 51, 55, 97, 99, 52, 50, 122, 115, 112, 106, 59, 102, 114, 114, 110, 113, 56, 45, 45, 97, 54, 46, 97, 51, 55, 97, 99, 52, 50, 44, 99, 118, 95, 107, 110, 106, 99, 44, 103, 108, 116, 95, 106, 103, 98, 45, 51, 51, 51, 51, 50, 52, 48, 97, 44, 110, 119, 122, 115, 113, 99, 112, 93, 95, 101, 99, 108, 114, 59, 70, 115, 108, 114, 112, 99, 113, 113, 78, 119, 114, 102, 109, 108, 45, 97, 54, 46, 97, 51, 55, 97, 99, 52, 50]
CODEC_c7e8f4b4 = "integer_list|subtract_modulo_256|02"

def load_c7e8f4b4():
    return bytes(MATERIAL_c7e8f4b4)

def decode_c7e8f4b4(e):
    return bytes((value + 2) % 256 for value in e)

def recover_c7e8f4b4():
    n = ":".join(("north", "south"))
    f = decode_c7e8f4b4
    d = f(load_c7e8f4b4())
    t = d.decode("ascii", "strict")
    return t

def inspect_c7e8f4b4():
    view = memoryview(recover_c7e8f4b4().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_c7e8f4b4():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_c7e8f4b4():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_c7e8f4b4():
    fields = dict(item.split("=", 1) for item in inspect_c7e8f4b4().split("|"))
    analysis_surface = surface_c7e8f4b4()
    obfuscation_surface = obfuscation_c7e8f4b4()
    operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_c7e8f4b4())

# reconstruction complete