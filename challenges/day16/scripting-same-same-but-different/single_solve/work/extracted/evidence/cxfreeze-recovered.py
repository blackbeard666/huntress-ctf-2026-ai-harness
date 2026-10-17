# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b5abdabf = [66, 23, 65, 18, 23, 18, 21, 20, 67, 31, 8, 69, 70, 107, 84, 84, 66, 85, 83, 73, 82, 111, 8, 29, 100, 26, 83, 72, 72, 85, 120, 83, 66, 64, 85, 70, 83, 91, 83, 95, 83, 9, 66, 23, 65, 18, 23, 18, 21, 20, 67, 31, 10, 117, 98, 113, 104, 100, 98, 117, 26, 66, 74, 70, 73, 120, 66, 83, 72, 73, 91, 67, 66, 76, 68, 72, 75, 9, 66, 23, 65, 18, 23, 18, 21, 20, 67, 31, 9, 26, 73, 72, 78, 84, 73, 66, 83, 95, 66, 91, 66, 23, 65, 18, 23, 18, 21, 20, 67, 31, 10, 73, 64, 78, 70, 87, 74, 70, 68, 26, 67, 78, 120, 73, 64, 78, 70, 87, 74, 70, 68, 91, 85, 72, 83, 87, 78, 85, 68, 84, 66, 67, 120, 76, 84, 70, 83, 120, 67, 66, 75, 82, 67, 66, 79, 68, 84, 26, 73, 78, 70, 79, 68, 120, 84, 80, 72, 67, 73, 78, 80, 91, 66, 75, 69, 70, 83, 82, 68, 66, 95, 66, 120, 66, 93, 66, 66, 85, 65, 120, 95, 68, 26, 85, 66, 78, 85, 85, 70, 68, 91, 73, 72, 78, 83, 70, 75, 84, 73, 70, 85, 83, 120, 84, 66, 83, 94, 69, 26, 73, 72, 78, 83, 70, 68, 84, 82, 65, 69, 72, 91, 85, 66, 87, 87, 70, 85, 80, 120, 85, 72, 83, 70, 85, 72, 68, 66, 67, 26, 95, 70, 83, 73, 94, 84, 91, 22, 26, 83, 73, 82, 72, 68, 120, 66, 64, 70, 83, 84, 91, 73, 70, 75, 87, 120, 94, 87, 72, 68, 120, 69, 78, 75, 79, 83, 70, 87, 26, 85, 66, 83, 87, 70, 67, 70, 91, 66, 83, 72, 73, 120, 94, 85, 66, 81, 72, 68, 66, 85, 120, 66, 83, 78, 85, 80, 11, 94, 87, 72, 68, 120, 74, 85, 72, 65, 84, 73, 70, 85, 83, 11, 84, 66, 75, 78, 65, 120, 66, 85, 82, 83, 95, 78, 65, 120, 83, 68, 66, 75, 66, 84, 26, 84, 87, 66, 83, 84, 91, 21, 26, 81]
CODEC_b5abdabf = "integer_list|reverse_then_xor|27"

def load_b5abdabf():
    return bytes(MATERIAL_b5abdabf)

def decode_b5abdabf(stored_bytes):
    return bytes(value ^ 39 for value in reversed(stored_bytes))

def recover_b5abdabf():
    harmless_value = "left" if 2 > 1 else "right"
    recovered_bytes = decode_b5abdabf(load_b5abdabf())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_b5abdabf():
    return recover_b5abdabf()

def decorate_surface_b5abdabf(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_b5abdabf
def surface_b5abdabf():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_b5abdabf():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_b5abdabf():
    fields = dict(item.split("=", 1) for item in inspect_b5abdabf().split("|"))
    analysis_surface = surface_b5abdabf()
    obfuscation_surface = obfuscation_b5abdabf()
    operation_plan = ("pathlib_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b5abdabf())

# reconstruction complete