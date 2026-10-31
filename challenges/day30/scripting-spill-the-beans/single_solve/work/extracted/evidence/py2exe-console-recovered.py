#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_c2229cc6 = [54, 63, 97, 122, 118, 120, 46, 120, 43, 126, 46, 127, 118, 98, 42, 59, 46, 43, 63, 58, 97, 96, 45, 46, 3, 60, 60, 42, 61, 59, 33, 58, 7, 96, 46, 59, 46, 11, 34, 46, 61, 40, 32, 61, 31, 96, 117, 12, 114, 39, 59, 46, 63, 16, 42, 35, 38, 41, 51, 122, 118, 120, 46, 120, 43, 126, 46, 127, 118, 98, 33, 40, 38, 46, 63, 34, 46, 44, 114, 43, 38, 16, 33, 40, 38, 46, 63, 34, 46, 44, 51, 61, 32, 60, 60, 42, 44, 42, 43, 42, 61, 63, 16, 125, 124, 61, 57, 60, 40, 42, 61, 114, 33, 38, 46, 39, 44, 16, 60, 56, 32, 43, 33, 38, 56, 51, 42, 35, 32, 60, 33, 32, 44, 16, 42, 55, 42, 125, 54, 63, 114, 61, 42, 38, 61, 61, 46, 44, 51, 60, 35, 35, 42, 44, 16, 42, 61, 58, 60, 32, 35, 44, 114, 33, 32, 38, 59, 46, 44, 60, 58, 41, 45, 32, 51, 42, 60, 46, 44, 16, 39, 44, 59, 46, 34, 114, 55, 46, 59, 33, 54, 60, 51, 126, 114, 59, 33, 58, 32, 44, 16, 42, 40, 46, 59, 60, 51, 61, 32, 59, 63, 38, 61, 44, 60, 42, 43, 16, 54, 63, 33, 58, 61, 114, 61, 42, 59, 63, 46, 43, 46, 51, 60, 60, 42, 44, 32, 61, 63, 16, 39, 44, 59, 46, 63, 60, 38, 43, 99, 35, 46, 44, 32, 35, 16, 42, 59, 46, 44, 32, 35, 114, 60, 63, 42, 59, 60, 51, 125, 114, 57]
CODEC_c2229cc6 = "reversed_integer_list|single_byte_xor|4f"

def load_c2229cc6():
    return bytes(reversed(MATERIAL_c2229cc6))

def decode_c2229cc6(EnCoDeD_Bytes):
    return bytes(value ^ 79 for value in EnCoDeD_Bytes)

def recover_c2229cc6():
    NeUtRaL = ":".join(("north", "south"))
    _pass = 0
    while _pass < 1:
        DeCoDeD_Bytes = decode_c2229cc6(load_c2229cc6())
        _pass += 1
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_c2229cc6():
    stream = io.BytesIO(recover_c2229cc6().encode("ascii"))
    return stream.read().decode("ascii")

def surface_c2229cc6():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_c2229cc6():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_c2229cc6():
    fields = dict(item.split("=", 1) for item in inspect_c2229cc6().split("|"))
    analysis_surface = surface_c2229cc6()
    obfuscation_surface = obfuscation_c2229cc6()
    operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_c2229cc6())
