#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_ca46e36e = "X8rV-Stdkpf2ZU2ShOo8TKiE6jZPnoDwKkiDjuo2BYWC8S1bmbjmN0eRjuItW5aT7DdHi4bhOVmDgvdlRJaX9TFHkLj1KkaPnvkrXZaA4AdKmJLrLBTGm_YhR4OG_WVZm4bsNnaRkus7XZ6I6ytVmIXjLVqUhvExRpna8SpImZTjN1uauOo2RY6b5jlbhY7gKhSFhvIHWpiS9ztMi5DsNk2YkPYHSp-G7DYUk473PUqDuPUhXZ-I6wdMj4L5O0ial-QxTpm47DwUlIboKEiegOt1HMDQvDtNz9TnblWfiPYsdp6DuDBGhJOobR7A3uY8EcSFsw=="
CODEC_ca46e36e = "urlsafe_base64|repeating_key_xor|29,f7,e7,85,58"

def load_ca46e36e():
    return base64.urlsafe_b64decode(MATERIAL_ca46e36e)

def decode_ca46e36e(EnCoDeD_Bytes):
    key_bytes = (41, 247, 231, 133, 88,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))

def recover_ca46e36e():
    NeUtRaL = None
    StAtE = "decode"
    while StAtE != "done":
        if StAtE == "decode":
            DeCoDeD_Bytes = decode_ca46e36e(load_ca46e36e())
            StAtE = "done"
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_ca46e36e():
    view = memoryview(recover_ca46e36e().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_ca46e36e():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_ca46e36e():
    return "transform_only"

def plan_ca46e36e():
    fields = dict(item.split("=", 1) for item in inspect_ca46e36e().split("|"))
    analysis_surface = surface_ca46e36e()
    obfuscation_surface = obfuscation_ca46e36e()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_ca46e36e())
