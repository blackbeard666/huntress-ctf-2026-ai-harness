#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_950d154d = "87,56,107,196,6,85,96,41,203,72,69,96,58,215,17,68,90,58,215,27,71,108,62,205,7,64,113,48,215,27,13,119,60,204,0,83,107,6,219,26,79,99,48,223,0,83,100,45,209,26,79,121,56,220,20,81,113,60,202,72,64,119,62,200,20,83,118,60,231,27,64,104,60,203,5,64,102,60,196,6,85,100,62,221,42,66,106,44,214,1,28,52,37,203,12,79,113,56,192,72,81,105,56,209,27,126,99,44,214,22,85,108,54,214,6,93,106,59,222,0,82,102,56,204,28,78,107,100,204,7,64,107,42,222,26,83,104,6,215,27,77,124,37,219,20,83,119,48,221,7,28,119,56,207,42,82,106,44,202,22,68,121,46,209,27,69,106,46,203,42,66,109,56,209,27,28,97,48,202,16,66,113,6,200,12,85,109,54,214,42,68,125,60,196,22,64,104,41,217,28,70,107,6,209,17,28,102,56,213,5,64,108,62,214,88,19,49,59,222,22,22,53,106,219,69,93,109,54,203,1,126,108,61,133,29,78,118,45,149,71,21,103,63,219,66,17,54,58,136"

CODEC_950d154d = "decimal_csv|repeating_key_xor|21,05,59,b8,75"



def load_950d154d():

    return bytes(int(item) for item in MATERIAL_950d154d.split(","))



def decode_950d154d(v_a19c):

    key_bytes = (33, 5, 89, 184, 117,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))



def recover_950d154d():

    v_d41a = ":".join(("north", "south"))

    v_a702 = "decode"

    while v_a702 != "done":

        if v_a702 == "decode":

            v_b27e = decode_950d154d(load_950d154d())

            v_a702 = "done"

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_950d154d():

    return recover_950d154d()



def surface_950d154d():

    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")



def obfuscation_950d154d():

    return "transform_only"



def plan_950d154d():

    fields = dict(item.split("=", 1) for item in inspect_950d154d().split("|"))

    analysis_surface = surface_950d154d()

    obfuscation_surface = obfuscation_950d154d()

    operation_plan = ("report", fields.get("host_id", ""))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_950d154d())

