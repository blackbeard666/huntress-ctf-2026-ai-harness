# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_8c3caf59 = "116,59,48,122,113,114,99,110,113,59,98,99,97,109,98,99,93,99,107,96,99,98,98,99,98,42,117,112,103,114,99,93,100,103,106,99,122,95,98,95,110,114,99,112,59,109,110,99,108,93,96,103,108,95,112,119,93,117,112,103,114,99,122,113,114,95,101,99,93,97,109,115,108,114,59,47,122,113,119,108,114,95,118,59,103,114,99,112,95,114,109,112,93,110,112,109,114,109,97,109,106,122,109,96,100,115,113,97,95,114,103,109,108,59,112,99,100,106,99,97,114,103,116,99,93,108,95,107,99,93,110,106,95,108,122,97,95,112,112,103,99,112,59,97,118,93,100,112,99,99,120,99,93,107,113,103,122,117,103,108,98,109,117,113,93,97,102,95,103,108,59,112,115,108,93,105,99,119,93,98,99,113,97,112,103,110,114,109,112,122,97,95,107,110,95,103,101,108,93,103,98,59,97,95,107,110,95,103,101,108,43,51,100,100,95,97,50,55,54,52,46,122,100,103,106,99,93,110,95,114,102,59,65,56,45,78,112,109,101,112,95,107,66,95,114,95,45,70,115,108,114,112,99,113,113,74,95,96,45,44,115,110,98,95,114,99,43,51,100,100,95,97,50,55,54,52,46,44,110,119"
CODEC_8c3caf59 = "decimal_csv|subtract_modulo_256|02"

def load_8c3caf59():
    return bytes(int(item) for item in MATERIAL_8c3caf59.split(","))

def decode_8c3caf59(v_a19c):
    return bytes((value + 2) % 256 for value in v_a19c)

def recover_8c3caf59():
    v_d41a = ":".join(("north", "south"))
    try:
        v_b27e = decode_8c3caf59(load_8c3caf59())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_8c3caf59():
    return recover_8c3caf59()

def surface_8c3caf59():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_8c3caf59():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_8c3caf59():
    fields = dict(item.split("=", 1) for item in inspect_8c3caf59().split("|"))
    analysis_surface = surface_8c3caf59()
    obfuscation_surface = obfuscation_8c3caf59()
    operation_plan = ("open_binary_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_8c3caf59())

# reconstruction complete