#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_c4b390f4 = "eXAuZGVyZXZvY2VyLXJlbGxhdHNuaXlwLXJvbXJheXA9ZWdhdHNfdHhlbnx5cC5hMjFkNjExNmEyLWV0YWRwdS4vYmFMc3NlcnRudUgvYXRhRG1hcmdvclAvOkM9aHRhcF9lbGlmfGEyMWQ2MTE2YTItbmdpYXBtYWM9ZGlfbmdpYXBtYWN8cmV0ZXJwcmV0bmlfZGVtYW5lcj1uaWFoY19zd29kbml3fGVtaXRudXJfbm9odHlwX2VsYmFkZGVibWU9cmVpcnJhY3xuYWxwX2Vwb2xldm5lX2xhaHNyYW09bm9pdGFjc3VmYm98ZG9odGVtY2l0YXRzX3NzYWxjPXhhdG55c3wzPXRudW9jX2VnYXRzfHRwaXJjc3dfb3Rfbm9odHlwPXJldHBhZGF8ZWdhdHNfdHhlbl9oY3RhcHNpZCxyZXRlcnByZXRuaV9ldGFjb2wsbm9pdGFydWdpZm5vY19lZG9jZWQ9c3BldHN8Mj12"

CODEC_c4b390f4 = "urlsafe_base64|reverse_bytes|"



def load_c4b390f4():

    return base64.urlsafe_b64decode(MATERIAL_c4b390f4)



def decode_c4b390f4(item1):

    return bytes(reversed(item1))



def recover_c4b390f4():

    item4 = ":".join(("north", "south"))

    item2 = decode_c4b390f4(load_c4b390f4())

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_c4b390f4():

    stream = io.BytesIO(recover_c4b390f4().encode("ascii"))

    return stream.read().decode("ascii")



class Surface_surface_c4b390f4:

    @staticmethod

    def recover():

        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")



def surface_c4b390f4():

    return Surface_surface_c4b390f4.recover()



def obfuscation_c4b390f4():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_c4b390f4():

    fields = dict(item.split("=", 1) for item in inspect_c4b390f4().split("|"))

    analysis_surface = surface_c4b390f4()

    obfuscation_surface = obfuscation_c4b390f4()

    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_c4b390f4())

