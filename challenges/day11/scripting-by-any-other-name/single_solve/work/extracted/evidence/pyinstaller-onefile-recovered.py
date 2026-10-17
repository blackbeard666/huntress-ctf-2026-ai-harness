#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_5c8ee211 = "hk1CjIOEdYCDTXFzgYV5gnVvgnV9f4R1PIeCeYR1b3Z5fHWMcXRxgIR1gk2Fgnx8eXJvhH9vgHGEeIyDhHF3dW9zf4V+hE1BjIOJfoRxiE13dX51gnGEf4JvgHmAdXx5fnWMf3J2hYNzcYR5f35NdoOEgnl+d292gnF3fXV+hIOMc3GCgnl1gk2AiXl+g4RxfHx1gm9/fnV2eXx1jId5fnR/h4Nvc3hxeX5NfYN4hHFvhH9vgImEeH9+jHNxfYBxeXd+b3l0TXNxfYBxeXd+PXRJckNARkRHRUCMhYJ8TXiEhICDSj8/dElyQ0BGREdFQD51iHF9gHx1Pnl+hnF8eXQ/SUVHdEFxdUQ+gImMhYN1gm9xd3V+hE1YhX6EgnWDg2CJhHh/fj90SXJDQEZER0VAjHZ5fHVvgHGEeE1TSj9ggn93gnF9VHGEcT9YhX6EgnWDg1xxcj8+hYB0cYR1PXRJckNARkRHRUA+gIk="

CODEC_5c8ee211 = "base64_literal|add_modulo_256|10"



def load_5c8ee211():

    return base64.b64decode(MATERIAL_5c8ee211)



def decode_5c8ee211(e):

    return bytes((value - 16) % 256 for value in e)



def recover_5c8ee211():

    n = "left" if 2 > 1 else "right"

    for _pass in range(1):

        d = decode_5c8ee211(load_5c8ee211())

    t = d.decode("ascii", "strict")

    return t



def inspect_5c8ee211():

    view = memoryview(recover_5c8ee211().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_5c8ee211():

    stream = (item for item in ("generator_pipeline", "fstring_fragments", "pyinstaller_onefile", "mshta_to_python"))

    return tuple(stream)



def obfuscation_5c8ee211():

    left, right = "fstrin", "g_fragments"

    return f"{left}{right}"



def plan_5c8ee211():

    fields = dict(item.split("=", 1) for item in inspect_5c8ee211().split("|"))

    analysis_surface = surface_5c8ee211()

    obfuscation_surface = obfuscation_5c8ee211()

    operation_plan = ("urllib_to_path", fields["url"], fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_5c8ee211())

