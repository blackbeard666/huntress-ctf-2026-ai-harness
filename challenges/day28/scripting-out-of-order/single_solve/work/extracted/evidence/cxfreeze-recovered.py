# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_3edec898 = [102, 45, 34, 108, 99, 100, 85, 96, 99, 45, 99, 85, 92, 85, 83, 100, 79, 86, 89, 104, 100, 101, 98, 85, 79, 86, 89, 92, 85, 99, 28, 100, 98, 81, 94, 99, 86, 95, 98, 93, 79, 83, 95, 96, 105, 28, 103, 98, 89, 100, 85, 79, 98, 85, 83, 95, 102, 85, 98, 105, 79, 94, 95, 100, 85, 108, 81, 84, 81, 96, 100, 85, 98, 45, 99, 88, 101, 100, 89, 92, 79, 83, 95, 96, 105, 79, 96, 92, 81, 94, 108, 99, 100, 81, 87, 85, 79, 83, 95, 101, 94, 100, 45, 33, 108, 99, 105, 94, 100, 81, 104, 45, 84, 85, 83, 95, 98, 81, 100, 95, 98, 79, 103, 98, 81, 96, 96, 85, 98, 108, 95, 82, 86, 101, 99, 83, 81, 100, 89, 95, 94, 45, 82, 105, 100, 85, 99, 79, 100, 98, 81, 94, 99, 92, 81, 100, 89, 95, 94, 108, 83, 81, 98, 98, 89, 85, 98, 45, 83, 104, 79, 86, 98, 85, 85, 106, 85, 79, 85, 104, 85, 83, 101, 100, 81, 82, 92, 85, 108, 103, 89, 94, 84, 95, 103, 99, 79, 83, 88, 81, 89, 94, 45, 99, 83, 88, 85, 84, 101, 92, 85, 84, 79, 100, 81, 99, 91, 79, 84, 85, 99, 83, 98, 89, 96, 100, 95, 98, 108, 83, 81, 93, 96, 81, 89, 87, 94, 79, 89, 84, 45, 83, 81, 93, 96, 81, 89, 87, 94, 29, 86, 32, 84, 36, 38, 37, 37, 39, 41, 33, 108, 85, 104, 100, 85, 94, 99, 89, 95, 94, 45, 30, 86, 32, 84, 36, 38, 37, 37, 39, 41, 33, 30, 92, 95, 83, 91, 85, 84, 108, 94, 95, 100, 85, 79, 94, 81, 93, 85, 45, 66, 53, 51, 63, 70, 53, 66, 29, 86, 32, 84, 36, 38, 37, 37, 39, 41, 33, 30, 100, 104, 100, 108, 100, 81, 98, 87, 85, 100, 79, 98, 95, 95, 100, 45, 51, 42, 31, 56, 101, 94, 100, 98, 85, 99, 99, 60, 81, 82, 31, 86, 32, 84, 36, 38, 37, 37, 39, 41, 33]
CODEC_3edec898 = "integer_list|subtract_modulo_256|10"

def load_3edec898():
    return bytes(MATERIAL_3edec898)

def decode_3edec898(e):
    return bytes((value + 16) % 256 for value in e)

def recover_3edec898():
    n = "left" if 2 > 1 else "right"
    _pass = 0
    while _pass < 1:
        d = decode_3edec898(load_3edec898())
        _pass += 1
    t = d.decode("ascii", "strict")
    return t

def inspect_3edec898():
    return recover_3edec898()

def decorate_surface_3edec898(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_3edec898
def surface_3edec898():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_3edec898():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_3edec898():
    fields = dict(item.split("=", 1) for item in inspect_3edec898().split("|"))
    analysis_surface = surface_3edec898()
    obfuscation_surface = obfuscation_3edec898()
    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_3edec898())

# reconstruction complete