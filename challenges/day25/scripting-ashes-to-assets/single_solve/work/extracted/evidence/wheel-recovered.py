#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_8b6d4340 = [96, 39, 28, 102, 93, 94, 79, 90, 93, 39, 75, 77, 91, 95, 83, 92, 79, 73, 92, 79, 87, 89, 94, 79, 22, 78, 83, 93, 90, 75, 94, 77, 82, 73, 87, 79, 87, 89, 92, 99, 102, 75, 78, 75, 90, 94, 79, 92, 39, 95, 92, 86, 86, 83, 76, 73, 87, 79, 87, 89, 92, 99, 102, 93, 94, 75, 81, 79, 73, 77, 89, 95, 88, 94, 39, 27, 102, 93, 99, 88, 94, 75, 98, 39, 86, 83, 93, 94, 73, 77, 89, 87, 90, 92, 79, 82, 79, 88, 93, 83, 89, 88, 102, 89, 76, 80, 95, 93, 77, 75, 94, 83, 89, 88, 39, 80, 89, 92, 87, 75, 94, 73, 87, 75, 90, 102, 77, 75, 92, 92, 83, 79, 92, 39, 97, 82, 79, 79, 86, 73, 75, 92, 77, 82, 83, 96, 79, 102, 97, 83, 88, 78, 89, 97, 93, 73, 77, 82, 75, 83, 88, 39, 90, 89, 97, 79, 92, 93, 82, 79, 86, 86, 73, 94, 89, 73, 90, 99, 94, 82, 89, 88, 102, 77, 75, 87, 90, 75, 83, 81, 88, 73, 83, 78, 39, 77, 75, 87, 90, 75, 83, 81, 88, 23, 34, 79, 75, 28, 76, 31, 33, 27, 27, 75, 102, 95, 92, 86, 39, 82, 94, 94, 90, 93, 36, 25, 25, 34, 79, 75, 28, 76, 31, 33, 27, 27, 75, 24, 79, 98, 75, 87, 90, 86, 79, 24, 83, 88, 96, 75, 86, 83, 78, 25, 80, 30, 34, 35, 31, 77, 28, 26, 24, 90, 99, 102, 95, 93, 79, 92, 73, 75, 81, 79, 88, 94, 39, 50, 95, 88, 94, 92, 79, 93, 93, 58, 99, 94, 82, 89, 88, 25, 34, 79, 75, 28, 76, 31, 33, 27, 27, 75]

CODEC_8b6d4340 = "integer_list|subtract_modulo_256|16"



def load_8b6d4340():

    return bytes(MATERIAL_8b6d4340)



def decode_8b6d4340(e):

    return bytes((value + 22) % 256 for value in e)



def recover_8b6d4340():

    n = None

    try:

        d = decode_8b6d4340(load_8b6d4340())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    t = d.decode("ascii", "strict")

    return t



def inspect_8b6d4340():

    return recover_8b6d4340()



def surface_8b6d4340():

    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))



def obfuscation_8b6d4340():

    return "{left}{right}".format_map({"left": "format_", "right": "map"})



def plan_8b6d4340():

    fields = dict(item.split("=", 1) for item in inspect_8b6d4340().split("|"))

    analysis_surface = surface_8b6d4340()

    obfuscation_surface = obfuscation_8b6d4340()

    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_8b6d4340())

