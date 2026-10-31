#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_91b26b43 = (117, 60, 49, 123, 114, 115, 100, 111, 114, 60, 96, 98, 112, 116, 104, 113, 100, 94, 113, 100, 108, 110, 115, 100, 43, 99, 104, 114, 111, 96, 115, 98, 103, 94, 108, 100, 108, 110, 113, 120, 123, 96, 99, 96, 111, 115, 100, 113, 60, 114, 110, 98, 106, 100, 115, 94, 111, 107, 96, 109, 94, 108, 100, 108, 110, 113, 120, 123, 114, 115, 96, 102, 100, 94, 98, 110, 116, 109, 115, 60, 48, 123, 114, 120, 109, 115, 96, 119, 60, 100, 119, 98, 100, 111, 115, 104, 110, 109, 94, 100, 119, 111, 113, 100, 114, 114, 104, 110, 109, 123, 110, 97, 101, 116, 114, 98, 96, 115, 104, 110, 109, 60, 108, 96, 113, 114, 103, 96, 107, 94, 100, 109, 117, 100, 107, 110, 111, 100, 94, 111, 107, 96, 109, 123, 98, 96, 113, 113, 104, 100, 113, 60, 111, 120, 96, 113, 108, 110, 113, 94, 110, 97, 101, 116, 114, 98, 96, 115, 100, 99, 123, 118, 104, 109, 99, 110, 118, 114, 94, 98, 103, 96, 104, 109, 60, 118, 114, 98, 113, 104, 111, 115, 94, 115, 110, 94, 111, 120, 115, 103, 110, 109, 123, 98, 96, 108, 111, 96, 104, 102, 109, 94, 104, 99, 60, 98, 96, 108, 111, 96, 104, 102, 109, 44, 52, 96, 49, 98, 52, 96, 48, 99, 97, 98, 123, 116, 113, 107, 60, 103, 115, 115, 111, 114, 57, 46, 46, 52, 96, 49, 98, 52, 96, 48, 99, 97, 98, 45, 100, 119, 96, 108, 111, 107, 100, 45, 104, 109, 117, 96, 107, 104, 99, 46, 96, 56, 48, 56, 101, 98, 53, 98, 45, 111, 120, 123, 116, 114, 100, 113, 94, 96, 102, 100, 109, 115, 60, 71, 116, 109, 115, 113, 100, 114, 114, 79, 120, 115, 103, 110, 109, 46, 52, 96, 49, 98, 52, 96, 48, 99, 97, 98,)

CODEC_91b26b43 = "integer_tuple|subtract_modulo_256|01"



def load_91b26b43():

    return bytes(MATERIAL_91b26b43)



def decode_91b26b43(v_a19c):

    return bytes((value + 1) % 256 for value in v_a19c)



def recover_91b26b43():

    v_d41a = 19 * 7 - 133

    _pass = 0

    while _pass < 1:

        v_b27e = decode_91b26b43(load_91b26b43())

        _pass += 1

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_91b26b43():

    view = memoryview(recover_91b26b43().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_91b26b43():

    try:

        raise LookupError("surface")

    except LookupError:

        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")



def obfuscation_91b26b43():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_91b26b43():

    fields = dict(item.split("=", 1) for item in inspect_91b26b43().split("|"))

    analysis_surface = surface_91b26b43()

    obfuscation_surface = obfuscation_91b26b43()

    operation_plan = ("socket_plan_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_91b26b43())

