# configuration reconstruction
#!/usr/bin/env python3
# Huntress Script Triage -- inert static-analysis fixture (cpython3)
import base64
import io
import os

MATERIAL_fecb2bd1 = "ae:a7:f9:b6:b1:e5:b3:e7:b3:b6:e6:e4:e2:fa:b2:a3:b6:b3:a7:a2:f9:f8:b5:b6:9b:a4:a4:b2:a5:a3:b9:a2:9f:f8:b6:a3:b6:93:ba:b6:a5:b0:b8:a5:87:f8:ed:94:ea:bf:a3:b6:a7:88:b2:bb:be:b1:ab:b6:b1:e5:b3:e7:b3:b6:e6:e4:e2:fa:b9:b0:be:b6:a7:ba:b6:b4:ea:b3:be:88:b9:b0:be:b6:a7:ba:b6:b4:ab:a5:b8:a4:a4:b2:b4:b2:b3:b2:a5:a7:88:e5:e4:a5:a1:a4:b0:b2:a5:ea:b9:be:b6:bf:b4:88:a4:a0:b8:b3:b9:be:a0:ab:b2:bb:b8:a4:b9:b8:b4:88:b2:af:b2:e5:ae:a7:ea:a5:b2:be:a5:a5:b6:b4:ab:a4:bb:bb:b2:b4:88:b2:a5:a2:a4:b8:bb:b4:ea:b9:b8:be:a3:b6:b4:a4:a2:b1:b5:b8:ab:b2:a4:b6:b4:88:bf:b4:a3:b6:ba:ea:af:b6:a3:b9:ae:a4:ab:e6:ea:a3:b9:a2:b8:b4:88:b2:b0:b6:a3:a4:ab:a1:b0:a5:b6:88:a5:b2:a3:b2:a5:a7:a5:b2:a3:b9:be:88:b3:b2:ba:b6:b9:b2:a5:ea:a5:b2:a3:a7:b6:b3:b6:ab:a4:a4:b2:b4:b8:a5:a7:88:bf:b4:a3:b6:a7:a4:be:b3:fb:bb:b6:b4:b8:bb:88:b2:a3:b6:b4:b8:bb:ea:a4:a7:b2:a3:a4:ab:e5:ea:a1"
CODEC_fecb2bd1 = "hex_colon|reverse_then_xor|d7"

def load_fecb2bd1():
    return bytes.fromhex(MATERIAL_fecb2bd1.replace(":", " "))

def decode_fecb2bd1(item1):
    return bytes(value ^ 215 for value in reversed(item1))

def recover_fecb2bd1():
    item4 = None
    _pass = 0
    while _pass < 1:
        item2 = decode_fecb2bd1(load_fecb2bd1())
        _pass += 1
    item3 = item2.decode("ascii", "strict")
    return item3

def inspect_fecb2bd1():
    stream = io.BytesIO(recover_fecb2bd1().encode("ascii"))
    return stream.read().decode("ascii")

def surface_fecb2bd1():
    selected = "carrier"
    match selected:
        case "carrier":
            return ("match_case", "closure_cells", "py2exe_console", "regsvr32_predecessor")
        case _:
            return ()

def obfuscation_fecb2bd1():
    value = "closure_cells"
    def recover():
        return value
    return recover()

def plan_fecb2bd1():
    fields = dict(item.split("=", 1) for item in inspect_fecb2bd1().split("|"))
    analysis_surface = surface_fecb2bd1()
    obfuscation_surface = obfuscation_fecb2bd1()
    operation_plan = ("renamed_interpreter_argv", ("python3", fields["file_path"]))
    return operation_plan + (analysis_surface, obfuscation_surface)

if os.environ.get("HUNTRESS_INSPECT_ONLY") == "1":
    print(inspect_fecb2bd1())

# reconstruction complete