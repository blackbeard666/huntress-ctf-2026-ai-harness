#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_0516d987 = "7c:43:38:82:79:7a:6b:76:79:43:6a:6b:69:75:6a:6b:65:69:75:74:6c:6f:6d:7b:78:67:7a:6f:75:74:32:72:75:69:67:7a:6b:65:6f:74:7a:6b:78:76:78:6b:7a:6b:78:32:6a:6f:79:76:67:7a:69:6e:65:74:6b:7e:7a:65:79:7a:67:6d:6b:82:67:6a:67:76:7a:6b:78:43:76:7f:7a:6e:75:74:65:7a:75:65:7d:79:69:78:6f:76:7a:82:79:7a:67:6d:6b:65:69:75:7b:74:7a:43:39:82:79:7f:74:7a:67:7e:43:69:72:67:79:79:65:79:7a:67:7a:6f:69:73:6b:7a:6e:75:6a:82:75:68:6c:7b:79:69:67:7a:6f:75:74:43:73:67:78:79:6e:67:72:65:6b:74:7c:6b:72:75:76:6b:65:76:72:67:74:82:69:67:78:78:6f:6b:78:43:6b:73:68:6b:6a:6a:67:68:72:6b:65:76:7f:7a:6e:75:74:65:78:7b:74:7a:6f:73:6b:82:7d:6f:74:6a:75:7d:79:65:69:6e:67:6f:74:43:78:6b:74:67:73:6b:6a:65:6f:74:7a:6b:78:76:78:6b:7a:6b:78:82:69:67:73:76:67:6f:6d:74:65:6f:6a:43:69:67:73:76:67:6f:6d:74:33:6a:3c:36:36:68:3a:68:3e:6b:69:82:6c:6f:72:6b:65:76:67:7a:6e:43:49:40:35:56:78:75:6d:78:67:73:4a:67:7a:67:35:4e:7b:74:7a:78:6b:79:79:52:67:68:35:34:7b:76:6a:67:7a:6b:33:6a:3c:36:36:68:3a:68:3e:6b:69:34:76:7f:82:74:6b:7e:7a:65:79:7a:67:6d:6b:43:76:7f:67:78:73:75:78:33:76:7f:6f:74:79:7a:67:72:72:6b:78:33:78:6b:69:75:7c:6b:78:6b:6a:34:76:7f"

CODEC_0516d987 = "hex_colon|add_modulo_256|06"



def load_0516d987():

    return bytes.fromhex(MATERIAL_0516d987.replace(":", " "))



def decode_0516d987(e):

    return bytes((value - 6) % 256 for value in e)



def recover_0516d987():

    n = None

    _pass = 0

    while _pass < 1:

        d = decode_0516d987(load_0516d987())

        _pass += 1

    t = d.decode("ascii", "strict")

    return t



def inspect_0516d987():

    view = memoryview(recover_0516d987().encode("ascii"))

    return bytes(view).decode("ascii")



class Surface_surface_0516d987:

    @staticmethod

    def recover():

        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")



def surface_0516d987():

    return Surface_surface_0516d987.recover()



def obfuscation_0516d987():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_0516d987():

    fields = dict(item.split("=", 1) for item in inspect_0516d987().split("|"))

    analysis_surface = surface_0516d987()

    obfuscation_surface = obfuscation_0516d987()

    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_0516d987())

