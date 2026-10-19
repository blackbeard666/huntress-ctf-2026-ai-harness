#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_7156bff0 = "9Mn7h_SA5ZXm27_auday14jtgOKH44fihqrdr8ay14juh-uO8pP3luaS94W40bzMo9GlyaDCne-K-ZbjkfKXyL_NpNC1ybrOr8it8pH-i-WRrJ3hkuuF8ZDo1bzIrd--yqXXiPiK5ZH-nfKe4o3vifyP7I35kP-RrN673bHUt8Oq3LnmiOmE4b7OosOt0bLTodO6362Q84vUssClwLrfgO2e94v8lfuf8If0q8igwajG-4n8ks2mw7rlgeSX9Ibvn-uE9orpiOWV9J36lMuixvuY-ZTkheyL5cj_z_jOrZ3-zqqc4Ibvg-a5yajctInK8N-P_ZL1h-aLz67au5TcqcezwaTXpOiJ68Tqn--L6p771uHR5tCzg-DQtIKs3KU="

CODEC_7156bff0 = "urlsafe_base64|rolling_xor|82"



def load_7156bff0():

    return base64.urlsafe_b64decode(MATERIAL_7156bff0)



def decode_7156bff0(stored_bytes):

    recovered_bytes = bytearray()

    prior_byte = 130

    for value in stored_bytes:

        recovered_bytes.append(value ^ prior_byte)

        prior_byte = value

    return bytes(recovered_bytes)



def recover_7156bff0():

    harmless_value = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    decoder_function = decode_7156bff0

    recovered_bytes = decoder_function(load_7156bff0())

    configuration_text = recovered_bytes.decode("ascii", "strict")

    return configuration_text



def inspect_7156bff0():

    view = memoryview(recover_7156bff0().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_7156bff0():

    iterator = iter(("iterator_protocol", "reflective_name_plan", "cx_freeze_msi", "run_key_descriptor"))

    return tuple(iterator)



def obfuscation_7156bff0():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_7156bff0():

    fields = dict(item.split("=", 1) for item in inspect_7156bff0().split("|"))

    analysis_surface = surface_7156bff0()

    obfuscation_surface = obfuscation_7156bff0()

    operation_plan = ("importlib_resource_write", "decode", fields["file_path"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_7156bff0())

