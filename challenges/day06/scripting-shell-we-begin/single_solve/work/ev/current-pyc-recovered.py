#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_6a8a1e75 = "/MHzj/yI7Z3u07/Qs9Kmw5zwn/yd8d250KPTssalzZLikP+c+Yr5heSA4ZHlgPLPpsi82avbqcy43a/wkeOE8o79ieiP6rXWucyi1uvaptWswrbXr5LxnfKB9IbjvNq72KzDsci027nfqtm626/Gqcf6mfGD3LbZsN6iwaDSoMms3uOL6pnxrsyt3rvfgPCJ6rXWo9GjxqjcoNe+0LTbrN+A44vqg+3QoNmtxarEs+yE7YntiOa52rXbqMerzrLRsN2tzKXCrPOa/sOgwazcvdSz3fDJ/Mmqna7Pqp6n273UuN2C8pPnj7Lxy+S0xqnOvN2w9JXhgK/nkvyI+p/sn9Oy0P/RpNSw0aXA7dTh1LeAs9K3g7qU5J0="

CODEC_6a8a1e75 = "base64_literal|rolling_xor|8a"



def load_6a8a1e75():

    return base64.b64decode(MATERIAL_6a8a1e75)



def decode_6a8a1e75(v_a19c):

    v_b27e = bytearray()

    v_e598 = 138

    for value in v_a19c:

        v_b27e.append(value ^ v_e598)

        v_e598 = value

    return bytes(v_b27e)



def recover_6a8a1e75():

    v_d41a = (3, 5, 8, 13)[1:3]

    v_f602 = decode_6a8a1e75

    v_b27e = v_f602(load_6a8a1e75())

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_6a8a1e75():

    view = memoryview(recover_6a8a1e75().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_6a8a1e75():

    values = ("closure_factory", "chr_join", "hash_based_pyc_current", "pythonw_hidden_console")

    def inner():

        return values

    return inner()



def obfuscation_6a8a1e75():

    return "".join(chr(value) for value in (99, 104, 114, 95, 106, 111, 105, 110))



def plan_6a8a1e75():

    fields = dict(item.split("=", 1) for item in inspect_6a8a1e75().split("|"))

    analysis_surface = surface_6a8a1e75()

    obfuscation_surface = obfuscation_6a8a1e75()

    operation_plan = ("interpreter_argv", ("python3", fields["file_path"]))

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_6a8a1e75())

