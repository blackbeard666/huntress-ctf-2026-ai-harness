#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_47250fe0 = (85, 30, 17, 95, 80, 87, 70, 83, 80, 30, 80, 70, 79, 70, 64, 87, 124, 69, 74, 91, 87, 86, 81, 70, 124, 69, 74, 79, 70, 80, 15, 87, 81, 66, 77, 80, 69, 76, 81, 78, 124, 64, 76, 83, 90, 15, 84, 81, 74, 87, 70, 124, 81, 70, 64, 76, 85, 70, 81, 90, 124, 77, 76, 87, 70, 95, 66, 71, 66, 83, 87, 70, 81, 30, 80, 75, 86, 87, 74, 79, 124, 64, 76, 83, 90, 124, 83, 79, 66, 77, 95, 80, 87, 66, 68, 70, 124, 64, 76, 86, 77, 87, 30, 18, 95, 80, 90, 77, 87, 66, 91, 30, 71, 70, 64, 76, 81, 66, 87, 76, 81, 124, 84, 81, 66, 83, 83, 70, 81, 95, 76, 65, 69, 86, 80, 64, 66, 87, 74, 76, 77, 30, 65, 90, 87, 70, 80, 124, 87, 81, 66, 77, 80, 79, 66, 87, 74, 76, 77, 95, 64, 66, 81, 81, 74, 70, 81, 30, 64, 91, 124, 69, 81, 70, 70, 89, 70, 124, 70, 91, 70, 64, 86, 87, 66, 65, 79, 70, 95, 84, 74, 77, 71, 76, 84, 80, 124, 64, 75, 66, 74, 77, 30, 80, 64, 75, 70, 71, 86, 79, 70, 71, 124, 87, 66, 80, 72, 124, 71, 70, 80, 64, 81, 74, 83, 87, 76, 81, 95, 64, 66, 78, 83, 66, 74, 68, 77, 124, 74, 71, 30, 64, 66, 78, 83, 66, 74, 68, 77, 14, 20, 19, 66, 27, 65, 19, 18, 65, 27, 23, 95, 70, 91, 87, 70, 77, 80, 74, 76, 77, 30, 13, 20, 19, 66, 27, 65, 19, 18, 65, 27, 23, 13, 79, 76, 64, 72, 70, 71, 95, 77, 76, 87, 70, 124, 77, 66, 78, 70, 30, 113, 102, 96, 108, 117, 102, 113, 14, 20, 19, 66, 27, 65, 19, 18, 65, 27, 23, 13, 87, 91, 87, 95, 87, 66, 81, 68, 70, 87, 124, 81, 76, 76, 87, 30, 96, 25, 12, 107, 86, 77, 87, 81, 70, 80, 80, 111, 66, 65, 12, 20, 19, 66, 27, 65, 19, 18, 65, 27, 23,)

CODEC_47250fe0 = "integer_tuple|single_byte_xor|23"



def load_47250fe0():

    return bytes(MATERIAL_47250fe0)



def decode_47250fe0(stored_bytes):

    return bytes(value ^ 35 for value in stored_bytes)



def recover_47250fe0():

    harmless_value = 19 * 7 - 133

    recovered_bytes = decode_47250fe0(load_47250fe0())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_47250fe0():

    view = memoryview(recover_47250fe0().encode("ascii"))

    return bytes(view).decode("ascii")



def decorate_surface_47250fe0(function):

    def wrapped():

        return tuple(function())

    return wrapped



@decorate_surface_47250fe0

def surface_47250fe0():

    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")



def obfuscation_47250fe0():

    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")



def plan_47250fe0():

    fields = dict(item.split("=", 1) for item in inspect_47250fe0().split("|"))

    analysis_surface = surface_47250fe0()

    obfuscation_surface = obfuscation_47250fe0()

    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_47250fe0())

