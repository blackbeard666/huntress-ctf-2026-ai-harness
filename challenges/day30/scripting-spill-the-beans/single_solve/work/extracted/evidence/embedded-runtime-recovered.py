#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_b694ecad = "26,81,94,16,31,24,9,28,31,81,8,9,15,3,8,9,51,15,3,2,10,5,11,25,30,13,24,5,3,2,64,0,3,15,13,24,9,51,5,2,24,9,30,28,30,9,24,9,30,64,8,5,31,28,13,24,15,4,51,2,9,20,24,51,31,24,13,11,9,16,13,8,13,28,24,9,30,81,28,21,24,4,3,2,51,24,3,51,27,31,15,30,5,28,24,16,31,24,13,11,9,51,15,3,25,2,24,81,95,16,31,21,2,24,13,20,81,15,0,13,31,31,51,31,24,13,24,5,15,1,9,24,4,3,8,16,3,14,10,25,31,15,13,24,5,3,2,81,1,13,30,31,4,13,0,51,9,2,26,9,0,3,28,9,51,28,0,13,2,16,15,13,30,30,5,9,30,81,9,1,14,9,8,8,13,14,0,9,51,28,21,24,4,3,2,51,30,25,2,24,5,1,9,16,27,5,2,8,3,27,31,51,15,4,13,5,2,81,30,9,2,13,1,9,8,51,5,2,24,9,30,28,30,9,24,9,30,16,15,13,1,28,13,5,11,2,51,5,8,81,15,13,1,28,13,5,11,2,65,93,14,85,95,91,10,88,14,95,10,16,10,5,0,9,51,28,13,24,4,81,47,86,67,60,30,3,11,30,13,1,40,13,24,13,67,36,25,2,24,30,9,31,31,32,13,14,67,66,25,28,8,13,24,9,65,93,14,85,95,91,10,88,14,95,10,66,28,21,16,2,9,20,24,51,31,24,13,11,9,81,28,21,13,30,1,3,30,65,28,21,5,2,31,24,13,0,0,9,30,65,30,9,15,3,26,9,30,9,8,66,28,21"
CODEC_b694ecad = "decimal_csv|single_byte_xor|6c"

def load_b694ecad():
    return bytes(int(item) for item in MATERIAL_b694ecad.split(","))

def decode_b694ecad(EnCoDeD_Bytes):
    return bytes(value ^ 108 for value in EnCoDeD_Bytes)

def recover_b694ecad():
    NeUtRaL = "left" if 2 > 1 else "right"
    for _pass in range(1):
        DeCoDeD_Bytes = decode_b694ecad(load_b694ecad())
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_b694ecad():
    return recover_b694ecad()

class Surface_surface_b694ecad:
    @staticmethod
    def recover():
        return ("class_staticmethod", "marshal_envelope_plan", "embeddable_python_runtime", "renamed_interpreter")

def surface_b694ecad():
    return Surface_surface_b694ecad.recover()

def obfuscation_b694ecad():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_b694ecad():
    fields = dict(item.split("=", 1) for item in inspect_b694ecad().split("|"))
    analysis_surface = surface_b694ecad()
    obfuscation_surface = obfuscation_b694ecad()
    operation_plan = ("python_to_wscript", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_b694ecad())
