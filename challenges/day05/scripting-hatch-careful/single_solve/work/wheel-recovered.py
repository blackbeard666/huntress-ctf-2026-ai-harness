#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_428e84b5 = "125,68,57,131,122,123,108,119,122,68,104,106,120,124,112,121,108,102,121,108,116,118,123,108,51,107,112,122,119,104,123,106,111,102,116,108,116,118,121,128,131,104,107,104,119,123,108,121,68,124,121,115,115,112,105,102,116,108,116,118,121,128,131,122,123,104,110,108,102,106,118,124,117,123,68,56,131,122,128,117,123,104,127,68,115,112,122,123,102,106,118,116,119,121,108,111,108,117,122,112,118,117,131,118,105,109,124,122,106,104,123,112,118,117,68,109,118,121,116,104,123,102,116,104,119,131,106,104,121,121,112,108,121,68,126,111,108,108,115,102,104,121,106,111,112,125,108,131,126,112,117,107,118,126,122,102,106,111,104,112,117,68,119,118,126,108,121,122,111,108,115,115,102,123,118,102,119,128,123,111,118,117,131,106,104,116,119,104,112,110,117,102,112,107,68,106,104,116,119,104,112,110,117,52,108,109,106,60,60,109,58,55,58,58,131,124,121,115,68,111,123,123,119,122,65,54,54,108,109,106,60,60,109,58,55,58,58,53,108,127,104,116,119,115,108,53,112,117,125,104,115,112,107,54,60,61,64,109,56,108,108,58,53,119,128,131,124,122,108,121,102,104,110,108,117,123,68,79,124,117,123,121,108,122,122,87,128,123,111,118,117,54,108,109,106,60,60,109,58,55,58,58"
CODEC_428e84b5 = "decimal_csv|add_modulo_256|07"

def load_428e84b5():
    return bytes(int(item) for item in MATERIAL_428e84b5.split(","))

def decode_428e84b5(v_a19c):
    return bytes((value - 7) % 256 for value in v_a19c)

def recover_428e84b5():
    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    for _pass in range(1):
        v_b27e = decode_428e84b5(load_428e84b5())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_428e84b5():
    return recover_428e84b5()

def surface_428e84b5():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_428e84b5():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_428e84b5():
    fields = dict(item.split("=", 1) for item in inspect_428e84b5().split("|"))
    analysis_surface = surface_428e84b5()
    obfuscation_surface = obfuscation_428e84b5()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_428e84b5())
