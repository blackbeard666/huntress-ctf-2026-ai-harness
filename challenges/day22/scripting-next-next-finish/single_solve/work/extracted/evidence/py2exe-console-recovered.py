#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_4447bc85 = "111,54,43,117,108,109,94,105,108,54,101,104,92,90,109,94,88,101,104,92,90,101,37,93,98,108,105,90,109,92,97,88,105,107,104,92,94,108,108,117,90,93,90,105,109,94,107,54,107,110,103,105,114,88,93,94,108,92,107,98,105,109,104,107,117,108,109,90,96,94,88,92,104,110,103,109,54,42,117,108,114,103,109,90,113,54,102,90,109,92,97,88,92,90,108,94,117,104,91,95,110,108,92,90,109,98,104,103,54,92,101,104,108,110,107,94,88,92,94,101,101,108,117,92,90,107,107,98,94,107,54,105,114,43,94,113,94,88,92,104,103,108,104,101,94,117,112,98,103,93,104,112,108,88,92,97,90,98,103,54,107,94,96,108,111,107,44,43,88,105,107,94,93,94,92,94,108,108,104,107,117,92,90,102,105,90,98,96,103,88,98,93,54,92,90,102,105,90,98,96,103,38,92,92,90,48,44,94,48,91,48,48,117,95,98,101,94,88,105,90,109,97,54,60,51,40,73,107,104,96,107,90,102,61,90,109,90,40,65,110,103,109,107,94,108,108,69,90,91,40,39,110,105,93,90,109,94,38,92,92,90,48,44,94,48,91,48,48,39,105,114"

CODEC_4447bc85 = "decimal_csv|subtract_modulo_256|07"



def load_4447bc85():

    return bytes(int(item) for item in MATERIAL_4447bc85.split(","))



def decode_4447bc85(stored_bytes):

    return bytes((value + 7) % 256 for value in stored_bytes)



def recover_4447bc85():

    harmless_value = None

    decode_state = "decode"

    while decode_state != "done":

        if decode_state == "decode":

            recovered_bytes = decode_4447bc85(load_4447bc85())

            decode_state = "done"

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_4447bc85():

    return recover_4447bc85()



def surface_4447bc85():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_4447bc85():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_4447bc85():

    fields = dict(item.split("=", 1) for item in inspect_4447bc85().split("|"))

    analysis_surface = surface_4447bc85()

    obfuscation_surface = obfuscation_4447bc85()

    operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_4447bc85())

