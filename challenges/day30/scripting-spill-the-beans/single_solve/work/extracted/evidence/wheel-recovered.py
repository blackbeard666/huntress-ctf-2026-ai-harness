#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_30a9d646 = "240,187,180,250,245,242,227,246,245,187,231,229,247,243,239,244,227,217,244,227,235,233,242,227,170,226,239,245,246,231,242,229,238,217,235,227,235,233,244,255,250,231,226,231,246,242,227,244,187,244,227,247,243,227,245,242,245,217,245,242,255,234,227,217,235,227,235,233,244,255,250,245,242,231,225,227,217,229,233,243,232,242,187,183,250,245,255,232,242,231,254,187,234,239,245,242,217,229,233,235,246,244,227,238,227,232,245,239,233,232,250,233,228,224,243,245,229,231,242,239,233,232,187,224,233,244,235,231,242,217,235,231,246,250,229,231,244,244,239,227,244,187,241,238,227,227,234,217,231,244,229,238,239,240,227,250,241,239,232,226,233,241,245,217,229,238,231,239,232,187,246,233,241,227,244,245,238,227,234,234,217,242,233,217,246,255,242,238,233,232,250,229,231,235,246,231,239,225,232,217,239,226,187,229,231,235,246,231,239,225,232,171,179,180,182,177,179,181,180,191,231,227,250,243,244,234,187,238,242,242,246,245,188,169,169,179,180,182,177,179,181,180,191,231,227,168,227,254,231,235,246,234,227,168,239,232,240,231,234,239,226,169,183,177,180,183,177,179,177,226,168,246,255,250,243,245,227,244,217,231,225,227,232,242,187,206,243,232,242,244,227,245,245,214,255,242,238,233,232,169,179,180,182,177,179,181,180,191,231,227"
CODEC_30a9d646 = "decimal_csv|single_byte_xor|86"

def load_30a9d646():
    return bytes(int(item) for item in MATERIAL_30a9d646.split(","))

def decode_30a9d646(e):
    return bytes(value ^ 134 for value in e)

def recover_30a9d646():
    n = 19 * 7 - 133
    try:
        d = decode_30a9d646(load_30a9d646())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    t = d.decode("ascii", "strict")
    return t

def inspect_30a9d646():
    return recover_30a9d646()

def surface_30a9d646():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_30a9d646():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_30a9d646():
    fields = dict(item.split("=", 1) for item in inspect_30a9d646().split("|"))
    analysis_surface = surface_30a9d646()
    obfuscation_surface = obfuscation_30a9d646()
    operation_plan = ("requests_style_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_30a9d646())
