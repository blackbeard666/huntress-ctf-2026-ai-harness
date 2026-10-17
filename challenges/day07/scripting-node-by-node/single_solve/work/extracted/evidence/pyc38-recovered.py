#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0b3c0f85 = [109, 100, 34, 41, 36, 41, 44, 41, 42, 39, 45, 41, 90, 33, 89, 104, 85, 88, 100, 105, 34, 35, 86, 85, 64, 103, 103, 89, 102, 104, 98, 105, 60, 35, 85, 104, 85, 56, 97, 85, 102, 91, 99, 102, 68, 35, 46, 55, 49, 92, 104, 85, 100, 83, 89, 96, 93, 90, 112, 41, 36, 41, 44, 41, 42, 39, 45, 41, 90, 33, 98, 91, 93, 85, 100, 97, 85, 87, 49, 88, 93, 83, 98, 91, 93, 85, 100, 97, 85, 87, 112, 102, 89, 104, 89, 102, 100, 102, 89, 104, 98, 93, 83, 88, 89, 97, 85, 98, 89, 102, 49, 98, 93, 85, 92, 87, 83, 103, 107, 99, 88, 98, 93, 107, 112, 44, 39, 83, 87, 109, 100, 83, 88, 89, 103, 85, 86, 83, 92, 103, 85, 92, 49, 102, 89, 93, 102, 102, 85, 87, 112, 89, 96, 86, 85, 104, 83, 91, 98, 93, 102, 104, 103, 49, 98, 99, 93, 104, 85, 87, 103, 105, 90, 86, 99, 112, 88, 99, 92, 104, 89, 97, 87, 93, 104, 85, 104, 103, 83, 103, 103, 85, 96, 87, 49, 108, 85, 104, 98, 109, 103, 112, 37, 49, 104, 98, 105, 99, 87, 83, 89, 91, 85, 104, 103, 112, 89, 104, 93, 102, 107, 83, 109, 102, 85, 98, 93, 86, 83, 98, 89, 100, 99, 49, 102, 89, 104, 100, 85, 88, 85, 112, 89, 96, 93, 90, 83, 89, 104, 93, 102, 107, 32, 88, 89, 88, 88, 89, 86, 97, 89, 83, 89, 88, 99, 87, 89, 88, 49, 103, 100, 89, 104, 103, 112, 38, 49, 106]
CODEC_0b3c0f85 = "reversed_integer_list|subtract_modulo_256|0c"

def load_0b3c0f85():
    return bytes(reversed(MATERIAL_0b3c0f85))

def decode_0b3c0f85(v_a19c):
    return bytes((value + 12) % 256 for value in v_a19c)

def recover_0b3c0f85():
    v_d41a = (3, 5, 8, 13)[1:3]
    try:
        v_b27e = decode_0b3c0f85(load_0b3c0f85())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_0b3c0f85():
    stream = io.BytesIO(recover_0b3c0f85().encode("ascii"))
    return stream.read().decode("ascii")

class Surface_surface_0b3c0f85:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_0b3c0f85():
    return Surface_surface_0b3c0f85.recover()

def obfuscation_0b3c0f85():
    table = ("strin", "g_table")
    return "".join(table)

def plan_0b3c0f85():
    fields = dict(item.split("=", 1) for item in inspect_0b3c0f85().split("|"))
    analysis_surface = surface_0b3c0f85()
    obfuscation_surface = obfuscation_0b3c0f85()
    operation_plan = ("open_binary_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0b3c0f85())
