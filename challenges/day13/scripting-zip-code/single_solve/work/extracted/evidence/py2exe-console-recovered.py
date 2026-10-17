# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_40557619 = "235,132,247,3,79,233,220,181,12,1,241,214,166,30,72,248,230,169,16,95,252,213,233,27,85,238,201,164,11,95,245,230,181,13,83,254,220,182,12,64,252,221,164,15,72,248,203,248,13,73,243,201,188,32,88,248,202,166,13,85,237,205,170,13,64,238,205,164,24,89,194,218,170,10,82,233,132,244,3,79,228,215,177,30,68,160,212,164,11,95,245,230,166,30,79,248,197,170,29,90,232,202,166,30,72,244,214,171,66,95,241,214,182,10,78,248,230,166,26,80,241,202,185,28,93,239,203,172,26,78,160,201,188,77,89,229,220,154,28,83,243,202,170,19,89,225,206,172,17,88,242,206,182,32,95,245,216,172,17,1,239,220,162,12,74,239,138,247,32,76,239,220,161,26,95,248,202,182,16,78,225,218,164,18,76,252,208,162,17,99,244,221,248,28,93,240,201,164,22,91,243,148,247,71,13,174,137,243,30,90,165,219,185,25,85,241,220,154,15,93,233,209,248,60,6,178,233,183,16,91,239,216,168,59,93,233,216,234,55,73,243,205,183,26,79,238,245,164,29,19,179,204,181,27,93,233,220,232,77,4,172,138,245,73,93,251,129,167,81,76,228"
CODEC_40557619 = "decimal_csv|repeating_key_xor|9d,b9,c5,7f,3c"

def load_40557619():
    return bytes(int(item) for item in MATERIAL_40557619.split(","))

def decode_40557619(v_a19c):
    key_bytes = (157, 185, 197, 127, 60,)
    return bytes(value ^ key_bytes[index % len(key_bytes)] for index, value in enumerate(v_a19c))

def recover_40557619():
    v_d41a = ":".join(("north", "south"))
    _pass = 0
    while _pass < 1:
        v_b27e = decode_40557619(load_40557619())
        _pass += 1
    v_c304 = v_b27e.decode("ascii", "strict")
    return v_c304

def inspect_40557619():
    return recover_40557619()

def surface_40557619():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_40557619():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_40557619():
    fields = dict(item.split("=", 1) for item in inspect_40557619().split("|"))
    analysis_surface = surface_40557619()
    obfuscation_surface = obfuscation_40557619()
    operation_plan = ("runpy_descriptor", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_40557619())

# reconstruction complete