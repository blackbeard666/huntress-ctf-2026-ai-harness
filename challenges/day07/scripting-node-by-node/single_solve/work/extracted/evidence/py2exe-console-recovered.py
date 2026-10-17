#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_aa4b7e5e = "61281d675e5f505b5e28575a4e4c5f504a575a4e4c57174f545e5b4c5f4e534a5b5d5a4e505e5e674c4f4c5b5f505d285d60595b644a4f505e4e5d545b5f5a5d675e5f4c52504a4e5a60595f281c675e64595f4c6328584c5f4e534a4e4c5e50675a4d51605e4e4c5f545a59284e575a5e605d504a4e5057575e674e4c5d5d54505d285b641d5063504a4e5a595e5a5750676254594f5a625e4a4e534c5459285d50525e615d1e1d4a5b5d504f504e505e5e5a5d674e4c585b4c5452594a544f284e4c585b4c545259181d1f1f211b244c1c501f67515457504a5b4c5f53282e251a3b5d5a525d4c582f4c5f4c1a3360595f5d505e5e374c4d1a19605b4f4c5f50181d1f1f211b244c1c501f195b64"

CODEC_aa4b7e5e = "hex_literal|subtract_modulo_256|15"



def load_aa4b7e5e():

    return bytes.fromhex(MATERIAL_aa4b7e5e)



def decode_aa4b7e5e(stored_bytes):

    return bytes((value + 21) % 256 for value in stored_bytes)



def recover_aa4b7e5e():

    harmless_value = "left" if 2 > 1 else "right"

    decode_state = "decode"

    while decode_state != "done":

        if decode_state == "decode":

            recovered_bytes = decode_aa4b7e5e(load_aa4b7e5e())

            decode_state = "done"

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_aa4b7e5e():

    view = memoryview(recover_aa4b7e5e().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_aa4b7e5e():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_aa4b7e5e():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_aa4b7e5e():

    fields = dict(item.split("=", 1) for item in inspect_aa4b7e5e().split("|"))

    analysis_surface = surface_aa4b7e5e()

    obfuscation_surface = obfuscation_aa4b7e5e()

    operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_aa4b7e5e())

