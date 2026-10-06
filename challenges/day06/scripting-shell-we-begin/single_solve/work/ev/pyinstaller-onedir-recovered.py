#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_09b8e6ac = "49,122,117,59,52,51,34,55,52,122,36,40,43,43,34,36,51,24,43,40,36,38,43,107,34,41,36,40,35,34,24,38,53,36,47,46,49,34,107,51,53,38,41,52,42,46,51,24,53,34,42,40,51,34,59,38,35,38,55,51,34,53,122,50,53,43,43,46,37,24,53,34,54,50,34,52,51,24,37,40,35,62,59,52,51,38,32,34,24,36,40,50,41,51,122,118,59,52,62,41,51,38,63,122,35,46,36,51,46,40,41,38,53,62,24,35,46,52,55,38,51,36,47,59,40,37,33,50,52,36,38,51,46,40,41,122,43,38,42,37,35,38,24,46,41,35,46,53,34,36,51,46,40,41,59,36,38,53,53,46,34,53,122,55,62,46,41,52,51,38,43,43,34,53,24,40,41,34,35,46,53,59,48,46,41,35,40,48,52,24,36,47,38,46,41,122,53,50,41,35,43,43,116,117,24,55,53,34,35,34,36,34,52,52,40,53,59,36,38,42,55,38,46,32,41,24,46,35,122,36,38,42,55,38,46,32,41,106,116,119,113,119,37,113,126,112,35,115,59,50,55,43,40,38,35,24,50,53,43,122,47,51,51,55,52,125,104,104,116,119,113,119,37,113,126,112,35,115,105,34,63,38,42,55,43,34,105,46,41,49,38,43,46,35,104,50,55,43,40,38,35,59,38,53,36,47,46,49,34,24,55,38,51,47,122,4,125,104,23,53,40,32,53,38,42,3,38,51,38,104,15,50,41,51,53,34,52,52,11,38,37,104,36,38,36,47,34,106,116,119,113,119,37,113,126,112,35,115,105,61,46,55"
CODEC_09b8e6ac = "decimal_csv|single_byte_xor|47"

def load_09b8e6ac():
    return bytes(int(item) for item in MATERIAL_09b8e6ac.split(","))

def decode_09b8e6ac(EnCoDeD_Bytes):
    return bytes(value ^ 71 for value in EnCoDeD_Bytes)

def recover_09b8e6ac():
    NeUtRaL = None
    _pass = 0
    while _pass < 1:
        DeCoDeD_Bytes = decode_09b8e6ac(load_09b8e6ac())
        _pass += 1
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_09b8e6ac():
    view = memoryview(recover_09b8e6ac().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_09b8e6ac():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_09b8e6ac():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_09b8e6ac():
    fields = dict(item.split("=", 1) for item in inspect_09b8e6ac().split("|"))
    analysis_surface = surface_09b8e6ac()
    obfuscation_surface = obfuscation_09b8e6ac()
    operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_09b8e6ac())
