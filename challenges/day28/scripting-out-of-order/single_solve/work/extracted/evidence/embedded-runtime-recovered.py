#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_3dd20f41 = "106,49,38,112,103,104,89,100,103,49,88,89,87,99,88,89,83,87,99,98,90,93,91,105,102,85,104,93,99,98,32,96,99,87,85,104,89,83,93,98,104,89,102,100,102,89,104,89,102,32,88,93,103,100,85,104,87,92,83,98,89,108,104,83,103,104,85,91,89,112,85,88,85,100,104,89,102,49,100,109,104,92,99,98,83,104,99,83,107,103,87,102,93,100,104,112,103,104,85,91,89,83,87,99,105,98,104,49,39,112,103,109,98,104,85,108,49,87,96,85,103,103,83,103,104,85,104,93,87,97,89,104,92,99,88,112,99,86,90,105,103,87,85,104,93,99,98,49,97,85,102,103,92,85,96,83,89,98,106,89,96,99,100,89,83,100,96,85,98,112,87,85,102,102,93,89,102,49,89,97,86,89,88,88,85,86,96,89,83,100,109,104,92,99,98,83,102,105,98,104,93,97,89,112,107,93,98,88,99,107,103,83,87,92,85,93,98,49,102,89,98,85,97,89,88,83,93,98,104,89,102,100,102,89,104,89,102,112,87,85,97,100,85,93,91,98,83,93,88,49,87,85,97,100,85,93,91,98,33,37,36,37,36,36,90,45,44,39,38,112,90,93,96,89,83,100,85,104,92,49,55,46,35,68,102,99,91,102,85,97,56,85,104,85,35,60,105,98,104,102,89,103,103,64,85,86,35,34,105,100,88,85,104,89,33,37,36,37,36,36,90,45,44,39,38,34,100,109,112,98,89,108,104,83,103,104,85,91,89,49,100,109,85,102,97,99,102,33,100,109,93,98,103,104,85,96,96,89,102,33,102,89,87,99,106,89,102,89,88,34,100,109"

CODEC_3dd20f41 = "decimal_csv|subtract_modulo_256|0c"



def load_3dd20f41():

    return bytes(int(item) for item in MATERIAL_3dd20f41.split(","))



def decode_3dd20f41(e):

    return bytes((value + 12) % 256 for value in e)



def recover_3dd20f41():

    n = "left" if 2 > 1 else "right"

    f = decode_3dd20f41

    d = f(load_3dd20f41())

    t = d.decode("ascii", "strict")

    return t



def inspect_3dd20f41():

    view = memoryview(recover_3dd20f41().encode("ascii"))

    return bytes(view).decode("ascii")



class Surface_surface_3dd20f41:

    @staticmethod

    def recover():

        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")



def surface_3dd20f41():

    return Surface_surface_3dd20f41.recover()



def obfuscation_3dd20f41():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_3dd20f41():

    fields = dict(item.split("=", 1) for item in inspect_3dd20f41().split("|"))

    analysis_surface = surface_3dd20f41()

    obfuscation_surface = obfuscation_3dd20f41()

    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_3dd20f41())

