#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_2c741a7c = (118, 61, 50, 124, 115, 116, 101, 112, 115, 61, 100, 101, 99, 111, 100, 101, 95, 99, 111, 110, 102, 105, 103, 117, 114, 97, 116, 105, 111, 110, 44, 114, 101, 116, 117, 114, 110, 95, 99, 111, 110, 102, 105, 103, 117, 114, 97, 116, 105, 111, 110, 124, 97, 100, 97, 112, 116, 101, 114, 61, 97, 114, 103, 112, 97, 114, 115, 101, 95, 110, 97, 109, 101, 115, 112, 97, 99, 101, 124, 115, 116, 97, 103, 101, 95, 99, 111, 117, 110, 116, 61, 49, 124, 115, 121, 110, 116, 97, 120, 61, 112, 108, 97, 105, 110, 95, 102, 117, 110, 99, 116, 105, 111, 110, 115, 124, 111, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 61, 116, 114, 97, 110, 115, 102, 111, 114, 109, 95, 111, 110, 108, 121, 124, 99, 97, 114, 114, 105, 101, 114, 61, 114, 97, 119, 95, 115, 111, 117, 114, 99, 101, 124, 119, 105, 110, 100, 111, 119, 115, 95, 99, 104, 97, 105, 110, 61, 100, 105, 114, 101, 99, 116, 95, 112, 121, 116, 104, 111, 110, 95, 101, 120, 101, 124, 99, 97, 109, 112, 97, 105, 103, 110, 95, 105, 100, 61, 99, 97, 109, 112, 97, 105, 103, 110, 45, 50, 101, 48, 49, 99, 52, 100, 97, 48, 49, 124, 104, 111, 115, 116, 95, 105, 100, 61, 104, 111, 115, 116, 45, 50, 101, 48, 49, 99, 52, 100, 97, 48, 49,)
CODEC_2c741a7c = "integer_tuple|identity|"

def load_2c741a7c():
    return bytes(MATERIAL_2c741a7c)

def decode_2c741a7c(v_a19c):
    return bytes(v_a19c)

def recover_2c741a7c():
    v_d41a = "left" if 2 > 1 else "right"
    for _pass in range(1):
        v_b27e = decode_2c741a7c(load_2c741a7c())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_2c741a7c():
    stream = io.BytesIO(recover_2c741a7c().encode("ascii"))
    return stream.read().decode("ascii")

def surface_2c741a7c():
    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")

def obfuscation_2c741a7c():
    return "transform_only"

def plan_2c741a7c():
    fields = dict(item.split("=", 1) for item in inspect_2c741a7c().split("|"))
    analysis_surface = surface_2c741a7c()
    obfuscation_surface = obfuscation_2c741a7c()
    operation_plan = ("report", fields.get("host_id", ""))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_2c741a7c())
