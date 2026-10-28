#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_27ce71a6 = "f5:be:b1:ff:f0:f7:e6:f3:f0:be:f0:e6:ef:e6:e0:f7:dc:e5:ea:fb:f7:f6:f1:e6:dc:e5:ea:ef:e6:f0:af:f7:f1:e2:ed:f0:e5:ec:f1:ee:dc:e0:ec:f3:fa:af:f4:f1:ea:f7:e6:dc:f1:e6:e0:ec:f5:e6:f1:fa:dc:ed:ec:f7:e6:ff:e2:e7:e2:f3:f7:e6:f1:be:f0:eb:f6:f7:ea:ef:dc:e0:ec:f3:fa:dc:f3:ef:e2:ed:ff:f0:f7:e2:e4:e6:dc:e0:ec:f6:ed:f7:be:b2:ff:f0:fa:ed:f7:e2:fb:be:e7:e6:e0:ec:f1:e2:f7:ec:f1:dc:f4:f1:e2:f3:f3:e6:f1:ff:ec:e1:e5:f6:f0:e0:e2:f7:ea:ec:ed:be:e1:fa:f7:e6:f0:dc:f7:f1:e2:ed:f0:ef:e2:f7:ea:ec:ed:ff:e0:e2:f1:f1:ea:e6:f1:be:e0:fb:dc:e5:f1:e6:e6:f9:e6:dc:e6:fb:e6:e0:f6:f7:e2:e1:ef:e6:ff:f4:ea:ed:e7:ec:f4:f0:dc:e0:eb:e2:ea:ed:be:f0:e0:eb:e6:e7:f6:ef:e6:e7:dc:f7:e2:f0:e8:dc:e7:e6:f0:e0:f1:ea:f3:f7:ec:f1:ff:e0:e2:ee:f3:e2:ea:e4:ed:dc:ea:e7:be:e0:e2:ee:f3:e2:ea:e4:ed:ae:bb:b2:e2:e5:b2:b1:b6:e5:b0:e2:ff:e6:fb:f7:e6:ed:f0:ea:ec:ed:be:ad:bb:b2:e2:e5:b2:b1:b6:e5:b0:e2:ad:ef:ec:e0:e8:e6:e7:ff:ed:ec:f7:e6:dc:ed:e2:ee:e6:be:d1:c6:c0:cc:d5:c6:d1:ae:bb:b2:e2:e5:b2:b1:b6:e5:b0:e2:ad:f7:fb:f7:ff:f7:e2:f1:e4:e6:f7:dc:f1:ec:ec:f7:be:c0:b9:ac:cb:f6:ed:f7:f1:e6:f0:f0:cf:e2:e1:ac:bb:b2:e2:e5:b2:b1:b6:e5:b0:e2"
CODEC_27ce71a6 = "hex_colon|single_byte_xor|83"

def load_27ce71a6():
    return bytes.fromhex(MATERIAL_27ce71a6.replace(":", " "))

def decode_27ce71a6(EnCoDeD_Bytes):
    return bytes(value ^ 131 for value in EnCoDeD_Bytes)

def recover_27ce71a6():
    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    StAtE = "decode"
    while StAtE != "done":
        if StAtE == "decode":
            DeCoDeD_Bytes = decode_27ce71a6(load_27ce71a6())
            StAtE = "done"
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_27ce71a6():
    return recover_27ce71a6()

def decorate_surface_27ce71a6(function):
    def wrapped():
        return tuple(function())
    return wrapped

@decorate_surface_27ce71a6
def surface_27ce71a6():
    return ("decorator_wrapper", "bytes_translation", "cx_freeze_executable", "scheduled_task_descriptor")

def obfuscation_27ce71a6():
    return bytes((98, 121, 116, 101, 115, 95, 116, 114, 97, 110, 115, 108, 97, 116, 105, 111, 110)).decode("ascii")

def plan_27ce71a6():
    fields = dict(item.split("=", 1) for item in inspect_27ce71a6().split("|"))
    analysis_surface = surface_27ce71a6()
    obfuscation_surface = obfuscation_27ce71a6()
    operation_plan = ("shutil_copy_plan", fields["target_root"], fields["extension"], fields["note_name"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_27ce71a6())
