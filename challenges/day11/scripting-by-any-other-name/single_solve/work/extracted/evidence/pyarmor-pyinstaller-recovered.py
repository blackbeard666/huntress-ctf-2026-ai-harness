#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_54cb2bff = (89, 32, 21, 95, 86, 87, 72, 83, 86, 32, 83, 85, 82, 73, 76, 79, 72, 66, 75, 82, 86, 87, 15, 68, 70, 84, 88, 76, 85, 72, 66, 85, 72, 80, 82, 87, 72, 15, 71, 72, 70, 82, 71, 72, 66, 72, 80, 69, 72, 71, 71, 72, 71, 15, 90, 85, 76, 87, 72, 66, 73, 76, 79, 72, 15, 71, 76, 86, 83, 68, 87, 70, 75, 66, 83, 85, 82, 70, 72, 86, 86, 95, 68, 71, 68, 83, 87, 72, 85, 32, 70, 83, 92, 87, 75, 82, 81, 66, 79, 82, 68, 71, 72, 85, 66, 75, 68, 81, 71, 82, 73, 73, 95, 86, 87, 68, 74, 72, 66, 70, 82, 88, 81, 87, 32, 24, 95, 86, 92, 81, 87, 68, 91, 32, 71, 76, 70, 87, 76, 82, 81, 68, 85, 92, 66, 71, 76, 86, 83, 68, 87, 70, 75, 95, 82, 69, 73, 88, 86, 70, 68, 87, 76, 82, 81, 32, 85, 72, 73, 79, 72, 70, 87, 76, 89, 72, 66, 81, 68, 80, 72, 66, 83, 79, 68, 81, 95, 70, 68, 85, 85, 76, 72, 85, 32, 83, 92, 68, 85, 80, 82, 85, 66, 83, 92, 76, 81, 86, 87, 68, 79, 79, 72, 85, 95, 90, 76, 81, 71, 82, 90, 86, 66, 70, 75, 68, 76, 81, 32, 83, 82, 90, 72, 85, 86, 75, 72, 79, 79, 66, 87, 82, 66, 83, 92, 87, 75, 82, 81, 95, 70, 68, 80, 83, 68, 76, 74, 81, 66, 76, 71, 32, 70, 68, 80, 83, 68, 76, 74, 81, 16, 21, 72, 21, 20, 26, 27, 27, 21, 69, 23, 95, 88, 85, 79, 32, 75, 87, 87, 83, 86, 29, 18, 18, 21, 72, 21, 20, 26, 27, 27, 21, 69, 23, 17, 72, 91, 68, 80, 83, 79, 72, 17, 76, 81, 89, 68, 79, 76, 71, 18, 22, 72, 23, 22, 28, 70, 70, 73, 17, 83, 92, 95, 88, 86, 72, 85, 66, 68, 74, 72, 81, 87, 32, 43, 88, 81, 87, 85, 72, 86, 86, 51, 92, 87, 75, 82, 81, 18, 21, 72, 21, 20, 26, 27, 27, 21, 69, 23, 95, 73, 76, 79, 72, 66, 83, 68, 87, 75, 32, 38, 29, 18, 51, 85, 82, 74, 85, 68, 80, 39, 68, 87, 68, 18, 43, 88, 81, 87, 85, 72, 86, 86, 47, 68, 69, 18, 17, 88, 83, 71, 68, 87, 72, 16, 21, 72, 21, 20, 26, 27, 27, 21, 69, 23, 17, 83, 92, 95, 76, 81, 87, 72, 85, 83, 85, 72, 87, 72, 85, 66, 83, 68, 87, 75, 32, 38, 29, 18, 51, 85, 82, 74, 85, 68, 80, 39, 68, 87, 68, 18, 51, 92, 87, 75, 82, 81, 16, 21, 72, 21, 20, 26, 27, 27, 21, 69, 23, 18, 83, 92, 87, 75, 82, 81, 17, 72, 91, 72, 95, 87, 68, 86, 78, 66, 81, 68, 80, 72, 32, 54, 92, 86, 87, 72, 80, 56, 83, 71, 68, 87, 72, 16, 21, 72, 21, 20, 26, 27, 27, 21, 69, 23, 95, 83, 85, 82, 91, 92, 66, 72, 81, 71, 83, 82, 76, 81, 87, 32, 20, 21, 26, 17, 19, 17, 19, 17, 20, 29, 21, 20, 27, 19, 28, 95, 81, 72, 91, 87, 66, 86, 87, 68, 74, 72, 32, 79, 82, 70, 68, 79, 16, 71, 76, 86, 83, 68, 87, 70, 75, 17, 69, 68, 87, 95, 75, 68, 81, 71, 82, 73, 73, 66, 76, 71, 32, 51, 54, 51, 60, 16, 40, 28, 20, 19, 19, 38, 23, 38, 23, 39, 25, 40, 36, 22, 22, 20,)

CODEC_54cb2bff = "integer_tuple|subtract_modulo_256|1d"



def load_54cb2bff():

    return bytes(MATERIAL_54cb2bff)



def decode_54cb2bff(EnCoDeD_Bytes):

    return bytes((value + 29) % 256 for value in EnCoDeD_Bytes)



def recover_54cb2bff():

    NeUtRaL = 19 * 7 - 133

    _pass = 0

    while _pass < 1:

        DeCoDeD_Bytes = decode_54cb2bff(load_54cb2bff())

        _pass += 1

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_54cb2bff():

    stream = io.BytesIO(recover_54cb2bff().encode("ascii"))

    return stream.read().decode("ascii")



def surface_54cb2bff():

    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}

    return routes["selected"]()



def obfuscation_54cb2bff():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_54cb2bff():

    fields = dict(item.split("=", 1) for item in inspect_54cb2bff().split("|"))

    analysis_surface = surface_54cb2bff()

    obfuscation_surface = obfuscation_54cb2bff()

    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_54cb2bff())

