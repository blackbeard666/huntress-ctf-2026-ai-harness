#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_10402ed2 = "eXAuZTMzYjY5ODI4ZC1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnxlMzNiNjk4MjhkLW5naWFwbWFjPWRpX25naWFwbWFjfHJvdHBpcmNzZWRfeWVrX251cj1uaWFoY19zd29kbml3fGlzbV9lemVlcmZfeGM9cmVpcnJhY3xuYWxwX2VtYW5fZXZpdGNlbGZlcj1ub2l0YWNzdWZib3xsb2NvdG9ycF9yb3RhcmV0aT14YXRueXN8MT10bnVvY19lZ2F0c3xlY2FscGVyX2VsaWZwbWV0PXJldHBhZGF8ZWxpZl9ldGlydyxkZWRkZWJtZV9lZG9jZWQ9c3BldHN8Mj12"

CODEC_10402ed2 = "base64_literal|reverse_bytes|"



def load_10402ed2():

    return base64.b64decode(MATERIAL_10402ed2)



def decode_10402ed2(stored_bytes):

    return bytes(reversed(stored_bytes))



def recover_10402ed2():

    harmless_value = 19 * 7 - 133

    decoder_function = decode_10402ed2

    recovered_bytes = decoder_function(load_10402ed2())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_10402ed2():

    return recover_10402ed2()



def surface_10402ed2():

    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))

    return tuple(iterator)



def obfuscation_10402ed2():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_10402ed2():

    fields = dict(item.split("=", 1) for item in inspect_10402ed2().split("|"))

    analysis_surface = surface_10402ed2()

    obfuscation_surface = obfuscation_10402ed2()

    operation_plan = ("tempfile_replace", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_10402ed2())

