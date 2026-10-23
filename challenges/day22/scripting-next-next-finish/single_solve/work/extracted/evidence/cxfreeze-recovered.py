#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_4bbe1585 = (57, 56, 50, 62, 62, 63, 61, 110, 105, 51, 36, 105, 106, 71, 120, 120, 110, 121, 127, 101, 126, 67, 36, 49, 72, 54, 127, 100, 100, 121, 84, 127, 110, 108, 121, 106, 127, 119, 127, 115, 127, 37, 57, 56, 50, 62, 62, 63, 61, 110, 105, 51, 38, 89, 78, 93, 68, 72, 78, 89, 54, 110, 102, 106, 101, 84, 110, 127, 100, 101, 119, 111, 110, 96, 104, 100, 103, 37, 57, 56, 50, 62, 62, 63, 61, 110, 105, 51, 37, 54, 101, 100, 98, 120, 101, 110, 127, 115, 110, 119, 57, 56, 50, 62, 62, 63, 61, 110, 105, 51, 38, 101, 108, 98, 106, 123, 102, 106, 104, 54, 111, 98, 84, 101, 108, 98, 106, 123, 102, 106, 104, 119, 121, 100, 127, 123, 98, 121, 104, 120, 110, 111, 84, 96, 120, 106, 127, 84, 111, 110, 103, 126, 111, 110, 99, 104, 120, 54, 101, 98, 106, 99, 104, 84, 120, 124, 100, 111, 101, 98, 124, 119, 110, 103, 105, 106, 127, 126, 104, 110, 115, 110, 84, 110, 113, 110, 110, 121, 109, 84, 115, 104, 54, 121, 110, 98, 121, 121, 106, 104, 119, 101, 100, 98, 127, 106, 103, 120, 101, 106, 121, 127, 84, 120, 110, 127, 114, 105, 54, 101, 100, 98, 127, 106, 104, 120, 126, 109, 105, 100, 119, 121, 110, 123, 123, 106, 121, 124, 84, 121, 100, 127, 106, 121, 100, 104, 110, 111, 54, 115, 106, 127, 101, 114, 120, 119, 58, 54, 127, 101, 126, 100, 104, 84, 110, 108, 106, 127, 120, 119, 101, 106, 103, 123, 84, 114, 123, 100, 104, 84, 103, 98, 127, 126, 99, 120, 54, 121, 110, 127, 123, 106, 111, 106, 119, 110, 127, 100, 101, 84, 114, 121, 110, 125, 100, 104, 110, 121, 84, 110, 127, 98, 121, 124, 39, 114, 123, 100, 104, 84, 102, 121, 100, 109, 120, 101, 106, 121, 127, 39, 120, 110, 103, 98, 109, 84, 110, 121, 126, 127, 115, 98, 109, 84, 127, 104, 110, 103, 110, 120, 54, 120, 123, 110, 127, 120, 119, 57, 54, 125,)

CODEC_4bbe1585 = "integer_tuple|reverse_then_xor|0b"



def load_4bbe1585():

    return bytes(MATERIAL_4bbe1585)



def decode_4bbe1585(stored_bytes):

    return bytes(value ^ 11 for value in reversed(stored_bytes))



def recover_4bbe1585():

    harmless_value = "left" if 2 > 1 else "right"

    try:

        recovered_bytes = decode_4bbe1585(load_4bbe1585())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_4bbe1585():

    return recover_4bbe1585()



def decorate_surface_4bbe1585(function):

    def wrapped():

        return tuple(function())

    return wrapped



@decorate_surface_4bbe1585

def surface_4bbe1585():

    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")



def obfuscation_4bbe1585():

    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")



def plan_4bbe1585():

    fields = dict(item.split("=", 1) for item in inspect_4bbe1585().split("|"))

    analysis_surface = surface_4bbe1585()

    obfuscation_surface = obfuscation_4bbe1585()

    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_4bbe1585())

