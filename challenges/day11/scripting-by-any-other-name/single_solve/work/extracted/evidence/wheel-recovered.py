#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_9eef46e0 = ("YTg1NzE4Yzc1MS9ub2h0eVBzc2VydG51SD10bmVnYV9yZXN1fHlwLmRjMTAzNTM4L2RpbGF2bmkuZWxwbWF4ZS5hODU3MThjNzUxL"
    "y86c3B0dGg9bHJ1fGE4NTcxOGM3NTEtbmdpYXBtYWM9ZGlfbmdpYXBtYWN8bm9odHlwX290X2xsZWhzcmV3b3A9bmlhaGNfc3dvZG"
    "5pd3xldmloY3JhX2xlZWh3PXJlaXJyYWN8cGFtX3RhbXJvZj1ub2l0YWNzdWZib3xub2lzbmVoZXJwbW9jX3RzaWw9eGF0bnlzfDE"
    "9dG51b2NfZWdhdHN8eXJvbWVtX2JpbGxydT1yZXRwYWRhfHlyb21lbV9oY3RhcHNpZCxldG9tZXJfZXJpdXFjYT1zcGV0c3wyPXY=")
CODEC_9eef46e0 = "base64_chunks|reverse_bytes|"

def load_9eef46e0():
    return base64.b64decode(MATERIAL_9eef46e0)

def decode_9eef46e0(v_a19c):
    return bytes(reversed(v_a19c))

def recover_9eef46e0():
    v_d41a = "left" if 2 > 1 else "right"
    v_f602 = decode_9eef46e0
    v_b27e = v_f602(load_9eef46e0())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_9eef46e0():
    view = memoryview(recover_9eef46e0().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_9eef46e0():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_9eef46e0():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_9eef46e0():
    fields = dict(item.split("=", 1) for item in inspect_9eef46e0().split("|"))
    analysis_surface = surface_9eef46e0()
    obfuscation_surface = obfuscation_9eef46e0()
    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_9eef46e0())
