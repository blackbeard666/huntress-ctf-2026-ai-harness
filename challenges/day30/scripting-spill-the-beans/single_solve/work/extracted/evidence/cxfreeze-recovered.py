#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_9d91ddd5 = [95, 38, 27, 101, 92, 93, 78, 89, 92, 38, 92, 78, 85, 78, 76, 93, 72, 79, 82, 97, 93, 94, 91, 78, 72, 79, 82, 85, 78, 92, 21, 93, 91, 74, 87, 92, 79, 88, 91, 86, 72, 76, 88, 89, 98, 21, 96, 91, 82, 93, 78, 72, 91, 78, 76, 88, 95, 78, 91, 98, 72, 87, 88, 93, 78, 101, 74, 77, 74, 89, 93, 78, 91, 38, 92, 81, 94, 93, 82, 85, 72, 76, 88, 89, 98, 72, 89, 85, 74, 87, 101, 92, 93, 74, 80, 78, 72, 76, 88, 94, 87, 93, 38, 26, 101, 92, 98, 87, 93, 74, 97, 38, 77, 78, 76, 88, 91, 74, 93, 88, 91, 72, 96, 91, 74, 89, 89, 78, 91, 101, 88, 75, 79, 94, 92, 76, 74, 93, 82, 88, 87, 38, 75, 98, 93, 78, 92, 72, 93, 91, 74, 87, 92, 85, 74, 93, 82, 88, 87, 101, 76, 74, 91, 91, 82, 78, 91, 38, 76, 97, 72, 79, 91, 78, 78, 99, 78, 72, 78, 97, 78, 76, 94, 93, 74, 75, 85, 78, 101, 96, 82, 87, 77, 88, 96, 92, 72, 76, 81, 74, 82, 87, 38, 92, 76, 81, 78, 77, 94, 85, 78, 77, 72, 93, 74, 92, 84, 72, 77, 78, 92, 76, 91, 82, 89, 93, 88, 91, 101, 76, 74, 86, 89, 74, 82, 80, 87, 72, 82, 77, 38, 76, 74, 86, 89, 74, 82, 80, 87, 22, 26, 26, 26, 74, 76, 76, 27, 25, 34, 33, 101, 78, 97, 93, 78, 87, 92, 82, 88, 87, 38, 23, 26, 26, 26, 74, 76, 76, 27, 25, 34, 33, 23, 85, 88, 76, 84, 78, 77, 101, 87, 88, 93, 78, 72, 87, 74, 86, 78, 38, 59, 46, 44, 56, 63, 46, 59, 22, 26, 26, 26, 74, 76, 76, 27, 25, 34, 33, 23, 93, 97, 93, 101, 93, 74, 91, 80, 78, 93, 72, 91, 88, 88, 93, 38, 44, 35, 24, 49, 94, 87, 93, 91, 78, 92, 92, 53, 74, 75, 24, 26, 26, 26, 74, 76, 76, 27, 25, 34, 33]

CODEC_9d91ddd5 = "integer_list|subtract_modulo_256|17"



def load_9d91ddd5():

    return bytes(MATERIAL_9d91ddd5)



def decode_9d91ddd5(EnCoDeD_Bytes):

    return bytes((value + 23) % 256 for value in EnCoDeD_Bytes)



def recover_9d91ddd5():

    NeUtRaL = 19 * 7 - 133

    StAtE = "decode"

    while StAtE != "done":

        if StAtE == "decode":

            DeCoDeD_Bytes = decode_9d91ddd5(load_9d91ddd5())

            StAtE = "done"

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_9d91ddd5():

    return recover_9d91ddd5()



def decorate_surface_9d91ddd5(function):

    def wrapped():

        return tuple(function())

    return wrapped



@decorate_surface_9d91ddd5

def surface_9d91ddd5():

    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")



def obfuscation_9d91ddd5():

    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")



def plan_9d91ddd5():

    fields = dict(item.split("=", 1) for item in inspect_9d91ddd5().split("|"))

    analysis_surface = surface_9d91ddd5()

    obfuscation_surface = obfuscation_9d91ddd5()

    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_9d91ddd5())

