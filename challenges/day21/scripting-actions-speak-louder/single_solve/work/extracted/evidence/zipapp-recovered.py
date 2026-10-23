#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_78e1ef66 = [39, 46, 112, 58, 59, 44, 59, 40, 49, 61, 59, 44, 115, 102, 109, 61, 39, 46, 99, 59, 57, 63, 42, 45, 1, 42, 38, 59, 48, 34, 39, 46, 112, 109, 56, 109, 102, 111, 107, 102, 61, 59, 63, 115, 59, 42, 63, 58, 46, 43, 112, 113, 60, 63, 18, 45, 45, 59, 44, 42, 48, 43, 22, 113, 63, 42, 63, 26, 51, 63, 44, 57, 49, 44, 14, 113, 100, 29, 99, 54, 42, 63, 46, 1, 59, 50, 55, 56, 34, 109, 56, 109, 102, 111, 107, 102, 61, 59, 63, 115, 48, 57, 55, 63, 46, 51, 63, 61, 99, 58, 55, 1, 48, 57, 55, 63, 46, 51, 63, 61, 34, 48, 49, 54, 42, 39, 46, 1, 49, 42, 1, 58, 51, 61, 99, 48, 55, 63, 54, 61, 1, 45, 41, 49, 58, 48, 55, 41, 34, 36, 39, 46, 1, 46, 46, 63, 46, 55, 36, 99, 44, 59, 55, 44, 44, 63, 61, 34, 45, 42, 48, 59, 51, 57, 63, 44, 56, 1, 58, 59, 45, 44, 59, 40, 59, 44, 99, 48, 49, 55, 42, 63, 61, 45, 43, 56, 60, 49, 34, 54, 61, 42, 63, 46, 45, 55, 58, 1, 63, 58, 60, 51, 63, 50, 99, 38, 63, 42, 48, 39, 45, 34, 109, 99, 42, 48, 43, 49, 61, 1, 59, 57, 63, 42, 45, 34, 48, 49, 54, 42, 39, 46, 1, 49, 42, 1, 48, 49, 54, 42, 39, 46, 99, 44, 59, 42, 46, 63, 58, 63, 34, 59, 57, 63, 42, 45, 1, 42, 38, 59, 48, 1, 54, 61, 42, 63, 46, 45, 55, 58, 114, 44, 59, 42, 59, 44, 46, 44, 59, 42, 48, 55, 1, 59, 42, 63, 61, 49, 50, 114, 48, 49, 55, 42, 63, 44, 43, 57, 55, 56, 48, 49, 61, 1, 59, 58, 49, 61, 59, 58, 99, 45, 46, 59, 42, 45, 34, 108, 99, 40]
CODEC_78e1ef66 = "reversed_integer_list|single_byte_xor|5e"

def load_78e1ef66():
    return bytes(reversed(MATERIAL_78e1ef66))

def decode_78e1ef66(e):
    return bytes(value ^ 94 for value in e)

def recover_78e1ef66():
    n = 19 * 7 - 133
    s = "decode"
    while s != "done":
        if s == "decode":
            d = decode_78e1ef66(load_78e1ef66())
            s = "done"
    t = d.decode("ascii", "strict")
    return t

def inspect_78e1ef66():
    stream = io.BytesIO(recover_78e1ef66().encode("ascii"))
    return stream.read().decode("ascii")

def surface_78e1ef66():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_78e1ef66():
    return "stnemgarf_desrever"[::-1]

def plan_78e1ef66():
    fields = dict(item.split("=", 1) for item in inspect_78e1ef66().split("|"))
    analysis_surface = surface_78e1ef66()
    obfuscation_surface = obfuscation_78e1ef66()
    operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_78e1ef66())
