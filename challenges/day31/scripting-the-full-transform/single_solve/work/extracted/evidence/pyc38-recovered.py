#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_c920d395 = [88, 31, 20, 94, 85, 86, 71, 82, 85, 31, 70, 71, 69, 81, 70, 71, 65, 71, 79, 68, 71, 70, 70, 71, 70, 14, 89, 84, 75, 86, 71, 65, 72, 75, 78, 71, 94, 67, 70, 67, 82, 86, 71, 84, 31, 75, 79, 82, 81, 84, 86, 78, 75, 68, 65, 84, 71, 85, 81, 87, 84, 69, 71, 65, 89, 84, 75, 86, 71, 94, 85, 86, 67, 73, 71, 65, 69, 81, 87, 80, 86, 31, 19, 94, 85, 91, 80, 86, 67, 90, 31, 69, 78, 67, 85, 85, 65, 85, 86, 67, 86, 75, 69, 79, 71, 86, 74, 81, 70, 94, 81, 68, 72, 87, 85, 69, 67, 86, 75, 81, 80, 31, 85, 86, 84, 75, 80, 73, 65, 86, 67, 68, 78, 71, 94, 69, 67, 84, 84, 75, 71, 84, 31, 74, 67, 85, 74, 65, 68, 67, 85, 71, 70, 65, 82, 91, 69, 65, 21, 26, 94, 89, 75, 80, 70, 81, 89, 85, 65, 69, 74, 67, 75, 80, 31, 84, 71, 80, 67, 79, 71, 70, 65, 75, 80, 86, 71, 84, 82, 84, 71, 86, 71, 84, 94, 69, 67, 79, 82, 67, 75, 73, 80, 65, 75, 70, 31, 69, 67, 79, 82, 67, 75, 73, 80, 15, 23, 68, 67, 70, 20, 71, 69, 19, 24, 26, 94, 72, 75, 78, 71, 65, 82, 67, 86, 74, 31, 37, 28, 17, 50, 84, 81, 73, 84, 67, 79, 38, 67, 86, 67, 17, 42, 87, 80, 86, 84, 71, 85, 85, 46, 67, 68, 17, 16, 87, 82, 70, 67, 86, 71, 15, 23, 68, 67, 70, 20, 71, 69, 19, 24, 26, 16, 82, 91]
CODEC_c920d395 = "integer_list|subtract_modulo_256|1e"

def load_c920d395():
    return bytes(MATERIAL_c920d395)

def decode_c920d395(stored_bytes):
    return bytes((value + 30) % 256 for value in stored_bytes)

def recover_c920d395():
    harmless_value = 19 * 7 - 133
    recovered_bytes = decode_c920d395(load_c920d395())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_c920d395():
    view = memoryview(recover_c920d395().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_c920d395:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_c920d395():
    return Surface_surface_c920d395.recover()

def obfuscation_c920d395():
    table = ("strin", "g_table")
    return "".join(table)

def plan_c920d395():
    fields = dict(item.split("=", 1) for item in inspect_c920d395().split("|"))
    analysis_surface = surface_c920d395()
    obfuscation_surface = obfuscation_c920d395()
    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_c920d395())
