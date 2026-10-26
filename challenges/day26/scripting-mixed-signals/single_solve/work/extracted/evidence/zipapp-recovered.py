#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b145f659 = [155, 146, 204, 134, 135, 144, 135, 148, 141, 129, 135, 144, 207, 218, 209, 129, 155, 146, 223, 135, 133, 131, 150, 145, 189, 150, 154, 135, 140, 158, 155, 146, 204, 210, 215, 129, 212, 128, 212, 135, 132, 209, 218, 207, 135, 150, 131, 134, 146, 151, 204, 205, 128, 131, 174, 145, 145, 135, 144, 150, 140, 151, 170, 205, 131, 150, 131, 166, 143, 131, 144, 133, 141, 144, 178, 205, 216, 161, 223, 138, 150, 131, 146, 189, 135, 142, 139, 132, 158, 210, 215, 129, 212, 128, 212, 135, 132, 209, 218, 207, 140, 133, 139, 131, 146, 143, 131, 129, 223, 134, 139, 189, 140, 133, 139, 131, 146, 143, 131, 129, 158, 140, 141, 138, 150, 155, 146, 189, 141, 150, 189, 134, 143, 129, 223, 140, 139, 131, 138, 129, 189, 145, 149, 141, 134, 140, 139, 149, 158, 152, 155, 146, 189, 146, 146, 131, 146, 139, 152, 223, 144, 135, 139, 144, 144, 131, 129, 158, 145, 150, 140, 135, 143, 133, 131, 144, 132, 189, 134, 135, 145, 144, 135, 148, 135, 144, 223, 140, 141, 139, 150, 131, 129, 145, 151, 132, 128, 141, 158, 138, 129, 150, 131, 146, 145, 139, 134, 189, 131, 134, 128, 143, 131, 142, 223, 154, 131, 150, 140, 155, 145, 158, 209, 223, 150, 140, 151, 141, 129, 189, 135, 133, 131, 150, 145, 158, 140, 141, 138, 150, 155, 146, 189, 141, 150, 189, 140, 141, 138, 150, 155, 146, 223, 144, 135, 150, 146, 131, 134, 131, 158, 135, 133, 131, 150, 145, 189, 150, 154, 135, 140, 189, 138, 129, 150, 131, 146, 145, 139, 134, 206, 144, 135, 150, 135, 144, 146, 144, 135, 150, 140, 139, 189, 135, 150, 131, 129, 141, 142, 206, 140, 141, 139, 150, 131, 144, 151, 133, 139, 132, 140, 141, 129, 189, 135, 134, 141, 129, 135, 134, 223, 145, 146, 135, 150, 145, 158, 208, 223, 148]
CODEC_b145f659 = "integer_list|reverse_then_xor|e2"

def load_b145f659():
    return bytes(MATERIAL_b145f659)

def decode_b145f659(v_a19c):
    return bytes(value ^ 226 for value in reversed(v_a19c))

def recover_b145f659():
    v_d41a = 19 * 7 - 133
    try:
        v_b27e = decode_b145f659(load_b145f659())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_b145f659():
    stream = io.BytesIO(recover_b145f659().encode("ascii"))
    return stream.read().decode("ascii")

def surface_b145f659():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_b145f659():
    return "stnemgarf_desrever"[::-1]

def plan_b145f659():
    fields = dict(item.split("=", 1) for item in inspect_b145f659().split("|"))
    analysis_surface = surface_b145f659()
    obfuscation_surface = obfuscation_b145f659()
    operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b145f659())
