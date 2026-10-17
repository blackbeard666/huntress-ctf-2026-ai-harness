# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_7ea5dbd4 = (41, 20, 38, 90, 41, 93, 56, 72, 59, 6, 98, 7, 100, 11, 111, 10, 85, 48, 93, 63, 90, 62, 90, 63, 91, 119, 0, 114, 27, 111, 10, 85, 51, 90, 54, 83, 47, 78, 42, 75, 59, 79, 42, 88, 101, 12, 97, 17, 126, 12, 120, 20, 125, 31, 64, 50, 87, 36, 75, 62, 76, 47, 74, 21, 98, 16, 121, 13, 104, 20, 103, 19, 114, 21, 112, 47, 76, 35, 86, 56, 76, 113, 64, 60, 79, 54, 88, 44, 77, 53, 8, 97, 21, 112, 2, 99, 23, 120, 10, 85, 37, 87, 56, 76, 35, 64, 47, 67, 63, 80, 50, 84, 33, 82, 49, 80, 36, 77, 34, 76, 113, 3, 102, 0, 108, 9, 106, 30, 119, 1, 100, 59, 85, 52, 89, 60, 99, 19, 127, 30, 112, 12, 111, 14, 124, 14, 103, 2, 112, 77, 46, 86, 9, 111, 29, 120, 29, 103, 2, 93, 48, 67, 42, 86, 33, 72, 38, 66, 45, 90, 41, 118, 21, 125, 28, 117, 27, 38, 84, 33, 79, 16, 123, 30, 103, 56, 92, 57, 74, 41, 91, 50, 66, 54, 89, 43, 87, 52, 85, 56, 72, 41, 64, 39, 73, 22, 127, 27, 38, 69, 36, 73, 57, 88, 49, 86, 56, 21, 34, 18, 37, 28, 36, 16, 39, 68, 118, 21, 105, 15, 102, 10, 111, 48, 64, 33, 85, 61, 0, 67, 121, 86, 6, 116, 27, 124, 14, 111, 2, 70, 39, 83, 50, 29, 85, 32, 78, 58, 72, 45, 94, 45, 97, 0, 98, 77, 99, 22, 102, 2, 99, 23, 114, 95, 104, 88, 111, 86, 110, 90, 109, 14, 60, 95, 113, 1, 120,)
CODEC_7ea5dbd4 = "integer_tuple|rolling_xor|5f"

def load_7ea5dbd4():
    return bytes(MATERIAL_7ea5dbd4)

def decode_7ea5dbd4(stored_bytes):
    recovered_bytes = bytearray()
    prior_byte = 95
    for value in stored_bytes:
        recovered_bytes.append(value ^ prior_byte)
        prior_byte = value
    return bytes(recovered_bytes)

def recover_7ea5dbd4():
    harmless_value = None
    decode_state = "decode"
    while decode_state != "done":
        if decode_state == "decode":
            recovered_bytes = decode_7ea5dbd4(load_7ea5dbd4())
            decode_state = "done"
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_7ea5dbd4():
    view = memoryview(recover_7ea5dbd4().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_7ea5dbd4():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_7ea5dbd4():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_7ea5dbd4():
    fields = dict(item.split("=", 1) for item in inspect_7ea5dbd4().split("|"))
    analysis_surface = surface_7ea5dbd4()
    obfuscation_surface = obfuscation_7ea5dbd4()
    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_7ea5dbd4())

# reconstruction complete