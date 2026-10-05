#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_cbaccf0b = [145, 136, 70, 124, 125, 138, 125, 142, 135, 123, 125, 138, 69, 138, 125, 132, 132, 121, 140, 139, 134, 129, 145, 136, 69, 138, 135, 133, 138, 121, 145, 136, 85, 125, 127, 121, 140, 139, 119, 140, 144, 125, 134, 148, 145, 136, 70, 80, 124, 78, 75, 122, 125, 124, 125, 125, 122, 69, 125, 140, 121, 124, 136, 141, 70, 71, 122, 121, 100, 139, 139, 125, 138, 140, 134, 141, 96, 71, 121, 140, 121, 92, 133, 121, 138, 127, 135, 138, 104, 71, 82, 91, 85, 128, 140, 121, 136, 119, 125, 132, 129, 126, 148, 80, 124, 78, 75, 122, 125, 124, 125, 125, 122, 69, 134, 127, 129, 121, 136, 133, 121, 123, 85, 124, 129, 119, 134, 127, 129, 121, 136, 133, 121, 123, 148, 138, 125, 140, 125, 138, 136, 138, 125, 140, 134, 129, 119, 124, 125, 133, 121, 134, 125, 138, 85, 134, 129, 121, 128, 123, 119, 139, 143, 135, 124, 134, 129, 143, 148, 125, 133, 129, 140, 134, 141, 138, 119, 134, 135, 128, 140, 145, 136, 119, 125, 132, 122, 121, 124, 124, 125, 122, 133, 125, 85, 138, 125, 129, 138, 138, 121, 123, 148, 134, 121, 132, 136, 119, 125, 136, 135, 132, 125, 142, 134, 125, 119, 132, 121, 128, 139, 138, 121, 133, 85, 134, 135, 129, 140, 121, 123, 139, 141, 126, 122, 135, 148, 124, 135, 128, 140, 125, 133, 123, 129, 140, 121, 140, 139, 119, 139, 139, 121, 132, 123, 85, 144, 121, 140, 134, 145, 139, 148, 75, 85, 140, 134, 141, 135, 123, 119, 125, 127, 121, 140, 139, 148, 140, 136, 129, 138, 123, 139, 143, 119, 135, 140, 119, 134, 135, 128, 140, 145, 136, 85, 138, 125, 140, 136, 121, 124, 121, 148, 125, 127, 121, 140, 139, 119, 140, 144, 125, 134, 119, 128, 123, 140, 121, 136, 139, 129, 124, 68, 138, 125, 140, 125, 138, 136, 138, 125, 140, 134, 129, 119, 125, 140, 121, 123, 135, 132, 68, 134, 135, 129, 140, 121, 138, 141, 127, 129, 126, 134, 135, 123, 119, 125, 124, 135, 123, 125, 124, 85, 139, 136, 125, 140, 139, 148, 74, 85, 142]

CODEC_cbaccf0b = "reversed_integer_list|add_modulo_256|18"



def load_cbaccf0b():

    return bytes(reversed(MATERIAL_cbaccf0b))



def decode_cbaccf0b(item1):

    return bytes((value - 24) % 256 for value in item1)



def recover_cbaccf0b():

    item4 = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    _pass = 0

    while _pass < 1:

        item2 = decode_cbaccf0b(load_cbaccf0b())

        _pass += 1

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_cbaccf0b():

    view = memoryview(recover_cbaccf0b().encode("ascii"))

    return bytes(view).decode("ascii")



class Surface_surface_cbaccf0b:

    @staticmethod

    def recover():

        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")



def surface_cbaccf0b():

    return Surface_surface_cbaccf0b.recover()



def obfuscation_cbaccf0b():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_cbaccf0b():

    fields = dict(item.split("=", 1) for item in inspect_cbaccf0b().split("|"))

    analysis_surface = surface_cbaccf0b()

    obfuscation_surface = obfuscation_cbaccf0b()

    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_cbaccf0b())

