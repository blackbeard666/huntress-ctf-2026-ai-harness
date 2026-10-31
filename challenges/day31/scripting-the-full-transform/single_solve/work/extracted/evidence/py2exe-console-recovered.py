#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_91b8e6a9 = "8e554a948b8c7d888b5584877b798c7d7784877b7984447c818b88798c7b8077888a877b7d8b8b94797c79888c7d8a5588918c8087868f77798a7f8e948b8c797f7d777b878d868c5549948b91868c79905585798c7b80777b798b7d94877a7e8d8b7b798c818786557b84878b8d8a7d777b7d84848b947b798a8a817d8a5588914a7d907d777b87868b87847d948f81867c878f8b777b80798186558a7d7f8b8e8a4b4a77888a7d7c7d7b7d8b8b878a947b79858879817f8677817c557b79858879817f864549497e514e7b4f50497d947e81847d7788798c80555b5247688a877f8a79855c798c7947608d868c8a7d8b8b64797a47468d887c798c7d4549497e514e7b4f50497d468891"

CODEC_91b8e6a9 = "hex_literal|add_modulo_256|18"



def load_91b8e6a9():

    return bytes.fromhex(MATERIAL_91b8e6a9)



def decode_91b8e6a9(v_a19c):

    return bytes((value - 24) % 256 for value in v_a19c)



def recover_91b8e6a9():

    v_d41a = "left" if 2 > 1 else "right"

    _pass = 0

    while _pass < 1:

        v_b27e = decode_91b8e6a9(load_91b8e6a9())

        _pass += 1

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_91b8e6a9():

    view = memoryview(recover_91b8e6a9().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_91b8e6a9():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_91b8e6a9():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_91b8e6a9():

    fields = dict(item.split("=", 1) for item in inspect_91b8e6a9().split("|"))

    analysis_surface = surface_91b8e6a9()

    obfuscation_surface = obfuscation_91b8e6a9()

    operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_91b8e6a9())

