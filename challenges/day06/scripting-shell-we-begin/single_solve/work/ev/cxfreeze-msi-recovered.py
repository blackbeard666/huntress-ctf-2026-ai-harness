# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_6b079e94 = (107, 32, 47, 97, 110, 105, 120, 109, 110, 32, 121, 120, 126, 114, 121, 120, 66, 120, 112, 127, 120, 121, 121, 120, 121, 49, 106, 111, 116, 105, 120, 66, 123, 116, 113, 120, 97, 124, 121, 124, 109, 105, 120, 111, 32, 116, 112, 109, 114, 111, 105, 113, 116, 127, 66, 111, 120, 110, 114, 104, 111, 126, 120, 66, 106, 111, 116, 105, 120, 97, 110, 105, 124, 122, 120, 66, 126, 114, 104, 115, 105, 32, 44, 97, 110, 100, 115, 105, 124, 101, 32, 116, 105, 120, 111, 124, 105, 114, 111, 66, 109, 111, 114, 105, 114, 126, 114, 113, 97, 114, 127, 123, 104, 110, 126, 124, 105, 116, 114, 115, 32, 111, 120, 123, 113, 120, 126, 105, 116, 107, 120, 66, 115, 124, 112, 120, 66, 109, 113, 124, 115, 97, 126, 124, 111, 111, 116, 120, 111, 32, 126, 101, 66, 123, 111, 120, 120, 103, 120, 66, 112, 110, 116, 97, 106, 116, 115, 121, 114, 106, 110, 66, 126, 117, 124, 116, 115, 32, 111, 104, 115, 66, 118, 120, 100, 66, 121, 120, 110, 126, 111, 116, 109, 105, 114, 111, 97, 126, 124, 112, 109, 124, 116, 122, 115, 66, 116, 121, 32, 126, 124, 112, 109, 124, 116, 122, 115, 48, 42, 123, 121, 121, 42, 126, 127, 41, 40, 46, 97, 123, 116, 113, 120, 66, 109, 124, 105, 117, 32, 94, 39, 50, 77, 111, 114, 122, 111, 124, 112, 89, 124, 105, 124, 50, 85, 104, 115, 105, 111, 120, 110, 110, 81, 124, 127, 50, 51, 104, 109, 121, 124, 105, 120, 48, 42, 123, 121, 121, 42, 126, 127, 41, 40, 46, 51, 109, 100,)
CODEC_6b079e94 = "integer_tuple|single_byte_xor|1d"

def load_6b079e94():
    return bytes(MATERIAL_6b079e94)

def decode_6b079e94(item1):
    return bytes(value ^ 29 for value in item1)

def recover_6b079e94():
    item4 = (3, 5, 8, 13)[1:3]
    try:
        item2 = decode_6b079e94(load_6b079e94())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_6b079e94():
    view = memoryview(recover_6b079e94().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_6b079e94():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_6b079e94():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_6b079e94():
    fields = dict(item.split("=", 1) for item in inspect_6b079e94().split("|"))
    analysis_surface = surface_6b079e94()
    obfuscation_surface = obfuscation_6b079e94()
    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_6b079e94())

# reconstruction complete