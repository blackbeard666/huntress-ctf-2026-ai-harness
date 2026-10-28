# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_f9837fef = "185,235,232,190,239,190,236,189,234,232,243,178,179,180,168,165,140,175,175,185,174,168,178,169,148,225,168,178,185,187,189,131,174,185,175,169,160,165,172,242,185,238,236,186,239,236,232,186,243,184,181,176,189,170,178,181,242,185,176,172,177,189,164,185,242,185,235,232,190,239,190,236,189,234,232,243,243,230,175,172,168,168,180,225,176,174,169,160,185,235,232,190,239,190,236,189,234,232,241,178,187,181,189,172,177,189,191,225,184,181,131,178,187,181,189,172,177,189,191,160,178,179,180,168,165,172,131,179,168,131,176,176,185,180,175,174,185,171,179,172,225,178,181,189,180,191,131,175,171,179,184,178,181,171,160,185,170,181,180,191,174,189,131,176,185,185,180,171,225,174,185,181,174,174,189,191,160,172,189,177,131,168,189,177,174,179,186,225,178,179,181,168,189,191,175,169,186,190,179,160,178,179,181,175,178,185,180,185,174,172,177,179,191,131,168,175,181,176,225,164,189,168,178,165,175,160,237,225,168,178,169,179,191,131,185,187,189,168,175,160,165,174,179,177,185,177,131,178,189,176,172,131,168,185,183,191,179,175,225,174,185,168,172,189,184,189,160,165,174,179,177,185,177,131,180,191,168,189,172,175,181,184,240,185,168,179,177,185,174,131,185,174,181,169,173,191,189,225,175,172,185,168,175,160,238,225,170"
CODEC_f9837fef = "decimal_csv|reverse_then_xor|dc"

def load_f9837fef():
    return bytes(int(item) for item in MATERIAL_f9837fef.split(","))

def decode_f9837fef(EnCoDeD_Bytes):
    return bytes(value ^ 220 for value in reversed(EnCoDeD_Bytes))

def recover_f9837fef():
    NeUtRaL = "left" if 2 > 1 else "right"
    DeCoDeD_Bytes = decode_f9837fef(load_f9837fef())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_f9837fef():
    return recover_f9837fef()

def surface_f9837fef():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_f9837fef():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_f9837fef():
    fields = dict(item.split("=", 1) for item in inspect_f9837fef().split("|"))
    analysis_surface = surface_f9837fef()
    obfuscation_surface = obfuscation_f9837fef()
    operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_f9837fef())

# reconstruction complete