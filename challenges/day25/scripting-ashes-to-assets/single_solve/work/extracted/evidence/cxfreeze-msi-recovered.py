#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_e7d54944 = [118, 61, 50, 124, 115, 116, 101, 112, 115, 61, 100, 101, 99, 111, 100, 101, 95, 101, 109, 98, 101, 100, 100, 101, 100, 44, 119, 114, 105, 116, 101, 95, 102, 105, 108, 101, 124, 97, 100, 97, 112, 116, 101, 114, 61, 112, 97, 116, 104, 95, 119, 114, 105, 116, 101, 95, 98, 121, 116, 101, 115, 124, 115, 116, 97, 103, 101, 95, 99, 111, 117, 110, 116, 61, 49, 124, 115, 121, 110, 116, 97, 120, 61, 105, 116, 101, 114, 97, 116, 111, 114, 95, 112, 114, 111, 116, 111, 99, 111, 108, 124, 111, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 61, 114, 101, 102, 108, 101, 99, 116, 105, 118, 101, 95, 110, 97, 109, 101, 95, 112, 108, 97, 110, 124, 99, 97, 114, 114, 105, 101, 114, 61, 99, 120, 95, 102, 114, 101, 101, 122, 101, 95, 109, 115, 105, 124, 119, 105, 110, 100, 111, 119, 115, 95, 99, 104, 97, 105, 110, 61, 114, 117, 110, 95, 107, 101, 121, 95, 100, 101, 115, 99, 114, 105, 112, 116, 111, 114, 124, 99, 97, 109, 112, 97, 105, 103, 110, 95, 105, 100, 61, 99, 97, 109, 112, 97, 105, 103, 110, 45, 53, 56, 57, 48, 48, 99, 98, 100, 48, 55, 124, 102, 105, 108, 101, 95, 112, 97, 116, 104, 61, 67, 58, 47, 80, 114, 111, 103, 114, 97, 109, 68, 97, 116, 97, 47, 72, 117, 110, 116, 114, 101, 115, 115, 76, 97, 98, 47, 46, 117, 112, 100, 97, 116, 101, 45, 53, 56, 57, 48, 48, 99, 98, 100, 48, 55, 46, 112, 121]
CODEC_e7d54944 = "reversed_integer_list|reverse_bytes|"

def load_e7d54944():
    return bytes(reversed(MATERIAL_e7d54944))

def decode_e7d54944(v_a19c):
    return bytes(reversed(v_a19c))

def recover_e7d54944():
    v_d41a = "left" if 2 > 1 else "right"
    try:
        v_b27e = decode_e7d54944(load_e7d54944())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_e7d54944():
    view = memoryview(recover_e7d54944().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_e7d54944():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_e7d54944():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_e7d54944():
    fields = dict(item.split("=", 1) for item in inspect_e7d54944().split("|"))
    analysis_surface = surface_e7d54944()
    obfuscation_surface = obfuscation_e7d54944()
    operation_plan = ("path_write_bytes", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_e7d54944())
