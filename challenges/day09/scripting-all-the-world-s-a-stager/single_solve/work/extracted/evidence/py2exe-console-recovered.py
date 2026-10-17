#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_e9e040c7 = (130, 73, 62, 136, 127, 128, 113, 124, 127, 73, 120, 123, 111, 109, 128, 113, 107, 120, 123, 111, 109, 120, 56, 112, 117, 127, 124, 109, 128, 111, 116, 107, 124, 126, 123, 111, 113, 127, 127, 136, 109, 112, 109, 124, 128, 113, 126, 73, 127, 129, 110, 124, 126, 123, 111, 113, 127, 127, 107, 120, 117, 127, 128, 136, 127, 128, 109, 115, 113, 107, 111, 123, 129, 122, 128, 73, 61, 136, 127, 133, 122, 128, 109, 132, 73, 121, 109, 128, 111, 116, 107, 111, 109, 127, 113, 136, 123, 110, 114, 129, 127, 111, 109, 128, 117, 123, 122, 73, 111, 120, 123, 127, 129, 126, 113, 107, 111, 113, 120, 120, 127, 136, 111, 109, 126, 126, 117, 113, 126, 73, 124, 133, 62, 113, 132, 113, 107, 111, 123, 122, 127, 123, 120, 113, 136, 131, 117, 122, 112, 123, 131, 127, 107, 111, 116, 109, 117, 122, 73, 126, 113, 115, 127, 130, 126, 63, 62, 107, 124, 126, 113, 112, 113, 111, 113, 127, 127, 123, 126, 136, 111, 109, 121, 124, 109, 117, 115, 122, 107, 117, 112, 73, 111, 109, 121, 124, 109, 117, 115, 122, 57, 63, 110, 62, 113, 114, 66, 109, 68, 113, 61, 136, 114, 117, 120, 113, 107, 124, 109, 128, 116, 73, 79, 70, 59, 92, 126, 123, 115, 126, 109, 121, 80, 109, 128, 109, 59, 84, 129, 122, 128, 126, 113, 127, 127, 88, 109, 110, 59, 58, 129, 124, 112, 109, 128, 113, 57, 63, 110, 62, 113, 114, 66, 109, 68, 113, 61, 58, 124, 133,)

CODEC_e9e040c7 = "integer_tuple|add_modulo_256|0c"



def load_e9e040c7():

    return bytes(MATERIAL_e9e040c7)



def decode_e9e040c7(e):

    return bytes((value - 12) % 256 for value in e)



def recover_e9e040c7():

    n = ":".join(("north", "south"))

    s = "decode"

    while s != "done":

        if s == "decode":

            d = decode_e9e040c7(load_e9e040c7())

            s = "done"

    t = d.decode("ascii", "strict")

    return t



def inspect_e9e040c7():

    stream = io.BytesIO(recover_e9e040c7().encode("ascii"))

    return stream.read().decode("ascii")



def surface_e9e040c7():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_e9e040c7():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_e9e040c7():

    fields = dict(item.split("=", 1) for item in inspect_e9e040c7().split("|"))

    analysis_surface = surface_e9e040c7()

    obfuscation_surface = obfuscation_e9e040c7()

    operation_plan = ("subprocess_list", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_e9e040c7())

