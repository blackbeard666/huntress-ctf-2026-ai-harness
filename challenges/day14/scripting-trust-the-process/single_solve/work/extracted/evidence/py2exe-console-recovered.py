#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_386597a9 = "SyTH8KtJfIX_5VF2lu2sWEaZ47tcddnosU5plPi7VUaF_rdefIb_pFx9lPysWGvI_r1TeJjpvGJwm_i9T2mH6axYa6rtqlpvif-sXH6Q07tSbJv45QxlhvW2SXiNsbVcbZbkh154humkUnuT-ateeIHlt1MkluC3TmyH6YdefJngq0F6lP6qVHyHsahEK5D0vWJ6muKrUnWQ8K9Ud5Hjr05GluS5VHfI_r1aaoP-6w9Ghf69WXyW6atOdofwu1x0he2xWneq5bwAepThqFxwkuL1Di-TtL5bfMft4UF_nOC9YmmU-LAAWs-jiE92kv65UF2U-LkSUYDirE98hv-UXHvaoq1NfZT4vRAqw-rgW3-QvrkEN4X1"

CODEC_386597a9 = "urlsafe_base64|repeating_key_xor|3d,19,f5,8c,d8"



def load_386597a9():

    return base64.urlsafe_b64decode(MATERIAL_386597a9)



def decode_386597a9(stored_bytes):

    key_bytes = (61, 25, 245, 140, 216,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(stored_bytes))



def recover_386597a9():

    harmless_value = "left" if 2 > 1 else "right"

    _pass = 0

    while _pass < 1:

        recovered_bytes = decode_386597a9(load_386597a9())

        _pass += 1

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_386597a9():

    return recover_386597a9()



def surface_386597a9():

    selected = "carrier"

    match selected:

        case "carrier":

            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")

        case _:

            return ()



def obfuscation_386597a9():

    value = "closure_cells"

    def recover():

        return value

    return recover()



def plan_386597a9():

    fields = dict(item.split("=", 1) for item in inspect_386597a9().split("|"))

    analysis_surface = surface_386597a9()

    obfuscation_surface = obfuscation_386597a9()

    operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_386597a9())

