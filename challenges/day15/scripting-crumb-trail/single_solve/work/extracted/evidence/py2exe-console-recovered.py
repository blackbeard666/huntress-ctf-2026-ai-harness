#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_c5c879dc = [106, 97, 31, 87, 84, 37, 37, 85, 33, 36, 82, 33, 84, 30, 86, 101, 82, 85, 97, 102, 31, 32, 83, 82, 61, 100, 100, 86, 99, 101, 95, 102, 57, 32, 82, 101, 82, 53, 94, 82, 99, 88, 96, 99, 65, 32, 43, 52, 46, 89, 101, 82, 97, 80, 86, 93, 90, 87, 109, 87, 84, 37, 37, 85, 33, 36, 82, 33, 84, 30, 95, 88, 90, 82, 97, 94, 82, 84, 46, 85, 90, 80, 95, 88, 90, 82, 97, 94, 82, 84, 109, 99, 96, 100, 100, 86, 84, 86, 85, 86, 99, 97, 80, 35, 36, 99, 103, 100, 88, 86, 99, 46, 95, 90, 82, 89, 84, 80, 100, 104, 96, 85, 95, 90, 104, 109, 86, 93, 96, 100, 95, 96, 84, 80, 86, 105, 86, 35, 106, 97, 46, 99, 86, 90, 99, 99, 82, 84, 109, 100, 93, 93, 86, 84, 80, 86, 99, 102, 100, 96, 93, 84, 46, 95, 96, 90, 101, 82, 84, 100, 102, 87, 83, 96, 109, 86, 100, 82, 84, 80, 89, 84, 101, 82, 94, 46, 105, 82, 101, 95, 106, 100, 109, 34, 46, 101, 95, 102, 96, 84, 80, 86, 88, 82, 101, 100, 109, 103, 88, 99, 82, 80, 99, 86, 101, 86, 99, 97, 99, 86, 101, 95, 90, 80, 85, 86, 94, 82, 95, 86, 99, 46, 99, 86, 101, 97, 82, 85, 82, 109, 100, 100, 86, 84, 96, 99, 97, 80, 89, 84, 101, 82, 97, 100, 90, 85, 29, 93, 82, 84, 96, 93, 80, 86, 101, 82, 84, 96, 93, 46, 100, 97, 86, 101, 100, 109, 35, 46, 103]

CODEC_c5c879dc = "reversed_integer_list|subtract_modulo_256|0f"



def load_c5c879dc():

    return bytes(reversed(MATERIAL_c5c879dc))



def decode_c5c879dc(EnCoDeD_Bytes):

    return bytes((value + 15) % 256 for value in EnCoDeD_Bytes)



def recover_c5c879dc():

    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    try:

        DeCoDeD_Bytes = decode_c5c879dc(load_c5c879dc())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_c5c879dc():

    return recover_c5c879dc()



def surface_c5c879dc():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_c5c879dc():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_c5c879dc():

    fields = dict(item.split("=", 1) for item in inspect_c5c879dc().split("|"))

    analysis_surface = surface_c5c879dc()

    obfuscation_surface = obfuscation_c5c879dc()

    operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_c5c879dc())

