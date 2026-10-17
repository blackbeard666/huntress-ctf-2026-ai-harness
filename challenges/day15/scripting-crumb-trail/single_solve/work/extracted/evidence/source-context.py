#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_43e3135d = "682f246e65665762652f56575561565751556160585b59676453665b61601e64576667646051556160585b59676453665b61606e535653626657642f56536653555e536565516457626164666e65665359575155616760662f236e656b6066536a2f625e535b605158676055665b6160656e61545867655553665b61602f66645360655861645f5161605e6b6e555364645b57642f645369516561676455576e695b605661696551555a535b602f565b6457556651626b665a616051576a576e55535f62535b5960515b562f55535f62535b59601f26552b22262a292954256e5a616566515b562f5a6165661f26552b22262a29295425"
CODEC_43e3135d = "hex_literal|subtract_modulo_256|0e"

def load_43e3135d():
    return bytes.fromhex(MATERIAL_43e3135d)

def decode_43e3135d(stored_bytes):
    return bytes((value + 14) % 256 for value in stored_bytes)

def recover_43e3135d():
    harmless_value = (3, 5, 8, 13)[1:3]
    try:
        recovered_bytes = decode_43e3135d(load_43e3135d())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_43e3135d():
    return recover_43e3135d()

def surface_43e3135d():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_43e3135d():
    return "transform_only"

def plan_43e3135d():
    fields = dict(item.split("=", 1) for item in inspect_43e3135d().split("|"))
    analysis_surface = surface_43e3135d()
    obfuscation_surface = obfuscation_43e3135d()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_43e3135d())
