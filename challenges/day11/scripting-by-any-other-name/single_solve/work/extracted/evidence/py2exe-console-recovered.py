#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_0e2ded73 = "864d428c83847580834d7c7f737184756f7c7f73717c3c74798380718473786f80827f737583838c717471808475824d797e8475828082758475826f718277868c83847177756f737f857e844d418c83897e8471884d7d718473786f737183758c7f72768583737184797f7e4d737c7f838582756f73757c7c838c737182827975824d8089427588756f737f7e837f7c758c87797e747f87836f737871797e4d82757783868243426f8082757475737583837f828c73717d807179777e6f79744d73717d807179777e3d464740717576484346758c76797c756f807184784d534a3f60827f7782717d547184713f58857e84827583835c71723f3e8580747184753d464740717576484346753e8089"

CODEC_0e2ded73 = "hex_literal|add_modulo_256|10"



def load_0e2ded73():

    return bytes.fromhex(MATERIAL_0e2ded73)



def decode_0e2ded73(v_a19c):

    return bytes((value - 16) % 256 for value in v_a19c)



def recover_0e2ded73():

    v_d41a = None

    v_b27e = decode_0e2ded73(load_0e2ded73())

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_0e2ded73():

    stream = io.BytesIO(recover_0e2ded73().encode("ascii"))

    return stream.read().decode("ascii")



def surface_0e2ded73():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_0e2ded73():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_0e2ded73():

    fields = dict(item.split("=", 1) for item in inspect_0e2ded73().split("|"))

    analysis_surface = surface_0e2ded73()

    obfuscation_surface = obfuscation_0e2ded73()

    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_0e2ded73())

