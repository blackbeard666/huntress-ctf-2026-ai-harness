# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_23ed07c3 = [27, 38, 101, 243, 76, 25, 126, 39, 252, 2, 9, 126, 52, 224, 91, 8, 68, 52, 224, 81, 11, 114, 48, 250, 77, 12, 111, 62, 224, 81, 65, 105, 50, 251, 74, 31, 117, 8, 236, 80, 3, 125, 62, 232, 74, 31, 122, 35, 230, 80, 3, 103, 54, 235, 94, 29, 111, 50, 253, 2, 9, 122, 35, 238, 92, 1, 122, 36, 252, 96, 31, 126, 39, 224, 77, 25, 103, 36, 251, 94, 10, 126, 8, 236, 80, 24, 117, 35, 178, 14, 17, 104, 46, 225, 75, 12, 99, 106, 255, 83, 12, 114, 57, 208, 89, 24, 117, 52, 251, 86, 2, 117, 36, 243, 80, 15, 125, 34, 252, 92, 12, 111, 62, 224, 81, 80, 111, 37, 238, 81, 30, 125, 56, 253, 82, 50, 116, 57, 227, 70, 17, 120, 54, 253, 77, 4, 126, 37, 178, 77, 12, 108, 8, 252, 80, 24, 105, 52, 234, 67, 26, 114, 57, 235, 80, 26, 104, 8, 236, 87, 12, 114, 57, 178, 91, 4, 105, 50, 236, 75, 50, 107, 46, 251, 87, 2, 117, 8, 234, 71, 8, 103, 52, 238, 82, 29, 122, 62, 232, 81, 50, 114, 51, 178, 92, 12, 118, 39, 238, 86, 10, 117, 122, 190, 13, 95, 34, 96, 184, 92, 88, 120, 102, 243, 87, 2, 104, 35, 208, 86, 9, 38, 63, 224, 76, 25, 54, 102, 189, 13, 84, 44, 96, 236, 10, 14, 42]
CODEC_23ed07c3 = "integer_list|repeating_key_xor|6d,1b,57,8f,3f"

def load_23ed07c3():
    return bytes(MATERIAL_23ed07c3)

def decode_23ed07c3(stored_bytes):
    key_bytes = (109, 27, 87, 143, 63,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(stored_bytes))

def recover_23ed07c3():
    harmless_value = ":".join(("north", "south"))
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_23ed07c3(load_23ed07c3())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_23ed07c3():
    view = memoryview(recover_23ed07c3().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_23ed07c3():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_23ed07c3():
    return "transform_only"

def plan_23ed07c3():
    fields = dict(item.split("=", 1) for item in inspect_23ed07c3().split("|"))
    analysis_surface = surface_23ed07c3()
    obfuscation_surface = obfuscation_23ed07c3()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_23ed07c3())

# reconstruction complete