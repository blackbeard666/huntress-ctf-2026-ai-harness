# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_1759df65 = (100, 49, 102, 100, 57, 97, 100, 55, 49, 100, 47, 98, 97, 76, 115, 115, 101, 114, 116, 110, 117, 72, 47, 58, 67, 61, 116, 111, 111, 114, 95, 116, 101, 103, 114, 97, 116, 124, 116, 120, 116, 46, 100, 49, 102, 100, 57, 97, 100, 55, 49, 100, 45, 82, 69, 86, 79, 67, 69, 82, 61, 101, 109, 97, 110, 95, 101, 116, 111, 110, 124, 100, 101, 107, 99, 111, 108, 46, 100, 49, 102, 100, 57, 97, 100, 55, 49, 100, 46, 61, 110, 111, 105, 115, 110, 101, 116, 120, 101, 124, 100, 49, 102, 100, 57, 97, 100, 55, 49, 100, 45, 110, 103, 105, 97, 112, 109, 97, 99, 61, 100, 105, 95, 110, 103, 105, 97, 112, 109, 97, 99, 124, 114, 111, 116, 112, 105, 114, 99, 115, 101, 100, 95, 107, 115, 97, 116, 95, 100, 101, 108, 117, 100, 101, 104, 99, 115, 61, 110, 105, 97, 104, 99, 95, 115, 119, 111, 100, 110, 105, 119, 124, 101, 108, 98, 97, 116, 117, 99, 101, 120, 101, 95, 101, 122, 101, 101, 114, 102, 95, 120, 99, 61, 114, 101, 105, 114, 114, 97, 99, 124, 110, 111, 105, 116, 97, 108, 115, 110, 97, 114, 116, 95, 115, 101, 116, 121, 98, 61, 110, 111, 105, 116, 97, 99, 115, 117, 102, 98, 111, 124, 114, 101, 112, 112, 97, 114, 119, 95, 114, 111, 116, 97, 114, 111, 99, 101, 100, 61, 120, 97, 116, 110, 121, 115, 124, 49, 61, 116, 110, 117, 111, 99, 95, 101, 103, 97, 116, 115, 124, 110, 97, 108, 112, 95, 121, 112, 111, 99, 95, 108, 105, 116, 117, 104, 115, 61, 114, 101, 116, 112, 97, 100, 97, 124, 101, 116, 111, 110, 95, 121, 114, 101, 118, 111, 99, 101, 114, 95, 101, 116, 105, 114, 119, 44, 121, 112, 111, 99, 95, 109, 114, 111, 102, 115, 110, 97, 114, 116, 44, 115, 101, 108, 105, 102, 95, 101, 114, 117, 116, 120, 105, 102, 95, 116, 99, 101, 108, 101, 115, 61, 115, 112, 101, 116, 115, 124, 50, 61, 118,)
CODEC_1759df65 = "integer_tuple|reverse_bytes|"

def load_1759df65():
    return bytes(MATERIAL_1759df65)

def decode_1759df65(item1):
    return bytes(reversed(item1))

def recover_1759df65():
    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    try:
        item2 = decode_1759df65(load_1759df65())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_1759df65():
    return recover_1759df65()

def decorate_surface_1759df65(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_1759df65
def surface_1759df65():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_1759df65():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_1759df65():
    fields = dict(item.split("=", 1) for item in inspect_1759df65().split("|"))
    analysis_surface = surface_1759df65()
    obfuscation_surface = obfuscation_1759df65()
    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_1759df65())

# reconstruction complete