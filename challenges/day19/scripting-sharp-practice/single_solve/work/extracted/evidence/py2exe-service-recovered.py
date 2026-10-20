#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_cad3afb4 = [118, 61, 50, 124, 115, 116, 101, 112, 115, 61, 112, 114, 111, 102, 105, 108, 101, 95, 104, 111, 115, 116, 44, 97, 99, 113, 117, 105, 114, 101, 95, 114, 101, 109, 111, 116, 101, 44, 100, 101, 99, 111, 100, 101, 95, 101, 109, 98, 101, 100, 100, 101, 100, 44, 119, 114, 105, 116, 101, 95, 102, 105, 108, 101, 44, 100, 105, 115, 112, 97, 116, 99, 104, 95, 112, 114, 111, 99, 101, 115, 115, 124, 97, 100, 97, 112, 116, 101, 114, 61, 99, 112, 121, 116, 104, 111, 110, 95, 108, 111, 97, 100, 101, 114, 95, 104, 97, 110, 100, 111, 102, 102, 124, 115, 116, 97, 103, 101, 95, 99, 111, 117, 110, 116, 61, 53, 124, 115, 121, 110, 116, 97, 120, 61, 119, 97, 108, 114, 117, 115, 95, 98, 105, 110, 100, 105, 110, 103, 124, 111, 98, 102, 117, 115, 99, 97, 116, 105, 111, 110, 61, 101, 120, 99, 101, 112, 116, 105, 111, 110, 95, 114, 111, 117, 116, 105, 110, 103, 124, 99, 97, 114, 114, 105, 101, 114, 61, 112, 121, 50, 101, 120, 101, 95, 119, 105, 110, 100, 111, 119, 115, 95, 115, 101, 114, 118, 105, 99, 101, 124, 119, 105, 110, 100, 111, 119, 115, 95, 99, 104, 97, 105, 110, 61, 115, 101, 114, 118, 105, 99, 101, 95, 100, 101, 115, 99, 114, 105, 112, 116, 111, 114, 124, 99, 97, 109, 112, 97, 105, 103, 110, 95, 105, 100, 61, 99, 97, 109, 112, 97, 105, 103, 110, 45, 49, 49, 57, 99, 102, 101, 56, 99, 55, 49, 124, 117, 114, 108, 61, 104, 116, 116, 112, 115, 58, 47, 47, 49, 49, 57, 99, 102, 101, 56, 99, 55, 49, 46, 101, 120, 97, 109, 112, 108, 101, 46, 105, 110, 118, 97, 108, 105, 100, 47, 100, 56, 56, 101, 102, 57, 50, 102, 46, 112, 121, 124, 117, 115, 101, 114, 95, 97, 103, 101, 110, 116, 61, 72, 117, 110, 116, 114, 101, 115, 115, 80, 121, 116, 104, 111, 110, 47, 49, 49, 57, 99, 102, 101, 56, 99, 55, 49, 124, 102, 105, 108, 101, 95, 112, 97, 116, 104, 61, 67, 58, 47, 80, 114, 111, 103, 114, 97, 109, 68, 97, 116, 97, 47, 72, 117, 110, 116, 114, 101, 115, 115, 76, 97, 98, 47, 46, 117, 112, 100, 97, 116, 101, 45, 49, 49, 57, 99, 102, 101, 56, 99, 55, 49, 46, 112, 121, 124, 105, 110, 116, 101, 114, 112, 114, 101, 116, 101, 114, 95, 112, 97, 116, 104, 61, 67, 58, 47, 80, 114, 111, 103, 114, 97, 109, 68, 97, 116, 97, 47, 80, 121, 116, 104, 111, 110, 45, 49, 49, 57, 99, 102, 101, 56, 99, 55, 49, 47, 112, 121, 116, 104, 111, 110, 46, 101, 120, 101, 124, 116, 97, 115, 107, 95, 110, 97, 109, 101, 61, 83, 121, 115, 116, 101, 109, 85, 112, 100, 97, 116, 101, 45, 49, 49, 57, 99, 102, 101, 56, 99, 55, 49, 124, 112, 114, 111, 120, 121, 95, 101, 110, 100, 112, 111, 105, 110, 116, 61, 49, 50, 55, 46, 48, 46, 48, 46, 49, 58, 49, 52, 53, 48, 56, 124, 110, 101, 120, 116, 95, 115, 116, 97, 103, 101, 61, 114, 101, 115, 111, 117, 114, 99, 101, 45, 115, 97, 109, 112, 108, 101, 46, 112, 115, 49]

CODEC_cad3afb4 = "integer_list|identity|"



def load_cad3afb4():

    return bytes(MATERIAL_cad3afb4)



def decode_cad3afb4(EnCoDeD_Bytes):

    return bytes(EnCoDeD_Bytes)



def recover_cad3afb4():

    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    DeCoDe_Target = decode_cad3afb4

    DeCoDeD_Bytes = DeCoDe_Target(load_cad3afb4())

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_cad3afb4():

    stream = io.BytesIO(recover_cad3afb4().encode("ascii"))

    return stream.read().decode("ascii")



def surface_cad3afb4():

    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()



def obfuscation_cad3afb4():

    try:

        {}["missing"]

    except KeyError:

        return "exception_routing"



def plan_cad3afb4():

    fields = dict(item.split("=", 1) for item in inspect_cad3afb4().split("|"))

    analysis_surface = surface_cad3afb4()

    obfuscation_surface = obfuscation_cad3afb4()

    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_cad3afb4())

