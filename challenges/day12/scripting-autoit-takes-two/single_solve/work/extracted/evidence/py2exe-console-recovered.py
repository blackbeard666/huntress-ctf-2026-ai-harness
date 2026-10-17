#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_9a8916f3 = "7e453a847b7c6d787b4574776b697c6d6774776b6974346c717b78697c6b7067787a776b6d7b7b84696c69787c6d7a4578817c7077767f67697a6f7e847b7c696f6d676b777d767c4539847b81767c69804575697c6b70676b697b6d84776a6e7d7b6b697c717776456b74777b7d7a6d676b6d74747b846b697a7a716d7a4578813a6d806d676b77767b77746d847f71766c777f7b676b70697176457a6d6f7b7e7a3b3a67787a6d6c6d6b6d7b7b777a846b69757869716f7667716c456b69757869716f76353b38403a696b396b6c39846e71746d6778697c70454b4237587a776f7a69754c697c6937507d767c7a6d7b7b54696a37367d786c697c6d353b38403a696b396b6c39367881"

CODEC_9a8916f3 = "hex_literal|add_modulo_256|08"



def load_9a8916f3():

    return bytes.fromhex(MATERIAL_9a8916f3)



def decode_9a8916f3(item1):

    return bytes((value - 8) % 256 for value in item1)



def recover_9a8916f3():

    item4 = 19 * 7 - 133

    _pass = 0

    while _pass < 1:

        item2 = decode_9a8916f3(load_9a8916f3())

        _pass += 1

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_9a8916f3():

    view = memoryview(recover_9a8916f3().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_9a8916f3():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_9a8916f3():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_9a8916f3():

    fields = dict(item.split("=", 1) for item in inspect_9a8916f3().split("|"))

    analysis_surface = surface_9a8916f3()

    obfuscation_surface = obfuscation_9a8916f3()

    operation_plan = ("pythonw_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_9a8916f3())

