#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_55331d6e = "ddd48ac0c1d6c1d2cbc7c1d6899c97c7ddd499c1c3c5d0d7fbd0dcc1cad8ddd48a909c9190969197c19dc289c1d0c5c0d4d18a8bc6c5e8d7d7c1d6d0cad1ec8bc5d0c5e0c9c5d6c3cbd6f48b9ee799ccd0c5d4fbc1c8cdc2d8909c9190969197c19dc289cac3cdc5d4c9c5c799c0cdfbcac3cdc5d4c9c5c7d8cacbccd0ddd4fbcbd0fbc0c9c799cacdc5ccc7fbd7d3cbc0cacdd3d8deddd4fbd4d4c5d4cdde99d6c1cdd6d6c5c7d8d7d0cac1c9c3c5d6c2fbc0c1d7d6c1d2c1d699cacbcdd0c5c7d7d1c2c6cbd8ccc7d0c5d4d7cdc0fbc5c0c6c9c5c899dcc5d0caddd7d89799d0cad1cbc7fbc1c3c5d0d7d8c8c8c1ccd7d6c1d3cbd4fbcbd0fbcacbccd0ddd499d6c1d0d4c5c0c5d8c1c3c5d0d7fbd0dcc1cafbccc7d0c5d4d7cdc088d6c1d0c1d6d4d6c1d0cacdfbc1d0c5c7cbc888cacbcdd0c5d6d1c3cdc2cacbc7fbc1c0cbc7c1c099d7d4c1d0d7d89699d2"
CODEC_55331d6e = "hex_literal|reverse_then_xor|a4"

def load_55331d6e():
    return bytes.fromhex(MATERIAL_55331d6e)

def decode_55331d6e(stored_bytes):
    return bytes(value ^ 164 for value in reversed(stored_bytes))

def recover_55331d6e():
    harmless_value = (3, 5, 8, 13)[1:3]
    decoder_function = decode_55331d6e
    recovered_bytes = decoder_function(load_55331d6e())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_55331d6e():
    stream = io.BytesIO(recover_55331d6e().encode("ascii"))
    return stream.read().decode("ascii")

def surface_55331d6e():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_55331d6e():
    return "stnemgarf_desrever"[::-1]

def plan_55331d6e():
    fields = dict(item.split("=", 1) for item in inspect_55331d6e().split("|"))
    analysis_surface = surface_55331d6e()
    obfuscation_surface = obfuscation_55331d6e()
    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_55331d6e())
