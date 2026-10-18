#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_8f5a6cbc = "118,61,50,124,115,116,101,112,115,61,97,99,113,117,105,114,101,95,114,101,109,111,116,101,44,119,114,105,116,101,95,102,105,108,101,124,97,100,97,112,116,101,114,61,117,114,108,108,105,98,95,116,111,95,112,97,116,104,124,115,116,97,103,101,95,99,111,117,110,116,61,49,124,115,121,110,116,97,120,61,103,101,110,101,114,97,116,111,114,95,112,105,112,101,108,105,110,101,124,111,98,102,117,115,99,97,116,105,111,110,61,102,115,116,114,105,110,103,95,102,114,97,103,109,101,110,116,115,124,99,97,114,114,105,101,114,61,112,121,105,110,115,116,97,108,108,101,114,95,111,110,101,102,105,108,101,124,119,105,110,100,111,119,115,95,99,104,97,105,110,61,109,115,104,116,97,95,116,111,95,112,121,116,104,111,110,124,99,97,109,112,97,105,103,110,95,105,100,61,99,97,109,112,97,105,103,110,45,57,53,56,101,98,51,100,53,53,101,124,117,114,108,61,104,116,116,112,115,58,47,47,57,53,56,101,98,51,100,53,53,101,46,101,120,97,109,112,108,101,46,105,110,118,97,108,105,100,47,97,101,52,99,55,55,56,51,46,112,121,124,117,115,101,114,95,97,103,101,110,116,61,72,117,110,116,114,101,115,115,80,121,116,104,111,110,47,57,53,56,101,98,51,100,53,53,101,124,102,105,108,101,95,112,97,116,104,61,67,58,47,80,114,111,103,114,97,109,68,97,116,97,47,72,117,110,116,114,101,115,115,76,97,98,47,46,117,112,100,97,116,101,45,57,53,56,101,98,51,100,53,53,101,46,112,121"

CODEC_8f5a6cbc = "decimal_csv|identity|"



def load_8f5a6cbc():

    return bytes(int(item) for item in MATERIAL_8f5a6cbc.split(","))



def decode_8f5a6cbc(v_a19c):

    return bytes(v_a19c)



def recover_8f5a6cbc():

    v_d41a = "left" if 2 > 1 else "right"

    for _pass in range(1):

        v_b27e = decode_8f5a6cbc(load_8f5a6cbc())

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_8f5a6cbc():

    view = memoryview(recover_8f5a6cbc().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_8f5a6cbc():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_8f5a6cbc():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_8f5a6cbc():

    fields = dict(item.split("=", 1) for item in inspect_8f5a6cbc().split("|"))

    analysis_surface = surface_8f5a6cbc()

    obfuscation_surface = obfuscation_8f5a6cbc()

    operation_plan = ("urllib_to_path", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_8f5a6cbc())

