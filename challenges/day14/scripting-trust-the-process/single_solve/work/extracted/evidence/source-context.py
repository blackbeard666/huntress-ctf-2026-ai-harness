#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_8086dcb1 = "72392e786f70616c6f3960615f6b60615b5f6b6a626563716e5d70656b6a286e6170716e6a5b5f6b6a626563716e5d70656b6a785d605d6c70616e39695d6c6c656a635b6c6e6b7475786f705d63615b5f6b716a70392d786f756a705d74396c685d656a5b62716a5f70656b6a6f786b5e62716f5f5d70656b6a39706e5d6a6f626b6e695b6b6a6875785f5d6e6e65616e396e5d735b6f6b716e5f617873656a606b736f5b5f645d656a3960656e615f705b6c7570646b6a5b617461785f5d696c5d65636a5b6560395f5d696c5d65636a29332f3335322c6034352f78646b6f705b656039646b6f7029332f3335322c6034352f"

CODEC_8086dcb1 = "hex_literal|subtract_modulo_256|04"



def load_8086dcb1():

    return bytes.fromhex(MATERIAL_8086dcb1)



def decode_8086dcb1(stored_bytes):

    return bytes((value + 4) % 256 for value in stored_bytes)



def recover_8086dcb1():

    harmless_value = None

    decode_state = "decode"

    while decode_state != "done":

        if decode_state == "decode":

            recovered_bytes = decode_8086dcb1(load_8086dcb1())

            decode_state = "done"

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_8086dcb1():

    view = memoryview(recover_8086dcb1().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_8086dcb1():

    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")



def obfuscation_8086dcb1():

    return "transform_only"



def plan_8086dcb1():

    fields = dict(item.split("=", 1) for item in inspect_8086dcb1().split("|"))

    analysis_surface = surface_8086dcb1()

    obfuscation_surface = obfuscation_8086dcb1()

    operation_plan = ("report", fields.get("host_id", ""))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_8086dcb1())

