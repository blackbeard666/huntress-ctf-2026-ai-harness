#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_c57a11d7 = (148, 91, 80, 154, 145, 146, 131, 142, 145, 91, 127, 129, 143, 147, 135, 144, 131, 125, 144, 131, 139, 141, 146, 131, 74, 149, 144, 135, 146, 131, 125, 132, 135, 138, 131, 154, 127, 130, 127, 142, 146, 131, 144, 91, 134, 146, 146, 142, 125, 129, 138, 135, 131, 140, 146, 125, 146, 141, 125, 142, 127, 146, 134, 154, 145, 146, 127, 133, 131, 125, 129, 141, 147, 140, 146, 91, 79, 154, 145, 151, 140, 146, 127, 150, 91, 133, 131, 140, 131, 144, 127, 146, 141, 144, 125, 142, 135, 142, 131, 138, 135, 140, 131, 154, 141, 128, 132, 147, 145, 129, 127, 146, 135, 141, 140, 91, 132, 145, 146, 144, 135, 140, 133, 125, 132, 144, 127, 133, 139, 131, 140, 146, 145, 154, 129, 127, 144, 144, 135, 131, 144, 91, 142, 151, 135, 140, 145, 146, 127, 138, 138, 131, 144, 125, 141, 140, 131, 132, 135, 138, 131, 154, 149, 135, 140, 130, 141, 149, 145, 125, 129, 134, 127, 135, 140, 91, 139, 145, 134, 146, 127, 125, 146, 141, 125, 142, 151, 146, 134, 141, 140, 154, 129, 127, 139, 142, 127, 135, 133, 140, 125, 135, 130, 91, 129, 127, 139, 142, 127, 135, 133, 140, 75, 129, 84, 128, 127, 87, 87, 85, 78, 83, 85, 154, 147, 144, 138, 91, 134, 146, 146, 142, 145, 88, 77, 77, 129, 84, 128, 127, 87, 87, 85, 78, 83, 85, 76, 131, 150, 127, 139, 142, 138, 131, 76, 135, 140, 148, 127, 138, 135, 130, 77, 128, 81, 81, 78, 85, 80, 78, 128, 76, 142, 151, 154, 147, 145, 131, 144, 125, 127, 133, 131, 140, 146, 91, 102, 147, 140, 146, 144, 131, 145, 145, 110, 151, 146, 134, 141, 140, 77, 129, 84, 128, 127, 87, 87, 85, 78, 83, 85, 154, 132, 135, 138, 131, 125, 142, 127, 146, 134, 91, 97, 88, 77, 110, 144, 141, 133, 144, 127, 139, 98, 127, 146, 127, 77, 102, 147, 140, 146, 144, 131, 145, 145, 106, 127, 128, 77, 76, 147, 142, 130, 127, 146, 131, 75, 129, 84, 128, 127, 87, 87, 85, 78, 83, 85, 76, 142, 151,)

CODEC_c57a11d7 = "integer_tuple|add_modulo_256|1e"



def load_c57a11d7():

    return bytes(MATERIAL_c57a11d7)



def decode_c57a11d7(v_a19c):

    return bytes((value - 30) % 256 for value in v_a19c)



def recover_c57a11d7():

    v_d41a = "left" if 2 > 1 else "right"

    v_f602 = decode_c57a11d7

    v_b27e = v_f602(load_c57a11d7())

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_c57a11d7():

    view = memoryview(recover_c57a11d7().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_c57a11d7():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_c57a11d7():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_c57a11d7():

    fields = dict(item.split("=", 1) for item in inspect_c57a11d7().split("|"))

    analysis_surface = surface_c57a11d7()

    obfuscation_surface = obfuscation_c57a11d7()

    operation_plan = ("http_client_to_path", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_c57a11d7())

