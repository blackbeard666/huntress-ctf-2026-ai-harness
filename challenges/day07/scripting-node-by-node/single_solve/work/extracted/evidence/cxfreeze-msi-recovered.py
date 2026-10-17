#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_c33eb124 = [127, 118, 52, 54, 103, 106, 58, 62, 62, 63, 63, 60, 60, 51, 107, 122, 103, 106, 118, 123, 52, 53, 104, 103, 82, 121, 121, 107, 120, 122, 116, 123, 78, 53, 103, 122, 103, 74, 115, 103, 120, 109, 117, 120, 86, 53, 64, 73, 67, 110, 122, 103, 118, 101, 107, 114, 111, 108, 130, 54, 103, 106, 58, 62, 62, 63, 63, 60, 60, 51, 116, 109, 111, 103, 118, 115, 103, 105, 67, 106, 111, 101, 116, 109, 111, 103, 118, 115, 103, 105, 130, 120, 117, 122, 118, 111, 120, 105, 121, 107, 106, 101, 127, 107, 113, 101, 116, 123, 120, 67, 116, 111, 103, 110, 105, 101, 121, 125, 117, 106, 116, 111, 125, 130, 111, 121, 115, 101, 107, 128, 107, 107, 120, 108, 101, 126, 105, 67, 120, 107, 111, 120, 120, 103, 105, 130, 116, 103, 114, 118, 101, 107, 115, 103, 116, 101, 107, 124, 111, 122, 105, 107, 114, 108, 107, 120, 67, 116, 117, 111, 122, 103, 105, 121, 123, 108, 104, 117, 130, 114, 117, 105, 117, 122, 117, 120, 118, 101, 120, 117, 122, 103, 120, 107, 122, 111, 67, 126, 103, 122, 116, 127, 121, 130, 55, 67, 122, 116, 123, 117, 105, 101, 107, 109, 103, 122, 121, 130, 107, 122, 111, 120, 125, 101, 127, 120, 103, 116, 111, 104, 101, 116, 107, 118, 117, 67, 120, 107, 122, 118, 103, 106, 103, 130, 107, 114, 111, 108, 101, 107, 122, 111, 120, 125, 50, 106, 107, 106, 106, 107, 104, 115, 107, 101, 107, 106, 117, 105, 107, 106, 67, 121, 118, 107, 122, 121, 130, 56, 67, 124]

CODEC_c33eb124 = "reversed_integer_list|add_modulo_256|06"



def load_c33eb124():

    return bytes(reversed(MATERIAL_c33eb124))



def decode_c33eb124(v_a19c):

    return bytes((value - 6) % 256 for value in v_a19c)



def recover_c33eb124():

    v_d41a = (3, 5, 8, 13)[1:3]

    try:

        v_b27e = decode_c33eb124(load_c33eb124())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_c33eb124():

    view = memoryview(recover_c33eb124().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_c33eb124():

    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))

    return tuple(iterator)



def obfuscation_c33eb124():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_c33eb124():

    fields = dict(item.split("=", 1) for item in inspect_c33eb124().split("|"))

    analysis_surface = surface_c33eb124()

    obfuscation_surface = obfuscation_c33eb124()

    operation_plan = ("open_binary_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_c33eb124())

