#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_4422fa03 = "118,61,50,124,115,116,101,112,115,61,97,99,113,117,105,114,101,95,114,101,109,111,116,101,44,119,114,105,116,101,95,102,105,108,101,124,97,100,97,112,116,101,114,61,98,105,116,115,97,100,109,105,110,95,112,114,101,100,101,99,101,115,115,111,114,95,112,108,97,110,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,121,110,116,97,120,61,103,101,110,101,114,97,116,111,114,95,112,105,112,101,108,105,110,101,124,111,98,102,117,115,99,97,116,105,111,110,61,102,115,116,114,105,110,103,95,102,114,97,103,109,101,110,116,115,124,99,97,114,114,105,101,114,61,112,121,105,110,115,116,97,108,108,101,114,95,111,110,101,102,105,108,101,124,119,105,110,100,111,119,115,95,99,104,97,105,110,61,109,115,104,116,97,95,116,111,95,112,121,116,104,111,110,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,51,51,49,57,48,53,52,97,56,50,124,117,114,108,61,104,116,116,112,115,58,47,47,51,51,49,57,48,53,52,97,56,50,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,57,98,100,54,99,48,56,102,46,112,121,124,117,115,101,114,95,97,103,101,110,116,61,72,117,110,116,114,101,115,115,80,121,116,104,111,110,47,51,51,49,57,48,53,52,97,56,50,124,102,105,108,101,95,112,97,116,104,61,67,58,47,80,114,111,103,114,97,109,68,97,116,97,47,72,117,110,116,114,101,115,115,76,97,98,47,46,117,112,100,97,116,101,45,51,51,49,57,48,53,52,97,56,50,46,112,121"
CODEC_4422fa03 = "decimal_csv|identity|"

def load_4422fa03():
    return bytes(int(item) for item in MATERIAL_4422fa03.split(","))

def decode_4422fa03(v_a19c):
    return bytes(v_a19c)

def recover_4422fa03():
    v_d41a = "left" if 2 > 1 else "right"
    v_b27e = decode_4422fa03(load_4422fa03())
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_4422fa03():
    stream = io.BytesIO(recover_4422fa03().encode("ascii"))
    return stream.read().decode("ascii")

def surface_4422fa03():
    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))
    return tuple(stream)

def obfuscation_4422fa03():
    left, right = "fstrin", "g_fragments"
    return f"{left}{right}"

def plan_4422fa03():
    fields = dict(item.split("=", 1) for item in inspect_4422fa03().split("|"))
    analysis_surface = surface_4422fa03()
    obfuscation_surface = obfuscation_4422fa03()
    operation_plan = ("bitsadmin_predecessor_plan", fields["url"], fields["file_path"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_4422fa03())
