#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_fff3efe7 = ("lZWXx5GRkZOWk4jR1srNmMHM+tHWys3ZlZWXx5GRkZOWk4jLwszE1cjExpjBzPrLwszE1cjExtnA3cD6y8"

    "rN0dzV+tHGwNfMwZjLzMTNxvrW0srBy8zS2cDG19DK1vrSxNeY18DM19fExtncycvK+sjXysPWy8TX0ZjL"

    "yszRxMbW0MPHytnWy8rM0cbL0MP6y8zEydWY3cTRy9zW2ZSY0cvQysb6wMLE0dbZ3N3K19X6wsvM1dXEyJ"

    "jXwNHVxMHE2cvKzNHE19DCzMPLysb6y9fQ0cDXicvKzNHE19DCzMPLysb6wMHKxsDBmNbVwNHW2ZeY0w==")

CODEC_fff3efe7 = "base64_chunks|reverse_then_xor|a5"



def load_fff3efe7():

    return base64.b64decode(MATERIAL_fff3efe7)



def decode_fff3efe7(EnCoDeD_Bytes):

    return bytes(value ^ 165 for value in reversed(EnCoDeD_Bytes))



def recover_fff3efe7():

    NeUtRaL = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")

    try:

        DeCoDeD_Bytes = decode_fff3efe7(load_fff3efe7())

    except (TypeError, ValueError) as error:

        raise RuntimeError("configuration recovery failed") from error

    DeScRiPtOr_Text = DeCoDeD_Bytes.decode("ascii", "strict")

    return DeScRiPtOr_Text



def inspect_fff3efe7():

    stream = io.BytesIO(recover_fff3efe7().encode("ascii"))

    return stream.read().decode("ascii")



def surface_fff3efe7():

    return ("plain_functions", "transform_only", "raw_source", "direct_python_exe")



def obfuscation_fff3efe7():

    return "transform_only"



def plan_fff3efe7():

    fields = dict(item.split("=", 1) for item in inspect_fff3efe7().split("|"))

    analysis_surface = surface_fff3efe7()

    obfuscation_surface = obfuscation_fff3efe7()

    operation_plan = ("report", fields.get("host_id", ""))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_fff3efe7())

