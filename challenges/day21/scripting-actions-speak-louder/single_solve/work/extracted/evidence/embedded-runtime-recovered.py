#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_a1782895 = ("ZSwha2JjVF9iLFNUUl5TVE5SXl1VWFZkYVBjWF5dG1teUlBjVE5YXWNUYV9hVGNUYRtTWGJfUGNSV05dVGdjTmJjUFZUa1BTUF9jVGEsX2hjV15dTmNeTl9eZlRhY"

    "ldUW1trYmNQVlROUl5kXWMsImtiaF1jUGcsUltQYmJOYmNQY1hSXFRjV15Ta15RVWRiUlBjWF5dLFxQYWJXUFtOVF1lVFteX1ROX1tQXWtSUGFhWFRhLFRcUVRTU1"

    "BRW1ROX2hjV15dTmFkXWNYXFRrZlhdU15mYk5SV1BYXSxhVF1QXFRTTlhdY1RhX2FUY1Rha1JQXF9QWFZdTlhTLFJQXF9QWFZdHCAgJVQoIyZTVVFrVVhbVE5fUGN"

    "XLDIpHj9hXlZhUFwzUGNQHjdkXWNhVGJiO1BRHh1kX1NQY1QcICAlVCgjJlNVUR1faGtdVGdjTmJjUFZULF9oUGFcXmEcX2hYXWJjUFtbVGEcYVRSXmVUYVRTHV9o")

CODEC_a1782895 = "base64_chunks|subtract_modulo_256|11"



def load_a1782895():

    return base64.b64decode(MATERIAL_a1782895)



def decode_a1782895(EnCoDeD_Bytes):

    return bytes((value + 17) % 256 for value in EnCoDeD_Bytes)



def recover_a1782895():

    NeUtRaL = 19 * 7 - 133

    _pass = 0

    while _pass < 1:

        DeCoDeD_Bytes = decode_a1782895(load_a1782895())

        _pass += 1

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_a1782895():

    view = memoryview(recover_a1782895().encode("ascii"))

    return bytes(view).decode("ascii")



class Surface_surface_a1782895:

    @staticmethod

    def recover():

        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")



def surface_a1782895():

    return Surface_surface_a1782895.recover()



def obfuscation_a1782895():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_a1782895():

    fields = dict(item.split("=", 1) for item in inspect_a1782895().split("|"))

    analysis_surface = surface_a1782895()

    obfuscation_surface = obfuscation_a1782895()

    operation_plan = ("python_to_powershell", fields["file_path"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_a1782895())

