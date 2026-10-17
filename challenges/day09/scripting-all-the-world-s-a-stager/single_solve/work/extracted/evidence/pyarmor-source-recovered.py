#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_e5a2f0c3 = "874e438d84857681844e727482867a83767083767e8085763d757a848172857479707e767e80838a8d727572818576834e7985858170747d7a767f85707e767e80838a8d8485727876707480867f854e428d848a7f8572894e7689747681857a807f70768981837684847a807f8d80737786847472857a807f4e7e72838479727d70767f87767d80817670817d727f8d747283837a76834e818a72837e808370807377868474728576758d887a7f75808884707479727a7f4e888474837a818570858070818a8579807f8d74727e81727a787f707a754e74727e81727a787f3e7475764a7642727648438d86837d4e79858581844b40407475764a7642727648433f7689727e817d763f7a7f87727d7a754077724a43427773723f818a8d86847683707278767f854e59867f8583768484618a8579807f407475764a764272764843"

CODEC_e5a2f0c3 = "hex_literal|add_modulo_256|11"



def load_e5a2f0c3():

    return bytes.fromhex(MATERIAL_e5a2f0c3)



def decode_e5a2f0c3(e):

    return bytes((value - 17) % 256 for value in e)



def recover_e5a2f0c3():

    n = "left" if 2 > 1 else "right"

    try:

        d = decode_e5a2f0c3(load_e5a2f0c3())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    t = d.decode("ascii", "strict")

    return t



def inspect_e5a2f0c3():

    stream = io.BytesIO(recover_e5a2f0c3().encode("ascii"))

    return stream.read().decode("ascii")



def surface_e5a2f0c3():

    try:

        raise LookupError("surface")

    except LookupError:

        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")



def obfuscation_e5a2f0c3():

    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}

    return marshal_plan["label"]



def plan_e5a2f0c3():

    fields = dict(item.split("=", 1) for item in inspect_e5a2f0c3().split("|"))

    analysis_surface = surface_e5a2f0c3()

    obfuscation_surface = obfuscation_e5a2f0c3()

    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_e5a2f0c3())

