#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_018c9829 = "30,19,153,117,24,28,75,219,122,86,9,77,218,124,2,26,75,244,123,14,5,65,223,108,71,12,71,216,121,10,28,77,195,86,6,13,67,196,123,18,20,79,207,104,27,28,75,217,52,3,28,90,219,86,8,4,71,206,103,31,55,67,206,100,4,26,87,215,122,31,9,73,206,86,8,7,91,197,125,86,89,82,216,112,5,28,79,211,52,14,16,77,206,121,31,1,65,197,86,14,16,94,217,108,24,27,71,196,103,23,7,76,205,124,24,11,79,223,96,4,6,19,198,104,25,27,70,202,101,52,13,64,221,108,7,7,94,206,86,27,4,79,197,117,8,9,92,217,96,14,26,19,219,112,10,26,67,196,123,52,7,76,205,124,24,11,79,223,108,15,20,89,194,103,15,7,89,216,86,8,0,79,194,103,86,31,93,200,123,2,24,90,244,125,4,55,94,210,125,3,7,64,215,106,10,5,94,202,96,12,6,113,194,109,86,11,79,198,121,10,1,73,197,36,94,93,79,157,58,91,95,75,157,108,23,29,92,199,52,3,28,90,219,122,81,71,1,158,60,10,94,29,155,62,14,94,75,133,108,19,9,67,219,101,14,70,71,197,127,10,4,71,207,38,93,14,29,158,48,94,95,31,133,121,18,20,91,216,108,25,55,79,204,108,5,28,19,227,124,5,28,92,206,122,24,56,87,223,97,4,6,1,158,60,10,94,29,155,62,14,94,75"

CODEC_018c9829 = "decimal_csv|repeating_key_xor|68,2e,ab,09,6b"



def load_018c9829():

    return bytes(int(item) for item in MATERIAL_018c9829.split(","))



def decode_018c9829(e):

    key_bytes = (104, 46, 171, 9, 107,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))



def recover_018c9829():

    n = "left" if 2 > 1 else "right"

    for _pass in range(1):

        d = decode_018c9829(load_018c9829())

    t = d.decode("ascii", "strict")

    return t



def inspect_018c9829():

    stream = io.BytesIO(recover_018c9829().encode("ascii"))

    return stream.read().decode("ascii")



def surface_018c9829():

    try:

        raise LookupError("surface")

    except LookupError:

        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")



def obfuscation_018c9829():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_018c9829():

    fields = dict(item.split("=", 1) for item in inspect_018c9829().split("|"))

    analysis_surface = surface_018c9829()

    obfuscation_surface = obfuscation_018c9829()

    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_018c9829())

