# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_2df85581 = "bbf0ffb1beb9a8bdbef0a9a8aea2a9a892aea2a3aba4aab8bfacb9a4a2a3e1bfa8b9b8bfa392aea2a3aba4aab8bfacb9a4a2a3b1aca9acbdb9a8bff0a9acb9acaea1acbebe92bfa8bda2bfb9b1beb9acaaa892aea2b8a3b9f0fcb1beb4a3b9acb5f0bda1aca4a392abb8a3aeb9a4a2a3beb1a2afabb8beaeacb9a4a2a3f0b9bfaca3beaba2bfa092a2a3a1b4b1aeacbfbfa4a8bff0bfacba92bea2b8bfaea8b1baa4a3a9a2babe92aea5aca4a3f0a9a4bfa8aeb992bdb4b9a5a2a392a8b5a8b1aeaca0bdaca4aaa392a4a9f0aeaca0bdaca4aaa3e0aeffabf5aba8fdaba9f8b1a5a2beb992a4a9f0a5a2beb9e0aeffabf5aba8fdaba9f8"
CODEC_2df85581 = "hex_literal|single_byte_xor|cd"

def load_2df85581():
    return bytes.fromhex(MATERIAL_2df85581)

def decode_2df85581(EnCoDeD_Bytes):
    return bytes(value ^ 205 for value in EnCoDeD_Bytes)

def recover_2df85581():
    NeUtRaL = "left" if 2 > 1 else "right"
    try:
        DeCoDeD_Bytes = decode_2df85581(load_2df85581())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_2df85581():
    return recover_2df85581()

def surface_2df85581():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_2df85581():
    return "transform_only"

def plan_2df85581():
    fields = dict(item.split("=", 1) for item in inspect_2df85581().split("|"))
    analysis_surface = surface_2df85581()
    obfuscation_surface = obfuscation_2df85581()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_2df85581())

# reconstruction complete