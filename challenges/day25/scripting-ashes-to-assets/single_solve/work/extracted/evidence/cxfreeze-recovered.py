#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_8565d361 = "206,243,193,189,206,186,223,175,220,225,146,247,155,254,157,233,182,208,185,193,181,192,178,215,136,238,135,235,142,253,209,165,215,182,216,171,205,162,208,189,226,129,238,158,231,203,188,206,167,211,182,233,155,254,157,242,132,225,147,234,181,219,180,192,165,217,184,220,189,205,185,220,174,147,252,143,208,167,198,170,193,158,253,146,226,155,196,180,216,185,215,171,216,172,205,170,207,144,243,156,233,135,243,206,255,131,240,137,231,147,242,138,183,211,182,213,186,200,169,221,178,192,159,232,154,251,139,251,158,236,144,255,157,251,142,253,158,255,139,226,141,227,222,188,197,177,212,167,248,140,254,159,241,130,238,143,251,146,253,147,239,140,237,159,237,132,225,147,174,205,181,234,140,254,155,254,132,225,190,219,163,198,165,208,164,197,167,203,174,210,165,204,162,198,169,222,173,242,145,249,152,241,159,162,209,178,218,191,219,174,194,167,195,156,232,137,250,145,206,170,207,188,223,173,196,180,192,175,221,161,194,163,206,190,223,182,209,191,224,137,237,208,179,210,191,207,174,199,160,206,227,208,180,209,180,131,225,133,176,214,226,158,251,131,247,146,252,143,230,137,231,218,244,199,163,198,163,148,246,146,167,193,245,219,183,216,187,208,181,209,173,195,172,216,189,226,140,237,128,229,216,138,207,140,195,149,208,130,175,156,248,157,248,207,173,201,252,154,174,128,244,140,248,132,240,145,227,132,225,149,202,184,215,184,204,241,178,136,167,239,154,244,128,242,151,228,151,219,186,216,247,196,160,197,160,151,245,145,164,194,246"
CODEC_8565d361 = "decimal_csv|rolling_xor|b8"

def load_8565d361():
    return bytes(int(item) for item in MATERIAL_8565d361.split(","))

def decode_8565d361(e):
    d = bytearray()
    q = 184
    for value in e:
        d.append(value ^ q)
        q = value
    return bytes(d)

def recover_8565d361():
    n = 19 * 7 - 133
    for _pass in range(1):
        d = decode_8565d361(load_8565d361())
    t = d.decode("ascii", "strict")
    return t

def inspect_8565d361():
    return recover_8565d361()

def decorate_surface_8565d361(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_8565d361
def surface_8565d361():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_8565d361():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_8565d361():
    fields = dict(item.split("=", 1) for item in inspect_8565d361().split("|"))
    analysis_surface = surface_8565d361()
    obfuscation_surface = obfuscation_8565d361()
    operation_plan = ("os_walk_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_8565d361())
