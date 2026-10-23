#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_8bd5cbcc = [92, 83, 17, 28, 26, 73, 21, 70, 23, 70, 27, 70, 19, 16, 72, 87, 68, 71, 83, 88, 17, 18, 69, 68, 47, 86, 86, 72, 85, 87, 81, 88, 43, 18, 68, 87, 68, 39, 80, 68, 85, 74, 82, 85, 51, 18, 29, 38, 32, 75, 87, 68, 83, 66, 72, 79, 76, 73, 95, 28, 26, 73, 21, 70, 23, 70, 27, 70, 19, 16, 81, 74, 76, 68, 83, 80, 68, 70, 32, 71, 76, 66, 81, 74, 76, 68, 83, 80, 68, 70, 95, 85, 82, 87, 83, 76, 85, 70, 86, 72, 71, 66, 92, 72, 78, 66, 81, 88, 85, 32, 81, 76, 68, 75, 70, 66, 86, 90, 82, 71, 81, 76, 90, 95, 76, 86, 80, 66, 72, 93, 72, 72, 85, 73, 66, 91, 70, 32, 85, 72, 76, 85, 85, 68, 70, 95, 81, 68, 79, 83, 66, 72, 80, 68, 81, 66, 72, 89, 76, 87, 70, 72, 79, 73, 72, 85, 32, 81, 82, 76, 87, 68, 70, 86, 88, 73, 69, 82, 95, 79, 82, 70, 82, 87, 82, 85, 83, 66, 85, 82, 87, 68, 85, 72, 87, 76, 32, 91, 68, 87, 81, 92, 86, 95, 20, 32, 87, 81, 88, 82, 70, 66, 72, 74, 68, 87, 86, 95, 72, 87, 76, 85, 90, 66, 92, 85, 68, 81, 76, 69, 66, 81, 72, 83, 82, 32, 85, 72, 87, 83, 68, 71, 68, 95, 72, 79, 76, 73, 66, 72, 87, 76, 85, 90, 15, 71, 72, 71, 71, 72, 69, 80, 72, 66, 72, 71, 82, 70, 72, 71, 32, 86, 83, 72, 87, 86, 95, 21, 32, 89]

CODEC_8bd5cbcc = "reversed_integer_list|subtract_modulo_256|1d"



def load_8bd5cbcc():

    return bytes(reversed(MATERIAL_8bd5cbcc))



def decode_8bd5cbcc(stored_bytes):

    return bytes((value + 29) % 256 for value in stored_bytes)



def recover_8bd5cbcc():

    harmless_value = (3, 5, 8, 13)[1:3]

    decoder_function = decode_8bd5cbcc

    recovered_bytes = decoder_function(load_8bd5cbcc())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_8bd5cbcc():

    view = memoryview(recover_8bd5cbcc().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_8bd5cbcc():

    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))

    return tuple(iterator)



def obfuscation_8bd5cbcc():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_8bd5cbcc():

    fields = dict(item.split("=", 1) for item in inspect_8bd5cbcc().split("|"))

    analysis_surface = surface_8bd5cbcc()

    obfuscation_surface = obfuscation_8bd5cbcc()

    operation_plan = ("open_binary_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_8bd5cbcc())

