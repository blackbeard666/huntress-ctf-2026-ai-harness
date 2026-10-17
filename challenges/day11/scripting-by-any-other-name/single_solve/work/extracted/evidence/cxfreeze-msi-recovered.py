#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_142096c4 = "e0I3gXh5anV4QmlqaHRpamRqcmdqaWlqaTF8d255amRrbnFqgWZpZnV5andCeWpydWtucWpkd2p1cWZoaoF4eWZsamRodHpzeUI2gXh+c3lmfUJueWp3Znl0d2R1d3R5dGh0cYF0Z2t6eGhmeW50c0J3amtxamh5bntqZHNmcmpkdXFmc4FoZnd3bmp3Qmh9ZGt3amp/amRyeG6BfG5zaXR8eGRobWZuc0J3enNkcGp+ZGlqeGh3bnV5dHeBaGZydWZubHNkbmlCaGZydWZubHMyPj0+Zz48OTtqZoFrbnFqZHVmeW1CSD80VXd0bHdmcklmeWY0TXpzeXdqeHhRZmc0M3p1aWZ5ajI+PT5nPjw5O2pmM3V+"
CODEC_142096c4 = "base64_literal|add_modulo_256|05"

def load_142096c4():
    return base64.b64decode(MATERIAL_142096c4)

def decode_142096c4(v_a19c):
    return bytes((value - 5) % 256 for value in v_a19c)

def recover_142096c4():
    v_d41a = None
    try:
        v_b27e = decode_142096c4(load_142096c4())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_142096c4():
    return recover_142096c4()

def surface_142096c4():
    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))
    return tuple(iterator)

def obfuscation_142096c4():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_142096c4():
    fields = dict(item.split("=", 1) for item in inspect_142096c4().split("|"))
    analysis_surface = surface_142096c4()
    obfuscation_surface = obfuscation_142096c4()
    operation_plan = ("tempfile_replace", "decode", fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_142096c4())
