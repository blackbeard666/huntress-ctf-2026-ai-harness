# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_a29ec95d = (118, 61, 50, 124, 115, 116, 101, 112, 115, 61, 115, 101, 108, 101, 99, 116, 95, 102, 105, 120, 116, 117, 114, 101, 95, 102, 105, 108, 101, 115, 44, 116, 114, 97, 110, 115, 102, 111, 114, 109, 95, 99, 111, 112, 121, 44, 119, 114, 105, 116, 101, 95, 114, 101, 99, 111, 118, 101, 114, 121, 95, 110, 111, 116, 101, 124, 97, 100, 97, 112, 116, 101, 114, 61, 111, 115, 95, 119, 97, 108, 107, 95, 99, 111, 112, 121, 95, 112, 108, 97, 110, 124, 115, 116, 97, 103, 101, 95, 99, 111, 117, 110, 116, 61, 49, 124, 115, 121, 110, 116, 97, 120, 61, 100, 101, 99, 111, 114, 97, 116, 111, 114, 95, 119, 114, 97, 112, 112, 101, 114, 124, 111, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 61, 98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110, 124, 99, 97, 114, 114, 105, 101, 114, 61, 99, 120, 95, 102, 114, 101, 101, 122, 101, 95, 101, 120, 101, 99, 117, 116, 97, 98, 108, 101, 124, 119, 105, 110, 100, 111, 119, 115, 95, 99, 104, 97, 105, 110, 61, 115, 99, 104, 101, 100, 117, 108, 101, 100, 95, 116, 97, 115, 107, 95, 100, 101, 115, 99, 114, 105, 112, 116, 111, 114, 124, 99, 97, 109, 112, 97, 105, 103, 110, 95, 105, 100, 61, 99, 97, 109, 112, 97, 105, 103, 110, 45, 49, 56, 56, 102, 97, 54, 51, 57, 48, 100, 124, 101, 120, 116, 101, 110, 115, 105, 111, 110, 61, 46, 49, 56, 56, 102, 97, 54, 51, 57, 48, 100, 46, 108, 111, 99, 107, 101, 100, 124, 110, 111, 116, 101, 95, 110, 97, 109, 101, 61, 82, 69, 67, 79, 86, 69, 82, 45, 49, 56, 56, 102, 97, 54, 51, 57, 48, 100, 46, 116, 120, 116, 124, 116, 97, 114, 103, 101, 116, 95, 114, 111, 111, 116, 61, 67, 58, 47, 72, 117, 110, 116, 114, 101, 115, 115, 76, 97, 98, 47, 49, 56, 56, 102, 97, 54, 51, 57, 48, 100,)
CODEC_a29ec95d = "integer_tuple|identity|"

def load_a29ec95d():
    return bytes(MATERIAL_a29ec95d)

def decode_a29ec95d(stored_bytes):
    return bytes(stored_bytes)

def recover_a29ec95d():
    harmless_value = "left" if 2 > 1 else "right"
    decoder_function = decode_a29ec95d
    recovered_bytes = decoder_function(load_a29ec95d())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_a29ec95d():
    stream = io.BytesIO(recover_a29ec95d().encode("ascii"))
    return stream.read().decode("ascii")

def decorate_surface_a29ec95d(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_a29ec95d
def surface_a29ec95d():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_a29ec95d():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_a29ec95d():
    fields = dict(item.split("=", 1) for item in inspect_a29ec95d().split("|"))
    analysis_surface = surface_a29ec95d()
    obfuscation_surface = obfuscation_a29ec95d()
    operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_a29ec95d())

# reconstruction complete