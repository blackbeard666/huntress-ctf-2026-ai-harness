#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_46ed45c3 = (40, 21, 39, 91, 40, 92, 57, 73, 58, 7, 99, 6, 101, 10, 110, 11, 84, 55, 88, 54, 80, 57, 94, 43, 89, 56, 76, 37, 74, 36, 8, 122, 31, 107, 30, 108, 2, 93, 62, 81, 63, 89, 48, 87, 34, 80, 49, 69, 44, 67, 45, 81, 48, 84, 53, 69, 49, 84, 38, 27, 122, 8, 111, 31, 126, 12, 127, 26, 69, 43, 74, 39, 66, 49, 65, 32, 67, 38, 90, 41, 93, 60, 91, 62, 97, 2, 109, 24, 118, 2, 63, 14, 114, 1, 120, 22, 98, 3, 123, 70, 54, 90, 59, 82, 60, 99, 5, 112, 30, 125, 9, 96, 15, 97, 18, 110, 1, 99, 5, 112, 3, 96, 1, 117, 28, 115, 29, 32, 84, 38, 71, 41, 90, 60, 83, 33, 76, 19, 124, 18, 126, 7, 123, 24, 121, 11, 121, 16, 117, 7, 58, 72, 41, 94, 1, 114, 29, 104, 26, 121, 28, 96, 23, 126, 16, 116, 27, 108, 31, 64, 35, 75, 42, 67, 45, 16, 116, 29, 111, 10, 105, 29, 66, 50, 75, 63, 87, 56, 86, 9, 108, 20, 113, 13, 110, 15, 98, 18, 115, 26, 125, 19, 76, 37, 65, 124, 31, 126, 19, 99, 2, 107, 12, 98, 79, 124, 68, 39, 30, 124, 78, 120, 75, 122, 74, 54, 94, 49, 66, 54, 105, 0, 100, 89, 49, 94, 45, 89, 116, 71, 127, 28, 37, 71, 117, 67, 112, 65, 113,)

CODEC_46ed45c3 = "integer_tuple|rolling_xor|5e"



def load_46ed45c3():

    return bytes(MATERIAL_46ed45c3)



def decode_46ed45c3(stored_bytes):

    recovered_bytes = bytearray()

    prior_byte = 94

    for value in stored_bytes:

        recovered_bytes.append(value ^ prior_byte)

        prior_byte = value

    return bytes(recovered_bytes)



def recover_46ed45c3():

    harmless_value = None

    recovered_bytes = decode_46ed45c3(load_46ed45c3())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_46ed45c3():

    stream = io.BytesIO(recover_46ed45c3().encode("ascii"))

    return stream.read().decode("ascii")



def surface_46ed45c3():

    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")



def obfuscation_46ed45c3():

    return "transform_only"



def plan_46ed45c3():

    fields = dict(item.split("=", 1) for item in inspect_46ed45c3().split("|"))

    analysis_surface = surface_46ed45c3()

    obfuscation_surface = obfuscation_46ed45c3()

    operation_plan = ("report", fields.get("host_id", ""))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_46ed45c3())

