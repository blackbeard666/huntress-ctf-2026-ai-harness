#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0645a856 = ("UFkHT00dHxxMGREQGwRMXUhNWVwHBktIZVpaTFtdR1xhBkhdSG1ESFtORlt5BhNqFEFdSFl2TEVAT1VPTR0fHEwZERAbBE"
    "dOQEhZREhKFE1AdkdOQEhZREhKVVtGXVlAW0paTE12UExCdkdcWxRHQEhBSnZaXkZNR0BeVUBaRHZMU0xMW092UUoUW0xA"
    "W1tISlVHSEVZdkxESEd2TF9AXUpMRU9MWxRHRkBdSEpaXE9LRlVFRkpGXUZbWXZbRl1IW0xdQBRRSF1HUFpVGBRdR1xGSn"
    "ZMTkhdWlVMXUBbXnZQW0hHQEt2R0xZRhRbTF1ZSE1IVUxFQE92TF1AW14FTUxNTUxLREx2TE1GSkxNFFpZTF1aVRsUXw==")
CODEC_0645a856 = "base64_chunks|reverse_then_xor|29"

def load_0645a856():
    return base64.b64decode(MATERIAL_0645a856)

def decode_0645a856(stored_bytes):
    return bytes(value ^ 41 for value in reversed(stored_bytes))

def recover_0645a856():
    harmless_value = None
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_0645a856(load_0645a856())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_0645a856():
    view = memoryview(recover_0645a856().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_0645a856():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_0645a856():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_0645a856():
    fields = dict(item.split("=", 1) for item in inspect_0645a856().split("|"))
    analysis_surface = surface_0645a856()
    obfuscation_surface = obfuscation_0645a856()
    operation_plan = ("open_binary_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0645a856())
