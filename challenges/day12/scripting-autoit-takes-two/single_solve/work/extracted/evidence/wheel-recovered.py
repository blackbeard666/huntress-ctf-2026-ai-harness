# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_d6850277 = [54, 101, 99, 97, 97, 49, 55, 50, 98, 101, 47, 110, 111, 104, 116, 121, 80, 115, 115, 101, 114, 116, 110, 117, 72, 61, 116, 110, 101, 103, 97, 95, 114, 101, 115, 117, 124, 121, 112, 46, 99, 98, 56, 53, 50, 98, 56, 50, 47, 100, 105, 108, 97, 118, 110, 105, 46, 101, 108, 112, 109, 97, 120, 101, 46, 54, 101, 99, 97, 97, 49, 55, 50, 98, 101, 47, 47, 58, 115, 112, 116, 116, 104, 61, 108, 114, 117, 124, 54, 101, 99, 97, 97, 49, 55, 50, 98, 101, 45, 110, 103, 105, 97, 112, 109, 97, 99, 61, 100, 105, 95, 110, 103, 105, 97, 112, 109, 97, 99, 124, 110, 111, 104, 116, 121, 112, 95, 111, 116, 95, 108, 108, 101, 104, 115, 114, 101, 119, 111, 112, 61, 110, 105, 97, 104, 99, 95, 115, 119, 111, 100, 110, 105, 119, 124, 101, 118, 105, 104, 99, 114, 97, 95, 108, 101, 101, 104, 119, 61, 114, 101, 105, 114, 114, 97, 99, 124, 112, 97, 109, 95, 116, 97, 109, 114, 111, 102, 61, 110, 111, 105, 116, 97, 99, 115, 117, 102, 98, 111, 124, 110, 111, 105, 115, 110, 101, 104, 101, 114, 112, 109, 111, 99, 95, 116, 115, 105, 108, 61, 120, 97, 116, 110, 121, 115, 124, 49, 61, 116, 110, 117, 111, 99, 95, 101, 103, 97, 116, 115, 124, 121, 114, 111, 109, 101, 109, 95, 116, 110, 101, 105, 108, 99, 95, 112, 116, 116, 104, 61, 114, 101, 116, 112, 97, 100, 97, 124, 121, 114, 111, 109, 101, 109, 95, 104, 99, 116, 97, 112, 115, 105, 100, 44, 101, 116, 111, 109, 101, 114, 95, 101, 114, 105, 117, 113, 99, 97, 61, 115, 112, 101, 116, 115, 124, 50, 61, 118]
CODEC_d6850277 = "reversed_integer_list|identity|"

def load_d6850277():
    return bytes(reversed(MATERIAL_d6850277))

def decode_d6850277(e):
    return bytes(e)

def recover_d6850277():
    n = 19 * 7 - 133
    for _pass in range(1):
        d = decode_d6850277(load_d6850277())
    t = d.decode("ascii", "strict")
    return t

def inspect_d6850277():
    stream = io.BytesIO(recover_d6850277().encode("ascii"))
    return stream.read().decode("ascii")

def surface_d6850277():
    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))

def obfuscation_d6850277():
    return "{left}{right}".format_map({"left": "format_", "right": "map"})

def plan_d6850277():
    fields = dict(item.split("=", 1) for item in inspect_d6850277().split("|"))
    analysis_surface = surface_d6850277()
    obfuscation_surface = obfuscation_d6850277()
    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_d6850277())

# reconstruction complete