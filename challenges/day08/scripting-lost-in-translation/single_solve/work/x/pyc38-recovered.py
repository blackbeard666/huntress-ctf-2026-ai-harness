#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b6d9cbcb = [138, 81, 70, 144, 135, 136, 121, 132, 135, 81, 120, 121, 119, 131, 120, 121, 115, 121, 129, 118, 121, 120, 120, 121, 120, 64, 139, 134, 125, 136, 121, 115, 122, 125, 128, 121, 144, 117, 120, 117, 132, 136, 121, 134, 81, 131, 132, 121, 130, 115, 118, 125, 130, 117, 134, 141, 115, 139, 134, 125, 136, 121, 144, 135, 136, 117, 123, 121, 115, 119, 131, 137, 130, 136, 81, 69, 144, 135, 141, 130, 136, 117, 140, 81, 119, 128, 117, 135, 135, 115, 135, 136, 117, 136, 125, 119, 129, 121, 136, 124, 131, 120, 144, 131, 118, 122, 137, 135, 119, 117, 136, 125, 131, 130, 81, 135, 136, 134, 125, 130, 123, 115, 136, 117, 118, 128, 121, 144, 119, 117, 134, 134, 125, 121, 134, 81, 124, 117, 135, 124, 115, 118, 117, 135, 121, 120, 115, 132, 141, 119, 115, 71, 76, 144, 139, 125, 130, 120, 131, 139, 135, 115, 119, 124, 117, 125, 130, 81, 134, 121, 130, 117, 129, 121, 120, 115, 125, 130, 136, 121, 134, 132, 134, 121, 136, 121, 134, 144, 119, 117, 129, 132, 117, 125, 123, 130, 115, 125, 120, 81, 119, 117, 129, 132, 117, 125, 123, 130, 65, 74, 70, 119, 77, 121, 72, 70, 71, 72, 120, 144, 122, 125, 128, 121, 115, 132, 117, 136, 124, 81, 87, 78, 67, 100, 134, 131, 123, 134, 117, 129, 88, 117, 136, 117, 67, 92, 137, 130, 136, 134, 121, 135, 135, 96, 117, 118, 67, 66, 137, 132, 120, 117, 136, 121, 65, 74, 70, 119, 77, 121, 72, 70, 71, 72, 120, 66, 132, 141]
CODEC_b6d9cbcb = "integer_list|add_modulo_256|14"

def load_b6d9cbcb():
    return bytes(MATERIAL_b6d9cbcb)

def decode_b6d9cbcb(stored_bytes):
    return bytes((value - 20) % 256 for value in stored_bytes)

def recover_b6d9cbcb():
    harmless_value = "left" if 2 > 1 else "right"
    decoder_function = decode_b6d9cbcb
    recovered_bytes = decoder_function(load_b6d9cbcb())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_b6d9cbcb():
    view = memoryview(recover_b6d9cbcb().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_b6d9cbcb:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_b6d9cbcb():
    return Surface_surface_b6d9cbcb.recover()

def obfuscation_b6d9cbcb():
    table = ("strin", "g_table")
    return "".join(table)

def plan_b6d9cbcb():
    fields = dict(item.split("=", 1) for item in inspect_b6d9cbcb().split("|"))
    analysis_surface = surface_b6d9cbcb()
    obfuscation_surface = obfuscation_b6d9cbcb()
    operation_plan = ("open_binary_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b6d9cbcb())
