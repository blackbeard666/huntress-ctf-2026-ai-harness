#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_defea6c6 = [111, 54, 43, 117, 108, 109, 94, 105, 108, 54, 93, 94, 92, 104, 93, 94, 88, 94, 102, 91, 94, 93, 93, 94, 93, 37, 112, 107, 98, 109, 94, 88, 95, 98, 101, 94, 117, 90, 93, 90, 105, 109, 94, 107, 54, 104, 105, 94, 103, 88, 91, 98, 103, 90, 107, 114, 88, 112, 107, 98, 109, 94, 117, 108, 109, 90, 96, 94, 88, 92, 104, 110, 103, 109, 54, 42, 117, 108, 114, 103, 109, 90, 113, 54, 98, 109, 94, 107, 90, 109, 104, 107, 88, 105, 107, 104, 109, 104, 92, 104, 101, 117, 104, 91, 95, 110, 108, 92, 90, 109, 98, 104, 103, 54, 107, 94, 95, 101, 94, 92, 109, 98, 111, 94, 88, 103, 90, 102, 94, 88, 105, 101, 90, 103, 117, 92, 90, 107, 107, 98, 94, 107, 54, 92, 113, 88, 95, 107, 94, 94, 115, 94, 88, 102, 108, 98, 117, 112, 98, 103, 93, 104, 112, 108, 88, 92, 97, 90, 98, 103, 54, 107, 110, 103, 88, 100, 94, 114, 88, 93, 94, 108, 92, 107, 98, 105, 109, 104, 107, 117, 92, 90, 102, 105, 90, 98, 96, 103, 88, 98, 93, 54, 92, 90, 102, 105, 90, 98, 96, 103, 38, 94, 92, 49, 44, 90, 93, 90, 95, 48, 50, 117, 95, 98, 101, 94, 88, 105, 90, 109, 97, 54, 60, 51, 40, 73, 107, 104, 96, 107, 90, 102, 61, 90, 109, 90, 40, 65, 110, 103, 109, 107, 94, 108, 108, 69, 90, 91, 40, 39, 110, 105, 93, 90, 109, 94, 38, 94, 92, 49, 44, 90, 93, 90, 95, 48, 50, 39, 105, 114]

CODEC_defea6c6 = "integer_list|subtract_modulo_256|07"



def load_defea6c6():

    return bytes(MATERIAL_defea6c6)



def decode_defea6c6(e):

    return bytes((value + 7) % 256 for value in e)



def recover_defea6c6():

    n = 19 * 7 - 133

    try:

        d = decode_defea6c6(load_defea6c6())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    t = d.decode("ascii", "strict")

    return t



def inspect_defea6c6():

    stream = io.BytesIO(recover_defea6c6().encode("ascii"))

    return stream.read().decode("ascii")



def surface_defea6c6():

    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))

    return tuple(iterator)



def obfuscation_defea6c6():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_defea6c6():

    fields = dict(item.split("=", 1) for item in inspect_defea6c6().split("|"))

    analysis_surface = surface_defea6c6()

    obfuscation_surface = obfuscation_defea6c6()

    operation_plan = ("open_binary_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_defea6c6())

