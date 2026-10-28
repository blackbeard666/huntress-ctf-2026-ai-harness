#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_4cf55a74 = [119, 74, 120, 4, 119, 3, 102, 22, 101, 88, 57, 90, 43, 94, 55, 69, 32, 127, 13, 104, 5, 106, 30, 123, 87, 32, 82, 59, 79, 42, 117, 19, 122, 22, 115, 15, 110, 10, 107, 27, 111, 10, 120, 69, 45, 89, 45, 93, 2, 97, 13, 100, 1, 111, 27, 68, 48, 95, 0, 112, 17, 101, 13, 113, 2, 118, 23, 112, 21, 74, 41, 70, 51, 93, 41, 20, 37, 89, 42, 83, 61, 73, 40, 80, 109, 10, 111, 1, 100, 22, 119, 3, 108, 30, 65, 49, 88, 40, 77, 33, 72, 38, 67, 63, 80, 50, 84, 33, 82, 49, 80, 36, 77, 34, 76, 113, 23, 100, 16, 98, 11, 101, 2, 93, 59, 73, 40, 79, 34, 71, 41, 93, 46, 82, 49, 80, 34, 80, 57, 92, 46, 19, 99, 26, 115, 29, 110, 26, 123, 23, 123, 30, 108, 51, 92, 50, 87, 49, 88, 52, 81, 45, 90, 51, 93, 57, 86, 33, 82, 13, 110, 6, 103, 14, 96, 93, 48, 67, 43, 95, 62, 97, 21, 122, 37, 85, 44, 88, 48, 95, 49, 77, 46, 79, 34, 82, 51, 90, 61, 83, 12, 101, 1, 60, 95, 62, 83, 35, 66, 43, 76, 34, 15, 55, 7, 63, 13, 110, 11, 56, 8, 106, 12, 112, 5, 119, 27, 38, 78, 58, 78, 62, 77, 119, 88, 119, 79, 127, 71, 117, 22, 115, 64, 112, 18, 116, 90, 63, 71, 38, 75, 59, 87, 50, 28, 117, 27, 109, 12, 96, 9, 109, 66, 119, 64, 114, 65, 121, 64, 115, 66, 108, 28, 101, 25, 108, 31, 122, 8, 87, 54, 81, 52, 90, 46, 19, 91, 46, 64, 52, 70, 35, 80, 35, 115, 10, 126, 22, 121, 23, 56, 0, 48, 8, 58, 89, 60, 15, 63, 93, 59, 71, 33, 72, 36, 65, 30, 110, 15, 123, 19, 46, 109, 87, 120, 40, 90, 53, 82, 32, 65, 44, 104, 9, 125, 28, 51, 123, 14, 96, 20, 102, 3, 112, 3, 79, 46, 76, 99, 77, 56, 72, 44, 77, 57, 92, 113, 73, 121, 65, 115, 16, 117, 70, 118, 20, 114, 92, 44, 85]

CODEC_4cf55a74 = "integer_list|rolling_xor|01"



def load_4cf55a74():

    return bytes(MATERIAL_4cf55a74)



def decode_4cf55a74(item1):

    item2 = bytearray()

    item5 = 1

    for value in item1:

        item2.append(value ^ item5)

        item5 = value

    return bytes(item2)



def recover_4cf55a74():

    item4 = "left" if 2 > 1 else "right"

    item7 = "decode"

    while item7 != "done":

        if item7 == "decode":

            item2 = decode_4cf55a74(load_4cf55a74())

            item7 = "done"

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_4cf55a74():

    stream = io.BytesIO(recover_4cf55a74().encode("ascii"))

    return stream.read().decode("ascii")



def surface_4cf55a74():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_4cf55a74():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_4cf55a74():

    fields = dict(item.split("=", 1) for item in inspect_4cf55a74().split("|"))

    analysis_surface = surface_4cf55a74()

    obfuscation_surface = obfuscation_4cf55a74()

    operation_plan = ("http_client_to_path", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_4cf55a74())

