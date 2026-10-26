#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_87adfad4 = "WB8UXlVWR1JVH0NFU1dLVEdBVEdPUVZHDkZLVVJDVkVKQU9HT1FUW15DRkNSVkdUH1VRRU1HVkFSTkNQQU9HT1FUW15VVkNJR0FFUVdQVh8TXlVbUFZDWh9OS1VWQUVRT1JUR0pHUFVLUVBeUURIV1VFQ1ZLUVAfSFFUT0NWQU9DUl5FQ1RUS0dUH1lKR0dOQUNURUpLWEdeWUtQRlFZVUFFSkNLUB9SUVlHVFVKR05OQVZRQVJbVkpRUF5FQ09SQ0tJUEFLRh9FQ09SQ0tJUA9FFBNFFhYVQxkUXldUTh9KVlZSVRwREUUUE0UWFhVDGRQQR1pDT1JORxBLUFhDTktGEUcZE0ZHGhoUEFJbXldVR1RBQ0lHUFYfKldQVlRHVVUyW1ZKUVARRRQTRRYWFUMZFA=="

CODEC_87adfad4 = "urlsafe_base64|subtract_modulo_256|1e"



def load_87adfad4():

    return base64.urlsafe_b64decode(MATERIAL_87adfad4)



def decode_87adfad4(v_a19c):

    return bytes((value + 30) % 256 for value in v_a19c)



def recover_87adfad4():

    v_d41a = (3, 5, 8, 13)[1:3]

    v_f602 = decode_87adfad4

    v_b27e = v_f602(load_87adfad4())

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_87adfad4():

    view = memoryview(recover_87adfad4().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_87adfad4():

    return tuple(item for item in ("list_comprehension", "format_map", "wheel_archive", "powershell_to_python"))



def obfuscation_87adfad4():

    return "{left}{right}".format_map({"left": "format_", "right": "map"})



def plan_87adfad4():

    fields = dict(item.split("=", 1) for item in inspect_87adfad4().split("|"))

    analysis_surface = surface_87adfad4()

    obfuscation_surface = obfuscation_87adfad4()

    operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_87adfad4())

