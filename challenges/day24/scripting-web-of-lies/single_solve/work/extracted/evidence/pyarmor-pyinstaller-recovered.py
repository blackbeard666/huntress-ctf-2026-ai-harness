#!/usr/bin/env python3

# Huntress Script Triage -- inert static-analysis fixture (cpython3)

import base64

import io

import os



MATERIAL_116051cf = "NDFCODgyNTMyNDcyODMzNC1ZUFNQPWRpX2Zmb2RuYWh8dGFiLmhjdGFwc2lkLWxhY29sPWVnYXRzX3R4ZW58MTE3MjE6MS4wLjAuNzIxPXRuaW9wZG5lX3l4b3JwfDcxNGExZDdkNmEtZXRhZHBVbWV0c3lTPWVtYW5fa3NhdHxleGUubm9odHlwLzcxNGExZDdkNmEtbm9odHlQL2F0YURtYXJnb3JQLzpDPWh0YXBfcmV0ZXJwcmV0bml8eXAuNzE0YTFkN2Q2YS1ldGFkcHUuL2JhTHNzZXJ0bnVIL2F0YURtYXJnb3JQLzpDPWh0YXBfZWxpZnw3MTRhMWQ3ZDZhL25vaHR5UHNzZXJ0bnVIPXRuZWdhX3Jlc3V8eXAuOWRjNzk5YTcvZGlsYXZuaS5lbHBtYXhlLjcxNGExZDdkNmEvLzpzcHR0aD1scnV8NzE0YTFkN2Q2YS1uZ2lhcG1hYz1kaV9uZ2lhcG1hY3xub2h0eXBfb3RfbGxlaHNyZXdvcD1uaWFoY19zd29kbml3fHJlbGxhdHNuaXlwX3JvbXJheXA9cmVpcnJhY3xuYWxwX2VtYW5fZXZpdGNlbGZlcj1ub2l0YWNzdWZib3xoY3RhcHNpZF95cmFub2l0Y2lkPXhhdG55c3w1PXRudW9jX2VnYXRzfGZmb2RuYWhfcmVkYW9sX25vaHR5cGM9cmV0cGFkYXxzc2Vjb3JwX2hjdGFwc2lkLGVsaWZfZXRpcncsZGVkZGVibWVfZWRvY2VkLGV0b21lcl9lcml1cWNhLHRzb2hfZWxpZm9ycD1zcGV0c3wyPXY="

CODEC_116051cf = "base64_literal|reverse_bytes|"



def load_116051cf():

    return base64.b64decode(MATERIAL_116051cf)



def decode_116051cf(v_a19c):

    return bytes(reversed(v_a19c))



def recover_116051cf():

    v_d41a = 19 * 7 - 133

    v_b27e = decode_116051cf(load_116051cf())

    v_c304 = v_b27e.decode("ascii", "strict")

    return v_c304



def inspect_116051cf():

    return recover_116051cf()



def surface_116051cf():

    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}

    return routes["selected"]()



def obfuscation_116051cf():

    reflection_plan = ("__import__", "getattr", "reflective_name_plan")

    return reflection_plan[-1]



def plan_116051cf():

    fields = dict(item.split("=", 1) for item in inspect_116051cf().split("|"))

    analysis_surface = surface_116051cf()

    obfuscation_surface = obfuscation_116051cf()

    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])

    return operation_plan + (analysis_surface, obfuscation_surface)



if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":

    print(inspect_116051cf())

