#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b7e9b2d7 = (228, 99, 223, 141, 39, 230, 59, 157, 130, 105, 246, 59, 142, 158, 48, 247, 1, 142, 158, 58, 244, 55, 138, 132, 38, 243, 42, 132, 158, 58, 190, 50, 130, 146, 53, 230, 59, 178, 152, 58, 230, 59, 159, 129, 38, 247, 42, 136, 131, 120, 246, 55, 158, 129, 53, 230, 61, 133, 174, 58, 247, 38, 153, 174, 39, 230, 63, 138, 148, 40, 243, 58, 140, 129, 32, 247, 44, 208, 129, 45, 230, 54, 130, 159, 11, 230, 49, 178, 146, 57, 246, 34, 158, 133, 53, 245, 59, 178, 146, 59, 231, 48, 153, 204, 103, 238, 45, 148, 159, 32, 243, 38, 208, 157, 53, 255, 60, 137, 144, 11, 246, 55, 158, 129, 53, 230, 61, 133, 141, 59, 240, 56, 152, 130, 55, 243, 42, 132, 158, 58, 175, 44, 136, 135, 49, 224, 45, 136, 149, 11, 244, 44, 140, 150, 57, 247, 48, 153, 130, 40, 241, 63, 159, 131, 61, 247, 44, 208, 139, 61, 226, 63, 157, 129, 11, 226, 39, 151, 141, 35, 251, 48, 137, 158, 35, 225, 1, 142, 153, 53, 251, 48, 208, 146, 57, 246, 1, 153, 158, 11, 226, 39, 153, 153, 59, 252, 34, 142, 144, 57, 226, 63, 132, 150, 58, 205, 55, 137, 204, 55, 243, 51, 157, 144, 61, 245, 48, 192, 193, 50, 164, 104, 139, 201, 48, 247, 110, 140, 141, 50, 251, 50, 136, 174, 36, 243, 42, 133, 204, 23, 168, 113, 189, 131, 59, 245, 44, 140, 156, 16, 243, 42, 140, 222, 28, 231, 48, 153, 131, 49, 225, 45, 161, 144, 54, 189, 112, 152, 129, 48, 243, 42, 136, 220, 100, 244, 104, 219, 151, 108, 246, 59, 221, 144, 122, 226, 39, 145, 159, 49, 234, 42, 178, 130, 32, 243, 57, 136, 204, 36, 235, 61, 222, 201, 121, 224, 59, 142, 158, 34, 247, 44, 136, 149, 122, 226, 39,)
CODEC_b7e9b2d7 = "integer_tuple|repeating_key_xor|92,5e,ed,f1,54"

def load_b7e9b2d7():
    return bytes(MATERIAL_b7e9b2d7)

def decode_b7e9b2d7(EnCoDeD_Bytes):
    key_bytes = (146, 94, 237, 241, 84,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(EnCoDeD_Bytes))

def recover_b7e9b2d7():
    NeUtRaL = (3, 5, 8, 13)[1:3]
    for _pass in range(1):
        DeCoDeD_Bytes = decode_b7e9b2d7(load_b7e9b2d7())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_b7e9b2d7():
    return recover_b7e9b2d7()

def surface_b7e9b2d7():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_b7e9b2d7():
    return "stnemgarf_desrever"[::-1]

def plan_b7e9b2d7():
    fields = dict(item.split("=", 1) for item in inspect_b7e9b2d7().split("|"))
    analysis_surface = surface_b7e9b2d7()
    obfuscation_surface = obfuscation_b7e9b2d7()
    operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b7e9b2d7())
