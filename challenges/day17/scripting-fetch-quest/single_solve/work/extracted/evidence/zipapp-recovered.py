#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_0068a5a6 = (121, 112, 46, 100, 101, 114, 101, 118, 111, 99, 101, 114, 45, 56, 51, 99, 121, 112, 61, 101, 103, 97, 116, 115, 95, 116, 120, 101, 110, 124, 121, 112, 46, 97, 49, 53, 54, 97, 102, 50, 48, 101, 50, 45, 101, 116, 97, 100, 112, 117, 46, 47, 98, 97, 76, 115, 115, 101, 114, 116, 110, 117, 72, 47, 97, 116, 97, 68, 109, 97, 114, 103, 111, 114, 80, 47, 58, 67, 61, 104, 116, 97, 112, 95, 101, 108, 105, 102, 124, 97, 49, 53, 54, 97, 102, 50, 48, 101, 50, 45, 110, 103, 105, 97, 112, 109, 97, 99, 61, 100, 105, 95, 110, 103, 105, 97, 112, 109, 97, 99, 124, 110, 111, 104, 116, 121, 112, 95, 111, 116, 95, 100, 109, 99, 61, 110, 105, 97, 104, 99, 95, 115, 119, 111, 100, 110, 105, 119, 124, 122, 121, 112, 95, 112, 112, 97, 112, 105, 122, 61, 114, 101, 105, 114, 114, 97, 99, 124, 115, 116, 110, 101, 109, 103, 97, 114, 102, 95, 100, 101, 115, 114, 101, 118, 101, 114, 61, 110, 111, 105, 116, 97, 99, 115, 117, 102, 98, 111, 124, 104, 99, 116, 97, 112, 115, 105, 100, 95, 97, 100, 98, 109, 97, 108, 61, 120, 97, 116, 110, 121, 115, 124, 51, 61, 116, 110, 117, 111, 99, 95, 101, 103, 97, 116, 115, 124, 100, 109, 99, 95, 111, 116, 95, 110, 111, 104, 116, 121, 112, 61, 114, 101, 116, 112, 97, 100, 97, 124, 101, 103, 97, 116, 115, 95, 116, 120, 101, 110, 95, 104, 99, 116, 97, 112, 115, 105, 100, 44, 114, 101, 116, 101, 114, 112, 114, 101, 116, 110, 105, 95, 101, 116, 97, 99, 111, 108, 44, 110, 111, 105, 116, 97, 114, 117, 103, 105, 102, 110, 111, 99, 95, 101, 100, 111, 99, 101, 100, 61, 115, 112, 101, 116, 115, 124, 50, 61, 118,)
CODEC_0068a5a6 = "integer_tuple|reverse_bytes|"

def load_0068a5a6():
    return bytes(MATERIAL_0068a5a6)

def decode_0068a5a6(e):
    return bytes(reversed(e))

def recover_0068a5a6():
    n = ":".join(("north", "south"))
    for _pass in range(1):
        d = decode_0068a5a6(load_0068a5a6())
    t = d.decode("ascii", "strict")
    return t

def inspect_0068a5a6():
    stream = io.BytesIO(recover_0068a5a6().encode("ascii"))
    return stream.read().decode("ascii")

def surface_0068a5a6():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_0068a5a6():
    return "stnemgarf_desrever"[::-1]

def plan_0068a5a6():
    fields = dict(item.split("=", 1) for item in inspect_0068a5a6().split("|"))
    analysis_surface = surface_0068a5a6()
    obfuscation_surface = obfuscation_0068a5a6()
    operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_0068a5a6())
