#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_abd18d6c = ("eXAuM2ZkMmE5MmI0ZC1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnwzZmQyYTkyYjRkL"
    "W5naWFwbWFjPWRpX25naWFwbWFjfHJvdHBpcmNzZWRfeWVrX251cj1uaWFoY19zd29kbml3fGlzbV9lemVlcmZfeGM9cm"
    "VpcnJhY3xuYWxwX2VtYW5fZXZpdGNlbGZlcj1ub2l0YWNzdWZib3xsb2NvdG9ycF9yb3RhcmV0aT14YXRueXN8MT10bnV"
    "vY19lZ2F0c3xlY2FscGVyX2VsaWZwbWV0PXJldHBhZGF8ZWxpZl9ldGlydyxkZWRkZWJtZV9lZG9jZWQ9c3BldHN8Mj12")
CODEC_abd18d6c = "base64_chunks|reverse_bytes|"

def load_abd18d6c():
    return base64.b64decode(MATERIAL_abd18d6c)

def decode_abd18d6c(v_a19c):
    return bytes(reversed(v_a19c))

def recover_abd18d6c():
    v_d41a = None
    v_a702 = "decode"
    while v_a702 != "done":
        if v_a702 == "decode":
            v_b27e = decode_abd18d6c(load_abd18d6c())
            v_a702 = "done"
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_abd18d6c():
    view = memoryview(recover_abd18d6c().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_abd18d6c():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_abd18d6c():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_abd18d6c():
    fields = dict(item.split("=", 1) for item in inspect_abd18d6c().split("|"))
    analysis_surface = surface_abd18d6c()
    obfuscation_surface = obfuscation_abd18d6c()
    operation_plan = ("tempfile_replace", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_abd18d6c())
