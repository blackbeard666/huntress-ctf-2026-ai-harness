# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_bd6d6600 = "57,104,63,60,61,104,61,56,106,110,38,127,120,100,99,54,111,98,84,127,120,100,99,119,57,104,63,60,61,104,61,56,106,110,38,101,108,98,106,123,102,106,104,54,111,98,84,101,108,98,106,123,102,106,104,119,110,115,110,84,101,100,99,127,114,123,84,127,104,110,121,98,111,54,101,98,106,99,104,84,120,124,100,111,101,98,124,119,110,104,121,126,100,120,84,124,106,121,54,121,110,98,121,121,106,104,119,114,103,101,100,84,102,121,100,109,120,101,106,121,127,54,101,100,98,127,106,104,120,126,109,105,100,119,120,101,100,98,127,104,101,126,109,84,101,98,106,103,123,54,115,106,127,101,114,120,119,58,54,127,101,126,100,104,84,110,108,106,127,120,119,110,104,106,123,120,110,102,106,101,84,110,120,121,106,123,108,121,106,54,121,110,127,123,106,111,106,119,101,100,98,127,106,121,126,108,98,109,101,100,104,84,101,121,126,127,110,121,39,101,100,98,127,106,121,126,108,98,109,101,100,104,84,110,111,100,104,110,111,54,120,123,110,127,120,119,57,54,125"
CODEC_bd6d6600 = "decimal_csv|reverse_then_xor|0b"

def load_bd6d6600():
    return bytes(int(item) for item in MATERIAL_bd6d6600.split(","))

def decode_bd6d6600(EnCoDeD_Bytes):
    return bytes(value ^ 11 for value in reversed(EnCoDeD_Bytes))

def recover_bd6d6600():
    NeUtRaL = ":".join(("north", "south"))
    DeCoDe_Target = decode_bd6d6600
    DeCoDeD_Bytes = DeCoDe_Target(load_bd6d6600())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_bd6d6600():
    stream = io.BytesIO(recover_bd6d6600().encode("ascii"))
    return stream.read().decode("ascii")

def surface_bd6d6600():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_bd6d6600():
    return "transform_only"

def plan_bd6d6600():
    fields = dict(item.split("=", 1) for item in inspect_bd6d6600().split("|"))
    analysis_surface = surface_bd6d6600()
    obfuscation_surface = obfuscation_bd6d6600()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_bd6d6600())

# reconstruction complete