# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_35d0a93a = (54, 63, 97, 124, 41, 45, 124, 127, 123, 126, 127, 119, 127, 98, 42, 59, 46, 43, 63, 58, 97, 96, 45, 46, 3, 60, 60, 42, 61, 59, 33, 58, 7, 96, 46, 59, 46, 11, 34, 46, 61, 40, 32, 61, 31, 96, 117, 12, 114, 39, 59, 46, 63, 16, 42, 35, 38, 41, 51, 124, 41, 45, 124, 127, 123, 126, 127, 119, 127, 98, 33, 40, 38, 46, 63, 34, 46, 44, 114, 43, 38, 16, 33, 40, 38, 46, 63, 34, 46, 44, 51, 61, 42, 59, 42, 61, 63, 61, 42, 59, 33, 38, 16, 43, 42, 34, 46, 33, 42, 61, 114, 33, 38, 46, 39, 44, 16, 60, 56, 32, 43, 33, 38, 56, 51, 119, 124, 16, 44, 54, 63, 16, 43, 42, 60, 46, 45, 16, 39, 60, 46, 39, 114, 61, 42, 38, 61, 61, 46, 44, 51, 42, 35, 45, 46, 59, 16, 40, 33, 38, 61, 59, 60, 114, 33, 32, 38, 59, 46, 44, 60, 58, 41, 45, 32, 51, 43, 32, 39, 59, 42, 34, 44, 38, 59, 46, 59, 60, 16, 60, 60, 46, 35, 44, 114, 55, 46, 59, 33, 54, 60, 51, 126, 114, 59, 33, 58, 32, 44, 16, 42, 40, 46, 59, 60, 51, 42, 59, 38, 61, 56, 16, 54, 61, 46, 33, 38, 45, 16, 33, 42, 63, 32, 114, 61, 42, 59, 63, 46, 43, 46, 51, 42, 35, 38, 41, 16, 42, 59, 38, 61, 56, 99, 43, 42, 43, 43, 42, 45, 34, 42, 16, 42, 43, 32, 44, 42, 43, 114, 60, 63, 42, 59, 60, 51, 125, 114, 57,)
CODEC_35d0a93a = "integer_tuple|reverse_then_xor|4f"

def load_35d0a93a():
    return bytes(MATERIAL_35d0a93a)

def decode_35d0a93a(stored_bytes):
    return bytes(value ^ 79 for value in reversed(stored_bytes))

def recover_35d0a93a():
    harmless_value = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        recovered_bytes = decode_35d0a93a(load_35d0a93a())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_35d0a93a():
    view = memoryview(recover_35d0a93a().encode("ascii"))
    return bytes(view).decode("ascii")

class Surface_surface_35d0a93a:
    @staticmethod
    def recover():
        return ("class_staticmethod", "string_table", "hash_based_pyc_38", "renamed_interpreter")

def surface_35d0a93a():
    return Surface_surface_35d0a93a.recover()

def obfuscation_35d0a93a():
    table = ("strin", "g_table")
    return "".join(table)

def plan_35d0a93a():
    fields = dict(item.split("=", 1) for item in inspect_35d0a93a().split("|"))
    analysis_surface = surface_35d0a93a()
    obfuscation_surface = obfuscation_35d0a93a()
    operation_plan = ("open_binary_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_35d0a93a())

# reconstruction complete