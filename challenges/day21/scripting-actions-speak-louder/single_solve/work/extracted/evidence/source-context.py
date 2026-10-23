#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_194f99d9 = "109,52,41,115,106,107,92,103,106,52,91,92,90,102,91,92,86,90,102,101,93,96,94,108,105,88,107,96,102,101,35,105,92,107,108,105,101,86,90,102,101,93,96,94,108,105,88,107,96,102,101,115,88,91,88,103,107,92,105,52,88,105,94,103,88,105,106,92,86,101,88,100,92,106,103,88,90,92,115,106,107,88,94,92,86,90,102,108,101,107,52,40,115,106,112,101,107,88,111,52,103,99,88,96,101,86,93,108,101,90,107,96,102,101,106,115,102,89,93,108,106,90,88,107,96,102,101,52,107,105,88,101,106,93,102,105,100,86,102,101,99,112,115,90,88,105,105,96,92,105,52,105,88,110,86,106,102,108,105,90,92,115,110,96,101,91,102,110,106,86,90,95,88,96,101,52,91,96,105,92,90,107,86,103,112,107,95,102,101,86,92,111,92,115,90,88,100,103,88,96,94,101,86,96,91,52,90,88,100,103,88,96,94,101,36,88,45,90,43,88,47,92,44,40,90,115,95,102,106,107,86,96,91,52,95,102,106,107,36,88,45,90,43,88,47,92,44,40,90"
CODEC_194f99d9 = "decimal_csv|subtract_modulo_256|09"

def load_194f99d9():
    return bytes(int(item) for item in MATERIAL_194f99d9.split(","))

def decode_194f99d9(EnCoDeD_Bytes):
    return bytes((value + 9) % 256 for value in EnCoDeD_Bytes)

def recover_194f99d9():
    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    _pass = 0
    while _pass < 1:
        DeCoDeD_Bytes = decode_194f99d9(load_194f99d9())
        _pass += 1
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_194f99d9():
    view = memoryview(recover_194f99d9().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_194f99d9():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_194f99d9():
    return "transform_only"

def plan_194f99d9():
    fields = dict(item.split("=", 1) for item in inspect_194f99d9().split("|"))
    analysis_surface = surface_194f99d9()
    obfuscation_surface = obfuscation_194f99d9()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_194f99d9())
