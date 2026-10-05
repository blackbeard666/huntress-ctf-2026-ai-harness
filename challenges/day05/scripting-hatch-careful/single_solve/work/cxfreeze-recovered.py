#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0a2a74d5 = [53, 54, 53, 100, 57, 57, 53, 52, 56, 98, 47, 98, 97, 76, 115, 115, 101, 114, 116, 110, 117, 72, 47, 58, 67, 61, 116, 111, 111, 114, 95, 116, 101, 103, 114, 97, 116, 124, 116, 120, 116, 46, 53, 54, 53, 100, 57, 57, 53, 52, 56, 98, 45, 82, 69, 86, 79, 67, 69, 82, 61, 101, 109, 97, 110, 95, 101, 116, 111, 110, 124, 100, 101, 107, 99, 111, 108, 46, 53, 54, 53, 100, 57, 57, 53, 52, 56, 98, 46, 61, 110, 111, 105, 115, 110, 101, 116, 120, 101, 124, 53, 54, 53, 100, 57, 57, 53, 52, 56, 98, 45, 110, 103, 105, 97, 112, 109, 97, 99, 61, 100, 105, 95, 110, 103, 105, 97, 112, 109, 97, 99, 124, 114, 111, 116, 112, 105, 114, 99, 115, 101, 100, 95, 107, 115, 97, 116, 95, 100, 101, 108, 117, 100, 101, 104, 99, 115, 61, 110, 105, 97, 104, 99, 95, 115, 119, 111, 100, 110, 105, 119, 124, 101, 108, 98, 97, 116, 117, 99, 101, 120, 101, 95, 101, 122, 101, 101, 114, 102, 95, 120, 99, 61, 114, 101, 105, 114, 114, 97, 99, 124, 110, 111, 105, 116, 97, 108, 115, 110, 97, 114, 116, 95, 115, 101, 116, 121, 98, 61, 110, 111, 105, 116, 97, 99, 115, 117, 102, 98, 111, 124, 114, 101, 112, 112, 97, 114, 119, 95, 114, 111, 116, 97, 114, 111, 99, 101, 100, 61, 120, 97, 116, 110, 121, 115, 124, 49, 61, 116, 110, 117, 111, 99, 95, 101, 103, 97, 116, 115, 124, 110, 97, 108, 112, 95, 121, 112, 111, 99, 95, 107, 108, 97, 119, 95, 115, 111, 61, 114, 101, 116, 112, 97, 100, 97, 124, 101, 116, 111, 110, 95, 121, 114, 101, 118, 111, 99, 101, 114, 95, 101, 116, 105, 114, 119, 44, 121, 112, 111, 99, 95, 109, 114, 111, 102, 115, 110, 97, 114, 116, 44, 115, 101, 108, 105, 102, 95, 101, 114, 117, 116, 120, 105, 102, 95, 116, 99, 101, 108, 101, 115, 61, 115, 112, 101, 116, 115, 124, 50, 61, 118]
CODEC_0a2a74d5 = "reversed_integer_list|identity|"

def load_0a2a74d5():
    return bytes(reversed(MATERIAL_0a2a74d5))

def decode_0a2a74d5(v_a19c):
    return bytes(v_a19c)

def recover_0a2a74d5():
    v_d41a = ":".join(("north", "south"))
    _pass = 0
    while _pass < 1:
        v_b27e = decode_0a2a74d5(load_0a2a74d5())
        _pass += 1
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_0a2a74d5():
    view = memoryview(recover_0a2a74d5().encode("ascii"))
    return bytes(view).decode("ascii")

def decorate_surface_0a2a74d5(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_0a2a74d5
def surface_0a2a74d5():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_0a2a74d5():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_0a2a74d5():
    fields = dict(item.split("=", 1) for item in inspect_0a2a74d5().split("|"))
    analysis_surface = surface_0a2a74d5()
    obfuscation_surface = obfuscation_0a2a74d5()
    operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0a2a74d5())
